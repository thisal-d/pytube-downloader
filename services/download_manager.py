import queue
import threading
from collections.abc import Callable

from pytubefix import request as pytubefix_request

from settings.general_settings import GeneralSettings


class DownloadManager:
    """
    Manages the download queue and controls the download process.
    """

    # Class variables to keep track of active and queued loads
    active_download_count: int = 0
    queued_download_count: int = 0
    queued_downloads: list = []
    active_downloads: list = []
    status_change_callback: Callable = None

    # Queue used to signal the manager thread when the queue state changes
    _signal_queue: queue.Queue = queue.Queue()

    resolutions: list = [
        "Audio Only",
        "144p",
        "240p",
        "360p",
        "480p",
        "720p",
        "1080p",
        "1440p",
        "2160p",
        "4320p",
        "8640p",
        "17280p",
    ]

    default_chunk_size: int = 2097152

    @staticmethod
    def manage_download_queue() -> None:
        """
        Manages the download queue by starting downloads if conditions are met.

        Blocks on a queue.Queue instead of polling with time.sleep, so it wakes
        up immediately when a new item is registered or an active download finishes.
        """
        while True:
            # Block until signalled (no busy-wait)
            DownloadManager._signal_queue.get()

            if (
                GeneralSettings.settings["max_simultaneous_downloads"] > DownloadManager.active_download_count
                and DownloadManager.queued_download_count > 0
            ):
                try:
                    DownloadManager.queued_download_count -= 1
                    DownloadManager.queued_downloads[0].download_video()
                    DownloadManager.active_download_count += 1
                    DownloadManager.active_downloads.append(DownloadManager.queued_downloads.pop(0))
                except Exception as error:
                    print(f"download_manager.py : failed to start download: {error}")
                    # Re-queue the item count so the queue stays consistent
                    DownloadManager.queued_download_count += 1
                DownloadManager.status_change_callback()

    @staticmethod
    def _signal() -> None:
        """Puts a token into the internal signal queue to wake the manager thread."""
        DownloadManager._signal_queue.put(True)

    @staticmethod
    def register(video) -> None:
        """
        Registers a video to be downloaded.

        Adds the video to the download queue, updates the queued download count,
        and signals the manager thread.
        """
        DownloadManager.queued_downloads.append(video)
        DownloadManager.queued_download_count += 1
        DownloadManager.status_change_callback()
        DownloadManager._signal()

    @staticmethod
    def unregister_from_queued(video) -> None:
        """
        Unregisters a video from the download queue.

        Removes the video from the download queue and updates the queued download count.
        """
        if video in DownloadManager.queued_downloads:
            DownloadManager.queued_downloads.remove(video)
            DownloadManager.queued_download_count -= 1
        DownloadManager.status_change_callback()

    @staticmethod
    def unregister_from_active(video) -> None:
        """
        Unregisters a video from the active download list.

        Removes the video from the active download list, updates the active download
        count, and signals the manager thread so it can start the next queued item.
        """
        if video in DownloadManager.active_downloads:
            DownloadManager.active_downloads.remove(video)
            DownloadManager.active_download_count -= 1
        DownloadManager.status_change_callback()
        DownloadManager._signal()

    @staticmethod
    def initialize(status_change_callback: Callable = None) -> None:
        """
        Initializes the download manager by starting a separate thread for managing the download queue.

        Args:
            status_change_callback (Callable, optional): A callback function to be called on status changes.
        """
        DownloadManager.status_change_callback = status_change_callback
        DownloadManager.configure_chunk_size()
        downloading_manage_thread = threading.Thread(target=DownloadManager.manage_download_queue)
        downloading_manage_thread.daemon = True
        downloading_manage_thread.start()

    @staticmethod
    def configure_chunk_size() -> None:
        pytubefix_request.default_range_size = GeneralSettings.settings["chunk_size"]
