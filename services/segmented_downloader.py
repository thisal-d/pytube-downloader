import http.client
import os
import queue
import re
import threading
import time
import urllib.request
from typing import BinaryIO
from urllib.parse import urljoin, urlsplit

from utils.logger import get_logger

_log = get_logger(__name__)

_RANGE_PARAM = re.compile(r"[&?]range=\d+-\d+")


def _mark_sparse(file: BinaryIO) -> None:
    """
    On Windows, flag the file as sparse so that a worker writing ahead of the others
    does not make NTFS zero-fill the not-yet-downloaded gap before it.
    """
    if os.name != "nt":
        return
    try:
        import ctypes
        import msvcrt
        from ctypes import wintypes

        fsctl_set_sparse = 0x000900C4
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.DeviceIoControl.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            wintypes.LPVOID,
        ]
        kernel32.DeviceIoControl.restype = wintypes.BOOL
        returned = wintypes.DWORD()
        if not kernel32.DeviceIoControl(
            msvcrt.get_osfhandle(file.fileno()), fsctl_set_sparse, None, 0, None, 0, ctypes.byref(returned), None
        ):
            _log.debug("could not mark file sparse: error %s", ctypes.get_last_error())
    except Exception as error:
        _log.debug("could not mark file sparse: %s", error)


class _RangeConnection:
    """One keep-alive HTTPS connection that fetches byte ranges of a single URL."""

    HEADERS = {"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"}
    TIMEOUT = 30
    MAX_REDIRECTS = 5

    def __init__(self, url: str):
        self.connection: http.client.HTTPConnection | None = None
        self._set_url(url)

    def _set_url(self, url: str) -> None:
        self.url = url
        parts = urlsplit(url)
        self.scheme = parts.scheme
        self.host = parts.hostname or ""
        self.port = parts.port
        self.target = parts.path + ("?" + parts.query if parts.query else "")

    def _connect(self) -> http.client.HTTPConnection:
        connection_class = http.client.HTTPSConnection if self.scheme == "https" else http.client.HTTPConnection
        proxy = urllib.request.getproxies().get(self.scheme)
        if proxy and not urllib.request.proxy_bypass(self.host):
            proxy_parts = urlsplit(proxy if "//" in proxy else "//" + proxy)
            connection = connection_class(proxy_parts.hostname or "", proxy_parts.port, timeout=self.TIMEOUT)
            connection.set_tunnel(self.host, self.port)
            return connection
        return connection_class(self.host, self.port, timeout=self.TIMEOUT)

    def open_range(self, start: int, end: int) -> http.client.HTTPResponse:
        for _ in range(self.MAX_REDIRECTS):
            if self.connection is None:
                self.connection = self._connect()
            self.connection.request("GET", f"{self.target}&range={start}-{end}", headers=self.HEADERS)
            response = self.connection.getresponse()
            if response.status in (301, 302, 303, 307, 308):
                location = response.getheader("Location")
                self.close()
                if not location:
                    raise OSError("redirect without a location")
                self._set_url(_RANGE_PARAM.sub("", urljoin(self.url, location)))
                continue
            if response.status not in (200, 206):
                self.close()
                raise OSError(f"HTTP {response.status} {response.reason}")
            return response
        raise OSError("too many redirects")

    def close(self) -> None:
        if self.connection is not None:
            try:
                self.connection.close()
            except Exception as error:
                _log.debug("connection close failed: %s", error)
            self.connection = None


