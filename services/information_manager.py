import os
from utils import JsonUtility

class InformationManager:
    INFO = {
        "contributors": {},
        "explore_links": [
            {
                "name": "GitHub",
                "url": "https://github.com/Thisal-D/PyTube-Downloader"
            },
            {
                "name": "SourceForge",
                "url": "https://sourceforge.net/projects/pytube-downloader/"
            }
        ],
        "logo": "⚡",
        "name": "PyTube Downloader",
        "version": "6.0.1"
    }
    info = {}
    default_info_directory = f"data"
    default_info_file = default_info_directory + "\\info.json"
    user_info_directory = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\PyTube Downloader\\data"
    user_info_file = user_info_directory + "\\info.json"

    @staticmethod
    def is_backup_exists() -> bool:
        """
        Check is backup info exists
        """

        if os.path.exists(InformationManager.user_info_file):
            return True
        return False

    @staticmethod
    def initialize():
        """
        """

        if InformationManager.is_backup_exists():
            InformationManager.info = JsonUtility.read_from_file(InformationManager.user_info_file)
        else:
            InformationManager.info = JsonUtility.read_from_file(InformationManager.default_info_file)

        if not InformationManager.are_all_keys_present():
            InformationManager.add_missing_keys()
        
        InformationManager.resolve_info_conflicts()


    @staticmethod
    def save_info():
        JsonUtility.write_to_file(InformationManager.user_info_file, InformationManager.info)
    
    
    @staticmethod
    def resolve_info_conflicts():
        InformationManager.info["version"] = InformationManager.INFO["version"]

    @staticmethod
    def are_all_keys_present() -> bool:
        """
        Check if all required info keys are present in the initialized info.

        Returns:
            bool: True if all keys exist, False otherwise.
        """
        for key in InformationManager.INFO.keys():
            if key not in InformationManager.info.keys():
                return False
        return True

    @staticmethod
    def add_missing_keys() -> None:
        """
        Add any missing keys from the default info to the initialized info.

        This ensures that the info include all required keys with their default values.
        """
        for key in InformationManager.INFO.keys():
            if key not in InformationManager.info.keys():
                InformationManager.info[key] = InformationManager.INFO[key]