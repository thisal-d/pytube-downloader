import os
from typing import List


class FileUtility:
    """
    A utility class for handling file-related operations such as directory creation, path formatting,
    checking accessibility, sanitizing filenames, and obtaining available file names.
    """
    @staticmethod
    def create_directory(path: str):
        """
        Create the directory structure if it doesn't exist.

        Args:
            path (str): The path where the directory structure should be created.
        """
        try:
            if not os.path.exists(path):
                sub_paths = path.split("\\")
                for i in range(0, len(sub_paths)):
                    sub_path = "\\".join(sub_paths[0:i + 1])
                    if not os.path.exists(sub_path):
                        os.mkdir(sub_path)
        except Exception as error:
            print(f"file_utility: create_directory failed for {path!r}: {error}")
            raise

    @staticmethod
    def format_path(path: str) -> str:
        """
        Format the given path to replace forward slashes with backward slashes and remove redundant slashes.

        Args:
            path (str): The path to be formatted.

        Returns:
            str: The formatted path.
        """
        path = path.strip().replace("/", "\\")
        while "\\\\" in path:
            path = path.replace("\\\\", "\\")
        paths = [p for p in path.split("\\") if p.strip()]
        path = "\\".join(paths)
        if path.endswith("\\"):
            path = path[:-1]
        return path

    @staticmethod
    def is_accessible(path: str) -> bool:
        """
        Check if the given path is accessible by attempting to create a file.

        Args:
            path (str): The path to be checked.

        Returns:
            bool: True if the path is accessible, False otherwise.
        """
        file = os.path.join(path, "pytube.pytube")
        try:
            FileUtility.create_directory(path)
            with open(file, "w"):
                pass
            os.remove(file)
            return True
        except Exception as error:
            print(f"file_utility: is_accessible check failed for {path!r}: {error}")
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
        try:
            with open(path, "r"):
                pass
            return True
        except (OSError, UnicodeDecodeError):
            pass
        try:
            with open(path, "rb"):
                pass
            return True
        except Exception as error:
            print(f"file_utility: is_readable failed for {path!r}: {error}")
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
        if os.path.exists(original_file_name):
            split_path = original_file_name.split(".")
            base_name, extension = ".".join(split_path[0:-1]), split_path[-1]
            counter = 0
            while os.path.exists(f"{base_name} ({counter}).{extension}"):
                counter += 1

            return f"{base_name} ({counter}).{extension}"
        else:
            return original_file_name
    
    @staticmethod
    def delete_files(directory: str, files_to_keep: List[str] = None) -> None:
        """
        Delete files in the specified directory, except those listed in files_to_keep.

        Args:
            directory (str): The path to the directory containing the files to delete.
            files_to_keep (List[str], optional): A list of file names to exclude from deletion. Default is None.
        """
        for file_name in os.listdir(directory):
            try:
                if files_to_keep is None or file_name not in files_to_keep:
                    os.remove(os.path.join(directory, file_name))
            except Exception as error:
                print(f"file_utility: delete_files could not remove {file_name!r} from {directory!r}: {error}")
