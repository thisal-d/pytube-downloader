from pathlib import Path
from typing import List
from utils.logger import get_logger

_log = get_logger(__name__)


class FileUtility:
    """
    A utility class for handling file-related operations such as directory creation, path formatting,
    checking accessibility, sanitizing filenames, and obtaining available file names.
    """

    @staticmethod
    def create_directory(path: str) -> None:
        """
        Create the directory structure if it doesn't exist.

        Args:
            path (str): The path where the directory structure should be created.
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except Exception as error:
            _log.warning("create_directory failed for %r: %s", path, error)
            raise

    @staticmethod
    def format_path(path: str) -> str:
        """
        Normalize the given path using pathlib, removing redundant separators.

        This replaces the legacy Windows-only backslash-forcing implementation.
        The returned string uses the OS-native separator.

        Args:
            path (str): The path to be formatted.

        Returns:
            str: The normalized path string.
        """
        return str(Path(path.strip()))

    @staticmethod
    def is_accessible(path: str) -> bool:
        """
        Check if the given path is accessible by attempting to create a file.

        Args:
            path (str): The path to be checked.

        Returns:
            bool: True if the path is accessible, False otherwise.
        """
        probe = Path(path) / "pytube.pytube"
        try:
            FileUtility.create_directory(path)
            probe.write_text("")
            probe.unlink()
            return True
        except Exception as error:
            _log.warning("is_accessible check failed for %r: %s", path, error)
            return False

    @staticmethod
    def is_readable(path: str) -> bool:
        """
        Check if the file is readable.

        Args:
            path (str): The file to be checked.

        Returns:
            bool: True if the path is readable, False otherwise.
        """
        p = Path(path)
        try:
            p.open("r").close()
            return True
        except (OSError, UnicodeDecodeError):
            pass
        try:
            p.open("rb").close()
            return True
        except Exception as error:
            _log.warning("is_readable failed for %r: %s", path, error)
            return False

    @staticmethod
    def sanitize_filename(url: str) -> str:
        """
        Sanitize the filename by removing invalid characters.

        Args:
            url (str): The URL from which invalid characters are to be removed.

        Returns:
            str: The sanitized filename.
        """
        filename = url
        replaces = ["\\", "/", ":", '"', "?", "<", ">", "|", "*"]
        for char in replaces:
            filename = filename.replace(char, "~")
        return filename

    @staticmethod
    def get_available_file_name(original_file_name: str) -> str:
        """
        Get an available file name by appending a numerical suffix if the original file name already exists.

        Args:
            original_file_name (str): The original file name with extension.

        Returns:
            str: The available file name.
        """
        p = Path(original_file_name)
        if not p.exists():
            return original_file_name

        base_name = p.parent / p.stem
        extension = p.suffix.lstrip(".")
        counter = 0
        candidate = Path(f"{base_name} ({counter}).{extension}")
        while candidate.exists():
            counter += 1
            candidate = Path(f"{base_name} ({counter}).{extension}")
        return str(candidate)

    @staticmethod
    def delete_files(directory: str, files_to_keep: List[str] = None) -> None:
        """
        Delete files in the specified directory, except those listed in files_to_keep.

        Args:
            directory (str): The path to the directory containing the files to delete.
            files_to_keep (List[str], optional): A list of file names to exclude from deletion. Default is None.
        """
        for file_path in Path(directory).iterdir():
            try:
                if files_to_keep is None or file_path.name not in files_to_keep:
                    file_path.unlink()
            except Exception as error:
                _log.warning("delete_files could not remove %r from %r: %s", file_path.name, directory, error)
