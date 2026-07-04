import math
import tkinter as tk
from typing import Literal

import customtkinter as ctk

from services import HistoryManager, LanguageManager, ThemeManager
from settings import AppearanceSettings

from .history_playlist import HistoryPlaylist
from .history_video import HistoryVideo


class HistoryPanel(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTk = None,
        video_add_to_download_callback: callable = None,
        playlist_add_to_download_callback: callable = None,
    ):

        super().__init__(master=master)

        self.videos_button = ctk.CTkButton(
            master=self, text="Videos", command=lambda: self.place_nav_frame(self.videos_scrollable_frame, "videos")
        )
        self.playlists_button = ctk.CTkButton(
            master=self,
            text="Play Lists",
            command=lambda: self.place_nav_frame(self.playlists_scrollable_frame, "playlists"),
        )

        self.videos_scrollable_frame = ctk.CTkScrollableFrame(master=self)
        self.playlists_scrollable_frame = ctk.CTkScrollableFrame(master=self)

        self.videos_history_frame_info_label = ctk.CTkLabel(
            master=self,
            text="Downloaded videos history will be display here.",
        )
        self.playlists_history_frame_info_label = ctk.CTkLabel(
            master=self,
            text="Downloaded playlists history will be display here.",
        )

        self.playlists_frame_info_label_placed = False
        self.videos_frame_info_label_placed = False

        scale = AppearanceSettings.get_scale("decimal")
        self.history_video_width = 180 * scale
        self.history_video_grid_pad_y = 2 * scale
        self.history_video_grid_pad_x = 2 * scale
        self.videos_per_row = 0

        self.history_playlist_width = 180 * scale
        self.history_playlist_grid_pad_y = 2 * scale
        self.history_playlist_grid_pad_x = 2 * scale
        self.playlists_per_row = 0

        self.histoy_videos_widgets = []
        self.histoy_playlists_widgets = []

        self.video_add_to_download_callback = video_add_to_download_callback
        self.playlist_add_to_download_callback = playlist_add_to_download_callback

        self.set_widgets_sizes()
        self.set_widgets_colors()
        self.place_widgets()
        self.set_widgets_fonts()
        self.set_widgets_accent_color()
        self.set_widgets_texts()
        self.bind_widgets_events()

        self.after(1, self.configure_old_history_videos)
        self.after(1, self.configure_old_history_playlists)

        ThemeManager.register_widget(self)
        LanguageManager.register_widget(self)

        self.place_nav_frame(self.videos_scrollable_frame, "videos")

    def bring_video_to_top(self, no: int, url: str):
        for index, history_video in enumerate(self.histoy_videos_widgets):
            if history_video.url == url:
                history_video.no = no
                if index != 0:
                    history_video_temp = history_video
                    self.histoy_videos_widgets.remove(history_video)
                    self.histoy_videos_widgets.insert(0, history_video_temp)
                    self.place_history_videos()
                break

    def remove_history_video(self, history_video: HistoryVideo):
        is_last_video = history_video == self.histoy_videos_widgets[-1]
        history_video.grid_forget()
        self.histoy_videos_widgets.remove(history_video)
        if not is_last_video:
            self.place_history_videos()

        HistoryManager.remove_from_video_history(history_video.no)
        history_video.destroy()

    def add_hisory_video(
        self,
        no,
        channel,
        title,
        url,
        thumbnail_normal_path,
        thumbnail_hover_path,
        video_length,
        download_date,
        is_duplicated,
    ) -> None:
        if is_duplicated:
            self.bring_video_to_top(no=no, url=url)
        else:
            if len(self.histoy_videos_widgets) == HistoryManager.max_history:
                self.histoy_videos_widgets.pop().destroy()
            self.histoy_videos_widgets.insert(
                0,
                (
                    HistoryVideo(
                        master=self.videos_scrollable_frame,
                        no=no,
                        width=self.history_video_width,
                        channel=channel,
                        title=title,
                        url=url,
                        thumbnail_path_normal=thumbnail_normal_path,
                        thumbnail_path_hover=thumbnail_hover_path,
                        download_date=download_date,
                        length=video_length,
                        add_to_download_callback=self.video_add_to_download_callback,
                        remove_callback=self.remove_history_video,
                    )
                ),
            )

        self.place_history_videos()

    def place_history_videos(self) -> None:
        self.place_forget_videos()

        ## Place forget innfo label if there is any history videos
        if len(self.histoy_videos_widgets) > 0:
            self.place_forget_nav_labels(except_label="playlists")

        row = 0
        column = 0
        for history_video in self.histoy_videos_widgets:
            if not column < self.videos_per_row:
                row += 1
                column = 0
            history_video.grid(
                row=row, column=column, padx=self.history_video_grid_pad_x, pady=self.history_video_grid_pad_y
            )
            column += 1

    def place_forget_videos(self) -> None:
        for history_video in self.histoy_videos_widgets:
            history_video.grid_forget()

    def configure_old_history_videos(self) -> None:
        for video_date in HistoryManager.videos_history_data:
            self.histoy_videos_widgets.append(
                HistoryVideo(
                    master=self.videos_scrollable_frame,
                    width=self.history_video_width,
                    no=video_date[0],
                    channel=video_date[1],
                    title=video_date[2],
                    url=video_date[3],
                    thumbnail_path_normal=video_date[4],
                    thumbnail_path_hover=video_date[5],
                    length=video_date[6],
                    download_date=video_date[7],
                    add_to_download_callback=self.video_add_to_download_callback,
                    remove_callback=self.remove_history_video,
                )
            )
        self.configure_video_count_per_row()
        self.place_history_videos()

    def configure_history_videos(self) -> None:
        previous_video_count_per_row = self.videos_per_row
        self.configure_video_count_per_row()
        if previous_video_count_per_row != self.videos_per_row:
            self.place_history_videos()

    def configure_video_count_per_row(self) -> None:
        total_required_width_for_video = self.history_video_width + self.history_video_grid_pad_x
        self.videos_per_row = math.floor(
            (self.videos_scrollable_frame.cget("width") - 12) / total_required_width_for_video
        )

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def bring_playlist_to_top(self, no: int, url: str):
        for index, history_playlist in enumerate(self.histoy_playlists_widgets):
            if history_playlist.url == url:
                history_playlist.no = no
                if index != 0:
                    history_playlist_temp = history_playlist
                    self.histoy_playlists_widgets.remove(history_playlist)
                    self.histoy_playlists_widgets.insert(0, history_playlist_temp)
                    self.place_history_playlists()
                break

    def remove_history_playlist(self, history_playlist: HistoryPlaylist):
        is_last_video = history_playlist == self.histoy_playlists_widgets[-1]
        history_playlist.grid_forget()
        self.histoy_playlists_widgets.remove(history_playlist)
        if not is_last_video:
            self.place_history_playlists()

        HistoryManager.remove_from_playlist_history(history_playlist.no)
        history_playlist.destroy()

    def add_hisory_playlist(
        self,
        no,
        channel,
        title,
        url,
        thumbnail_normal_path,
        thumbnail_hover_path,
        video_count,
        download_date,
        is_duplicated,
    ) -> None:
        if is_duplicated:
            self.bring_playlist_to_top(no=no, url=url)
        else:
            if len(self.histoy_playlists_widgets) == HistoryManager.max_history:
                self.histoy_playlists_widgets.pop().destroy()
            self.histoy_playlists_widgets.insert(
                0,
                (
                    HistoryPlaylist(
                        master=self.playlists_scrollable_frame,
                        no=no,
                        width=self.history_video_width,
                        channel=channel,
                        title=title,
                        url=url,
                        thumbnail_path_normal=thumbnail_normal_path,
                        thumbnail_path_hover=thumbnail_hover_path,
                        download_date=download_date,
                        add_to_download_callback=self.playlist_add_to_download_callback,
                        videos_count=video_count,
                        remove_callback=self.remove_history_playlist,
                    )
                ),
            )
            self.place_history_playlists()

    def place_history_playlists(self) -> None:
        self.place_forget_playlists()

        ## Place forget innfo label if there is any history videos
        if len(self.histoy_playlists_widgets) > 0:
            self.place_forget_nav_labels(except_label="videos")

        row = 0
        column = 0
        for history_playlist in self.histoy_playlists_widgets:
            if not column < self.playlists_per_row:
                row += 1
                column = 0
            history_playlist.grid(
                row=row, column=column, padx=self.history_playlist_grid_pad_x, pady=self.history_playlist_grid_pad_y
            )
            column += 1

    def place_forget_playlists(self) -> None:
        for history_playlist in self.histoy_playlists_widgets:
            history_playlist.grid_forget()

    def configure_old_history_playlists(self) -> None:
        for playlist_date in HistoryManager.playlists_history_data:
            self.histoy_playlists_widgets.append(
                HistoryPlaylist(
                    master=self.playlists_scrollable_frame,
                    width=self.history_playlist_width,
                    no=playlist_date[0],
                    channel=playlist_date[1],
                    title=playlist_date[2],
                    url=playlist_date[3],
                    thumbnail_path_normal=playlist_date[4],
                    thumbnail_path_hover=playlist_date[5],
                    videos_count=playlist_date[6],
                    download_date=playlist_date[7],
                    add_to_download_callback=self.playlist_add_to_download_callback,
                    remove_callback=self.remove_history_playlist,
                )
            )
        self.configure_playlist_count_per_row()
        self.place_history_playlists()

    def configure_history_playlists(self) -> None:
        previous_playlist_count_per_row = self.playlists_per_row
        self.configure_playlist_count_per_row()
        if previous_playlist_count_per_row != self.playlists_per_row:
            self.place_history_playlists()

    def configure_playlist_count_per_row(self) -> None:
        total_required_width_for_playlist = self.history_playlist_width + self.history_playlist_grid_pad_x
        self.playlists_per_row = math.floor(
            (self.playlists_scrollable_frame.cget("width") - 12) / total_required_width_for_playlist
        )

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    def configure_panel(self) -> None:
        self.configure_history_videos()
        self.configure_history_playlists()

    def place_nav_label(self, frame_name: Literal["videos", "playlists"]) -> None:
        self.place_forget_nav_labels()

        if frame_name == "videos" and len(self.histoy_videos_widgets) == 0:
            self.videos_history_frame_info_label.place(
                y=self.cget("height") / 2 + 45, x=self.cget("width") / 2, anchor="center"
            )
            self.videos_frame_info_label_placed = True

        elif frame_name == "playlists" and len(self.histoy_playlists_widgets) == 0:
            self.playlists_history_frame_info_label.place(
                y=self.cget("height") / 2 + 45, x=self.cget("width") / 2, anchor="center"
            )
            self.playlists_frame_info_label_placed = True

    def place_nav_frame(self, frame: ctk.CTkScrollableFrame, frame_name: Literal["videos", "playlists"]) -> None:
        self.place_forget_nav_frames(except_frame=frame_name)
        scale = AppearanceSettings.get_scale("decimal")
        frame.place(y=10 + (25 * scale) + 10, x=0)
        self.place_nav_label(frame_name)

    def place_forget_nav_frames(self, except_frame: Literal["videos", "playlists"] = None) -> None:
        """
        Hides the navigation frames for added, downloading, downloaded, history content.
        """
        if except_frame != "videos":
            self.videos_scrollable_frame.place_forget()
            self.videos_frame_info_label_placed = False

        if except_frame != "playlists":
            self.playlists_scrollable_frame.place_forget()
            self.playlists_frame_info_label_placed = False

    def place_forget_nav_labels(self, except_label: Literal["videos", "playlists"] = None) -> None:
        """
        Hides the navigation labels for added, downloading, and downloaded content.
        """
        if except_label != "videos":
            self.videos_history_frame_info_label.place_forget()
        if except_label != "playlists":
            self.playlists_history_frame_info_label.place_forget()

    def set_widgets_sizes(self) -> None:
        scale = AppearanceSettings.get_scale("decimal")
        self.videos_button.configure(width=80 * scale, height=25 * scale)
        self.playlists_button.configure(width=80 * scale, height=25 * scale)

    def update_widgets_colors(self) -> None:
        self.set_widgets_colors()

    def set_widgets_colors(self) -> None:
        self.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            fg_color=ThemeManager.get_color_based_on_theme("background"),
        )
        self.videos_scrollable_frame.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            fg_color=ThemeManager.get_color_based_on_theme("background"),
        )
        self.playlists_scrollable_frame.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            fg_color=ThemeManager.get_color_based_on_theme("background"),
        )
        self.videos_history_frame_info_label.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            fg_color=ThemeManager.get_color_based_on_theme("background"),
            text_color=ThemeManager.get_color_based_on_theme("text_muted"),
        )
        self.playlists_history_frame_info_label.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            fg_color=ThemeManager.get_color_based_on_theme("background"),
            text_color=ThemeManager.get_color_based_on_theme("text_muted"),
        )
        self.videos_button.configure(text_color=ThemeManager.get_color_based_on_theme("background"))
        self.playlists_button.configure(text_color=ThemeManager.get_color_based_on_theme("background"))

    def set_widgets_accent_color(self) -> None:
        self.videos_button.configure(
            fg_color=ThemeManager.get_accent_color("normal"),
            hover_color=ThemeManager.get_accent_color("hover"),
        )
        self.playlists_button.configure(
            fg_color=ThemeManager.get_accent_color("normal"),
            hover_color=ThemeManager.get_accent_color("hover"),
        )

    def update_widgets_accent_color(self) -> None:
        """
        Update accent color.
        """
        self.set_widgets_accent_color()

    def update_widgets_text(self) -> None:
        self.set_widgets_texts()

    def place_widgets(self) -> None:
        scale = AppearanceSettings.get_scale("decimal")
        self.videos_button.place(x=0, y=10)
        self.playlists_button.place(x=(10 + 80) * scale, y=10)

    def set_widgets_fonts(self) -> None:
        # Segoe UI, Open Sans
        scale = AppearanceSettings.get_scale("decimal")

        button_font = ("Segoe UI", 11 * scale, "bold")
        self.videos_button.configure(font=button_font)
        self.playlists_button.configure(font=button_font)

        font_style_1 = ctk.CTkFont(family="Comic Sans MS", size=int(16 * scale), weight="bold", slant="italic")
        self.videos_history_frame_info_label.configure(font=font_style_1)
        self.playlists_history_frame_info_label.configure(font=font_style_1)

    def configure_widgets_size(self, width: int = None, height: int = None) -> None:
        self.configure(width=width, height=height)

        scale = AppearanceSettings.get_scale("decimal")

        scrollable_frame_height = height - (10 + (25 * scale) + 14)

        self.videos_scrollable_frame.configure(width=width - 22, height=scrollable_frame_height)
        self.playlists_scrollable_frame.configure(width=width - 22, height=scrollable_frame_height)

        if self.videos_frame_info_label_placed:
            self.place_nav_label("videos")
        elif self.playlists_frame_info_label_placed:
            self.place_nav_label("playlists")

    def bind_widgets_events(self) -> None:
        def on_mouse_enter_videos_histroy_frame_info_label(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the added frame information label.

            This function adjusts the text color of the added frame information label to reflect the hover state when
            the mouse enters the label. The color is obtained from the application's appearance settings
            for the hover state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.videos_history_frame_info_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal")
            )

        def on_mouse_leave_videos_histroy_frame_info_label(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the added frame information label.

            This function resets the text color of the added frame information label to its normal state when the mouse
            leaves the label. The color is obtained from the application's appearance settings for the normal state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.videos_history_frame_info_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_muted")
            )

        self.videos_history_frame_info_label.bind("<Enter>", on_mouse_enter_videos_histroy_frame_info_label)
        self.videos_history_frame_info_label.bind("<Leave>", on_mouse_leave_videos_histroy_frame_info_label)

        ######################################################################################

        def on_mouse_enter_playlists_histroy_frame_info_label(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the added frame information label.

            This function adjusts the text color of the added frame information label to reflect the hover state when
            the mouse enters the label. The color is obtained from the application's appearance settings
            for the hover state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.playlists_history_frame_info_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal")
            )

        def on_mouse_leave_playlists_histroy_frame_info_label(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the added frame information label.

            This function resets the text color of the added frame information label to its normal state when the mouse
            leaves the label. The color is obtained from the application's appearance settings for the normal state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.playlists_history_frame_info_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_muted")
            )

        self.playlists_history_frame_info_label.bind("<Enter>", on_mouse_enter_playlists_histroy_frame_info_label)
        self.playlists_history_frame_info_label.bind("<Leave>", on_mouse_leave_playlists_histroy_frame_info_label)

    def set_widgets_texts(self):
        self.videos_button.configure(text=LanguageManager.data["videos"])
        self.playlists_button.configure(text=LanguageManager.data["playlists"])
        self.videos_history_frame_info_label.configure(
            text=LanguageManager.data["downloaded_videos_history_will_be_display_here"]
        )
        self.playlists_history_frame_info_label.configure(
            text=LanguageManager.data["downloaded_playlists_history_will_be_display_here"]
        )
