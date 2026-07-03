import os
from typing import Literal

from utils import FileUtility, JsonUtility


class AppearanceSettings:
    """
    A class to manage appearance settings for the application.
    """

    settings: dict = {}
    default_settings_directory = "data"
    default_settings_file = default_settings_directory + "\\appearance.json"
    user_settings_directory = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\PyTube Downloader\\data"
    user_settings_file = user_settings_directory + "\\appearance.json"

    SETTINGS = {
        "accent": {
            "colors": [
                ["#0078D4", "#006CBE"],  # Blue
                ["#0A84FF", "#006CFF"],  # Bright blue
                ["#0099BC", "#0082A5"],  # Cyan
                ["#00B7C3", "#009FAE"],  # Teal
                ["#107C10", "#0C660C"],  # Green
                ["#16C60C", "#13A30A"],  # Lime green
                ["#6B69D6", "#5957C4"],  # Indigo
                ["#886CE4", "#7555D9"],  # Violet
                ["#B146C2", "#9D3AAE"],  # Orchid
                ["#E74856", "#D13438"],  # Red
                ["#FF5F5F", "#E14D4D"],  # Soft red
                ["#FF8C00", "#E57A00"],  # Orange
                ["#F7630C", "#DE5A0C"],  # Bright orange
                ["#FFB900", "#E5A500"],  # Amber
                ["#F9F1A5", "#EAE288"],  # Pale yellow
                ["#00CC6A", "#00B45C"],  # Emerald
            ],
            "selected": {"color": ["#886CE4", "#7555D9"], "is_custom": False},
        },
        "window": {"opacity": {"decimal": 0.95, "percentage": 95}, "scale": {"decimal": 1.0, "percentage": 100.0}},
        "theme": {"display_name": "Dark Default", "name": "dark_default"},
    }

    @staticmethod
    def get_opacity(type: Literal["decimal", "percentage"]) -> float | int:
        """
        Get the global window opacity setting.

        Returns:
            float | int : The opacity value as a float between 0.0 and 1.0 or 0 to 100.
        """
        # print(AppearanceSettings.settings["window"]["opacity"])
        return AppearanceSettings.settings["window"]["opacity"][type]

    staticmethod

    def get_scale(type: Literal["decimal", "percentage"]) -> float | int:
        """
        Get the global window opacity setting.

        Returns:
            float | int : The scale value as a float between 1.0 and 2.0 or 100 to 200.
        """
        return AppearanceSettings.settings["window"]["scale"][type]

    @staticmethod
    def set_opacity(type: Literal["decimal", "percentage"], value: int | float) -> None:
        """
        Set the global window opacity setting.
        """
        AppearanceSettings.settings["window"]["opacity"][type] = value

    staticmethod

    def set_scale(type: Literal["decimal", "percentage"], value: int | float) -> None:
        """
        Set the global window opacity setting.
        """
        AppearanceSettings.settings["window"]["scale"][type] = value

    @staticmethod
    def initialize() -> None:
        """
        Initialize settings from a JSON file.

        """
        backup_exists = AppearanceSettings.is_backup_exists()
        if not backup_exists:
            AppearanceSettings.create_backup()

        if backup_exists and FileUtility.is_accessible(AppearanceSettings.user_settings_directory):
            AppearanceSettings.settings = JsonUtility.read_from_file(AppearanceSettings.user_settings_file)
        else:
            AppearanceSettings.settings = JsonUtility.read_from_file(AppearanceSettings.default_settings_file)

        if not AppearanceSettings.are_all_keys_present(AppearanceSettings.SETTINGS, AppearanceSettings.settings):
            AppearanceSettings.add_missing_keys()

        AppearanceSettings.resolve_settings_conflicts()

    @staticmethod
    def resolve_settings_conflicts():
        AppearanceSettings.settings["accent"] = AppearanceSettings.SETTINGS["accent"]

    @staticmethod
    def save_settings() -> None:
        """
        Save the current settings to a file.
        """
        if not AppearanceSettings.is_backup_exists():
            AppearanceSettings.create_backup()

        JsonUtility.write_to_file(AppearanceSettings.user_settings_file, AppearanceSettings.settings)
        # JsonUtility.write_to_file(AppearanceSettings.default_settings_file, AppearanceSettings.settings)

    @staticmethod
    def is_backup_exists() -> bool:
        """
        Check is backup settings exists
        """
        if os.path.exists(AppearanceSettings.user_settings_file):
            return True
        return False

    @staticmethod
    def are_all_keys_present(required: dict, initialized: dict) -> bool:
        """
        Check if all required keys (nested) are present in the initialized settings.

        Args:
            required (dict): The dictionary defining the required structure.
            initialized (dict): The dictionary to check against the required structure.

        Returns:
            bool: True if all keys exist, False otherwise.
        """
        for key, value in required.items():
            if key not in initialized:
                return False
            # If the value is a dictionary, recursively check nested keys
            if isinstance(value, dict):
                if not isinstance(initialized[key], dict) or not AppearanceSettings.are_all_keys_present(
                    value, initialized[key]
                ):
                    return False
        return True

    @staticmethod
    def add_missing_keys() -> None:
        """
        Add any missing keys from the default settings to the initialized settings.
        Fixes missing or malformed keys.
        """

        def recursive_add_missing(default: dict, initialized: dict) -> None:
            for key, value in default.items():
                if key not in initialized or not isinstance(initialized[key], type(value)):
                    # Add missing or fix type mismatch
                    initialized[key] = value
                elif isinstance(value, dict):
                    # Recurse if both are dicts
                    recursive_add_missing(value, initialized[key])

        recursive_add_missing(AppearanceSettings.SETTINGS, AppearanceSettings.settings)

    @staticmethod
    def create_backup() -> None:
        FileUtility.create_directory(AppearanceSettings.user_settings_directory)
        JsonUtility.write_to_file(
            AppearanceSettings.user_settings_file, JsonUtility.read_from_file("data\\appearance.json")
        )
