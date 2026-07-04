import os
import queue
import threading
from collections.abc import Callable

from settings.general_settings import GeneralSettings
from utils.logger import get_logger

_log = get_logger(__name__)


class VideoConvertManager:
    """
    Manages the convert queue and controls the convert process.
    """

    import platform
    import shutil

    if platform.system() == "Windows":
        FFMPEG_PATH = os.path.join("ffmpeg", "ffmpeg.exe")
    else:
        FFMPEG_PATH = shutil.which("ffmpeg") or os.path.join("ffmpeg", "ffmpeg")

    # Class variables to keep track of active and queued converts
    active_convert_count: int = 0
    queued_convert_count: int = 0
    queued_converts: list = []
    active_converts: list = []
    status_change_callback: Callable = None

    # Queue used to signal the manager thread when the queue state changes
    _signal_queue: queue.Queue = queue.Queue()

    @staticmethod
    def manage_convert_queue() -> None:
        """
        Manages the convert queue by starting converts if conditions are met.

        Blocks on a queue.Queue instead of polling with time.sleep, so it wakes
        up immediately when a new item is registered or an active convert finishes.
        """
        while True:
            # Block until signalled (no busy-wait)
            VideoConvertManager._signal_queue.get()

            if (
                GeneralSettings.settings["max_simultaneous_converts"] > VideoConvertManager.active_convert_count
                and VideoConvertManager.queued_convert_count > 0
            ):
                try:
                    VideoConvertManager.queued_convert_count -= 1
                    VideoConvertManager.queued_converts[0].convert_video()
                    VideoConvertManager.active_convert_count += 1
                    VideoConvertManager.active_converts.append(VideoConvertManager.queued_converts.pop(0))
                except Exception:
                    _log.exception("failed to start convert")
                    # Re-queue the item count so the queue stays consistent
                    VideoConvertManager.queued_convert_count += 1
                VideoConvertManager.status_change_callback()

    @staticmethod
    def _signal() -> None:
        """Puts a token into the internal signal queue to wake the manager thread."""
        VideoConvertManager._signal_queue.put(True)

    @staticmethod
    def register(video) -> None:
        """
        Registers a video to be converted.

        Adds the video to the convert queue, updates the queued convert count,
        and signals the manager thread.
        """
        VideoConvertManager.queued_converts.append(video)
        VideoConvertManager.queued_convert_count += 1
        VideoConvertManager.status_change_callback()
        VideoConvertManager._signal()

    @staticmethod
    def unregister_from_queued(video) -> None:
        """
        Unregisters a video from the convert queue.

        Removes the video from the convert queue and updates the queued convert count.
        """
        if video in VideoConvertManager.queued_converts:
            VideoConvertManager.queued_converts.remove(video)
            VideoConvertManager.queued_convert_count -= 1
        VideoConvertManager.status_change_callback()

    @staticmethod
    def unregister_from_active(video) -> None:
        """
        Unregisters a video from the active convert list.

        Removes the video from the active convert list, updates the active convert count,
        and signals the manager thread so it can start the next queued item.
        """
        if video in VideoConvertManager.active_converts:
            VideoConvertManager.active_converts.remove(video)
            VideoConvertManager.active_convert_count -= 1
        VideoConvertManager.status_change_callback()
        VideoConvertManager._signal()

    @staticmethod
    def initialize(status_change_callback: Callable = None) -> None:
        """
        Initializes the convert manager by starting a separate thread for managing the convert queue.

        Args:
            status_change_callback (Callable, optional): A callback function to be called on status changes.
        """
        VideoConvertManager.status_change_callback = status_change_callback
        video_converting_manage_thread = threading.Thread(target=VideoConvertManager.manage_convert_queue)
        video_converting_manage_thread.daemon = True
        video_converting_manage_thread.start()
