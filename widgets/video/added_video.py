import threading
import time
import tkinter as tk
from collections.abc import Callable
from typing import Literal

import customtkinter as ctk
import pytubefix as pytube
from PIL import Image

from services import (
    LanguageManager,
    LoadManager,
    ThemeManager,
    VideoCountTracker,
)
from settings import (
    AppearanceSettings,
    GeneralSettings,
)
from utils import DownloadInfoUtility, FileUtility, ImageUtility
from utils.logger import get_logger
from widgets.video import Video

_log = get_logger(__name__)


class AddedVideo(Video):
    PYTUBE_CLIENTS: list[str] = [
        "WEB",
        "WEB_EMBED",
        "WEB_MUSIC",
        "WEB_CREATOR",
        "WEB_SAFARI",
        "MWEB",
        "WEB_KIDS",
        "ANDROID",
        "ANDROID_EMBED",
        "ANDROID_VR",
        "ANDROID_MUSIC",
        "ANDROID_CREATOR",
        "ANDROID_TESTSUITE",
        "ANDROID_PRODUCER",
        "ANDROID_KIDS",
        "IOS",
        "IOS_EMBED",
        "IOS_MUSIC",
        "IOS_CREATOR",
        "IOS_KIDS",
        "TV",
        "TV_EMBED",
        "MEDIA_CONNECT",
    ]

    def __init__(
        self,
        root: ctk.CTk,
        master: ctk.CTkFrame | ctk.CTkScrollableFrame,
        width: int = 0,
        height: int = 0,
        # video url
        video_url: str = "",
        # callback functions for buttons
        video_download_button_click_callback: Callable = None,
        # state callbacks only use if mode is play list
        mode: Literal["video", "playlist"] = "video",
        video_load_status_callback: callable = None,
    ):

        # video info
        self.video_stream_data: pytube.YouTube.streams = None
        self.support_download_types: list[dict[str, int]] | None = None
        # download info
        self.download_quality: Literal["128kbps", "360p", "720p"] = "720p"
        self.download_type: Literal["Audio", "Video"] = "Video"
        self.selected_download_type_info: dict = None
        # callback utils
        self.video_download_button_click_callback: Callable = video_download_button_click_callback
        self.video_load_status_callback: Callable = video_load_status_callback
        # state
        self.load_state: Literal["waiting", "loading", "failed", "loaded", "removed"] = "waiting"
        # widgets
        self.sub_frame: ctk.CTkFrame | None = None
        self.resolution_select_menu: ctk.CTkComboBox | None = None
        self.download_btn: ctk.CTkButton | None = None
        self.status_label: ctk.CTkLabel | None = None
        self.reload_btn: ctk.CTkButton | None = None
        # video object
        self.video: pytube.YouTube | None = None

        self.mode: Literal["video", "playlist"] = mode
        # Track automatically reload count
        self.automatically_reload_count: int = 0
        self.pytube_client_index: int = -1

        super().__init__(root=root, master=master, width=width, height=height, video_url=video_url)

        self.set_waiting()
        LoadManager.register(self)
        VideoCountTracker.add_added_video()

    def reload_video(self):
        self.load_state = None
        self.reload_btn.place_forget()
        self.thumbnail_btn.configure(disabledforeground=ThemeManager.get_color_based_on_theme("text_muted"))
        self.set_waiting()
        LoadManager.register(self)

    def load_video(self):
        self.load_state = "loading"
        if self.mode == "playlist":
            self.video_load_status_callback(self, self.load_state)
        self.status_label.configure(text=LanguageManager.data["loading"])
        load_thread = threading.Thread(target=self.retrieve_video_data)
        load_thread.daemon = True
        load_thread.start()

    def get_video_thumbnails(self) -> tuple[tk.PhotoImage, tk.PhotoImage]:
        thumbnail_size_for_video_object = (
            int(117 * AppearanceSettings.get_scale("decimal")),
            int(66 * AppearanceSettings.get_scale("decimal")),
        )

        thumbnail_for_video_object_save_directory = "temp/thumbnails/"
        thumbnail_for_video_history_object_save_directory = "history/thumbnails/"

        thumbnail_url = self.video.thumbnail_url
        # Generate download path to thumbnail based on url
        file_name = FileUtility.sanitize_filename(thumbnail_url)
        self.original_thumbnail_image_path = FileUtility.get_available_file_name(
            thumbnail_for_video_object_save_directory + file_name + "-og.png"
        )
        ImageUtility.download_image(image_url=thumbnail_url, output_image_path=self.original_thumbnail_image_path)
        # Open downloaded thumbnail as Image
        thumbnail = Image.open(self.original_thumbnail_image_path)

        # getting downloaded thumbnail width and height
        image_height = thumbnail.height
        image_width = thumbnail.width

        # save og thumbnail for notifications
        ignore_pos = int(image_height * 0.4 / 2)
        start_pos = (0, ignore_pos)
        end_pos = (image_width, image_height - ignore_pos)
        self.notification_thumbnail_image_path = FileUtility.get_available_file_name(
            thumbnail_for_video_object_save_directory + file_name + "-normal-notify-changed.png"
        )
        ImageUtility.crop_image(thumbnail, start_position=start_pos, end_position=end_pos).save(
            self.notification_thumbnail_image_path
        )

        if round(image_width / 4 * 3) <= image_height:
            is_thumbnail_need_to_crop = True
        else:
            is_thumbnail_need_to_crop = False

        if is_thumbnail_need_to_crop:
            ignore_pos = int(image_height * 0.25 / 2)
            start_pos = (0, ignore_pos)
            end_pos = (image_width, image_height - ignore_pos)
            thumbnail = ImageUtility.crop_image(image=thumbnail, start_position=start_pos, end_position=end_pos)

        thumbnail_hover = ImageUtility.create_image_with_hover_effect(image=thumbnail, intensity_increase=50)

        corner_radius = int(image_width / 18)
        thumbnail = ImageUtility.create_image_with_rounded_corners(thumbnail, radius=corner_radius)
        thumbnail_hover = ImageUtility.create_image_with_rounded_corners(thumbnail_hover, radius=corner_radius)

        ######################################################################################################################
        self.history_normal_thumbnail_image_path = FileUtility.get_available_file_name(
            thumbnail_for_video_history_object_save_directory + file_name + "-normal-changed.png"
        )
        self.history_hover_thumbnail_image_path = FileUtility.get_available_file_name(
            thumbnail_for_video_history_object_save_directory + file_name + "-hover-changed.png"
        )

        thumbnail.save(self.history_normal_thumbnail_image_path)
        thumbnail_hover.save(self.history_hover_thumbnail_image_path)

        ######################################################################################################################

        thumbnail = ImageUtility.resize_image(image=thumbnail, new_size=thumbnail_size_for_video_object)
        thumbnail_hover = ImageUtility.resize_image(image=thumbnail_hover, new_size=thumbnail_size_for_video_object)

        thumbnail_normal_save_path = FileUtility.get_available_file_name(
            thumbnail_for_video_object_save_directory + file_name + "-normal-changed.png"
        )
        thumbnail_hover_save_path = FileUtility.get_available_file_name(
            thumbnail_for_video_object_save_directory + file_name + "-hover-changed.png"
        )
        thumbnail.save(thumbnail_normal_save_path)
        thumbnail_hover.save(thumbnail_hover_save_path)

        thumbnail_normal = tk.PhotoImage(file=thumbnail_normal_save_path)
        thumbnail_hover = tk.PhotoImage(file=thumbnail_hover_save_path)

        return thumbnail_normal, thumbnail_hover

    @classmethod
    def get_default_thumbnails(self):
        if AddedVideo.default_thumbnails == (None, None):
            thumbnail_size_for_video_object = (
                int(117 * AppearanceSettings.get_scale("decimal")),
                int(66 * AppearanceSettings.get_scale("decimal")),
            )
            thumbnail_for_video_object_save_directory = "temp/thumbnails/"
            file_name = "default-thumbnail"
            thumbnail = Image.open("assets/ui images/default thumbnail.png")
            corner_radius = int(thumbnail.width / 18)
            thumbnail_hover = ImageUtility.create_image_with_hover_effect(thumbnail, intensity_increase=50)
            thumbnail = ImageUtility.create_image_with_rounded_corners(thumbnail, radius=corner_radius)
            thumbnail_hover = ImageUtility.create_image_with_rounded_corners(thumbnail_hover, radius=corner_radius)
            thumbnail = ImageUtility.resize_image(image=thumbnail, new_size=thumbnail_size_for_video_object)
            thumbnail_hover = ImageUtility.resize_image(image=thumbnail_hover, new_size=thumbnail_size_for_video_object)

            thumbnail_normal_save_path = FileUtility.get_available_file_name(
                thumbnail_for_video_object_save_directory + file_name + "-normal-changed.png"
            )
            thumbnail_hover_save_path = FileUtility.get_available_file_name(
                thumbnail_for_video_object_save_directory + file_name + "-hover-changed.png"
            )
            thumbnail.save(thumbnail_normal_save_path)
            thumbnail_hover.save(thumbnail_hover_save_path)

            thumbnail_normal = tk.PhotoImage(file=thumbnail_normal_save_path)
            thumbnail_hover = tk.PhotoImage(file=thumbnail_hover_save_path)

            AddedVideo.default_thumbnails = (thumbnail_normal, thumbnail_hover)

        return AddedVideo.default_thumbnails

    def retrieve_video_data(self):
        self.pytube_client_index += 1
        try:
            self.video = pytube.YouTube(self.video_url)
            self.video_title = str(self.video.title)
            self.channel = str(self.video.author)
            self.length = int(self.video.length)
            self.video_stream_data = self.video.streams
            self.channel_url = str(self.video.channel_url)
            if GeneralSettings.settings["load_thumbnail"]:
                self.thumbnails = self.get_video_thumbnails()
            else:
                self.thumbnails = self.get_default_thumbnails()
            self.support_download_types = DownloadInfoUtility.sort_download_qualities(
                DownloadInfoUtility.get_supported_download_types(self.video_stream_data)
            )
            self.set_video_data()
            self.set_loading_completed()
            self.download_automatically()

        # except pytube.exceptions.BotDetection as error:
        #     print(f"added_video.py L-231 : {error}")
        #    self.load_video()
        except pytube.exceptions.AgeRestrictedError:
            self.pytube_client_index = -1
            self.set_loading_failed()

        except pytube.exceptions.RegexMatchError:
            self.pytube_client_index = -1
            self.set_loading_failed()

        except Exception as error:
            _log.error("retrieve_video_data failed: %s", error)
            if self.pytube_client_index + 1 < len(AddedVideo.PYTUBE_CLIENTS):
                self.retrieve_video_data()
            else:
                self.pytube_client_index = -1
                self.set_loading_failed()

    def download_video(self):
        self.root.fade_effect()
        self.video_download_button_click_callback(self)

    def configure_download_resolution(self, selected_quality: str):
        self.download_quality = selected_quality.replace(" ", "").split("|")[0]
        if "kbps" in self.download_quality:
            self.download_type = "Audio"
        elif "p" in self.download_quality:
            self.download_type = "Video"

        selected_download_index = self.resolution_select_menu.cget("values").index(selected_quality)
        self.selected_download_type_info = self.support_download_types[selected_download_index]
        # print("selected_download_type_info", self.selected_download_type_info)

    def set_waiting(self):
        self.thumbnail_btn.run_loading_animation()
        self.status_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.load_state = "waiting"
        if self.mode == "playlist":
            self.video_load_status_callback(self, self.load_state)
        self.status_label.configure(text=LanguageManager.data["waiting"])

    def is_available_resolution(self, resolution: str):
        for available_resolution in [
            res.split(" | ")[0].replace(" ", "") for res in self.resolution_select_menu.cget("values")
        ]:
            if available_resolution == resolution:
                return True
        return False

    def select_download_resolution(self, selected_quality: str):
        if "Audio Only" in selected_quality:
            index = -1
        elif self.is_available_resolution(selected_quality):
            index = [res.split(" | ")[0].replace(" ", "") for res in self.resolution_select_menu.cget("values")].index(
                selected_quality
            )
        else:
            available_resolutions_int = [
                int(reso.split(" | ")[0].replace(" ", "")[0:-1])
                for reso in self.resolution_select_menu.cget("values")
                if "kbps" not in reso
            ]

            selected_quality_int = int(selected_quality.split(" | ")[0][0:-1])
            for index, available_resolution_int in enumerate(available_resolutions_int):
                if available_resolution_int <= selected_quality_int:
                    break

        self.resolution_select_menu.set(self.resolution_select_menu.cget("values")[index])

    def select_download_quality_automatic(self):
        self.select_download_resolution(GeneralSettings.settings["automatic_download"]["quality"])

    def download_automatically(self):
        if GeneralSettings.settings["automatic_download"]["status"] == "enable":
            self.select_download_quality_automatic()
            self.configure_download_resolution(self.resolution_select_menu.get())
            if self.mode == "video":
                self.video_download_button_click_callback(self)

    def set_loading_completed(self):
        if self.load_state != "removed":
            self.load_state = "loaded"
            if self.mode == "playlist":
                self.video_load_status_callback(self, self.load_state)
            self.status_label.configure(text=LanguageManager.data["loaded"])
            LoadManager.unregister_from_active(self)

    def set_loading_failed(self):
        if self.load_state == "removed":
            return

        self.load_state = "failed"
        if self.mode == "playlist":
            self.video_load_status_callback(self, self.load_state)

        if GeneralSettings.settings["reload_automatically"] and self.automatically_reload_count < 5:
            time.sleep(1)
            self.automatically_reload_count += 1
            self.load_video()
        else:
            self.status_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_warning"), text=LanguageManager.data["failed"]
            )
            LoadManager.unregister_from_active(self)
            self.thumbnail_btn.show_failure_indicator(text_color=ThemeManager.get_color_based_on_theme("text_warning"))
            self.reload_btn.place(relx=1, rely=0.5, anchor="w", x=-80 * AppearanceSettings.get_scale("decimal"))

    def set_video_data(self):
        if self.load_state != "removed":
            super().set_video_data()

            self.resolution_select_menu.configure(
                values=DownloadInfoUtility.generate_download_options(self.support_download_types)
            )
            self.resolution_select_menu.set(self.resolution_select_menu.cget("values")[0])
            self.configure_download_resolution(self.resolution_select_menu.get())
            self.resolution_select_menu.configure(command=self.configure_download_resolution)
            self.channel_btn.configure(state="normal")
            self.download_btn.configure(state="normal")

    # create widgets
    def create_widgets(self):
        super().create_widgets()

        self.sub_frame = ctk.CTkFrame(master=self)
        self.resolution_select_menu = ctk.CTkComboBox(
            master=self.sub_frame,
            values=["..........", "..........", ".........."],
            width=150 * AppearanceSettings.get_scale("decimal"),
            height=28 * AppearanceSettings.get_scale("decimal"),
        )
        self.download_btn = ctk.CTkButton(
            master=self.sub_frame,
            state="disabled",
            # hover=False,
            command=self.download_video,
        )
        self.status_label = ctk.CTkLabel(master=self.sub_frame, text="")
        self.reload_btn = ctk.CTkButton(master=self, text="⟳", command=self.reload_video, hover=False)

    def set_widgets_texts(self):
        super().set_widgets_texts()

        self.download_btn.configure(text=LanguageManager.data["download"])
        self.status_label.configure(text=LanguageManager.data[self.load_state])

    def set_widgets_fonts(self):
        super().set_widgets_fonts()

        scale = AppearanceSettings.get_scale("decimal")

        self.resolution_select_menu.configure(
            font=("Segoe UI", 13 * scale, "normal"), dropdown_font=("Segoe UI", 13 * scale, "normal")
        )
        self.download_btn.configure(font=("Segoe UI", 12 * scale, "bold"))
        self.status_label.configure(font=("Segoe UI", 12 * scale, "bold"))
        self.reload_btn.configure(font=("Segoe UI", 20 * scale, "normal"))

    def set_widgets_sizes(self):
        super().set_widgets_sizes()

        scale = AppearanceSettings.get_scale("decimal")

        self.sub_frame.configure(height=self.height - 3, width=270 * scale)
        self.download_btn.configure(width=80 * scale, height=25 * scale)
        self.resolution_select_menu.configure(width=150 * scale, height=28 * scale)
        self.status_label.configure(height=15 * scale, width=80 * scale)
        self.reload_btn.configure(width=15 * scale, height=15 * scale)

    # configure widgets colors
    def set_widgets_accent_color(self):
        super().set_widgets_accent_color()

        self.download_btn.configure(
            fg_color=ThemeManager.get_accent_color("normal"), hover_color=ThemeManager.get_accent_color("hover")
        )
        self.reload_btn.configure(text_color=ThemeManager.get_accent_color("normal"))
        self.resolution_select_menu.configure(dropdown_hover_color=ThemeManager.get_accent_color("hover"))

    def set_widgets_colors(self):
        super().set_widgets_colors()

        self.reload_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"))
        self.download_btn.configure(
            text_color=ThemeManager.get_color_based_on_theme("background"),
        )
        self.sub_frame.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"))
        self.status_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.resolution_select_menu.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            border_color=ThemeManager.get_color_based_on_theme("border"),
            dropdown_fg_color=ThemeManager.get_color_based_on_theme("primary"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            dropdown_text_color=ThemeManager.get_color_based_on_theme("text_muted"),
        )

    def on_mouse_enter_self(self, event):
        # super().on_mouse_enter_self(event)
        """
        self.sub_frame.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["hover"])
        self.reload_btn.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["hover"])
        """

    def on_mouse_leave_self(self, event):
        # super().on_mouse_leave_self(event)
        """
        self.sub_frame.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["normal"])
        self.reload_btn.configure(fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["normal"])
        """

    def bind_widgets_events(self):
        super().bind_widgets_events()

        """
        def on_mouse_enter_download_btn(_event):
            # self.on_mouse_enter_self(event)
            if self.download_btn.cget("state") == "normal":
                self.download_btn.configure(
                    fg_color=ThemeManager.get_accent_color("hover"),
                )

        def on_mouse_leave_download_btn(_event):
            # self.on_mouse_leave_self(event)
            if self.download_btn.cget("state") == "normal":
                self.download_btn.configure(
                    fg_color=ThemeManager.get_accent_color("normal"),
                )

        self.download_btn.bind("<Enter>", on_mouse_enter_download_btn)
        self.download_btn.bind("<Leave>", on_mouse_leave_download_btn)
        """

        # ----------------------------------------------------------------

        def on_mouse_enter_resolution_select_menu(event_):
            self.resolution_select_menu.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
                button_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            )

        def on_mouse_leave_resolution_select_menu(event_):
            self.resolution_select_menu.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
                button_color=ThemeManager.get_color_based_on_theme("secondary"),
            )

        self.resolution_select_menu.bind("<Enter>", on_mouse_enter_resolution_select_menu)
        self.resolution_select_menu.bind("<Leave>", on_mouse_leave_resolution_select_menu)

        def on_mouse_enter_reload_btn(_event):
            # self.on_mouse_enter_self(event)
            self.reload_btn.configure(text_color=ThemeManager.get_accent_color("hover"))

        def on_mouse_leave_reload_btn(_event):
            # self.on_mouse_leave_self(event)
            self.reload_btn.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))

        self.reload_btn.bind("<Enter>", on_mouse_enter_reload_btn)
        self.reload_btn.bind("<Leave>", on_mouse_leave_reload_btn)

    # place widgets
    def place_widgets(self):
        super().place_widgets()

        scale = AppearanceSettings.get_scale("decimal")

        self.sub_frame.place(y=1, relx=1, x=-370 * scale)

        self.resolution_select_menu.place(rely=0.5, anchor="w")
        self.download_btn.place(x=190 * scale, rely=0.3, anchor="w")
        self.status_label.place(x=190 * scale, rely=0.75, anchor="w")

    def configure_widget_sizes(self, _event):
        scale = AppearanceSettings.get_scale("decimal")
        self.info_frame.configure(
            width=(
                self.master_frame.winfo_width()
                - (370 * scale)
                - (self.thumbnail_btn.winfo_width() + 5)
                - (10 * scale)
                - (20 * scale)
            )
        )

    def __del__(self):
        """Clear the Memory."""
        del self.video_stream_data
        del self.support_download_types
        # download info
        del self.download_quality
        del self.download_type
        # callback utils
        del self.video_download_button_click_callback
        del self.video_load_status_callback
        # state
        del self.load_state
        # widgets
        del self.sub_frame
        del self.resolution_select_menu
        del self.download_btn
        del self.status_label
        del self.reload_btn
        # video object
        del self.video

        del self.mode
        # Track automatically reload count
        del self.automatically_reload_count

        super().__del__()

    def destroy_widgets(self):
        """Destroy the child widgets."""
        self.sub_frame.destroy()
        self.resolution_select_menu.destroy()
        self.download_btn.destroy()
        self.status_label.destroy()
        self.reload_btn.destroy()

        super().destroy_widgets()

    def kill(self):
        self.load_state = "removed"
        LoadManager.unregister_from_active(self)
        LoadManager.unregister_from_queued(self)
        VideoCountTracker.remove_added_video()
        if self.mode == "playlist":
            self.video_load_status_callback(self, self.load_state)

        super().kill()
