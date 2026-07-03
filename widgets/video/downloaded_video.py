import os
from collections.abc import Callable
from tkinter import PhotoImage
from typing import Literal

import customtkinter as ctk

from services import HistoryManager, LanguageManager, ThemeManager, VideoCountTracker
from settings import AppearanceSettings
from utils import ValueConvertUtility
from widgets.video import Video


class DownloadedVideo(Video):
    def __init__(
        self,
        root: ctk.CTk,
        master: ctk.CTkFrame | ctk.CTkScrollableFrame,
        height: int = 0,
        width: int = 0,
        # video info
        video_title: str = "",
        channel: str = "",
        video_url: str = "",
        channel_url: str = "",
        file_size: int = 0,
        length: int = 0,
        thumbnails: list[PhotoImage] = (None, None),
        original_thumbnail_image_path: str = "",
        # Hsitory thumbnail images
        history_normal_thumbnail_image_path: str = "",
        history_hover_thumbnail_image_path: str = "",
        # download info
        downloaded_file_name: str = "",
        download_quality: Literal["128kbps", "360p", "720p"] = "720p",
        download_type: Literal["Audio", "Video"] = "Video",
        # download mode
        mode: Literal["video", "playlist"] = "video",
        # state callbacks
        video_status_callback: Callable = None,
    ):

        # video info
        self.file_size: int = file_size
        # download info
        self.downloaded_file_name: str = downloaded_file_name
        self.download_quality: Literal["128kbps", "360p", "720p"] = download_quality
        self.download_type: Literal["Audio", "Video"] = download_type
        # widgets
        self.download_type_label: ctk.CTkLabel | None = None
        self.file_size_label: ctk.CTkLabel | None = None
        self.download_path_btn: ctk.CTkButton | None = None
        self.play_video_btn: ctk.CTkButton | None = None
        # status callbacks
        self.video_status_callback = video_status_callback
        self.mode = mode

        super().__init__(
            root=root,
            master=master,
            width=width,
            height=height,
            thumbnails=thumbnails,
            video_title=video_title,
            channel=channel,
            channel_url=channel_url,
            length=length,
            video_url=video_url,
            original_thumbnail_image_path=original_thumbnail_image_path,
            history_normal_thumbnail_image_path=history_normal_thumbnail_image_path,
            history_hover_thumbnail_image_path=history_hover_thumbnail_image_path,
        )

        if self.mode == "video":
            HistoryManager.save_video_to_history(self)

        VideoCountTracker.add_downloaded_video()
        self.set_video_data()

    def create_widgets(self):
        super().create_widgets()

        self.download_type_label = ctk.CTkLabel(master=self)
        self.file_size_label = ctk.CTkLabel(master=self, text=ValueConvertUtility.convert_size(self.file_size, 2))
        self.download_path_btn = ctk.CTkButton(
            master=self,
            text="📂",
            cursor="hand2",
            command=lambda: os.startfile("\\".join(self.downloaded_file_name.split("\\")[0:-1])),
            hover=False,
        )

        self.play_video_btn = ctk.CTkButton(
            master=self, text="▶", cursor="hand2", command=lambda: os.startfile(self.downloaded_file_name), hover=False
        )

    def set_widgets_texts(self):
        super().set_widgets_texts()

        self.download_type_label.configure(
            text=f"{LanguageManager.data[self.download_type.lower()]} : {self.download_quality}"
        )

    def set_widgets_fonts(self):
        super().set_widgets_fonts()

        scale = AppearanceSettings.get_scale("decimal")

        self.download_type_label.configure(font=("Segoe UI", 12 * scale, "bold"))
        self.file_size_label.configure(font=("Segoe UI", 12 * scale, "normal"))
        self.download_path_btn.configure(font=("Segoe UI", 30 * scale, "bold"))
        self.play_video_btn.configure(font=("Segoe UI", 35 * scale, "bold"))

    def set_widgets_sizes(self):
        super().set_widgets_sizes()

        scale = AppearanceSettings.get_scale("decimal")

        self.download_type_label.configure(height=15 * scale)
        self.file_size_label.configure(height=15 * scale)
        self.download_path_btn.configure(height=15 * scale, width=30 * scale)
        self.play_video_btn.configure(height=15 * scale, width=15 * scale)

    def set_widgets_accent_color(self):
        super().set_widgets_accent_color()

        self.download_path_btn.configure(text_color=ThemeManager.get_accent_color("normal"))
        self.play_video_btn.configure(text_color=ThemeManager.get_accent_color("normal"))

    def set_widgets_colors(self):
        super().set_widgets_colors()

        self.download_type_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))
        self.file_size_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))
        self.download_path_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"))
        self.play_video_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"))

    def on_mouse_enter_self(self, event):
        # super().on_mouse_enter_self(event)

        """
        self.download_path_btn.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["hover"])
        """

    def on_mouse_leave_self(self, event):
        super().on_mouse_leave_self(event)

    def bind_widgets_events(self):
        super().bind_widgets_events()

        def on_mouse_enter_download_path_btn(_event):
            self.download_path_btn.configure(text_color=ThemeManager.get_accent_color("hover"))
            # self.on_mouse_enter_self(event)

        def on_mouse_leave_download_path_btn(_event):
            self.download_path_btn.configure(text_color=ThemeManager.get_accent_color("normal"))

        self.download_path_btn.bind("<Enter>", on_mouse_enter_download_path_btn)
        self.download_path_btn.bind("<Leave>", on_mouse_leave_download_path_btn)

        def on_mouse_enter_play_video_btn(_event):
            self.play_video_btn.configure(text_color=ThemeManager.get_accent_color("hover"))
            # self.on_mouse_enter_self(event)

        def on_mouse_leave_play_video_btn(_event):
            self.play_video_btn.configure(text_color=ThemeManager.get_accent_color("normal"))

        self.play_video_btn.bind("<Enter>", on_mouse_enter_play_video_btn)
        self.play_video_btn.bind("<Leave>", on_mouse_leave_play_video_btn)

    def place_widgets(self):
        super().place_widgets()

        scale = AppearanceSettings.get_scale("decimal")

        self.download_type_label.place(relx=1, x=-300 * scale, rely=0.3, anchor="w")
        self.file_size_label.place(relx=1, x=-300 * scale, rely=0.7, anchor="w")

        self.download_path_btn.place(relx=1, x=-170 * scale, rely=0.5, anchor="w")
        self.play_video_btn.place(relx=1, x=-90 * scale, rely=0.5, anchor="w")

    def configure_widget_sizes(self, _event):
        scale = AppearanceSettings.get_scale("decimal")
        self.info_frame.configure(
            width=(
                self.master_frame.winfo_width()
                - (300 * scale)
                - (self.thumbnail_btn.winfo_width() + 5)
                - (10 * scale)
                - (20 * scale)
            )
        )

    def __del__(self):
        # video info
        del self.file_size
        # download info
        del self.downloaded_file_name
        del self.download_quality
        del self.download_type
        # widgets
        del self.download_type_label
        del self.file_size_label
        del self.download_path_btn
        del self.play_video_btn
        # status callbacks
        del self.video_status_callback
        del self.mode

        super().__del__()

    def destroy_widgets(self):
        """Destroy the child widgets."""
        self.download_type_label.destroy()
        self.file_size_label.destroy()
        self.download_path_btn.destroy()
        self.play_video_btn.destroy()

        super().destroy_widgets()

    def kill(self):
        if self.mode == "playlist":
            self.video_status_callback(self, "removed")
        VideoCountTracker.remove_downloaded_video()
        super().kill()
