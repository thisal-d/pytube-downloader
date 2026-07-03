import os  # Library for interacting with the operating system
import time
from typing import Literal  # Used for type hinting specific values

import win11toast  # Library for Windows 11 toast notifications

from utils.value_convert_utility import ValueConvertUtility  # Utility for size conversion


class NotificationManager:
    """
    A class to handle displaying Windows 11 toast notifications for
    video and playlist download progress, downloaded, and failure.
    """

    # Application identifier for the toast notifications
    APP_ID = "PyTube Downloader"

    queued_notifications = []
    running = False
    notification_duration = 6

    @staticmethod
    def manage_notification_queue():
        while True:
            if len(NotificationManager.queued_notifications) == 0:
                NotificationManager.running = False
                break
            # print(NotificationManager.queued_notifications[0])
            NotificationManager.show_advanced_notification(**NotificationManager.queued_notifications.pop(0))
            time.sleep(NotificationManager.notification_duration)
            win11toast.clear_toast()

    @staticmethod
    def show_advanced_notification(
        video_title: str = "Video Title",  # Title of the video
        playlist_title: str = "Playlist Title",  # Title of the playlist
        channel_name: str = "channel Name",  # Name of the video channel
        status_message: str = "Status Message",  # Message indicating the status
        completed_videos_count: int = 1,  # Number of videos completed in the playlist
        total_videos_count: int = 10,  # Total videos in the playlist
        thumbnail_path: str = "assets\\ui images\\default thumbnail.png",  # Path to the thumbnail image
        download_mode: Literal["video", "playlist"] = "video",  # Notification download_mode: 'video' or 'playlist'
        file_size: int = 1000,  # File size in bytes
        download_file_name: str = "",
        download_directory: str = "",
        downloaded_file_size: int = 1000,
        download_type: str = "720p Video",  # Download type/quality
        download_status: Literal[
            "downloaded", "failed", "playlist_completed"
        ] = "downloaded",  # Status of the download: 'downloaded' or 'failed'
    ):
        """
        Displays an advanced toast notification based on the provided parameters.
        """

        # Get absolute paths for file and folder
        abs_file_path = os.path.abspath(download_file_name)
        abs_folder_path = os.path.abspath(download_directory)

        # Configuration for the thumbnail image
        thumbnail_path = {
            "src": os.path.abspath(thumbnail_path),
            "placement": "hero",  # Indicates hero image placement
        }

        # Determine the appropriate audio path based on the download_status
        if download_status == "downloaded":
            # Action buttons for the notification
            buttons = [
                {"activationType": "protocol", "arguments": abs_file_path, "content": "Play"},  # Play button
                {
                    "activationType": "protocol",
                    "arguments": abs_folder_path,
                    "content": "Open Folder",
                },  # Open Folder button
            ]
        elif download_status == "playlist_completed":
            buttons = [
                {
                    "activationType": "protocol",
                    "arguments": abs_folder_path,
                    "content": "Open Folder",
                }  # Open Folder button
            ]
        else:
            buttons = []

        # Handle video-specific notifications
        if download_mode == "video":
            # Convert file size for display
            converted_file_size = ValueConvertUtility.convert_size(file_size, decimal_points=2)
            converted_downloaded_file_size = ValueConvertUtility.convert_size(downloaded_file_size, decimal_points=2)
            # Display notification for a video download
            win11toast.notify(
                title=video_title,  # Video title
                body=channel_name,  # Channel name
                app_id=NotificationManager.APP_ID,  # App ID for grouping notifications
                progress={  # Progress details
                    "title": status_message,  # Status message
                    "status": download_type,  # Download type
                    "value": str(downloaded_file_size / file_size),  # Progress percentage (completed)
                    "valueStringOverride": f"{converted_downloaded_file_size}/{converted_file_size}",  # File size
                },
                duration="short",
                on_click=abs_file_path,  # Action on click
                buttons=buttons,  # Buttons
                image=thumbnail_path,  # Thumbnail image
            )

        else:
            # Handle playlist-specific notifications
            win11toast.notify(
                title=video_title,  # Playlist's video title
                body=channel_name,  # Channel name
                app_id=NotificationManager.APP_ID,  # App ID
                progress={  # Progress details for playlist
                    "title": playlist_title,  # Playlist title
                    "status": status_message,  # Status message
                    "value": str(completed_videos_count / total_videos_count),  # Number of videos completed
                    "valueStringOverride": f"{completed_videos_count}/{total_videos_count} Videos",  # Videos completed/total
                },
                duration="short",
                on_click=abs_file_path,  # Action on click
                image=thumbnail_path,  # Thumbnail image
                buttons=buttons,  # Buttons
            )

    @staticmethod
    def register(
        video_title: str = "Video Title",  # Title of the video
        playlist_title: str = "Playlist Title",  # Title of the playlist
        channel_name: str = "channel Name",  # Name of the video channel
        status_message: str = "Status Message",  # Message indicating the status
        completed_videos_count: int = 1,  # Number of videos completed in the playlist
        total_videos_count: int = 10,  # Total videos in the playlist
        thumbnail_path: str = "assets\\ui images\\default thumbnail.png",  # Path to the thumbnail image
        download_mode: Literal["video", "playlist"] = "video",  # Notification type: 'video' or 'playlist'
        file_size: int = 1000,  # File size in bytes
        download_file_name: str = "",
        download_directory: str = "",
        downloaded_file_size: int = 1000,
        download_type: str = "720p Video",  # Download type/quality
        download_status: Literal[
            "downloaded", "failed", "playlist_completed"
        ] = "downloaded",  # Status of the download: 'downloaded' or 'failed'
    ):
        NotificationManager.queued_notifications.append(
            {
                "video_title": video_title,
                "playlist_title": playlist_title,
                "channel_name": channel_name,
                "status_message": status_message,
                "completed_videos_count": completed_videos_count,
                "total_videos_count": total_videos_count,
                "thumbnail_path": thumbnail_path,
                "download_mode": download_mode,
                "file_size": file_size,
                "download_file_name": download_file_name,
                "download_directory": download_directory,
                "download_type": download_type,
                "downloaded_file_size": downloaded_file_size,
                "download_status": download_status,
            }
        )

        if not NotificationManager.running:
            NotificationManager.running = True
            NotificationManager.manage_notification_queue()
