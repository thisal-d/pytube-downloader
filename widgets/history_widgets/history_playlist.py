from tkinter import PhotoImage

import customtkinter as ctk
from PIL import Image

from services import LanguageManager, ThemeManager
from settings import AppearanceSettings
from utils import FileUtility, ImageUtility

from .history_object import HistoryObject


class HistoryPlaylist(HistoryObject):
    default_thumbnail_dark_normal: PhotoImage = None
    default_thumbnail_dark_hover: PhotoImage = None

    default_thumbnail_light_normal: PhotoImage = None
    default_thumbnail_light_hover: PhotoImage = None

    default_thumbnail_path_light = "assets/ui images/playlist-light.png"
    default_thumbnail_path_dark = "assets/ui images/playlist-dark.png"

    def __init__(self, videos_count: int = 0, **kwargs):

        self.videos_count = videos_count

        super().__init__(**kwargs)

        LanguageManager.register_widget(self)

        self.set_widgets_texts()

    def get_default_thumbnail(self):
        if HistoryPlaylist.default_thumbnail_dark_normal is None:
            thumbnail_image_light = Image.open(HistoryPlaylist.default_thumbnail_path_light)
            thumbnail_image_dark = Image.open(HistoryPlaylist.default_thumbnail_path_dark)

            image_width = thumbnail_image_light.width
            corner_radius = int(image_width / 18)

            thumbnail_image_light_hover = ImageUtility.create_image_with_hover_effect(
                thumbnail_image_light, intensity_increase=-50
            )
            thumbnail_image_dark_hover = ImageUtility.create_image_with_hover_effect(
                thumbnail_image_dark, intensity_increase=50
            )

            thumbnail_image_light_normal = ImageUtility.create_image_with_rounded_corners(
                thumbnail_image_light, radius=corner_radius
            )
            thumbnail_image_dark_normal = ImageUtility.create_image_with_rounded_corners(
                thumbnail_image_dark, radius=corner_radius
            )
            thumbnail_image_light_hover = ImageUtility.create_image_with_rounded_corners(
                thumbnail_image_light_hover, radius=corner_radius
            )
            thumbnail_image_dark_hover = ImageUtility.create_image_with_rounded_corners(
                thumbnail_image_dark_hover, radius=corner_radius
            )

            thumbnail_size_for_video_history_object = (int(self.width) - 5, int(self.width / 16 * 9))
            thumbnail_image_light_normal = ImageUtility.resize_image(
                image=thumbnail_image_light_normal, new_size=thumbnail_size_for_video_history_object
            )
            thumbnail_image_dark_normal = ImageUtility.resize_image(
                image=thumbnail_image_dark_normal, new_size=thumbnail_size_for_video_history_object
            )
            thumbnail_image_light_hover = ImageUtility.resize_image(
                image=thumbnail_image_light_hover, new_size=thumbnail_size_for_video_history_object
            )
            thumbnail_image_dark_hover = ImageUtility.resize_image(
                image=thumbnail_image_dark_hover, new_size=thumbnail_size_for_video_history_object
            )

            thumbnail_image_path_light_normal = FileUtility.get_available_file_name("temp/thumbnails/history.png")
            thumbnail_image_light_normal.save(thumbnail_image_path_light_normal)

            thumbnail_image_path_dark_normal = FileUtility.get_available_file_name("temp/thumbnails/history.png")
            thumbnail_image_dark_normal.save(thumbnail_image_path_dark_normal)

            thumbnail_image_path_light_hover = FileUtility.get_available_file_name("temp/thumbnails/history.png")
            thumbnail_image_light_hover.save(thumbnail_image_path_light_hover)

            thumbnail_image_path_dark_hover = FileUtility.get_available_file_name("temp/thumbnails/history.png")
            thumbnail_image_dark_hover.save(thumbnail_image_path_dark_hover)

            HistoryPlaylist.default_thumbnail_dark_normal = PhotoImage(file=thumbnail_image_path_dark_normal)
            HistoryPlaylist.default_thumbnail_dark_hover = PhotoImage(file=thumbnail_image_path_dark_hover)

            HistoryPlaylist.default_thumbnail_light_normal = PhotoImage(file=thumbnail_image_path_light_normal)
            HistoryPlaylist.default_thumbnail_light_hover = PhotoImage(file=thumbnail_image_path_light_hover)

        self.configure_default_thumbnails()

    def configure_default_thumbnails(self):
        if ThemeManager.current_theme_mode == "Dark":
            self.thumbnail_normal = HistoryPlaylist.default_thumbnail_dark_normal
            self.thumbnail_hover = HistoryPlaylist.default_thumbnail_dark_hover
        else:
            self.thumbnail_normal = HistoryPlaylist.default_thumbnail_light_normal
            self.thumbnail_hover = HistoryPlaylist.default_thumbnail_light_hover

        self.thumbnail_button.configure(image=self.thumbnail_normal)

    def set_data(self):
        super().set_data()

        self.videos_count_label.configure(text=self.videos_count)

    def bind_widgets_events(self):
        super().bind_widgets_events()

        def on_mouse_enter_self(event):
            self.configure(border_color=AppearanceSettings.settings["root"]["accent_color"]["hover"])
            self.thumbnail_button.configure(image=self.thumbnail_hover)

        def on_mouse_leave_self(event):
            self.configure(border_color=AppearanceSettings.settings["root"]["accent_color"]["normal"])
            self.thumbnail_button.configure(image=self.thumbnail_normal)

        self.videos_count_label.bind("<Enter>", on_mouse_enter_self)
        self.videos_count_label.bind("<Leave>", on_mouse_leave_self)

    def create_widgets(self):
        super().create_widgets()

        self.videos_count_label = ctk.CTkLabel(master=self, text="", justify="left", anchor="e")

    def place_widgets(self):
        super().place_widgets()

        scale = AppearanceSettings.get_scale("decimal")
        y = (self.width) / 16 * 9 + 6

        self.videos_count_label.place(x=(self.width - 2), y=y, anchor="se")

    def set_widgets_sizes(self):
        super().set_widgets_sizes()

        scale = AppearanceSettings.get_scale("decimal")

        self.videos_count_label.configure(width=1, height=15 * scale)

    def set_widgets_fonts(self):
        super().set_widgets_fonts()

        scale = AppearanceSettings.get_scale("decimal")

        self.videos_count_label.configure(font=("Segoe UI", int(11 * scale), "bold"))

    def set_widgets_texts(self):
        self.videos_count_label.configure(text=f"☰♪ {self.videos_count} {LanguageManager.data['videos']}")

    def update_widgets_text(self):
        self.set_widgets_texts()

    def set_widgets_colors(self) -> None:
        super().set_widgets_colors()
        self.videos_count_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))
