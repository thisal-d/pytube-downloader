import tkinter as tk
import webbrowser
from typing import Any

import customtkinter as ctk
from PIL import Image

from services import LanguageManager, ThemeManager
from settings import AppearanceSettings


class ContributorProfileWidget:
    def __init__(
        self,
        master: Any = None,
        width: int = 35,
        height: int = 35,
        user_name: str = "",
        profile_url: str = "",
        profile_images_paths: tuple[str, str] = None,
    ):

        self.profile_images = (
            ctk.CTkImage(
                Image.open(profile_images_paths[0]),
                size=(
                    width * AppearanceSettings.get_scale("decimal"),
                    height * AppearanceSettings.get_scale("decimal"),
                ),
            ),
            ctk.CTkImage(
                Image.open(profile_images_paths[1]),
                size=(
                    width * AppearanceSettings.get_scale("decimal"),
                    height * AppearanceSettings.get_scale("decimal"),
                ),
            ),
        )

        self.profile_pic_button = ctk.CTkButton(
            master=master,
            hover=False,
            text="",
            command=lambda: webbrowser.open(profile_url),
            image=self.profile_images[0],
        )

        self.user_name_button = ctk.CTkButton(
            master=master,
            text=user_name,
            hover=False,
            width=1,
            command=lambda: webbrowser.open(profile_url),
        )

        self.profile_url_button = ctk.CTkButton(
            master=master,
            hover=False,
            command=lambda: webbrowser.open(profile_url),
        )

        self.hr = tk.Frame(
            master=master,
            height=1,
        )

        self.width = width
        self.height = height

        self.set_widgets_fonts()
        self.set_widgets_sizes()
        self.bind_widgets_events()
        self.set_widgets_accent_color()
        self.set_widgets_colors()
        self.set_widgets_texts()
        ThemeManager.register_widget(self)
        LanguageManager.register_widget(self)

    def bind_widgets_events(self):
        def on_mouse_enter(event_):
            self.profile_pic_button.configure(image=self.profile_images[1])
            self.user_name_button.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
            self.profile_url_button.configure(fg_color=ThemeManager.get_accent_color("hover"))

        def on_mouse_leave(event_):
            self.profile_pic_button.configure(image=self.profile_images[0])
            self.user_name_button.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))
            self.profile_url_button.configure(fg_color=ThemeManager.get_accent_color("normal"))

        self.profile_pic_button.bind("<Enter>", on_mouse_enter)
        self.user_name_button.bind("<Enter>", on_mouse_enter)
        self.profile_url_button.bind("<Enter>", on_mouse_enter)

        self.profile_pic_button.bind("<Leave>", on_mouse_leave)
        self.user_name_button.bind("<Leave>", on_mouse_leave)
        self.profile_url_button.bind("<Leave>", on_mouse_leave)

    def set_widgets_accent_color(self):
        self.hr.configure(bg=ThemeManager.get_accent_color("normal"))
        self.profile_url_button.configure(fg_color=ThemeManager.get_accent_color("normal"))

    def update_widgets_accent_color(self):
        self.set_widgets_accent_color()

    def update_widgets_colors(self):
        """Update colors for the widgets."""
        self.set_widgets_colors()

    def set_widgets_colors(self):
        self.profile_pic_button.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background"),
        )

        self.user_name_button.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background"),
            text_color=ThemeManager.get_color_based_on_theme("text_muted"),
        )

        self.profile_url_button.configure(text_color=ThemeManager.get_color_based_on_theme("background"))

    def set_widgets_sizes(self):
        scale = AppearanceSettings.get_scale("decimal")
        self.profile_pic_button.configure(width=self.width * scale, height=self.height * scale)

        self.profile_url_button.configure(
            width=1 * scale,
            height=26 * scale,
            corner_radius=(26 * scale) / 2,  # half of height → half-circle sides
        )

    def set_widgets_texts(self):
        self.profile_url_button.configure(text=f"🔗 {LanguageManager.data['profile']}")

    def update_widgets_text(self):
        self.set_widgets_texts()

    def set_widgets_fonts(self):
        scale = AppearanceSettings.get_scale("decimal")
        title_font = ("Segoe UI", 13 * scale, "bold")
        self.user_name_button.configure(font=title_font)

        value_font = ("Segoe UI", 11 * scale, "bold")
        self.profile_url_button.configure(font=value_font)

    def grid(
        self,
        row: int = 0,
        pady: int = 3,
        padx: tuple[int | tuple[int, int], int | tuple[int, int], int | tuple[int, int]] = None,
    ) -> None:
        scale = AppearanceSettings.get_scale("decimal")
        self.profile_pic_button.grid(row=row, column=0, padx=padx[0] * scale, pady=pady * scale, sticky="w")
        self.user_name_button.grid(row=row, column=1, padx=padx[1] * scale, pady=pady * scale, sticky="w")
        self.profile_url_button.grid(row=row, column=2, padx=padx[2] * scale, pady=pady * scale, sticky="w")
        self.hr.grid(columnspan=3, row=row + 1, column=0, sticky="ew", padx=50 * scale)
