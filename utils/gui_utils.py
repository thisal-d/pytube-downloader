import os
import subprocess
import sys
from pathlib import Path
from typing import Any


class GuiUtils:
    """
    A utility class for common GUI-related functions.
    """

    @staticmethod
    def do_nothing(*args: Any) -> None:
        """
        A placeholder method that does nothing.

        This method can be used as a default command for GUI elements
        when no action is desired.
        """
        pass

    @staticmethod
    def open_file(path: str | Path) -> None:
        """
        Opens a file or directory with the default system application.
        Cross-platform: works on Windows, macOS, and Linux.
        """
        path = Path(path)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
