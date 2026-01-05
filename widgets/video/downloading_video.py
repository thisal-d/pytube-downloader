from widgets.video import Video
import customtkinter as ctk
import threading
import subprocess
import os
import sys
import re
from tkinter import PhotoImage
from typing import Literal, List, Union, Dict
from pytubefix import request as pytube_request
import time
from settings import (
    GeneralSettings,
    AppearanceSettings,
)
from services import (
    DownloadManager,
    LanguageManager,
    VideoCountTracker,
    NotificationManager,
    VideoConvertManager,
    ThemeManager
)
from utils import (
    GuiUtils,
    ValueConvertUtility,
    FileUtility
)


class DownloadingVideo(Video):
    """A class representing a downloading video widget."""

    def __init__(
            self,
            root: ctk.CTk,
            master: Union[ctk.CTkFrame, ctk.CTkScrollableFrame],
            width: int = 0,
            height: int = 0,
            # download quality & type
            download_quality: Literal["128kbps", "360p", "720p"] = "720p",
            download_type: Literal["Video", "Audio"] = "Video",
            download_type_info: Dict = None,
            # video details
            video_title: str = "-------",
            channel: str = "-------",
            video_url: str = "-------",
            channel_url: str = "-------",
            length: int = 0,
            thumbnails: List[PhotoImage] = (None, None),
            original_thumbnail_image_path: str = "",
            notification_thumbnail_image_path: str = "",
            # Hsitory thumbnail images
            history_normal_thumbnail_image_path: str = "",
            history_hover_thumbnail_image_path: str = "",
            # video stream data
            video_stream_data: property = None,
            # video download callback utils @ only use if mode is video
            video_download_complete_callback: callable = None,
            # state callbacks only use if mode is playlist
            mode: Literal["video", "playlist"] = "video",
            playlist_title: str = None,
            video_download_status_callback: callable = None,
            video_download_progress_callback: callable = None):

        # download status track and callback
        self.download_state: Literal["waiting", "downloading", "failed", "downloaded", "removed", "converting"] = "waiting"
        self.pause_requested: bool = False
        self.pause_resume_btn_command: Literal["pause", "resume"] = "pause"
        # status and progress callbacks
        self.video_download_complete_callback: callable = video_download_complete_callback
        self.video_download_status_callback: callable = video_download_status_callback
        self.video_download_progress_callback: callable = video_download_progress_callback
        # download info
        self.download_quality: Literal["128kbps", "360p", "720p"] = download_quality
        self.download_type: Literal["Video", "Audio"] = download_type
        self.video_stream_data: property = video_stream_data
        self.download_type_info = download_type_info
        # download mode
        self.playlist_title: str = playlist_title
        self.mode: Literal["video", "playlist"] = mode
        # widgets
        self.sub_frame: Union[ctk.CTkFrame, None] = None
        self.download_progress_bar: Union[ctk.CTkProgressBar, None] = None
        self.download_progress_label: Union[ctk.CTkLabel, None] = None
        self.process_percentage_label: Union[ctk.CTkLabel, None] = None
        self.download_type_label: Union[ctk.CTkLabel, None] = None
        self.net_speed_label: Union[ctk.CTkLabel, None] = None
        self.status_label: Union[ctk.CTkLabel, None] = None
        self.re_download_btn: Union[ctk.CTkButton, None] = None
        self.pause_resume_btn: Union[ctk.CTkButton, None] = None
        # download file info
        self.bytes_downloaded: int = 0
        self.file_size: int = 0
        self.converted_file_size: str = "0 B"
        self.download_file_name: str = ""
        self.download_directory: str = ""
        # Track automatically re download count
        self.automatically_re_download_count = 0
        
        self.audio_for_video_download_completed: bool = False
        self.video_download_completed: bool = False
        self.audio_download_completed: bool = False
        self.audio_only_file_name: str = ""
        self.video_only_file_name: str = ""
        self.total_bytes_downloaded: int = 0
        self.converted_file_name: str = ""
        
        # download speed
        self.total_download_time: int = 0

        super().__init__(
            root=root,
            master=master,
            height=height,
            width=width,
            video_url=video_url,
            channel_url=channel_url,
            thumbnails=thumbnails,
            video_title=video_title,
            channel=channel,
            length=length,
            original_thumbnail_image_path=original_thumbnail_image_path,
            notification_thumbnail_image_path = notification_thumbnail_image_path,
            history_normal_thumbnail_image_path=history_normal_thumbnail_image_path,
            history_hover_thumbnail_image_path=history_hover_thumbnail_image_path
        )
        
        self.set_video_data()
        self.set_waiting()
        VideoCountTracker.add_downloading_video()
        DownloadManager.register(self)

    def download_video(self):
        """
        Start the video download process.
        """
        self.total_download_time = 0
        self.set_downloading_progress()
        threading.Thread(target=self.configure_downloading, daemon=True).start()
        self.set_pause_btn()
        self.pause_resume_btn.place(
            rely=0.5,
            anchor="w",
            relx=1,
            x=-80 * AppearanceSettings.get_scale("decimal"))
        self.download_state = "downloading"
        if self.mode == "playlist":
            self.video_download_status_callback(self, self.download_state)
        self.display_status()

    def re_download_video(self):
        """
        Re-download the video.
        """
        self.re_download_btn.place_forget()
        self.set_waiting()
        DownloadManager.register(self)
        
    def re_convert_video(self):
        """
        Re-convert the video
        """
        self.re_download_btn.place_forget()
        self.set_waiting()
        VideoConvertManager.register(self)

    def display_status(self):
        """
        Display the status of the download.
        """
        
        if self.download_state == "failed":
            self.status_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_warning"),
            )
        elif self.download_state == "waiting" or self.download_state == "paused" or self.download_state == "downloading" or \
            self.download_state == "pausing" or self.download_state == "downloaded" or self.download_state == "converting":
            self.status_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            )
            
        self.status_label.configure(text=LanguageManager.data[self.download_state])
            
    def configure_downloading(self):
        # print("Configure Downloading : configure_downloading()")
        self.download_type_label.configure(text=f"{LanguageManager.data[self.download_type.lower()]} : "
                                                f"{self.download_quality}")
        self.file_size = self.download_type_info["size"]
        self.converted_file_size = ValueConvertUtility.convert_size(self.file_size, 2)
        self.download_file_name = FileUtility.get_available_file_name(self.download_file_name)
        self.set_downloading_progress()
        
        self.download_directory = f"{GeneralSettings.settings['download_directory']}\\"
        
        if self.mode == "playlist" and GeneralSettings.settings["create_sep_path_for_playlists"]:
            self.download_directory += (
                f"{FileUtility.sanitize_filename(self.channel)} - "
                f"{FileUtility.sanitize_filename(self.playlist_title)}\\"
            )
            
        else:
            if GeneralSettings.settings["create_sep_path_for_videos_audios"]:
                self.download_directory += f"{self.download_type}s\\"

            if GeneralSettings.settings["create_sep_path_for_qualities"]:
                self.download_directory += f"{self.download_quality}\\"
            
        if not os.path.exists(self.download_directory):
                try:
                    FileUtility.create_directory(self.download_directory)
                except Exception as error:
                    print(f"downloading_video.py L-213 : {error}")
                    self.set_downloading_failed()
                    return

        self.download_file_name = self.download_directory + (
            f"{FileUtility.sanitize_filename(f"{self.channel} - {self.video_title}")}"
        )
        
        try:
            while (self.download_state == "downloading"):
                self.set_download_files_info()
        except Exception as error:
            print("downloading_video.py L-220 : ", error)
                
    def set_for_converting(self):
        DownloadManager.unregister_from_active(self)
        
        self.set_waiting()
        VideoConvertManager.register(self)
        self.net_speed_label.place_forget()
        self.download_progress_label.place_forget()
        
        self.pause_resume_btn.place_forget()
            
    def set_download_files_info(self):
        """
        Download the video.
        """

        try:
            if self.download_type_info["type"] == "video" and not self.video_download_completed:
                    if not self.download_type_info["inbuilt_audio"]:
                        self.video_only_file_name =  FileUtility.get_available_file_name(f"{self.download_directory}\\video.pytubetemp")
                        current_download_file_name = self.video_only_file_name
                        current_download_type = "video_only"
                    else:
                        self.download_file_name =  FileUtility.get_available_file_name(self.download_file_name + ".mp4")
                        current_download_file_name = self.download_file_name
                        current_download_type = "video"
                    current_stream = self.video_stream_data.get_by_itag(self.download_type_info["itag"])
                    
            elif self.download_type_info["type"] == "video" and self.video_download_completed:
                if not self.audio_for_video_download_completed:
                    self.audio_only_file_name =  FileUtility.get_available_file_name(f"{self.download_directory}\\audio.pytubetemp")
                    current_download_file_name = self.audio_only_file_name
                    current_stream = self.video_stream_data.get_audio_only()
                    current_download_type = "audio_for_video"
                        
            elif  self.download_type_info["type"] == "audio" and not self.audio_download_completed:
                self.download_file_name =  FileUtility.get_available_file_name(self.download_file_name + ".mp3")
                current_download_file_name = self.download_file_name
                current_stream = self.video_stream_data.get_audio_only()
                current_download_type = "audio"
        
        except Exception as error:
            print(f"downloading_video.py L-261 : {error}")
            self.set_downloading_failed()
            return
    
        if self.download_type_info["type"] == "video" and self.video_download_completed and self.audio_for_video_download_completed and not self.download_type_info["inbuilt_audio"]:
            self.set_for_converting()
            
        if self.download_type_info["type"] == "video" and self.video_download_completed and self.download_type_info["inbuilt_audio"]:
            self.set_downloading_completed()
            
        elif self.download_type_info["type"] == "audio" and self.audio_download_completed:
            self.set_downloading_completed()
        
        elif (self.download_type_info["type"] == "audio" and not self.audio_download_completed) or\
            (self.download_type_info["type"] == "video" and not self.video_download_completed and self.download_type_info["inbuilt_audio"]) or\
            (self.download_type_info["type"] == "video" and not self.video_download_completed or\
                self.download_type_info["type"] == "video" and not self.download_type_info["inbuilt_audio"] and not self.audio_for_video_download_completed):
            self.download_file(
                download_stream=current_stream, 
                download_file_name=current_download_file_name, 
                download_file_size=current_stream.filesize,
                download_type=current_download_type
            )

    def download_file(self, download_stream, download_file_name: str, download_file_size: int, download_type: Literal["audio", "video", "video_only", "audio_for_video"] = None):        
        self.bytes_downloaded = 0
        try:
            with open(download_file_name, "wb") as self.downloading_file:
                stream = pytube_request.stream(download_stream.url)
                while 1:
                    try:
                        if self.pause_requested:
                            if self.pause_resume_btn_command != "resume":
                                self.pause_resume_btn.configure(command=self.resume_downloading)
                                self.download_state = "paused"
                                if self.mode == "playlist":
                                    self.video_download_status_callback(self, self.download_state)
                                self.display_status()
                                self.set_resume_btn()
                                self.pause_resume_btn_command = "resume"
                            time.sleep(0.3)
                            continue
                    
                        time_s = time.time()
                        self.download_state = "downloading"
                        self.pause_resume_btn_command = "pause"
                        chunk = next(stream, None)
                        time_e = time.time()
                        self.total_download_time += time_e - time_s
                        if chunk:
                            self.downloading_file.write(chunk)
                            self.net_speed_label.configure(
                                text=ValueConvertUtility.convert_size(
                                    len(chunk) / (time_e - time_s),
                                    1
                                ) + "/s"
                            )
                            self.bytes_downloaded += len(chunk)
                            self.total_bytes_downloaded += len(chunk)

                            self.set_downloading_progress()
                        else:
                            if self.bytes_downloaded == download_file_size:
                                if download_type == "audio":
                                    self.audio_download_completed = True
                                elif download_type == "video":
                                    self.video_download_completed = True
                                    self.audio_for_video_download_completed = True
                                elif download_type == "video_only":
                                    self.video_download_completed = True
                                elif download_type == "audio_for_video":
                                    self.audio_for_video_download_completed = True
                                break
                            else:
                                self.total_bytes_downloaded -= self.bytes_downloaded
                                self.set_downloading_failed()
                                break
                            
                    except Exception as error:
                        print(f"downloading_video.py L-332 : {error}")
                        self.total_bytes_downloaded -= self.bytes_downloaded
                        self.set_downloading_failed()
                        break
                    
        except Exception as error:
            print(f"downloading_video.py L-336 : {error}")
            self.set_downloading_failed()
    
    
    def converting(self):
        self.download_file_name = FileUtility.get_available_file_name(
                self.download_file_name + ".mp4"
            )
            
        self.converted_file_name = FileUtility.get_available_file_name(f"{GeneralSettings.settings['download_directory']}\\temp-converting.mp4")
        
        command = [
            VideoConvertManager.FFMPEG_PATH,
            "-i", self.video_only_file_name,
            "-i", self.audio_only_file_name,
            "-map", "0:v:0",  # Map the video stream from the first input (video file)
            "-map", "1:a:0",  # Map the audio stream from the second input (audio file)
            "-c:v", "copy",
            "-c:a", "aac",
            self.converted_file_name,
            "-y"  # Overwrite the output file if it exists
        ]
        
        try:            
            # Start the process
            process = subprocess.Popen(
                command,
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            duration = None
            progress = 0

            # Read FFmpeg output in real-time
            for line in process.stderr:
                # Extract total duration
                if duration is None:
                    duration_match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", line)
                    if duration_match:
                        hours, minutes, seconds = map(float, duration_match.groups())
                        duration = hours * 3600 + minutes * 60 + seconds

                # Extract current time
                time_match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
                if time_match and duration:
                    hours, minutes, seconds = map(float, time_match.groups())
                    current_time = hours * 3600 + minutes * 60 + seconds
                    progress = (current_time / duration) * 100

                    # Invoke the callback with progress
                    self.set_convert_progress(progress)

            # Wait for the process to finish
            process.wait()

            # Check if the process was successful
            if process.returncode == 0:
                self.set_converting_completed()
            else:
                self.set_converting_failed()
        except Exception as error:
            print("downloading_video.py L-400 : ", error)
            self.set_converting_failed()
    
    def convert_video(self):
        self.download_state = "converting"
        self.set_convert_progress(0)
        self.display_status()
        if self.mode == "playlist":
            self.video_download_status_callback(self, self.download_state)
        threading.Thread(target=self.converting, daemon=True).start()
     
    def set_resume_btn(self):
        """
        Set the resume button.
        """

        self.pause_resume_btn.configure(text="▷")

    def set_pause_btn(self):
        """
        Set the pause button.
        """

        self.pause_resume_btn.configure(text="⏸")

    def pause_downloading(self):
        """
        Pause the downloading process.
        """

        self.pause_resume_btn.configure(command=GuiUtils.do_nothing)
        self.download_state = "pausing"
        self.display_status()
        self.pause_requested = True

    def resume_downloading(self):
        """
        Resume the downloading process.
        """

        self.pause_requested = False
        self.set_pause_btn()
        while self.download_state == "paused":
            time.sleep(0.3)
        self.pause_resume_btn.configure(command=self.pause_downloading)
        self.download_state = "downloading"
        if self.mode == "playlist":
            self.video_download_status_callback(self, self.download_state)
        self.display_status()
        
    def set_convert_progress(self, progress):
        self.process_percentage_label.configure(text=f"{round(progress, 2)} %")
        self.download_progress_bar.set(progress/100)

    def set_downloading_progress(self):
        """
        Set the progress of the downloading process.
        """

        completed_percentage = self.total_bytes_downloaded / self.download_type_info["size"]
        self.download_progress_bar.set(completed_percentage)
        self.process_percentage_label.configure(text=f"{round(completed_percentage * 100, 2)} %")
        self.download_progress_label.configure(
            text=f"{ValueConvertUtility.convert_size(self.total_bytes_downloaded, 2)} / {self.converted_file_size}"
        )
        if self.mode == "playlist":
            self.video_download_progress_callback()
            
    def set_downloading_failed(self):
        """
        Set the status to 'failed' if downloading fails.
        """
        try:
            if self.download_state == "removed":
                return
            
            self.download_state = "failed"
        
            if self.mode == "playlist":
                self.video_download_status_callback(self, self.download_state)
                
            if GeneralSettings.settings["re_download_automatically"] and self.automatically_re_download_count < 5:
                time.sleep(1)
                self.automatically_re_download_count += 1
                self.download_video()
            else:
                DownloadManager.unregister_from_active(self)
                self.display_status()
                self.pause_resume_btn.place_forget()
                self.re_download_btn.place(
                    rely=0.5,
                    anchor="w",
                    relx=1,
                    x=-80 * AppearanceSettings.get_scale("decimal"))

            if self.mode == "video":
                self.show_notification()
        except Exception as error:
            print("downloading_video.py L-540 : ", error)
            
    def set_converting_failed(self):
        VideoConvertManager.unregister_from_active(self)
        VideoConvertManager.unregister_from_queued(self)
        self.re_download_btn.configure(command=self.re_convert_video)
        self.set_downloading_failed()

    def set_waiting(self):
        """
        Set the status to 'waiting' if the download is queued.
        """
        
        self.download_state = "waiting"
        if self.mode == "playlist":
            self.video_download_status_callback(self, self.download_state)
        self.display_status()
        self.pause_resume_btn.place_forget()
        self.download_progress_bar.set(0.5)
        self.process_percentage_label.configure(text="")
        self.net_speed_label.configure(text="")
        self.download_progress_label.configure(text="")
        self.download_type_label.configure(text="")
    
    def set_downloading_completed(self):
        """
        Set the status to 'downloaded' if the download is downloaded.
        """
        self.download_state = "downloaded"
        DownloadManager.unregister_from_active(self)
        VideoConvertManager.unregister_from_active(self)
        VideoConvertManager.unregister_from_queued(self)
        self.pause_resume_btn.place_forget()
        self.display_status()
        
        if self.mode == "playlist":
            self.video_download_status_callback(self, self.download_state)
        if self.mode == "video":
            self.video_download_complete_callback(self)
            try:
                self.show_notification()
            except Exception as error:
                print("downloading_video.py L-562 : ", error)
            self.kill()
    
    def rename_to_original_name(self):
        self.download_file_name = FileUtility.get_available_file_name(self.download_file_name + ".mp4")
        os.rename(self.converted_file_name, self.download_file_name)
    
    def remove_temporary_files(self):
        try:
            os.remove(self.audio_only_file_name)
        except Exception as error:
            print("downloading_video.py L-573 : ", error)
            
        try:
            os.remove(self.video_only_file_name)
        except Exception as error:
            print("downloading_video.py L-578 : ", error)
    
    def set_converting_completed(self):
        self.set_convert_progress(100)
        VideoConvertManager.unregister_from_active(self)
        VideoConvertManager.unregister_from_queued(self)
        self.rename_to_original_name()
        self.status_label.configure(text="Converted")
        self.remove_temporary_files()
        self.set_downloading_completed()

    def show_notification(self):
        if GeneralSettings.settings["alerts"]:
            if self.download_state == "downloaded":
                status_message = LanguageManager.data["download_completed_notifi"]
            else:
                status_message = LanguageManager.data["download_failed_notifi"]
        
            # Show Download completed Notification
            NotificationManager.register(
                video_title=self.video_title,
                channel_name=self.channel,
                status_message=status_message,
                download_type="{}/{}".format(self.download_type, self.download_quality),
                file_size=self.file_size,
                download_directory=self.download_directory,
                download_file_name=self.download_file_name,
                downloaded_file_size=self.total_bytes_downloaded,
                download_mode=self.mode,
                download_status=self.download_state,
                thumbnail_path=self.notification_thumbnail_image_path
            )
    
    # create widgets
    def create_widgets(self):
        """
        Create all required widgets.
        """
        super().create_widgets()

        self.sub_frame = ctk.CTkFrame(self)
        self.download_progress_bar = ctk.CTkProgressBar(master=self.sub_frame)
        self.download_progress_label = ctk.CTkLabel(master=self.sub_frame, text="")
        self.process_percentage_label = ctk.CTkLabel(master=self.sub_frame, text="")
        self.download_type_label = ctk.CTkLabel(master=self.sub_frame, text="")
        self.net_speed_label = ctk.CTkLabel(master=self.sub_frame, text="")
        self.status_label = ctk.CTkLabel(master=self.sub_frame, text="")
        self.re_download_btn = ctk.CTkButton(
            master=self,
            text="⟳",
            command=self.re_download_video,
            hover=False
        )
        self.pause_resume_btn = ctk.CTkButton(
            master=self,
            text="⏸",
            command=self.pause_downloading,
            hover=False
        )

    def set_widgets_texts(self):
        
        super().set_widgets_texts()
        
        self.download_type_label.configure(text=f"{LanguageManager.data[self.download_type.lower()]} : "
                                                f"{self.download_quality}")
        self.display_status()
        
    def set_widgets_fonts(self):
        """
        Set fonts for all widgets.
        """
        
        super().set_widgets_fonts()

        scale = AppearanceSettings.get_scale("decimal")

        self.download_progress_label.configure(font=("Segoe UI", 12 * scale, "bold"))
        self.process_percentage_label.configure(font=("Segoe UI", 12 * scale, "bold"))
        self.download_type_label.configure(font=("Segoe UI", 12 * scale, "bold"))
        self.net_speed_label.configure(font=("Segoe UI", 12 * scale, "bold"), )
        self.status_label.configure(font=("Segoe UI", 12 * scale, "bold"))
        self.re_download_btn.configure(font=("Segoe UI", 20 * scale, "normal"))
        self.pause_resume_btn.configure(font=("Segoe UI", 20 * scale, "normal"))

    def set_widgets_sizes(self):
        """
        Set sizes for all widgets.
        """

        super().set_widgets_sizes()

        scale = AppearanceSettings.get_scale("decimal")

        self.sub_frame.configure(height=self.height - 3)
        self.download_progress_bar.configure(height=8 * scale, width=self.sub_frame.winfo_width())
        self.download_progress_label.configure(height=20 * scale)
        self.process_percentage_label.configure(height=20 * scale)
        self.download_type_label.configure(height=20 * scale)
        self.net_speed_label.configure(height=20 * scale)
        self.status_label.configure(height=20 * scale)
        self.re_download_btn.configure(width=15 * scale, height=15 * scale)
        self.pause_resume_btn.configure(width=15 * scale, height=15 * scale)

    def set_widgets_accent_color(self):
        """
        Set accent colors for widgets.
        """

        super().set_widgets_accent_color()

        self.download_progress_bar.configure(
            progress_color=ThemeManager.get_accent_color("normal")
        )
        self.re_download_btn.configure(text_color=ThemeManager.get_accent_color("normal"))
        self.pause_resume_btn.configure(text_color=ThemeManager.get_accent_color("normal"))

    def set_widgets_colors(self) -> None:
        """
        Set colors for all widgets.
        """

        super().set_widgets_colors()

        self.sub_frame.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"))
        self.download_progress_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )
        self.process_percentage_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )
        self.download_type_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )
        self.download_progress_bar.configure(fg_color=ThemeManager.get_color_based_on_theme("secondary"))
        self.net_speed_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))
        self.status_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.re_download_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"))
        self.pause_resume_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"))

    def on_mouse_enter_self(self, event):
        """
        Handle mouse entering the widget area.
        """

        # super().on_mouse_enter_self(event)

        """
        self.sub_frame.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["hover"])
        self.re_download_btn.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["hover"])
        self.pause_resume_btn.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["hover"])
        """

    def on_mouse_leave_self(self, event):
        """
        Handle mouse leaving the widget area.
        """

        # super().on_mouse_leave_self(event)

        """
        self.sub_frame.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["normal"])
        self.re_download_btn.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["normal"])
        self.pause_resume_btn.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["normal"])
        """
        
    def bind_widgets_events(self):
        """
        Bind events to all widgets.
        """

        super().bind_widgets_events()

        def on_mouse_enter_re_download_btn(_event):
            self.re_download_btn.configure(
                text_color=ThemeManager.get_accent_color("hover"),
            )
            # self.on_mouse_enter_self(event)

        def on_mouse_leave_download_btn(_event):
            self.re_download_btn.configure(
                text_color=ThemeManager.get_accent_color("normal"),
            )

        self.re_download_btn.bind("<Enter>", on_mouse_enter_re_download_btn)
        self.re_download_btn.bind("<Leave>", on_mouse_leave_download_btn)

        def on_mouse_enter_pause_resume_btn(_event):
            self.pause_resume_btn.configure(
                text_color=ThemeManager.get_accent_color("hover"),

            )
            # self.on_mouse_enter_self(event)

        def on_mouse_leave_pause_resume_btn(_event):
            self.pause_resume_btn.configure(
                text_color=ThemeManager.get_accent_color("normal"),
            )

        self.pause_resume_btn.bind("<Enter>", on_mouse_enter_pause_resume_btn)
        self.pause_resume_btn.bind("<Leave>", on_mouse_leave_pause_resume_btn)

    def place_widgets(self):
        """
        Place all widgets using a grid layout.
        """
        super().place_widgets()
        self.sub_frame.place(relx=0.5, y=1)
        self.download_progress_label.place(relx=0.25, anchor="center", rely=0.2)
        self.download_type_label.place(relx=0.75, anchor="center", rely=0.2)
        self.download_progress_bar.place(relwidth=1, rely=0.5, anchor="w")
        self.process_percentage_label.place(relx=0.115, anchor="center", rely=0.8)
        self.net_speed_label.place(relx=0.445, anchor="center", rely=0.8)
        self.status_label.place(relx=0.775, anchor="center", rely=0.8)

    def configure_widget_sizes(self, _event):
        """
        Configure widget sizes based on the parent widget's size.
        """
        scale = AppearanceSettings.get_scale("decimal")
        self.info_frame.configure(
            width=(
                    (self.winfo_width() / 2) - (self.thumbnail_btn.winfo_width() + 5) -
                    (10 * scale) - (20 * scale)
            )
        )
        self.sub_frame.configure(width=(self.winfo_width() / 2) - (100 * scale))

    def __del__(self):
        del self.download_state
        del self.pause_requested
        del self.pause_resume_btn_command
        # status and progress callbacks
        del self.video_download_complete_callback
        del self.video_download_status_callback
        del self.video_download_progress_callback
        # download info
        del self.download_quality
        del self.download_type
        del self.video_stream_data
        # download mode
        del self.playlist_title
        del self.mode
        # widgets
        del self.sub_frame
        del self.download_progress_bar
        del self.download_progress_label
        del self.process_percentage_label
        del self.download_type_label
        del self.net_speed_label
        del self.status_label
        del self.re_download_btn
        del self.pause_resume_btn
        # download file info
        del self.bytes_downloaded
        del self.file_size
        del self.converted_file_size
        del self.download_file_name
        del self.download_directory
        # Track automatically re download count
        del self.automatically_re_download_count

        super().__del__()

    def destroy_widgets(self):
        """Destroy the child widgets."""
        self.sub_frame.destroy()
        self.download_progress_bar.destroy()
        self.download_progress_label.destroy()
        self.process_percentage_label.destroy()
        self.download_type_label.destroy()
        self.net_speed_label.destroy()
        self.status_label.destroy()
        self.re_download_btn.destroy()
        self.pause_resume_btn.destroy()

        super().destroy_widgets()

    def kill(self):
        """
        Kill the downloading process.
        """
        DownloadManager.unregister_from_active(self)
        DownloadManager.unregister_from_queued(self)
        VideoConvertManager.unregister_from_active(self)
        VideoConvertManager.unregister_from_queued(self)
        VideoCountTracker.remove_downloading_video()
        self.download_state = "removed"
        if self.mode == "playlist":
            self.video_download_status_callback(self, self.download_state)
        
        super().kill()