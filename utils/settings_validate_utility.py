import os
import tkinter as tk
from utils.logger import get_logger

_log = get_logger(__name__)


class SettingsValidateUtility:
    @staticmethod
    def validate_simultaneous_count(count_str: str, with_range: bool) -> bool:
        """
        Validate the simultaneous count entered by the user.

        Args:
            count_str (str): The value entered by the user.

        Returns:
            bool: True if the value is a valid simultaneous count, False otherwise.
        """
        try:
            count = int(count_str)
            if with_range:
                if 0 < count < 11:
                    return True
                else:
                    return False
            else:
                return True
        except ValueError:
            return False

    @staticmethod
    def validate_download_path(path: str) -> bool:
        """
        Validate the download path entered by the user.

        Args:
            path (str): The download path entered by the user.

        Returns:
            bool: True if the path is valid, False otherwise.
        """
        paths = path.split(":")
        if not os.path.exists(paths[0] + ':'):
            return False
        if len(paths) != 2:
            return False
        elif paths[1] != "":
            if not paths[1].startswith("\\"):
                return False
        path = paths[1]
        invalid_characters = ['?', '%', '*', ':', '|', '"', '<', '>']
        for invalid_char in invalid_characters:
            if invalid_char in path:
                return False
        return True

    @staticmethod
    def validate_accent_color(color: str) -> bool:
        """
        Validate the accent color entered by the user.

        Args:
            color (str): The color value entered by the user.

        Returns:
            bool: True if the color is valid, False otherwise.
        """
        try:
            normal_color, hover_color = color.split(",")
            try:
                tk.Button(fg=normal_color, bg=hover_color)
                return True
            except Exception as error:
                _log.debug("validate_accent_color: invalid color %r: %s", color, error)
                return False
        except Exception as error:
            _log.debug("validate_accent_color: could not split color %r: %s", color, error)
            return False
        
    @staticmethod
    def validate_scale_value(value: str) -> bool:
        if value[-1] != "%":
            return False
        
        value = value[0:-1]
        
        try:
            value = float(value)
        except Exception as error:
            _log.debug("validate_scale_value: non-numeric value %r: %s", value, error)
            return False
        
        value = int(value)
        if value >= 100 and value <= 200:
            return True
        return False
    
    @staticmethod
    def validate_opacity_value(value: str) -> bool:
        if value[-1] != "%":
            return False
        
        value = value[0: -1]
        
        try:
            value = float(value)
        except Exception as error:
            _log.debug("validate_opacity_value: non-numeric value %r: %s", value, error)
            return False

        if value >= 60 and value <= 100:
            return True
        return False
    
    @staticmethod
    def validate_chunk_size_value(value: str) -> bool:
        # Check if the input ends with KB or MB
        if not (value.endswith("KB") or value.endswith("MB")):
            return False
        
        try:
            # Extract the numeric part and convert it to float
            numeric_value = float(value[:-2])
        except ValueError as error:
            _log.debug("validate_chunk_size_value: non-numeric value %r: %s", value, error)
            return False
        
        # Convert the value to bytes for consistent comparison
        if value.endswith("KB"):
            size_in_bytes = numeric_value * 1024  # 1 KB = 1024 bytes
        elif value.endswith("MB"):
            size_in_bytes = numeric_value * 1024 * 1024  # 1 MB = 1024 * 1024 bytes
        else:
            return False  # Just a fallback, though the earlier check ensures this won't occur

        # Validate the range in bytes
        min_size = 50 * 1024  # 50KB in bytes
        max_size = 11 * 1024 * 1024  # 11MB in bytes

        return min_size <= size_in_bytes <= max_size