from collections.abc import Callable


class VideoCountTracker:
    total_added_video_count: int = 0
    total_downloading_video_count: int = 0
    total_downloaded_video_count: int = 0

    status_call_back_function: Callable = None

    @staticmethod
    def add_added_video():
        VideoCountTracker.total_added_video_count += 1
        VideoCountTracker.return_status()

    @staticmethod
    def remove_added_video():
        VideoCountTracker.total_added_video_count -= 1
        VideoCountTracker.return_status()

    @staticmethod
    def add_downloading_video():
        VideoCountTracker.total_downloading_video_count += 1
        VideoCountTracker.return_status()

    @staticmethod
    def remove_downloading_video():
        VideoCountTracker.total_downloading_video_count -= 1
        VideoCountTracker.return_status()

    @staticmethod
    def add_downloaded_video():
        VideoCountTracker.total_downloaded_video_count += 1
        VideoCountTracker.return_status()

    @staticmethod
    def remove_downloaded_video():
        VideoCountTracker.total_downloaded_video_count -= 1
        VideoCountTracker.return_status()

    @staticmethod
    def return_status():
        VideoCountTracker.status_call_back_function(
            VideoCountTracker.total_added_video_count,
            VideoCountTracker.total_downloading_video_count,
            VideoCountTracker.total_downloaded_video_count,
        )

    @staticmethod
    def initialize(call_back_funtion: Callable):
        VideoCountTracker.status_call_back_function = call_back_funtion
