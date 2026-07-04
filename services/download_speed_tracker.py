import threading
import time
from collections.abc import Callable

from utils.logger import get_logger

from .download_manager import DownloadManager

_log = get_logger(__name__)


class DownloadSpeedTracker:
    callback = None

    @staticmethod
    def track_total_download_speed():
        while True:
            total_speed = 0
            if DownloadManager.active_download_count > 0:
                for video in DownloadManager.active_downloads:
                    try:
                        if video.download_state == "downloading":
                            video_download_speed = video.total_bytes_downloaded / video.total_download_time
                            total_speed += video_download_speed
                    except Exception:
                        _log.exception("failed to get download speed for a video")
            if DownloadSpeedTracker.callback is not None:
                try:
                    DownloadSpeedTracker.callback(total_speed)
                except Exception:
                    _log.exception("failed to invoke download speed callback")
            time.sleep(2)

    def initialize(self: Callable = None):
        DownloadSpeedTracker.callback = self
        thread = threading.Thread(target=DownloadSpeedTracker.track_total_download_speed, daemon=True)
        thread.start()
