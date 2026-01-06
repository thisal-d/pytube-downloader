import customtkinter as ctk
import time
from typing import List, Tuple, Any, Literal
import threading
from settings import AppearanceSettings
from utils import JsonUtility
from hPyT import title_bar_color, title_bar_text_color

class ThemeManager:
    # List to keep track of all registered child objects
    registered_widgets: List[Any] = []

    # Variable to track current theme mode
    current_theme_mode: Literal["Dark", "Light", None] = None

    theme_colors: dict = None
    
    @staticmethod
    def update_theme() -> None:
        ThemeManager.initialize()
        ThemeManager.update_widgets_colors()
        
    @staticmethod
    def get_color_based_on_theme(color: str) -> str:
        """Returns appropriate color based on the current theme mode."""
        return ThemeManager.theme_colors[color]  # For dark them

    @staticmethod
    def get_accent_color(state: Literal["normal", "hover"]) -> str:
        """Returns the current accent color."""
        # print(AppearanceSettings.settings["accent"]["selected"])
        if state == "normal":
            color = AppearanceSettings.settings["accent"]["selected"]["color"][0]
        elif state == "hover":
            color = AppearanceSettings.settings["accent"]["selected"]["color"][1]
        else:
            # print("theme_manager.py L31: Invalid state for accent color")
            color = AppearanceSettings.settings["accent"]["selected"][0]
        return color

    @staticmethod
    def track_theme_mode_changes() -> None:
        """
        Periodically checks for changes in theme and updates registered widgets.
        """
        while True:
            current_mode = ctk.get_appearance_mode()
            if current_mode != ThemeManager.current_theme_mode:
                ThemeManager.current_theme_mode = current_mode
                ThemeManager.update_widgets_colors()
            # Wait 1 second before checking the theme mode again
            time.sleep(1)

    @staticmethod
    def set_title_bar_style(window: ctk.CTk) -> None:
        while True:
            try:
                title_bar_color.set(window, ThemeManager.get_color_based_on_theme("background")) # sets the titlebar color to background color
                break
            except Exception as error:
                print("Error on changin title bar color")
                time.sleep(1)
                continue
        
        while True:
            try:
                title_bar_text_color.set(window, ThemeManager.get_color_based_on_theme("text_muted")) # sets the titlebar color to text color
                break
            except Exception as error:
                print("Error on changin title text color")
                time.sleep(1)
                continue

    @staticmethod
    def update_accent_color() -> None:
        """
        Updates accent color callback the change to registered widgets.
        """
        ThemeManager.update_widgets_accent_color()

    @staticmethod
    def update_widgets_colors() -> None:
        """
        Updates colors in all registered widgets based on the current theme mode.
        """
        for widget in ThemeManager.registered_widgets:
            try:
                widget.update_widgets_colors()
            except Exception as error:
                print(f"theme_manager.py L51 : {error}")

    @staticmethod
    def update_widgets_accent_color() -> None:
        """
        Updates accent color in all registered widgets.
        """
        for widget in ThemeManager.registered_widgets:
            try:
                widget.update_widgets_accent_color()
            except Exception as error:
                print(f"theme_manager.py L62 : {error}")

    @staticmethod
    def initialize() -> None:
        """
        Starts the theme tracking system in a separate thread.
        """
        lang_file = f"data\\themes\\{AppearanceSettings.settings["theme"]["name"]}.json"
        ThemeManager.theme_colors = JsonUtility.read_from_file(lang_file)

        """"""
        theme_tracking_thread = threading.Thread(target=ThemeManager.track_theme_mode_changes)
        theme_tracking_thread.daemon = True  # Daemonize the thread, so it exits when the main program exits
        theme_tracking_thread.start()

    @staticmethod
    def register_widget(widget: Any) -> None:
        """
        Registers a widget with the ThemeManager for theme updates.

        Args:
            widget (Any): The widget to register.
        """
        ThemeManager.registered_widgets.append(widget)

    @staticmethod
    def unregister_widget(widget: Any) -> None:
        """
        Unregisters a widget from the ThemeManager.

        Args:
            widget (Any): The widget to unregister.
        """
        ThemeManager.registered_widgets.remove(widget)
