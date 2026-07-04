import threading

from customtkinter import CTkScrollableFrame

from app import App
from services import InformationManager, LanguageManager, ThemeManager
from settings import AppearanceSettings, GeneralSettings
from utils.logger import get_logger

# Patch CTkScrollableFrame._check_if_valid_scroll to handle string widgets
# (e.g., when scrolling over ttk.Combobox dropdown which returns string)
_original_check_if_valid_scroll = CTkScrollableFrame._check_if_valid_scroll


def _patched_check_if_valid_scroll(self, widget):
    if isinstance(widget, str):
        try:
            widget = self.nametowidget(widget)
        except Exception:
            return False
    return _original_check_if_valid_scroll(self, widget)


CTkScrollableFrame._check_if_valid_scroll = _patched_check_if_valid_scroll

_log = get_logger(__name__)


def main() -> None:
    """Application entry point."""
    try:
        # configure settings
        GeneralSettings.initialize()
        AppearanceSettings.initialize()
        LanguageManager.initialize()
        ThemeManager.initialize()
        InformationManager.initialize()

        # Initialize app.
        app = App()
        app.after(100, threading.Thread(target=app.initialize, daemon=True).start)

        # just run the app
        app.run()
    except Exception as error:
        import traceback

        error_details = traceback.format_exc()
        _log.critical("PyTube Downloader failed to start:\n%s", error_details)
        try:
            import tkinter as tk
            from tkinter import messagebox

            _root = tk.Tk()
            _root.withdraw()
            messagebox.showerror(
                "PyTube Downloader - Startup Error",
                f"The application failed to start.\n\nReason: {error}\n\nCheck the console for full details.",
            )
            _root.destroy()
        except Exception:
            pass  # If tkinter itself is unavailable the console message is sufficient


if __name__ == "__main__":
    main()

# Codes under here will only execute when the app is closed
