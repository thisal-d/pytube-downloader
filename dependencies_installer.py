"""Install project dependencies.

Usage:
    python dependencies_installer.py          # core deps
    python dependencies_installer.py windows  # + windows-specific
    python dependencies_installer.py dev      # + dev tools
"""

import subprocess
import sys

extras = sys.argv[1] if len(sys.argv) > 1 else ""
spec = f".[{extras}]" if extras else "."
subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", spec])
