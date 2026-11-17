"""Tests for services/segmented_downloader.py against a local range-serving HTTP server."""

import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from services.segmented_downloader import SegmentedDownloader

PAYLOAD = os.urandom(3 * 1024 * 1024 + 12345)


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    fail_first_requests = 0
    delay = 0.0
    lock = threading.Lock()

    def do_GET(self):  # noqa: N802
        with _Handler.lock:
            fail = _Handler.fail_first_requests > 0
            if fail:
                _Handler.fail_first_requests -= 1
        if fail or "missing" in self.path:
            self.send_response(404 if "missing" in self.path else 503)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        start, end = map(int, re.search(r"range=(\d+)-(\d+)", self.path).groups())
        body = PAYLOAD[start : end + 1]
        time.sleep(_Handler.delay)
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture
def server_url():
    _Handler.fail_first_requests = 0
    _Handler.delay = 0.0
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}/video?id=1"
    server.shutdown()
    server.server_close()


def _run(downloader, timeout=30):
    downloader.start()
    deadline = time.time() + timeout
    while not downloader.finished and time.time() < deadline:
        time.sleep(0.01)
    return downloader


def test_downloads_file_byte_for_byte(server_url, tmp_path):
    path = tmp_path / "out.bin"
    downloader = _run(SegmentedDownloader(server_url, len(PAYLOAD), str(path), connections=8, chunk_size=256 * 1024))
    assert downloader.succeeded
    assert downloader.bytes_downloaded == len(PAYLOAD)
    assert path.read_bytes() == PAYLOAD


def test_single_connection_and_file_smaller_than_chunk(server_url, tmp_path):
    path = tmp_path / "out.bin"
    downloader = _run(SegmentedDownloader(server_url, 1000, str(path), connections=8, chunk_size=8 * 1024 * 1024))
    assert downloader.connections == 1
    assert downloader.succeeded
    assert path.read_bytes() == PAYLOAD[:1000]


def test_retries_transient_errors(server_url, tmp_path, monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    _Handler.fail_first_requests = 3
    path = tmp_path / "out.bin"
    downloader = _run(SegmentedDownloader(server_url, len(PAYLOAD), str(path), connections=2, chunk_size=1024 * 1024))
    assert downloader.succeeded
    assert path.read_bytes() == PAYLOAD


def test_reports_failure_when_server_keeps_failing(server_url, tmp_path, monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    path = tmp_path / "out.bin"
    url = server_url.replace("video", "missing")
    downloader = _run(SegmentedDownloader(url, len(PAYLOAD), str(path), connections=4, chunk_size=1024 * 1024))
    assert downloader.finished
    assert not downloader.succeeded
    assert downloader.error is not None


def test_pause_resume_and_cancel(server_url, tmp_path):
    _Handler.delay = 0.05
    path = tmp_path / "out.bin"
    downloader = SegmentedDownloader(server_url, len(PAYLOAD), str(path), connections=2, chunk_size=128 * 1024)
    downloader.start()
    time.sleep(0.2)
    downloader.pause()
    time.sleep(0.3)  # let in-flight reads settle
    paused_at = downloader.bytes_downloaded
    time.sleep(0.3)
    assert downloader.bytes_downloaded == paused_at
    assert not downloader.finished

    _Handler.delay = 0.0
    downloader.resume()
    deadline = time.time() + 30
    while not downloader.finished and time.time() < deadline:
        time.sleep(0.01)
    assert downloader.succeeded
    assert path.read_bytes() == PAYLOAD

    cancelled = SegmentedDownloader(server_url, len(PAYLOAD), str(path), connections=2, chunk_size=128 * 1024)
    _Handler.delay = 0.05
    cancelled.start()
    cancelled.cancel()
    cancelled.wait(10)
    assert cancelled.finished
    assert not cancelled.succeeded
    cancelled.remove_file()
    assert not path.exists()
