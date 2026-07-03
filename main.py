import threading

from app import App
from services import InformationManager, LanguageManager, ThemeManager
from settings import AppearanceSettings, GeneralSettings


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
        print(f"PyTube Downloader failed to start:\n{error_details}")
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