class SegmentedDownloader:
    """
    Downloads one file over several connections at once.

    The file is split into byte ranges. Each worker keeps a single HTTPS connection
    open and pulls ranges from a shared queue, reading them into a reusable buffer
    and writing them straight to their offset in the output file. One connection
    fetching one range at a time (and reconnecting for each) is what capped the
    original downloader well below the line speed.
    """

    BUFFER_SIZE = 1024 * 1024
    MAX_ATTEMPTS = 6

    def __init__(self, url: str, file_size: int, file_path: str, connections: int = 8, chunk_size: int = 8388608):
        self.url = url
        self.file_size = file_size
        self.file_path = file_path
        self.chunk_size = max(int(chunk_size), 64 * 1024)

        self._segments: queue.Queue[tuple[int, int]] = queue.Queue()
        for start in range(0, file_size, self.chunk_size):
            self._segments.put((start, min(start + self.chunk_size, file_size) - 1))
        self.connections = max(1, min(int(connections), self._segments.qsize() or 1))

        self._lock = threading.Lock()
        self._bytes_downloaded = 0
        self._running = threading.Event()
        self._running.set()
        self._cancelled = threading.Event()
        self._workers: list[threading.Thread] = []
        self.error: Exception | None = None

    @property
    def bytes_downloaded(self) -> int:
        return self._bytes_downloaded

    @property
    def finished(self) -> bool:
        """True once every worker has stopped, whether it succeeded, failed or was cancelled."""
        return not any(worker.is_alive() for worker in self._workers)

    @property
    def succeeded(self) -> bool:
        return (
            self.finished
            and self.error is None
            and not self._cancelled.is_set()
            and self._bytes_downloaded == self.file_size
        )

    def start(self) -> None:
        # Create the file empty; workers extend it by writing at their own offsets.
        # Reserving the full size up front makes Windows write zeros for the whole file first.
        with open(self.file_path, "wb") as file:
            _mark_sparse(file)
        for _ in range(self.connections):
            worker = threading.Thread(target=self._work, daemon=True)
            self._workers.append(worker)
            worker.start()

    def pause(self) -> None:
        self._running.clear()

    def resume(self) -> None:
        self._running.set()

    def cancel(self) -> None:
        self._cancelled.set()
        self._running.set()  # release paused workers so they can exit

    def wait(self, timeout: float | None = None) -> None:
        for worker in self._workers:
            worker.join(timeout)

    def remove_file(self) -> None:
        try:
            os.remove(self.file_path)
        except OSError as error:
            _log.warning("remove partial file failed: %s", error)

    def _work(self) -> None:
        connection = _RangeConnection(self.url)
        buffer = memoryview(bytearray(self.BUFFER_SIZE))
        try:
            with open(self.file_path, "r+b", buffering=0) as file:
                while not self._cancelled.is_set():
                    try:
                        start, end = self._segments.get_nowait()
                    except queue.Empty:
                        return
                    self._download_segment(connection, buffer, file, start, end)
        except Exception as error:
            _log.error("segment download failed: %s", error)
            if self.error is None:
                self.error = error
            self.cancel()
        finally:
            connection.close()

    def _download_segment(
        self, connection: _RangeConnection, buffer: memoryview, file: BinaryIO, start: int, end: int
    ) -> None:
        position = start
        attempts = 0
        while position <= end:
            self._running.wait()
            if self._cancelled.is_set():
                return
            try:
                response = connection.open_range(position, end)
                file.seek(position)
                while position <= end:
                    # Never read past the range, whatever the server sends.
                    received = response.readinto(buffer[: min(len(buffer), end - position + 1)])
                    if not received:
                        break
                    file.write(buffer[:received])
                    position += received
                    attempts = 0
                    with self._lock:
                        self._bytes_downloaded += received
                    if not self._running.is_set() or self._cancelled.is_set():
                        break
                if position <= end:
                    # Paused, cancelled or cut short: this connection has unread data, so drop it.
                    connection.close()
                    if self._running.is_set() and not self._cancelled.is_set():
                        raise OSError(f"incomplete range {position}-{end}")
            except Exception as error:
                connection.close()
                attempts += 1
                if attempts >= self.MAX_ATTEMPTS:
                    raise
                _log.warning("range %s-%s failed (attempt %s): %s", position, end, attempts, error)
                time.sleep(min(0.5 * 2**attempts, 8))
