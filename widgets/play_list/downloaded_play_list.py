from typing import Literal

import customtkinter as ctk

from services import HistoryManager
from settings import AppearanceSettings
from utils import GuiUtils
from widgets.play_list.play_list import PlayList
from widgets.video.downloaded_video import DownloadedVideo
from widgets.video.downloading_video import DownloadingVideo


class DownloadedPlayList(PlayList):
    def __init__(
        self,
        root: ctk.CTk = None,
        master: ctk.CTkScrollableFrame = None,
        width: int = 0,
        height: int = 0,
        # playlist info
        channel_url: str = "",
        playlist_url: str = "",
        playlist_title: str = "---------",
        channel: str = "---------",
        playlist_video_count: int = 0,
        playlist_original_video_count: int = 0,
        # videos of playlist
        videos: list[DownloadingVideo] = None,
    ):

        # playlist videos
        self.downloading_videos: list[DownloadingVideo] = videos

        super().__init__(
            root=root,
            master=master,
            width=width,
            height=height,
            # playlist info
            channel_url=channel_url,
            playlist_url=playlist_url,
            playlist_title=playlist_title,
            channel=channel,
            playlist_video_count=playlist_video_count,
            playlist_original_video_count=playlist_original_video_count,
        )

        self.display_downloaded_widgets()

        HistoryManager.save_playlist_to_history(self)

    def display_downloaded_widgets(self):
        for downloading_video in self.downloading_videos:
            video = DownloadedVideo(
                root=self.root,
                master=self.playlist_videos_frame,
                height=70 * AppearanceSettings.get_scale("decimal"),
                width=self.playlist_videos_frame.winfo_width() - 20,
                # video info
                thumbnails=downloading_video.thumbnails,
                video_title=downloading_video.video_title,
                channel=downloading_video.channel,
                channel_url=downloading_video.channel_url,
                video_url=downloading_video.video_url,
                file_size=downloading_video.file_size,
                length=downloading_video.length,
                original_thumbnail_image_path=downloading_video.original_thumbnail_image_path,
                # History thumbnail image paths
                history_normal_thumbnail_image_path=downloading_video.history_normal_thumbnail_image_path,
                history_hover_thumbnail_image_path=downloading_video.history_hover_thumbnail_image_path,
                # download info
                downloaded_file_name=downloading_video.download_file_name,
                download_quality=downloading_video.download_quality,
                download_type=downloading_video.download_type,
                # state callbacks
                mode=downloading_video.mode,
                video_status_callback=self.videos_status_track,
            )
            if self.last_viewed_index < PlayList.max_videos_per_page:
                video.pack(fill="x", padx=(20, 0), pady=(1, 0))
                self.last_viewed_index += 1
            self.videos.append(video)
        self.configure_videos_tab_view()
        self.view_btn.configure(state="normal")

    # status tracker
    def videos_status_track(self, video: DownloadedVideo, state: Literal["removed"]):
        if state == "removed":
            self.videos.remove(video)
            self.configure_videos_tab_view()
            self.playlist_video_count -= 1
            if self.playlist_video_count == 0:
                self.kill()
            else:
                self.playlist_video_count_label.configure(text=self.playlist_video_count)

    def configure_widget_sizes(self, _event):
        scale = AppearanceSettings.get_scale("decimal")
        self.info_frame.configure(width=self.master_frame.winfo_width() - (50 * scale + 15 * scale) - (60 * scale))

    def __del__(self):
        """Clear the Memory."""
        del self.downloading_videos

        super().__del__()

    def destroy_widgets(self):
        """Destroy the child widget."""

        super().destroy_widgets()

    def kill(self):
        self.pack_forget()

        for video in self.videos:
            video.video_status_callback = GuiUtils.do_nothing
            video.kill()

        super().kill()
