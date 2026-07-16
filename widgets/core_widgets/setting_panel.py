from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from services import ThemeManager
from settings import (
    AppearanceSettings,
)
from widgets.setting_panels import (
    AboutPanel,
    AppearancePanel,
    DownloadsPanel,
    GeneralPanel,
    NavigationPanel,
    NetworkPanel,
)


class SettingPanel(ctk.CTkFrame):
    def __init__(
        self,
        master: Any = None,
        # changes callbacks
        theme_settings_change_callback: Callable = None,
        general_settings_change_callback: Callable = None,
        restart_callback: Callable = None,
    ):

        super().__init__(
            master=master,
        )
        self.general_panel = GeneralPanel(
            master=self, general_settings_change_callback=general_settings_change_callback
        )
        self.appearance_panel = AppearancePanel(
            master=self,
            theme_settings_change_callback=theme_settings_change_callback,
            restart_callback=restart_callback,
        )

        self.network_panel = NetworkPanel(
            master=self, general_settings_change_callback=general_settings_change_callback
        )

        self.downloads_panel = DownloadsPanel(
            master=self,
            general_settings_change_callback=general_settings_change_callback,
            restart_callback=restart_callback,
        )

        self.about_panel = AboutPanel(master=self)

        self.panels = [
            self.general_panel,
            self.appearance_panel,
            self.network_panel,
            self.downloads_panel,
            self.about_panel,
        ]
        self.navigation_panel = NavigationPanel(
            master=self,
            navigation_panels=self.panels,
            navigation_button_on_click_callback=self.place_panel,
            navigation_buttons_texts=["general", "appearance", "network", "downloads", "about"],
            width=200 * AppearanceSettings.get_scale("decimal"),
        )

        self.vertical_line = ctk.CTkFrame(master=self, width=2)

        self.set_widgets_accent_color()
        self.set_widgets_colors()
        self.set_widgets_sizes()
        self.place_widgets()

        ThemeManager.register_widget(self)

    def place_widgets(self) -> None:
        self.navigation_panel.pack(side="left", fill="y")
        self.vertical_line.pack(side="left", fill="y")

    def place_panel(self, selected_panel: ctk.CTkFrame) -> None:
        for panel in self.panels:
            if panel is not selected_panel:
                panel.pack_forget()
            else:
                selected_panel.pack(side="right", fill="both", expand=True)

    def set_widgets_sizes(self):
        scale = AppearanceSettings.get_scale("decimal")
        self.navigation_panel.configure(width=int(400 * scale))

    def set_widgets_accent_color(self):
        self.vertical_line.configure(fg_color=ThemeManager.get_accent_color("normal"))

    def update_widgets_accent_color(self):
        self.set_widgets_accent_color()

    def set_widgets_colors(self):
        """Set colors for the widgets."""
        self.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))

    def update_widgets_colors(self):
        """Update colors for the widgets."""
        self.set_widgets_colors()
