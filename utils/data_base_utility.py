import os
import sqlite3

from utils.file_utility import FileUtility
from utils.logger import get_logger

_log = get_logger(__name__)


class DataBaseUtility:
    @staticmethod
    def create_data_base(data_base_dir: str, data_base_name: str) -> None:
        if not os.path.exists(data_base_dir):
            FileUtility.create_directory(data_base_dir)

        connection = sqlite3.connect(os.path.join(data_base_dir, data_base_name))
        connection.commit()
        connection.close()

    @staticmethod
    def create_table(data_base_name: str, table_name: str, columns: str) -> None:
        connection = sqlite3.connect(data_base_name)
        cursor = connection.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        cursor.close()
        connection.commit()
        connection.close()

    @staticmethod
    def is_data_base_exists(data_base: str) -> bool:
        if os.path.exists(data_base):
            try:
                connection = sqlite3.connect(data_base)
                cursor = connection.cursor()
                sql_videos = "SELECT * FROM videos"
                sql_playlists = "SELECT * FROM playlists"

                # Fetch the data from videos and playlists tables
                cursor.execute(sql_videos).fetchall()
                cursor.execute(sql_playlists).fetchall()
                return True
            except Exception:
                _log.exception("database check failed for %s", data_base)
                return False
        return False
