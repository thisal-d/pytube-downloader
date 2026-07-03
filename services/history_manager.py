import os
import platform
import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from utils import DataBaseUtility, DateTimeUtility, FileUtility


class HistoryManager:
    videos_history_data = []
    playlists_history_data = []
    _data_base_dir = (
        Path.home() / "Library" / "Application Support" / "PyTube Downloader"
        if platform.system() == "Darwin"
        else Path.home() / ".local" / "share" / "PyTube Downloader"
        if platform.system() == "Linux"
        else Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "PyTube Downloader"
    )
    data_base_dir = str(_data_base_dir)
    data_base_name = "history.db"
    data_base = str(_data_base_dir / data_base_name)
    connection = None
    cursor = None
    max_history = 40
    video_history_change_callback = None
    playlist_history_change_callback = None
    video_no = 0
    playlist_no = 0

    @staticmethod
    def initialize(
        video_history_change_callback: Callable = None, playlist_history_change_callback: Callable = None
    ) -> None:

        HistoryManager.video_history_change_callback = video_history_change_callback
        HistoryManager.playlist_history_change_callback = playlist_history_change_callback

        if not DataBaseUtility.is_data_base_exists(HistoryManager.data_base):
            DataBaseUtility.create_data_base(HistoryManager.data_base_dir, HistoryManager.data_base_name)
            DataBaseUtility.create_table(
                HistoryManager.data_base,
                "videos",
                "no INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, title TEXT, url TEXT, thumbnail_normal_path TEXT, thumbnail_hover_path TEXT, video_length INTEGER, download_date TEXT",
            )
            DataBaseUtility.create_table(
                HistoryManager.data_base,
                "playlists",
                "no INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, title TEXT, url TEXT, thumbnail_normal_path TEXT, thumbnail_hover_path TEXT, video_count INTEGER, download_date TEXT",
            )

        HistoryManager.connection = sqlite3.connect(HistoryManager.data_base, check_same_thread=False)
        HistoryManager.cursor = HistoryManager.connection.cursor()

        HistoryManager.initialize_history()
        HistoryManager.configure_video_and_playlist_no()

    @staticmethod
    def initialize_history():
        # SQL query to fetch the last 50 rows based on the primary key (no)
        sql_videos = "SELECT * FROM videos"
        sql_playlists = "SELECT * FROM playlists"

        # Fetch the data from videos and playlists tables
        HistoryManager.videos_history_data = HistoryManager.cursor.execute(sql_videos).fetchall()
        HistoryManager.playlists_history_data = HistoryManager.cursor.execute(sql_playlists).fetchall()

        if len(HistoryManager.videos_history_data) > HistoryManager.max_history:
            HistoryManager.videos_history_data = HistoryManager.videos_history_data[
                len(HistoryManager.videos_history_data) - HistoryManager.max_history : :
            ]

        if len(HistoryManager.playlists_history_data) > HistoryManager.max_history:
            HistoryManager.playlists_history_data = HistoryManager.playlists_history_data[
                len(HistoryManager.playlists_history_data) - HistoryManager.max_history : :
            ]

        HistoryManager.videos_history_data = HistoryManager.videos_history_data[::-1]
        HistoryManager.playlists_history_data = HistoryManager.playlists_history_data[::-1]

    @staticmethod
    def configure_video_and_playlist_no():
        sql_videos = "SELECT no FROM videos ORDER BY rowid DESC LIMIT 1"
        sql_playlists = "SELECT no FROM playlists ORDER BY rowid DESC LIMIT 1"

        HistoryManager.cursor.execute(sql_videos)
        data = HistoryManager.cursor.fetchone()
        if data is not None:
            HistoryManager.video_no = data[0]
        else:
            HistoryManager.video_no = 0

        HistoryManager.cursor.execute(sql_playlists)
        data = HistoryManager.cursor.fetchone()
        if data is not None:
            HistoryManager.playlist_no = data[0]
        else:
            HistoryManager.playlist_no = 0

    @staticmethod
    def remove_from_history(url: str, table: Literal["videos", "playlists"]) -> None:
        sql = f"DELETE FROM {table} WHERE url = ?"
        HistoryManager.cursor.execute(sql, (url,))
        HistoryManager.connection.commit()

    @staticmethod
    def remove_from_video_history(no: int) -> None:
        sql = "DELETE FROM videos WHERE no = ?"
        HistoryManager.cursor.execute(sql, (no,))
        HistoryManager.connection.commit()

    @staticmethod
    def remove_from_playlist_history(no: int) -> None:
        sql = "DELETE FROM playlists WHERE no = ?"
        HistoryManager.cursor.execute(sql, (no,))
        HistoryManager.connection.commit()

    @staticmethod
    def is_already_exists(video_url: str, table: Literal["videos", "playlists"]) -> bool:
        sql = f"SELECT COUNT(*) FROM {table} WHERE url = ?"
        HistoryManager.cursor.execute(sql, (video_url,))
        data = HistoryManager.cursor.fetchone()
        if data is not None and data[0] > 0:
            return True
        else:
            return False

    @staticmethod
    def save_video_to_history(video):  #: DownloadedVideo):
        channel = video.channel
        title = video.video_title
        url = video.video_url
        thumbnail_normal_path = video.history_normal_thumbnail_image_path
        thumbnail_hover_path = video.history_hover_thumbnail_image_path
        video_length = video.length
        download_date = DateTimeUtility.get_current_date_time()

        if HistoryManager.is_already_exists(url, "videos"):
            HistoryManager.remove_from_history(url, "videos")
            is_duplicated = True
        else:
            is_duplicated = False

        """
        HistoryManager.videos_history_data.insert(0, (None, channel, title, url, thumbnail_normal_path, thumbnail_hover_path, video_length, download_date))
        if len(HistoryManager.videos_history_data) > HistoryManager.max_history:
             HistoryManager.videos_history_data =  HistoryManager.videos_history_data[0:HistoryManager.max_history]
        """
        HistoryManager.video_no += 1
        sql = "Insert into videos (no, channel, title, url, thumbnail_normal_path, thumbnail_hover_path, video_length, download_date) values (?, ?, ?, ?, ?, ?, ?, ?)"
        HistoryManager.cursor.execute(
            sql,
            (
                HistoryManager.video_no,
                channel,
                title,
                url,
                thumbnail_normal_path,
                thumbnail_hover_path,
                video_length,
                download_date,
            ),
        )
        HistoryManager.connection.commit()

        HistoryManager.video_history_change_callback(
            HistoryManager.video_no,
            channel,
            title,
            url,
            thumbnail_normal_path,
            thumbnail_hover_path,
            video_length,
            download_date,
            is_duplicated,
        )

    @staticmethod
    def save_playlist_to_history(playlist):  #: DownloadedPlayList):
        channel = playlist.channel
        title = playlist.playlist_title
        url = playlist.playlist_url
        thumbnail_normal_path = playlist.downloading_videos[0].history_normal_thumbnail_image_path
        thumbnail_hover_path = playlist.downloading_videos[0].history_hover_thumbnail_image_path
        video_count = playlist.playlist_original_video_count
        download_date = DateTimeUtility.get_current_date_time()

        if HistoryManager.is_already_exists(url, "playlists"):
            HistoryManager.remove_from_history(url, "playlists")
            is_duplicated = True
        else:
            is_duplicated = False

        """
        HistoryManager.playlists_history_data.insert(0, (None, channel, title, url, thumbnail_normal_path, thumbnail_hover_path, video_count, download_date))
        if len(HistoryManager.playlists_history_data) > HistoryManager.max_history:
             HistoryManager.playlists_history_data =  HistoryManager.playlists_history_data[0:HistoryManager.max_history]
        """
        HistoryManager.playlist_no += 1
        sql = "Insert into playlists (no, channel, title, url, thumbnail_normal_path, thumbnail_hover_path, video_count, download_date) values (?, ?, ?, ?, ?, ?, ?, ?)"
        HistoryManager.cursor.execute(
            sql,
            (
                HistoryManager.playlist_no,
                channel,
                title,
                url,
                thumbnail_normal_path,
                thumbnail_hover_path,
                video_count,
                download_date,
            ),
        )
        HistoryManager.connection.commit()

        HistoryManager.playlist_history_change_callback(
            HistoryManager.playlist_no,
            channel,
            title,
            url,
            thumbnail_normal_path,
            thumbnail_hover_path,
            video_count,
            download_date,
            is_duplicated,
        )

    @staticmethod
    def maintain_history(table: str) -> None:
        sql_count = f"SELECT COUNT(*) FROM {table}"
        HistoryManager.cursor.execute(sql_count)
        total_rows = HistoryManager.cursor.fetchone()[0]

        if total_rows > HistoryManager.max_history:
            rows_to_delete = total_rows - HistoryManager.max_history
            sql_delete = f"DELETE FROM {table} WHERE no IN (SELECT no FROM {table} ORDER BY no ASC LIMIT ?)"
            HistoryManager.cursor.execute(sql_delete, (rows_to_delete,))
            HistoryManager.connection.commit()

    @staticmethod
    def clear_invalid_history() -> None:
        HistoryManager.maintain_history("videos")
        HistoryManager.maintain_history("playlists")

        videos_history_req_thumbnails = HistoryManager.cursor.execute(
            "SELECT thumbnail_normal_path, thumbnail_hover_path FROM videos"
        ).fetchall()
        playlists_history_req_thumbnails = HistoryManager.cursor.execute(
            "SELECT thumbnail_normal_path, thumbnail_hover_path FROM playlists"
        ).fetchall()

        required_thumbnails = ["this directory is necessary"]
        for thumbnail in videos_history_req_thumbnails + playlists_history_req_thumbnails:
            required_thumbnails.append(thumbnail[0].split("/")[-1])
            required_thumbnails.append(thumbnail[1].split("/")[-1])

        FileUtility.delete_files(directory="history/thumbnails", files_to_keep=required_thumbnails)
