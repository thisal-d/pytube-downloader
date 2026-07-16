from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from services import LanguageManager, ThemeManager
from settings import AppearanceSettings

from ..components.setting_navigate_button import SettingNavigateButton


class NavigationPanel(ctk.CTkFrame):
    def __init__(
        self,
        master: Any = None,
        navigation_panels: list[ctk.CTkFrame] = None,
        navigation_button_on_click_callback: Callable = None,
        navigation_buttons_texts: list[str] = None,
        width: int = None,
    ):

        super().__init__(master=master, width=width)

        self.navigation_buttons_texts = navigation_buttons_texts
        self.navigation_buttons = []
        for i in range(len(navigation_buttons_texts)):
            self.navigation_buttons.append(
                SettingNavigateButton(
                    master=self,
                    corner_radius=0,
                    text="",
                    hover=False,
                )
            )
            self.navigation_buttons[-1].configure(
                command=lambda panel=navigation_panels[i], button=self.navigation_buttons[-1]: (
                    self.on_click_navigation_button(button, panel)
                )
            )

        self.navigation_button_on_click_callback = navigation_button_on_click_callback
        self.width = width

        self.set_widgets_accent_color()
        self.set_widgets_colors()
        self.set_widgets_sizes()
        self.set_widgets_texts()
        self.set_widgets_fonts()
        self.bind_widgets_events()
        self.place_widgets()
        # place first panel @ startup
        self.on_click_navigation_button(self.navigation_buttons[0], navigation_panels[0])

        ThemeManager.register_widget(self)
        LanguageManager.register_widget(self)

    def on_click_navigation_button(self, clicked_button: SettingNavigateButton, navigation_panel: ctk.CTkFrame):
        clicked_button.set_clicked_state(True)
        clicked_button.configure(fg_color=ThemeManager.get_accent_color("normal"))

        for navigation_button in self.navigation_buttons:
            if navigation_button is not clicked_button:
                navigation_button.set_clicked_state(False)
                navigation_button.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"))
                navigation_button.configure(
                    text_color=ThemeManager.get_color_based_on_theme("text_muted"),
                    fg_color=ThemeManager.get_color_based_on_theme("primary"),
                )

        self.navigation_button_on_click_callback(navigation_panel)

    def place_widgets(self):
        self.navigation_buttons[0].pack(pady=(50 * AppearanceSettings.get_scale("decimal"), 0))
        for navigation_button in self.navigation_buttons[1::]:
            navigation_button.pack()

    def set_widgets_texts(self):
        for i, button in enumerate(self.navigation_buttons):
            button.configure(text=LanguageManager.data[self.navigation_buttons_texts[i]])

    def update_widgets_text(self):
        self.set_widgets_texts()

    def set_widgets_fonts(self):
        scale = AppearanceSettings.get_scale("decimal")
        button_font = ("Segoe UI", int(14 * scale), "bold")
        for navigation_button in self.navigation_buttons:
            navigation_button.configure(font=button_font)

    def set_widgets_sizes(self):
        scale = AppearanceSettings.get_scale("decimal")
        for navigation_button in self.navigation_buttons:
            navigation_button.configure(height=int(36 * scale), width=self.width)

    def bind_widgets_events(self):
        def on_leave(event, btn):
            if btn.is_clicked:
                btn.configure(
                    fg_color=ThemeManager.get_accent_color("normal"),
                    text_color=ThemeManager.get_color_based_on_theme("text_normal"),
                )
            else:
                btn.configure(
                    fg_color=ThemeManager.get_color_based_on_theme("primary"),
                    text_color=ThemeManager.get_color_based_on_theme("text_muted"),
                )

        def on_enter(event, btn):
            if btn.is_clicked:
                btn.configure(
                    fg_color=ThemeManager.get_accent_color("hover"),
                )
            else:
                btn.configure(
                    fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
                    text_color=ThemeManager.get_color_based_on_theme("text_normal"),
                )

        for navigation_button in self.navigation_buttons:
            navigation_button.bind("<Enter>", lambda event, btn=navigation_button: on_enter(event, btn))
            navigation_button.bind("<Leave>", lambda event, btn=navigation_button: on_leave(event, btn))

    def update_widgets_accent_color(self) -> None:
        self.set_widgets_accent_color()

    def set_widgets_accent_color(self):
        for navigation_button in self.navigation_buttons:
            if navigation_button.is_clicked:
                navigation_button.configure(
                    fg_color=ThemeManager.get_accent_color("normal"),
                )

    def set_widgets_colors(self):
        """Set colors for the widgets."""
        self.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))

        for navigation_button in self.navigation_buttons:
            if navigation_button.is_clicked:
                navigation_button.configure(
                    text_color=ThemeManager.get_color_based_on_theme("text_normal"),
                )
            else:
                navigation_button.configure(
                    fg_color=ThemeManager.get_color_based_on_theme("primary"),
                    text_color=ThemeManager.get_color_based_on_theme("text_muted"),
                )

    def update_widgets_colors(self):
        """Update colors for the widgets."""
        self.set_widgets_colors()
