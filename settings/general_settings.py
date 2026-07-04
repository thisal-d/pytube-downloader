import os
import platform
from pathlib import Path

from utils import FileUtility, JsonUtility


class GeneralSettings:
    """
    A class to manage general settings for the application.
    """

    settings: dict = {}
    default_settings_directory = "data"
    default_settings_file = str(Path("data") / "general.json")
    user_settings_directory = (
        str(Path.home() / "Library" / "Application Support" / "PyTube Downloader" / "data")
        if platform.system() == "Darwin"
        else str(Path.home() / ".local" / "share" / "PyTube Downloader" / "data")
        if platform.system() == "Linux"
        else str(Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "PyTube Downloader" / "data")
    )
    user_settings_file = str(Path(user_settings_directory) / "general.json")
    default_download_dir = str(Path.home() / "Downloads" / "PyTube Downloader")

    SETTINGS = {
        "automatic_download": {"quality": "1080p", "status": "disable"},
        "create_sep_path_for_playlists": False,
        "create_sep_path_for_qualities": False,
        "create_sep_path_for_videos_audios": False,
        "download_directory": False,
        "lang_code": "en",
        "language": "English",
        "load_thumbnail": True,
        "max_simultaneous_downloads": 1,
        "max_simultaneous_converts": 1,
        "max_simultaneous_loads": 1,
        "re_download_automatically": False,
        "reload_automatically": False,
        "update_delay": 0.5,
        "alerts": True,
        "window_geometry": "900x500-7+0",
        "chunk_size": 2097152,
        "display_download_speed_info": False,
    }

    @staticmethod
    def initialize() -> None:
        """
        Initialize settings from a JSON file.

        Returns:
            GeneralSettings: An instance of GeneralSettings initialized with the settings from the JSON file.
        """

        # Create settings backup on user:/app
        backup_exists = GeneralSettings.is_backup_exists()
        if not backup_exists:
            GeneralSettings.create_backup()

        if backup_exists and FileUtility.is_accessible(GeneralSettings.user_settings_directory):
            GeneralSettings.settings = JsonUtility.read_from_file(GeneralSettings.user_settings_file)
        else:
            GeneralSettings.settings = JsonUtility.read_from_file(GeneralSettings.default_settings_file)

        if not GeneralSettings.are_all_keys_present():
            GeneralSettings.add_missing_keys()

        GeneralSettings.restore_invalid_settings()

        if GeneralSettings.settings.get("download_directory") is False:
            GeneralSettings.settings["download_directory"] = GeneralSettings.default_download_dir

    @staticmethod
    def save_settings() -> None:
        """
        Save the current settings to a file.
        """
        if not GeneralSettings.is_backup_exists():
            GeneralSettings.create_backup()

        JsonUtility.write_to_file(GeneralSettings.user_settings_file, GeneralSettings.settings)
        # JsonUtility.write_to_file(GeneralSettings.default_settings_file, GeneralSettings.settings)

    @staticmethod
    def restore_invalid_settings() -> None:
        from services.download_manager import DownloadManager

        if GeneralSettings.settings["automatic_download"]["quality"] not in DownloadManager.resolutions:
            GeneralSettings.settings["automatic_download"]["quality"] = DownloadManager.resolutions[-1]

    @staticmethod
    def is_backup_exists() -> bool:
        """
        Check is backup settings exists
        """
        return bool(os.path.exists(GeneralSettings.user_settings_file))

    @staticmethod
    def are_all_keys_present() -> bool:
        """
        Check if all required settings keys are present in the initialized settings.

        Returns:
            bool: True if all keys exist, False otherwise.
        """
        return all(key in GeneralSettings.settings for key in GeneralSettings.SETTINGS)

    @staticmethod
    def add_missing_keys() -> None:
        """
        Add any missing keys from the default settings to the initialized settings.

        This ensures that the settings include all required keys with their default values.
        """
        for key in GeneralSettings.SETTINGS:
            if key not in GeneralSettings.settings:
                GeneralSettings.settings[key] = GeneralSettings.SETTINGS[key]

    @staticmethod
    def create_backup() -> None:
        FileUtility.create_directory(GeneralSettings.user_settings_directory)
        JsonUtility.write_to_file(GeneralSettings.user_settings_file, JsonUtility.read_from_file("data/general.json"))
