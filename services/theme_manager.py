import threading
import time
from pathlib import Path
from typing import Any, Literal

import customtkinter as ctk
from settings import AppearanceSettings

try:
    from hPyT import title_bar_color, title_bar_text_color
    _HAS_HPYT = True
except ImportError:
    _HAS_HPYT = False
from utils import JsonUtility


class ThemeManager:
    # List to keep track of all registered child objects
    registered_widgets: list[Any] = []

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
        Uses threading.Event.wait() instead of time.sleep() to avoid busy-polling.
        """
        stop_event = threading.Event()
        while not stop_event.is_set():
            current_mode = ctk.get_appearance_mode()
            if current_mode != ThemeManager.current_theme_mode:
                ThemeManager.current_theme_mode = current_mode
                ThemeManager.update_widgets_colors()
            # Block for 1 second; can be interrupted cleanly by setting the event
            stop_event.wait(timeout=1)

    @staticmethod
    def set_title_bar_style(window: ctk.CTk) -> None:
        if not _HAS_HPYT:
            return
        _MAX_RETRIES = 5
        _BACKOFF_BASE = 0.5  # seconds

        for attempt in range(_MAX_RETRIES):
            try:
                title_bar_color.set(window, ThemeManager.get_color_based_on_theme("background"))
                break
            except Exception as error:
                delay = _BACKOFF_BASE * (2**attempt)
                print(f"theme_manager: failed to set title bar color (attempt {attempt + 1}/{_MAX_RETRIES}): {error}")
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(delay)

        for attempt in range(_MAX_RETRIES):
            try:
                title_bar_text_color.set(window, ThemeManager.get_color_based_on_theme("text_muted"))
                break
            except Exception as error:
                delay = _BACKOFF_BASE * (2**attempt)
                print(
                    f"theme_manager: failed to set title bar text color (attempt {attempt + 1}/{_MAX_RETRIES}): {error}"
                )
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(delay)

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
                print(f"theme_manager: update_widgets_colors failed for {widget!r}: {error}")

    @staticmethod
    def update_widgets_accent_color() -> None:
        """
        Updates accent color in all registered widgets.
        """
        for widget in ThemeManager.registered_widgets:
            try:
                widget.update_widgets_accent_color()
            except Exception as error:
                print(f"theme_manager: update_widgets_accent_color failed for {widget!r}: {error}")

    @staticmethod
    def initialize() -> None:
        """
        Starts the theme tracking system in a separate thread.
        """
        lang_file = Path("data") / "themes" / f"{AppearanceSettings.settings['theme']['name']}.json"
        ThemeManager.theme_colors = JsonUtility.read_from_file(str(lang_file))

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
