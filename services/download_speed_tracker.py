import threading
import time
from collections.abc import Callable

from .download_manager import DownloadManager


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
                    except Exception as error:
                        print("download_speed_tracker.py L-18 : ", error)
            if DownloadSpeedTracker.callback is not None:
                try:
                    DownloadSpeedTracker.callback(total_speed)
                except Exception as error:
                    print("download_speed_tracker.py L-24 : ", error)
            time.sleep(2)

    def initialize(callback: Callable = None):
        DownloadSpeedTracker.callback = callback
        thread = threading.Thread(target=DownloadSpeedTracker.track_total_download_speed, daemon=True)
        thread.start()
