import os
import customtkinter as ctk
import tkinter as tk
import threading
import time
import sys
import webbrowser
import ctkchart
from typing import Literal
import pyautogui
from widgets import (
    AddedVideo, 
    DownloadingVideo, 
    DownloadedVideo,
    AddedPlayList, 
    DownloadingPlayList, 
    DownloadedPlayList,
    SettingPanel, 
    TrayMenu, 
    AlertWindow,
    HistoryPanel
)
from widgets.core_widgets.context_menu import ContextMenu
from services import (
    ThemeManager,
    DownloadManager, 
    LoadManager, 
    VideoConvertManager,
    LanguageManager,
    HistoryManager,
    LoadingIndicateManager,
    VideoCountTracker,
    DownloadSpeedTracker,
    InformationManager
)
from settings import (
    AppearanceSettings,
    GeneralSettings,
)
from utils import (
    FileUtility,
    DataRetrieveUtility,
    ValueConvertUtility
)


class App(ctk.CTk):
    """
    Initialize the application.

    This method sets up the initial state of the application by initializing attributes and widgets.

    Attributes:
        root_width (int): The initial width of the application window.
        root_height (int): The initial height of the application window.
        is_geometry_changes_tracker_running (bool): A flag indicating whether the geometry changes tracker is
                                                    running.
        selected_download_mode (str): The selected download mode, either "video" or "playlist".
        is_content_downloading (bool): A flag indicating whether content is currently being downloaded.
        is_content_downloaded (bool): A flag indicating whether content has been downloaded.
        is_content_added (bool): A flag indicating whether content has been added.
        added_video_count (int): The number of added videos.
        downloading_video_count (int): The number of videos currently being downloaded.
        downloaded_video_count (int): The number of videos that have been downloaded.
        # Add more attributes as needed...

    Widgets:
        url_entry (tk.Entry): Entry widget for entering URLs.
        add_url_btn (tk.Button): Button widget for adding URLs.
        # Add more widget descriptions as needed...
    """
    def __init__(self) -> None:
        super().__init__()

        # window width height save on these vars.
        # I will track window width, if it changed,app will call geometry tracker.
        self.root_width = self.winfo_width()
        self.root_height = self.winfo_height()

        # this var used to track status of geometry tracker. it's running or not
        # if it's running already running it's not be start again
        self.is_geometry_changes_tracker_running = False
        
        # Track app accessibility to all directories required
        self.is_accessible_to_required_dirs  = True
        self.is_app_running = True
        
        # download method
        self.selected_download_mode = "video"

        # check if any video added or downloading or downloaded
        self.is_content_downloading = False
        self.is_content_downloaded = False
        self.is_content_added = False

        self.added_video_count = 0
        self.downloading_video_count = 0
        self.downloaded_video_count = 0

        # widgets
        self.url_entry = None
        self.add_url_btn = None

        self.video_radio_btn = None
        self.playlist_radio_btn = None

        self.navigate_added_btn = None
        self.navigate_downloading_btn = None
        self.navigate_downloaded_btn = None
        self.navigate_history_btn = None

        self.added_content_scroll_frame = None
        self.downloading_content_scroll_frame = None
        self.downloaded_content_scroll_frame = None
        self.history_content_frame = None

        self.added_frame_info_label = None
        self.downloading_frame_info_label = None
        self.downloaded_frame_info_label = None

        self.added_frame_info_label_placed = False
        self.downloading_frame_info_label_placed = False
        self.downloaded_frame_info_label_placed = False

        self.videos_status_count_label = None

        self.context_menu = None
        self.settings_panel = None
        self.settings_btn = None

        self.logo_frame = None
        self.logo_label = None

        self.tray_menu = None

        self.is_settings_open = False
        self.is_in_full_screen_mode = False
        self.root_geometry = ""
        self.is_maximized = False
        
        self.net_speed_chart = None
        self.net_speed_line = None
        self.net_speed_label = None
        self.net_speed_temp_label = None
        self.net_speed_switch = None
        self.net_speed_switch_state = None
        
        self.current_max_download_speed_bytes = 0.00001
        self.current_download_speed_bytes = 0.00001

        ThemeManager.register_widget(self)
        
    def set_initializing_status(self, status: str):
        def set_text(text: str):
            self.initializing_state_label.configure(text = text)
        self.after(1, set_text, LanguageManager.data[status])
        
    def destroy_initializing_status_window(self):
        self.initializing_frame.place_forget()
        
    def create_initializing_status_window(self):
         # Disable window resizalbe 
        self.resizable(False, False)
        
        # Configure Some coliors for window
        self.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))
        scale = AppearanceSettings.get_scale("decimal")
        
        # Create loading screen widgets
        self.initializing_frame = ctk.CTkFrame(
            master=self,
            fg_color=ThemeManager.get_color_based_on_theme("background")
        )
        
        self.logo_name_version_frame = ctk.CTkFrame(
            master=self.initializing_frame,
            fg_color=ThemeManager.get_color_based_on_theme("background")
        )
        
        self.logo_label = ctk.CTkLabel(
            master=self.logo_name_version_frame,
            text=InformationManager.info["logo"],
            text_color=ThemeManager.get_accent_color("normal"),
            font=("Segoe UI", 30 * scale, "bold")
        )

        self.name_label = ctk.CTkLabel(
            master=self.logo_name_version_frame,
            text=InformationManager.info["name"],
            text_color=ThemeManager.get_accent_color("normal"),
            font=("Segoe UI", 24 * scale, "bold")
        )

        self.version_label = ctk.CTkButton(
            master=self.logo_name_version_frame,
            hover=False,
            text=f"v{InformationManager.info["version"]}",
            font=("Segoe UI", 10 * scale, "bold"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            border_color=ThemeManager.get_color_based_on_theme("border")
        )
        self.version_label.configure(
            width=1 * scale, 
            height=1 * scale
        )

        self.logo_label.grid(row=0, column=0, sticky="e")
        self.name_label.grid(row=0, column=1, sticky="e")
        self.version_label.grid(row=0, column=2, sticky="sw", padx=(8 * scale, 0))

        self.initializing_state_label = ctk.CTkLabel(
            master=self.initializing_frame,
            text="State : Initializing",
            font=("Segoe UI", 15 * scale, "bold"),
            text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )

        self.logo_name_version_frame.grid(row=1, column=1, sticky="")  # Center the label
        self.initializing_state_label.grid(row=2, column=1, sticky="")  # Center the button below the label

        self.initializing_frame.place(relwidth=1, relheight=1)
        
        self.set_initializing_status("initializing")

         # Center widgets vertically and horizontally
        self.initializing_frame.grid_rowconfigure(0, weight=1)  # Top empty row
        self.initializing_frame.grid_rowconfigure(1, weight=1)  # Center row
        self.initializing_frame.grid_rowconfigure(2, weight=1)  # Bottom empty row
        self.initializing_frame.grid_columnconfigure(0, weight=1)  # Left empty column
        self.initializing_frame.grid_columnconfigure(1, weight=1)  # Center column
        self.initializing_frame.grid_columnconfigure(2, weight=1)  # Right empty column
        
        loading_screen_width = int(400 * scale)
        loading_screen_height = int(150 * scale)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate x and y coordinates for the window
        x = (screen_width // 2) - (loading_screen_width // 2)
        y = (screen_height // 2) - (loading_screen_height // 2)
        
        # Set the geometry for loading screen
        self.geometry(f"{loading_screen_width}x{loading_screen_height}+{x}+{y}")

    def initialize(self) -> None:
        ctk.set_appearance_mode('dark')
        ThemeManager.set_title_bar_style(self)

        # Set the main window attr
        self.create_initializing_status_window()
        ThemeManager.set_title_bar_style(self)

        # set the app title
        self.title("PyTube Downloader")
        # configure alpha
        self.attributes("-alpha", AppearanceSettings.get_opacity("decimal"))
        # set the title icon
        self.iconbitmap("assets\\main icon\\512x512.ico")
        
        ctk.deactivate_automatic_dpi_awareness()
        
        self.set_initializing_status("configuring_theme")
        # set the theme mode, dark or light or system, by getting from data
        # ctk.set_appearance_mode(AppearanceSettings.themes[AppearanceSettings.settings["root"]["theme_mode"]])
        
        self.set_initializing_status("initializing_history")
        HistoryManager.initialize(
            video_history_change_callback=self.manage_history_videos, 
            playlist_history_change_callback=self.manage_history_playlists
        )

        # deactivate the automatic scale
        scale = AppearanceSettings.get_scale("decimal")

        self.set_initializing_status("initializing_services")
        # configure services
        self.set_initializing_status("initializing_load_manager")
        LoadManager.initialize(self.update_active_videos_count_status)
        self.set_initializing_status("initializing_download_manager")
        DownloadManager.initialize(self.update_active_videos_count_status)
        self.set_initializing_status("initializing_video_convert_manager")
        VideoConvertManager.initialize(self.update_active_videos_count_status)
        self.set_initializing_status("initializing_video_count_tracker")
        VideoCountTracker.initialize(self.update_total_videos_count_status)
        self.set_initializing_status("initializing_theme_manager")
        ThemeManager.initialize()
        self.set_initializing_status("initializing_loading_indicate_manager")
        LoadingIndicateManager.initialize()

        self.set_initializing_status("initializing_widgets")
        # Create the main widgets of the application
        self.create_widgets()
        
        self.set_initializing_status("initializing_download_speed_tracker")
        DownloadSpeedTracker.initialize(self.update_download_speed_status)
        
        self.set_initializing_status("configuring_widget_sizes")
        # set widgets sizes
        self.set_widgets_sizes()
        
        self.set_initializing_status("configuring_widget_texts")
        # set texts depend on language
        self.set_widgets_texts()
        
        self.set_initializing_status("configuring_widget_colors")
        # configure colors for main widgets
        self.set_widgets_colors()
        # configure theme color
        self.set_widgets_accent_color()
        
        self.set_initializing_status("configuring_widget_fonts")
        # configure fonts for main widgets
        self.set_widgets_fonts()
        
        self.set_initializing_status("configuring_widget_events")
        # app event bind
        self.bind_widgets_events()
        
        self.set_initializing_status("configuring_keyboard_shortcuts")
        # bind shortcut keys
        self.bind_keyboard_shortcuts()
        
        self.set_initializing_status("configuring_app_previous_state")
        self.configure_app_previous_state()
        # Reconfigure resizable state
        self.after(1, self.resizable, True, True)
        self.set_initializing_status("checking_updates")
        # place main widgets
        self.place_widgets()

        # place the app at the last placed geometry
        self.minsize(int(900 * scale), int(500 * scale))
        self.geometry(GeneralSettings.settings["window_geometry"])
        # set minimum window size to 900x500
        # Window close button configure
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.geometry_changes_tracker()
        self.destroy_initializing_status_window()
        
        self.resizable(True, True)
        # Check app updates       
        self.run_update_check()
        
        ThemeManager.set_title_bar_style(self)

    
    def create_widgets(self) -> None:
        """
        Creates and initializes all the GUI widgets for the application.

        This method sets up various widgets such as entry fields, radio buttons, buttons, scrollable frames, labels,
        and context menus. It also creates the settings panel and logo frame for the application.
        """
        self.url_entry = ctk.CTkEntry(master=self, placeholder_text="Enter Youtube URL", border_width=1)

        self.video_radio_btn = ctk.CTkRadioButton(
            master=self,
            text="Video",
            height=18,
            command=lambda: self.select_download_mode("video")
        )
        self.video_radio_btn.select()

        self.playlist_radio_btn = ctk.CTkRadioButton(
            master=self,
            text="Playlist",
            command=lambda: self.select_download_mode("playlist")
        )

        self.add_url_btn = ctk.CTkButton(
            master=self,
            text="Add +",
            border_width=1,
            command=self.add_video_playlist,
            hover=False,
        )

        self.added_content_scroll_frame = ctk.CTkScrollableFrame(master=self)
        self.downloading_content_scroll_frame = ctk.CTkScrollableFrame(master=self)
        self.downloaded_content_scroll_frame = ctk.CTkScrollableFrame(master=self)
        self.history_content_frame = HistoryPanel(
            master=self, 
            video_add_to_download_callback=self.add_video, 
            playlist_add_to_download_callback=self.add_playlist
        )

        self.navigate_added_btn = ctk.CTkButton(
            master=self,
            border_width=1,
            hover=False,
            command=lambda: self.place_nav_frame(self.added_content_scroll_frame, "added")
        )

        self.navigate_downloading_btn = ctk.CTkButton(
            master=self,
            hover=False,
            border_width=1,
            command=lambda: self.place_nav_frame(self.downloading_content_scroll_frame, "downloading")
        )

        self.navigate_downloaded_btn = ctk.CTkButton(
            master=self,
            border_width=1,
            command=lambda: self.place_nav_frame(self.downloaded_content_scroll_frame, "downloaded")
        )
        
        self.navigate_history_btn = ctk.CTkButton(
            master=self,
            hover=False,
            border_width=1,
            command=lambda: self.place_nav_frame(self.history_content_frame, "history")
        )

        self.added_frame_info_label = ctk.CTkLabel(
            master=self,
        )

        self.downloading_frame_info_label = ctk.CTkLabel(
            master=self,
        )

        self.downloaded_frame_info_label = ctk.CTkLabel(
            master=self,
        )

        self.videos_status_count_label = ctk.CTkLabel(
            master=self,
            anchor="w"
        )
        
        self.bottom_hr = ctk.CTkFrame(
            master=self
        )
        self.net_speed_chart = ctkchart.CTkLineChart(
            master=self, 
            y_axis_values=(0, 100), 
            x_axis_values=tuple([sec for sec in range(1, 61)]),
            x_axis_data="S",
            y_axis_data="MB/s",
            x_axis_label_count=1,
            y_axis_label_count=0,
            x_axis_section_count=0,
            y_axis_section_count=0,
        )

        self.net_speed_line = ctkchart.CTkLine(
            master=self.net_speed_chart,
            fill="enabled",
        )
        
        self.net_speed_label = ctk.CTkLabel(
            master=self,
            text="Download Speed : 0 KB/s"
        )
        
        self.net_speed_temp_label = ctk.CTkLabel(
            master=self,
            text="Download Speed : 0 KB/s"
        )
        self.net_speed_switch_state = ctk.BooleanVar(value=None)
        self.net_speed_switch = ctk.CTkSwitch(
            master=self,
            text="More",
            command=self.toggle_net_speed_switch,
            onvalue=True,
            offvalue=False,
            variable=self.net_speed_switch_state
        )
        
        self.confgiure_chart_y_axis_values()

        self.settings_panel = SettingPanel(
            master=self,
            theme_settings_change_callback=self.update_appearance_settings,
            general_settings_change_callback=self.update_general_settings,
            restart_callback=self.restart
        )

        self.settings_btn = ctk.CTkButton(
            master=self,
            text="⚡",
            border_spacing=0,
            hover=False,
            command=self.open_settings
        )

        self.context_menu = ContextMenu(
            master=self,
            options_texts=["select_all", "cut", "copy", "paste"],
            options_commands=[self.select_all_url, self.cut_url, self.copy_url, self.paste_url]
        )

        self.logo_frame = ctk.CTkFrame(master=self)
        self.logo_label = ctk.CTkLabel(master=self.logo_frame, text="⚡")

    def select_all_url(self) -> None:
        """
        Selects all text in the URL entry field.
        """
        self.url_entry.focus()
        pyautogui.hotkey("ctrl", "a")
        self.context_menu.place_forget()

    def cut_url(self) -> None:
        """
        Cuts text from the URL entry field.
        """
        self.url_entry.focus()
        pyautogui.hotkey("ctrl", "x")
        self.context_menu.place_forget()

    def copy_url(self) -> None:
        """
        Copies text from the URL entry field.
        """
        self.url_entry.focus()
        pyautogui.hotkey("ctrl", "c")
        self.context_menu.place_forget()

    def paste_url(self) -> None:
        """
        Pastes text into the URL entry field.
        """
        self.url_entry.focus()
        pyautogui.hotkey("ctrl", "v")
        self.context_menu.place_forget()

    def place_forget_nav_frames(self, except_frame: Literal["added", "downloading", "downloaded", "history"] = None) -> None:
        """
        Hides the navigation frames for added, downloading, downloaded, history content.
        """
        if except_frame != "added":
            self.added_content_scroll_frame.place_forget()
        if except_frame != "downloading":
            self.downloading_content_scroll_frame.place_forget()
        if except_frame != "downloaded":
            self.downloaded_content_scroll_frame.place_forget()
        if except_frame != "history":
            self.history_content_frame.place_forget()
            
    def place_forget_nav_labels(self) -> None:
        """
        Hides the navigation labels for added, downloading, and downloaded content.
        """
        self.added_frame_info_label_placed = False
        self.downloading_frame_info_label_placed = False
        self.downloaded_frame_info_label_placed = False
        self.added_frame_info_label.place_forget()
        self.downloading_frame_info_label.place_forget()
        self.downloaded_frame_info_label.place_forget()

    def place_nav_label(self, frame_name: str) -> None:
        """
        Places the navigation label for the specified frame in the center of the main window.

        Args:
            frame_name (str): The name of the frame ('added', 'downloading', or 'downloaded').
        """
        self.place_forget_nav_labels()
        if frame_name == "added" and self.is_content_added is not True:
            self.added_frame_info_label_placed = True
            self.added_frame_info_label.place(y=self.winfo_height() / 2 + 45, x=self.winfo_width() / 2, anchor="center")
        elif frame_name == "downloading" and self.is_content_downloading is not True:
            self.downloading_frame_info_label_placed = True
            self.downloading_frame_info_label.place(
                y=self.winfo_height() / 2 + 45,
                x=self.winfo_width() / 2,
                anchor="center"
            )
        elif frame_name == "downloaded" and self.is_content_downloaded is not True:
            self.downloaded_frame_info_label_placed = True
            self.downloaded_frame_info_label.place(
                y=self.winfo_height() / 2 + 45,
                x=self.winfo_width() / 2,
                anchor="center"
            )

    def place_nav_frame(self, frame: ctk.CTkScrollableFrame, frame_name: str) -> None:
        """
        Places the specified scrollable frame in the main window and updates the navigation label.

        Args:
            frame (ctk.CTkScrollableFrame): The scrollable frame to be placed.
            frame_name (str): The name of the frame ('added', 'downloading', or 'downloaded').
        """
        self.place_forget_nav_frames(except_frame=frame_name)
        frame.place(y=90 * AppearanceSettings.get_scale("decimal"), x=10)
        self.place_nav_label(frame_name)
        
    def configure_navigation_panels(self):
        scale = AppearanceSettings.get_scale("decimal")
        
        root_height = self.winfo_height()
        root_width = self.winfo_width()
        
        frame_height = root_height - (120 + 25) * scale
   
        if GeneralSettings.settings["display_download_speed_info"]:
            frame_height -= 90 * scale
        frame_width = root_width - 40
        self.added_content_scroll_frame.configure(height=frame_height, width=frame_width)
        self.downloading_content_scroll_frame.configure(height=frame_height, width=frame_width)
        self.downloaded_content_scroll_frame.configure(height=frame_height, width=frame_width)
        self.history_content_frame.configure_widgets_size(height=frame_height, width=frame_width + 22)
    
    def show_net_speed_info(self):
        scale = AppearanceSettings.get_scale("decimal")
        
        self.net_speed_temp_label.place_forget()
        self.bottom_hr.place(rely=1, y=-120 * scale - (5 + 8 * scale))
        self.net_speed_chart.place(x=10 + 300 * scale, rely=1, y=-120 * scale - 5)
        self.net_speed_label.place(x=10, rely=1, y=-50 * scale)
        
        self.configure_navigation_panels()
        
    def hide_net_speed_info(self):
        scale = AppearanceSettings.get_scale("decimal")
        
        self.bottom_hr.place_forget()
        self.net_speed_chart.place_forget()
        self.net_speed_label.place_forget()
        self.net_speed_temp_label.place(relx=1, rely=1, anchor="se", y=-5, x=-150*scale)
        self.configure_navigation_panels()
        
    def toggle_net_speed_switch(self):
        GeneralSettings.settings["display_download_speed_info"] = self.net_speed_switch.get()
        if self.net_speed_switch.get():
            self.show_net_speed_info()
        else:
            self.hide_net_speed_info()
        self.update_general_settings()

    def place_widgets(self) -> None:
        """
        Places all the GUI widgets in their respective positions within the main window.

        This method sets the position of various widgets such as buttons, entry fields, radio buttons, labels,
        and scrollable frames within the main window based on a predetermined layout.
        """
        scale = AppearanceSettings.get_scale("decimal")
        self.settings_btn.place(x=-5, y=4)
        self.url_entry.place(x=43 * scale, y=4)
        self.add_url_btn.place(y=4)
        self.video_radio_btn.place(y=5)
        self.playlist_radio_btn.place(y=25 * scale)
        self.navigate_added_btn.place(y=50 * scale, x=10)
        self.navigate_downloading_btn.place(y=50 * scale)
        self.navigate_downloaded_btn.place(y=50 * scale)
        self.navigate_history_btn.place(y=50 * scale)
        self.place_nav_frame(self.added_content_scroll_frame, "added")
        self.videos_status_count_label.place(x=10, rely=1, y=-20 * scale)
        self.logo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.net_speed_switch.place(relx=1, rely=1, anchor="se", y=-2, x=-5)

    def set_widgets_fonts(self) -> None:
        """
        Sets the fonts for various GUI widgets.

        This method configures the font settings for different GUI widgets such as entry fields, buttons, labels, etc.,
        based on a predetermined font style and size.
        """
        scale = AppearanceSettings.get_scale("decimal")

        self.url_entry.configure(
            font=ctk.CTkFont(
                family="Segoe UI",
                size=int(16 * scale),
                weight="normal",
                slant="italic",
                underline=True
            )
        )

        self.video_radio_btn.configure(font=("Segoe UI", 12 * scale, "bold"))
        self.playlist_radio_btn.configure(font=("Segoe UI", 12 * scale, "bold"))
        self.add_url_btn.configure(font=("Segoe UI", 15 * scale, "bold"))

        font_style_1 = ctk.CTkFont(
            family="Segoe UI",
            size=int(16 * scale),
            weight="bold",
            slant="italic"
        )
        self.added_frame_info_label.configure(font=font_style_1)
        self.downloading_frame_info_label.configure(font=font_style_1)
        self.downloaded_frame_info_label.configure(font=font_style_1)

        font_style_2 = ("Segoe UI", 15 * scale, "bold")
        self.navigate_added_btn.configure(font=font_style_2)
        self.navigate_downloading_btn.configure(font=font_style_2)
        self.navigate_downloaded_btn.configure(font=font_style_2)
        self.navigate_history_btn.configure(font=font_style_2)
        self.settings_btn.configure(font=("Segoe UI", 25 * scale, "normal"))
        self.context_menu.configure(font=("Segoe UI", 13 * scale, "bold"))
        self.videos_status_count_label.configure(font=("Segoe UI", 11 * scale, "normal"))
        self.logo_label.configure(font=("Segoe UI", 50 * scale, "normal"))
        
        self.net_speed_switch.configure(
            font=("Segoe UI", 11 * scale, "bold")
        )
        self.net_speed_chart.configure(
            axis_font_style=("Segoe UI", int(10 * scale), "normal"),
            data_font_style=("Segoe UI", int(10 * scale), "bold")
        )
        self.net_speed_label.configure(font=("Segoe UI", 15 * scale, "bold"))
        self.net_speed_temp_label.configure(font=("Segoe UI", 11 * scale, "normal"))
        
    def set_widgets_sizes(self) -> None:
        """
        Sets the sizes for various GUI widgets.

        This method configures the size settings for different GUI widgets such as entry fields, buttons,
        radio buttons, etc.,based on a predetermined scale value.
        """
        scale = AppearanceSettings.get_scale("decimal")
        self.url_entry.configure(height=int(40 * scale))
        self.video_radio_btn.configure(
            radiobutton_width=int(16 * scale),
            radiobutton_height=int(16 * scale),
            width=int(60 * scale),
            height=int(18 * scale)
        )
        self.playlist_radio_btn.configure(
            radiobutton_width=int(16 * scale),
            radiobutton_height=int(16 * scale),
            width=int(60 * scale),
            height=int(18 * scale)
        )
        self.add_url_btn.configure(height=int(40 * scale), width=int(100 * scale))
        self.navigate_added_btn.configure(height=int(40 * scale))
        self.navigate_downloading_btn.configure(height=int(40 * scale))
        self.navigate_downloaded_btn.configure(height=int(40 * scale))
        self.navigate_history_btn.configure(height=int(40 * scale))
        self.settings_btn.configure(width=int(30 * scale), height=int(40 * scale))
        self.context_menu.configure(
            width=int(120 * AppearanceSettings.get_scale("decimal")),
            height=int(130 * AppearanceSettings.get_scale("decimal"))
        )
        self.videos_status_count_label.configure(height=int(15 * scale), width=int(300 * scale))
        
        self.net_speed_switch.configure(
            width=50 * scale,
            height=20 * scale,
            switch_width=32 * scale,
            switch_height=16 * scale,
        )
        
        self.net_speed_chart.configure(
            axis_size=int(2*scale),
            height=int(120 * scale)
        )
        self.net_speed_line.configure(
            size=int(1 * scale)
        )
        self.bottom_hr.configure(height=int(2 * scale))
        self.net_speed_label.configure(height=int(20 * scale))
        self.net_speed_temp_label.configure(height=int(15 * scale), width=int(50 * scale))

    def configure_widgets_size(self) -> None:
        """
        Configures the size and placement of various GUI widgets based on the current size of the main window.

        This method adjusts the size and placement settings for different GUI widgets such as entry fields, buttons,
        scrollable frames, etc., based on the current size of the main window. It ensures that the widgets are
        appropriately sized and positioned to maintain a visually pleasing layout.
        """
        scale = AppearanceSettings.get_scale("decimal")
        root_width = self.winfo_width()
        self.url_entry.configure(width=root_width - 250 * scale)
        
        history_button_width = int(100*scale)
        button_margin = int(3 * scale)
        
        nav_button_width = int((root_width - 20 - button_margin * 4 - history_button_width) / 3)
        self.navigate_added_btn.configure(width=nav_button_width)
        self.navigate_downloading_btn.configure(width=nav_button_width)
        self.navigate_downloaded_btn.configure(width=nav_button_width)
        self.navigate_history_btn.configure(width=history_button_width)

        self.navigate_downloading_btn.place(x=nav_button_width + 10 + button_margin)
        self.navigate_downloaded_btn.place(x=nav_button_width * 2 + 10 + button_margin * 2)
        self.navigate_history_btn.place(x=nav_button_width * 3 + 10 + button_margin * 3)

        self.video_radio_btn.place(x=root_width - 202 * scale)
        self.playlist_radio_btn.place(x=root_width - 202 * scale)
        self.add_url_btn.place(x=root_width - 110 * scale)

        if self.added_frame_info_label_placed:
            self.place_nav_label("added")
        elif self.downloading_frame_info_label_placed:
            self.place_nav_label("downloading")
        elif self.downloaded_frame_info_label_placed:
            self.place_nav_label("downloaded")
                
        self.bottom_hr.configure(width=root_width)
        chart_width = int(self.winfo_width() - (10 + 300 * scale + 10 + 100 * scale))
        self.net_speed_chart.configure(width=chart_width)
        self.confgiure_chart_x_axis_values()
        self.configure_navigation_panels()

    def set_widgets_texts(self):
        self.url_entry.configure(
            placeholder_text=LanguageManager.data["enter_youtube_url"]
        )
        self.video_radio_btn.configure(text=LanguageManager.data["video"])
        self.playlist_radio_btn.configure(text=LanguageManager.data["playlist"])
        
        self.add_url_btn.configure(text=LanguageManager.data["add +"])
        
        self.navigate_added_btn.configure(text=f"{LanguageManager.data["added"]} ({VideoCountTracker.total_added_video_count})")
        self.navigate_downloading_btn.configure(text=f"{LanguageManager.data["downloading"]} ({VideoCountTracker.total_downloading_video_count})")
        self.navigate_downloaded_btn.configure(text=f"{LanguageManager.data["downloaded"]} ({VideoCountTracker.total_downloaded_video_count})")
        self.navigate_history_btn.configure(text=LanguageManager.data["history"])
        
        self.added_frame_info_label.configure(
            text=LanguageManager.data["added_videos_&_playlists_will_be_display_here"]
        )
        self.downloading_frame_info_label.configure(
            text=LanguageManager.data["downloading_videos_&_playlists_will_be_display_here"]
        )
        self.downloaded_frame_info_label.configure(
            text=LanguageManager.data["downloaded_videos_&_playlists_will_be_display_here"]
        )
        self.videos_status_count_label.configure(
            text=f"{LanguageManager.data['loading']} : {LoadManager.queued_load_count + LoadManager.active_load_count}"
                 f" | "
                 f"{LanguageManager.data['downloading']} : {DownloadManager.queued_download_count + 
                                                            DownloadManager.active_download_count}"
                 f" | "
                 f" {LanguageManager.data['converting']} : {VideoConvertManager.active_convert_count + 
                                                            VideoConvertManager.queued_convert_count}"
        )
        self.net_speed_label.configure(
            text=f"{LanguageManager.data['download_speed']} : {ValueConvertUtility.convert_size(self.current_download_speed_bytes, decimal_points=3)}/s"
        )
        
        self.net_speed_temp_label.configure(
            text=f"{LanguageManager.data['download_speed']} : {ValueConvertUtility.convert_size(self.current_download_speed_bytes, decimal_points=3)}/s"
        )
        
        self.net_speed_switch.configure(text=LanguageManager.data["more"])
        self.net_speed_chart.configure(
            y_axis_data=f"{LanguageManager.data['peak']} : {ValueConvertUtility.convert_size(self.current_max_download_speed_bytes, decimal_points=2)}/s"
        )
        
    def update_widgets_text(self):
        self.set_widgets_texts()

    def on_select_set_radio_btn_style(self, selected_radion_btn: Literal["playlist", "video"]) -> None:
        """
        Updates the style of radio buttons based on the selected option.

        Args:
            selected_radion_btn (str): The selected radio button option ('playlist' or 'video').
        """

        if selected_radion_btn == "playlist":
            self.playlist_radio_btn.configure(
                fg_color=ThemeManager.get_accent_color("normal")
            )
            self.video_radio_btn.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary")
            )
        elif selected_radion_btn == "video":
            self.video_radio_btn.configure(
                fg_color=ThemeManager.get_accent_color("normal")
            )
            self.playlist_radio_btn.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary")
            )

    def update_widgets_accent_color(self) -> None:
        self.set_widgets_accent_color()

    def set_widgets_accent_color(self) -> None:
        """
        Sets the accent color for various GUI widgets.

        This method configures the accent color for different GUI widgets such as buttons, radio buttons, labels, etc.,
        based on the current accent color setting in the application's appearance settings.
        """
        self.settings_btn.configure(
            text_color=ThemeManager.get_accent_color("normal")
        )
        self.video_radio_btn.configure(
            fg_color=ThemeManager.get_accent_color("normal")
        )
        self.playlist_radio_btn.configure(
            fg_color=ThemeManager.get_accent_color("normal")
        )
        self.add_url_btn.configure(
            fg_color=ThemeManager.get_accent_color("normal"),
            border_color=ThemeManager.get_accent_color("normal")
        )
        self.logo_label.configure(
            text_color=ThemeManager.get_accent_color("normal")
        )
     
        self.net_speed_line.configure(
            color=ThemeManager.get_accent_color("normal")
        )
        
        self.net_speed_switch.configure(
            progress_color=ThemeManager.get_accent_color("normal"),
        )

    def update_widgets_colors(self) -> None:
        self.set_widgets_colors()

    def set_widgets_colors(self) -> None:
        """
        Sets the colors for various GUI widgets.

        This method configures the color settings for different GUI widgets such as buttons, entry fields, radio buttons
        ,labels, etc., based on the current color settings in the application's appearance settings.
        """
        # Main window background color
        self.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))

        # Navigation buttons colors
        self.navigate_added_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"),
                                          bg_color=ThemeManager.get_color_based_on_theme("background"))
        self.navigate_downloading_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"),
                                          bg_color=ThemeManager.get_color_based_on_theme("background"))
        self.navigate_downloaded_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"),
                                          bg_color=ThemeManager.get_color_based_on_theme("background"))
        self.navigate_history_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"),
                                          bg_color=ThemeManager.get_color_based_on_theme("background"))

        # Navigation buttons colors
        self.navigate_added_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"),
                                          border_color=ThemeManager.get_color_based_on_theme("border"),
                                          bg_color=ThemeManager.get_color_based_on_theme("background"),
                                          text_color=ThemeManager.get_color_based_on_theme("text_muted"))
        self.navigate_downloading_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"),
                                          border_color=ThemeManager.get_color_based_on_theme("border"),
                                          bg_color=ThemeManager.get_color_based_on_theme("background"),
                                          text_color=ThemeManager.get_color_based_on_theme("text_muted"))
        self.navigate_downloaded_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"),
                                          border_color=ThemeManager.get_color_based_on_theme("border"),
                                          bg_color=ThemeManager.get_color_based_on_theme("background"),
                                          text_color=ThemeManager.get_color_based_on_theme("text_muted"))
        self.navigate_history_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"),
                                          border_color=ThemeManager.get_color_based_on_theme("border"),
                                          bg_color=ThemeManager.get_color_based_on_theme("background"),
                                          text_color=ThemeManager.get_color_based_on_theme("text_muted"))

        # Settings button colors
        self.settings_btn.configure(fg_color=ThemeManager.get_color_based_on_theme("background"),
                                    bg_color=ThemeManager.get_color_based_on_theme("background"))

        # URL entry colors
        self.url_entry.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            border_color=ThemeManager.get_color_based_on_theme("border"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
        )

        # Radio buttons colors
        self.video_radio_btn.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            text_color=ThemeManager.get_color_based_on_theme("text_muted"),
            border_color=ThemeManager.get_color_based_on_theme("primary"),
        )

        self.playlist_radio_btn.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            text_color=ThemeManager.get_color_based_on_theme("text_muted"),
            border_color=ThemeManager.get_color_based_on_theme("primary"),
        )

        if self.selected_download_mode == "playlist":
            self.playlist_radio_btn.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            )
        elif self.selected_download_mode == "video":
            self.video_radio_btn.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            )
        
        # Add URL button colors
        self.add_url_btn.configure(bg_color=ThemeManager.get_color_based_on_theme("background"),
                                   text_color=ThemeManager.get_color_based_on_theme("background"))

        # Scrollable frames colors
        self.added_content_scroll_frame.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background"),
            bg_color=ThemeManager.get_color_based_on_theme("background"),
        )
        self.downloading_content_scroll_frame.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background"),
            bg_color=ThemeManager.get_color_based_on_theme("background"),
        )
        self.downloaded_content_scroll_frame.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background"),
            bg_color=ThemeManager.get_color_based_on_theme("background"),
        )
        
        # Frame info labels colors
        self.added_frame_info_label.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            text_color=ThemeManager.get_color_based_on_theme("text_muted"),
        )
        self.downloading_frame_info_label.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            text_color=ThemeManager.get_color_based_on_theme("text_muted"),
        )
        self.downloaded_frame_info_label.configure(
            bg_color=ThemeManager.get_color_based_on_theme("background"),
            text_color=ThemeManager.get_color_based_on_theme("text_muted"),
        )
    
        self.videos_status_count_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal")
        )
        self.logo_frame.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background")
        )

        self.net_speed_switch.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            button_hover_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )      
       
        self.net_speed_chart.configure(
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            bg_color=ThemeManager.get_color_based_on_theme("primary"),
            axis_color=ThemeManager.get_color_based_on_theme("secondary"),
            x_axis_data_font_color=ThemeManager.get_color_based_on_theme("text_muted"),
            y_axis_data_font_color=ThemeManager.get_color_based_on_theme("text_muted"),
        )

        self.net_speed_line.configure(
            fill_color=ThemeManager.get_color_based_on_theme("secondary")
        )
        
     
        self.bottom_hr.configure(
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            bg_color=ThemeManager.get_color_based_on_theme("background")
        )
        
        self.net_speed_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal")
        )
        
        self.net_speed_temp_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal")
        )

        
    def bind_widgets_events(self) -> None:
        """
        Binds events to various GUI widgets for handling user interactions.

        This method binds different event handlers to GUI widgets such as entry fields, buttons, radio buttons, labels,
        etc.,for handling user interactions such as mouse clicks, mouse hover, focus changes, etc. It ensures that
        appropriate actions are taken in response to user interactions to maintain the desired functionality and
        user experience.
        """
        self.url_entry.bind("<Button-3>", self.open_context_menu)
        self.url_entry.bind("<Button-2>", self.open_context_menu)
        self.bind("<Button-2>", self.close_context_menu)
        self.bind("<Button-3>", self.close_context_menu)

        self.url_entry.bind("<Button-1>", self.close_context_menu_directly)
        self.bind("<Button-1>", self.close_context_menu_directly)
        self.bind('<FocusOut>', self.close_context_menu_directly)
        self.bind("<Configure>", self.run_geometry_changes_tracker)

        def on_mouse_enter_url_entry(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the URL entry field.

            This function is called when the mouse enters the URL entry field. It changes the appearance settings of
            the URL entry field to reflect the hover state, such as modifying foreground color, border color, and
            text color, based on the current color settings in the application's appearance settings.
            """
            self.url_entry.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
                border_color=ThemeManager.get_accent_color("hover")
            )

        def on_mouse_leave_url_entry(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the URL entry field.

            This function is called when the mouse leaves the URL entry field. It reverts the appearance settings of the
            URL entry field back to the normal state after hover, restoring the original foreground color, border color,
            and text color based on the current  color settings in the application's appearance settings.
            """
            self.url_entry.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
                border_color=ThemeManager.get_color_based_on_theme("border")
            )
        
        self.url_entry.bind("<Enter>", on_mouse_enter_url_entry)
        self.url_entry.bind("<Leave>", on_mouse_leave_url_entry)

        ######################################################################################

        def on_mouse_enter_settings_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the settings button.

            This function is called when the mouse enters the settings button. It adjusts the text color of the settings
            button to reflect the hover state, using the accent color defined in the application's appearance settings.
            """
            self.settings_btn.configure(text_color=ThemeManager.get_accent_color("hover"))

        def on_mouse_leave_settings_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the settings button.

            This function is called when the mouse leaves the settings button. It resets the text color of the settings
            button to its normal state, using the accent color defined in the application's appearance settings.
            """
            self.settings_btn.configure(text_color=ThemeManager.get_accent_color("normal"))

        self.settings_btn.bind("<Enter>", on_mouse_enter_settings_btn)
        self.settings_btn.bind("<Leave>", on_mouse_leave_settings_btn)

        ######################################################################################

        def on_mouse_enter_video_radio_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the video radio button.

            This function is called when the mouse enters the video radio button. It adjusts the text color and
            foreground color of the video radio button to reflect the hover state, using the colors defined in
            the application's appearance settings.
            """
            self.video_radio_btn.configure(
                border_color=ThemeManager.get_accent_color("hover"),
                fg_color=ThemeManager.get_accent_color("hover"),
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            )

        def on_mouse_leave_video_radio_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the video radio button.

            This function is called when the mouse leaves the video radio button. It resets the text color and
            foreground color of the video radio button to their normal states, using the colors defined in the
            application's appearance settings.
            """
            if self.selected_download_mode == "video":
                self.video_radio_btn.configure(
                    border_color=ThemeManager.get_color_based_on_theme("primary"),
                    fg_color=ThemeManager.get_accent_color("normal"),
                    text_color=ThemeManager.get_color_based_on_theme("text_normal"),
                )
            else:
                self.video_radio_btn.configure(
                    border_color=ThemeManager.get_color_based_on_theme("primary"),
                    fg_color=ThemeManager.get_color_based_on_theme("primary"),
                    text_color=ThemeManager.get_color_based_on_theme("text_muted"),
                )

        self.video_radio_btn.bind("<Enter>", on_mouse_enter_video_radio_btn)
        self.video_radio_btn.bind("<Leave>", on_mouse_leave_video_radio_btn)

        ######################################################################################

        def on_mouse_enter_playlist_radio_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the playlist radio button.

            This function is called when the mouse enters the playlist radio button. It adjusts the text color and
            foreground color of the playlist radio button to reflect the hover state, using the colors defined in
            the application's appearance settings.
            """
            self.playlist_radio_btn.configure(
                border_color=ThemeManager.get_accent_color("hover"),
                fg_color=ThemeManager.get_accent_color("hover"),
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            )

        def on_mouse_leave_playlist_radio_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the playlist radio button.

            This function is called when the mouse leaves the playlist radio button. It resets the text color and
            foreground color of the playlist radio button to their normal states, using the colors defined in the
            application's appearance settings.
            """
            if self.selected_download_mode == "playlist":
                self.playlist_radio_btn.configure(
                    border_color=ThemeManager.get_color_based_on_theme("primary"),
                    fg_color=ThemeManager.get_accent_color("normal"),
                    text_color=ThemeManager.get_color_based_on_theme("text_normal"),

                )
            else:
                self.playlist_radio_btn.configure(
                    border_color=ThemeManager.get_color_based_on_theme("primary"),
                    fg_color=ThemeManager.get_color_based_on_theme("primary"),
                    text_color=ThemeManager.get_color_based_on_theme("text_muted"),
                )

        self.playlist_radio_btn.bind("<Enter>", on_mouse_enter_playlist_radio_btn)
        self.playlist_radio_btn.bind("<Leave>", on_mouse_leave_playlist_radio_btn)

        ######################################################################################

        def on_mouse_enter_add_video_playlist_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the add video/playlist button.

            This function is called when the mouse enters the add video/playlist button. It adjusts the border color,
            text color, and foreground color of the button to reflect the hover state, using the colors defined in the
            application's appearance settings.
            """
            self.add_url_btn.configure(
                border_color=ThemeManager.get_accent_color("hover"),
                fg_color=ThemeManager.get_accent_color("hover"),
            )

        def on_mouse_leave_add_video_playlist_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the add video/playlist button.

            This function is called when the mouse leaves the add video/playlist button. It resets the border color,
            text color, and foreground color of the button to their normal states, using the colors defined in
            the application's appearance settings.
            """
            self.add_url_btn.configure(
                border_color=ThemeManager.get_accent_color("normal"),
                fg_color=ThemeManager.get_accent_color("normal"),
            )

        self.add_url_btn.bind("<Enter>", on_mouse_enter_add_video_playlist_btn)
        self.add_url_btn.bind("<Leave>", on_mouse_leave_add_video_playlist_btn)

        ######################################################################################

        def on_mouse_enter_navigate_added_frame_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the navigate added frame button.

            This function is called when the mouse enters the navigate added frame button. It adjusts the text color and
            foreground color of the button to reflect the hover state, using the colors defined in the
            application's appearance settings.
            """
            self.navigate_added_btn.configure(
                border_color=ThemeManager.get_accent_color("hover"),
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
                text_color=ThemeManager.get_accent_color("hover"),
            )
      
        def on_mouse_leave_navigate_added_frame_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the navigate added frame button.

            This function is called when the mouse leaves the navigate added frame button. It resets the text color and
            foreground color of the button to their normal states, using the colors defined in the application's
            appearance settings.
            """
            self.navigate_added_btn.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
                border_color=ThemeManager.get_color_based_on_theme("border"),
                text_color=ThemeManager.get_color_based_on_theme("text_muted")
            )
    
        self.navigate_added_btn.bind("<Enter>", on_mouse_enter_navigate_added_frame_btn)
        self.navigate_added_btn.bind("<Leave>", on_mouse_leave_navigate_added_frame_btn)

        ######################################################################################

        def on_mouse_enter_navigate_downloading_frame_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the navigate downloading frame button.

            This function adjusts the text color and foreground color of the navigate downloading frame button to
            reflect the hover state when the mouse enters the button.The colors are obtained from the application's
            appearance settings for the hover state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.navigate_downloading_btn.configure(
                border_color=ThemeManager.get_accent_color("hover"),
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
                text_color=ThemeManager.get_accent_color("hover"),
            )
      

        def on_mouse_leave_navigate_downloading_frame_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the navigate downloading frame button.

            This function resets the text color and foreground color of the navigate downloading frame button to their
            normal states when the mouse leaves the button.The colors are obtained from the application's appearance
            settings for the normal state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.navigate_downloading_btn.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
                border_color=ThemeManager.get_color_based_on_theme("border"),
                text_color=ThemeManager.get_color_based_on_theme("text_muted")
            )

        self.navigate_downloading_btn.bind("<Enter>", on_mouse_enter_navigate_downloading_frame_btn)
        self.navigate_downloading_btn.bind("<Leave>", on_mouse_leave_navigate_downloading_frame_btn)

        ######################################################################################

        def on_mouse_enter_navigate_downloaded_frame_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the navigate downloaded frame button.

            This function adjusts the text color and foreground color of the navigate downloaded frame button to reflect
            the hover state when the mouse enters the button.The colors are obtained from the application's appearance
            settings for the hover state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.navigate_downloaded_btn.configure(
                border_color=ThemeManager.get_accent_color("hover"),
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
                text_color=ThemeManager.get_accent_color("hover"),
            )
      

        def on_mouse_leave_navigate_downloaded_frame_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the navigate downloaded frame button.

            This function resets the text color and foreground color of the navigate downloaded frame button to their
            normal states when the mouse leaves the button. The colors are obtained from the application's appearance
            settings for the normal state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.navigate_downloaded_btn.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
                border_color=ThemeManager.get_color_based_on_theme("border"),
                text_color=ThemeManager.get_color_based_on_theme("text_muted")
            )

        self.navigate_downloaded_btn.bind("<Enter>", on_mouse_enter_navigate_downloaded_frame_btn)
        self.navigate_downloaded_btn.bind("<Leave>", on_mouse_leave_navigate_downloaded_frame_btn)
        
        ######################################################################################

        def on_mouse_enter_navigate_history_frame_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the navigate history frame button.

            This function adjusts the text color and foreground color of the navigate history frame button to reflect
            the hover state when the mouse enters the button.The colors are obtained from the application's appearance
            settings for the hover state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.navigate_history_btn.configure(
                border_color=ThemeManager.get_accent_color("hover"),
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
                text_color=ThemeManager.get_accent_color("hover"),
            )
      

        def on_mouse_leave_navigate_history_frame_btn(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the navigate history frame button.

            This function resets the text color and foreground color of the navigate history frame button to their
            normal states when the mouse leaves the button. The colors are obtained from the application's appearance
            settings for the normal state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.navigate_history_btn.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
                border_color=ThemeManager.get_color_based_on_theme("border"),
                text_color=ThemeManager.get_color_based_on_theme("text_muted")
            )

        self.navigate_history_btn.bind("<Enter>", on_mouse_enter_navigate_history_frame_btn)
        self.navigate_history_btn.bind("<Leave>", on_mouse_leave_navigate_history_frame_btn)
        
        #######################################################################################

        def on_mouse_enter_added_frame_info_label(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the added frame information label.

            This function adjusts the text color of the added frame information label to reflect the hover state when
            the mouse enters the label. The color is obtained from the application's appearance settings
            for the hover state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.added_frame_info_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal")
            )

        def on_mouse_leave_added_frame_info_label(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the added frame information label.

            This function resets the text color of the added frame information label to its normal state when the mouse
            leaves the label. The color is obtained from the application's appearance settings for the normal state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.added_frame_info_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_muted")
            )

        self.added_frame_info_label.bind("<Enter>", on_mouse_enter_added_frame_info_label)
        self.added_frame_info_label.bind("<Leave>", on_mouse_leave_added_frame_info_label)

        #######################################################################################

        def on_mouse_enter_downloading_frame_info_label(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the downloading frame information label.

            This function adjusts the text color of the downloading frame information label to reflect the hover state
            when the mouse enters the label. The color is obtained from the application's appearance settings
            for the hover state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.downloading_frame_info_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal")
            )

        def on_mouse_leave_downloading_frame_info_label(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the downloading frame information label.

            This function resets the text color of the downloading frame information label to its normal state when the
            mouse leaves the label. The color is obtained from the application's appearance settings for
            the normal state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.downloading_frame_info_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_muted")
            )

        self.downloading_frame_info_label.bind("<Enter>", on_mouse_enter_downloading_frame_info_label)
        self.downloading_frame_info_label.bind("<Leave>", on_mouse_leave_downloading_frame_info_label)

        #######################################################################################
        def on_mouse_enter_downloaded_frame_info_label(_event: tk.Event) -> None:
            """
            Event handler for mouse entering the downloaded frame information label.

            This function adjusts the text color of the downloaded frame information label to reflect the hover state
            when the mouse enters the label. The color is obtained from the application's appearance settings for
            the hover state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.downloaded_frame_info_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal")
            )

        def mouse_ot_downloaded_frame_info_label(_event: tk.Event) -> None:
            """
            Event handler for mouse leaving the downloaded frame information label.

            This function resets the text color of the downloaded frame information label to its normal state when the
            mouse leaves the label. The color is obtained from the application's appearance settings for the
            normal state.

            Parameters:
                _event (tk.Event): The event object.
            """
            self.downloaded_frame_info_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_muted")
            )

        self.downloaded_frame_info_label.bind("<Enter>", on_mouse_enter_downloaded_frame_info_label)
        self.downloaded_frame_info_label.bind("<Leave>", mouse_ot_downloaded_frame_info_label)
    
    def bind_keyboard_shortcuts(self):
        """
        Bind the keyboards shortcuts.
        """
        def toggle_settings(_event):
            if self.is_settings_open:
                self.close_settings()
            else:
                self.open_settings()
        
        def close_settings(_event):
            if self.is_settings_open:
                self.close_settings()
                
        self.bind("<Control-,>", toggle_settings)
        self.bind("<Escape>", close_settings)
        
        def choose_download_mode(_event):
            if self.selected_download_mode == "video":
                self.select_download_mode("playlist")
            else:
                self.select_download_mode("video")
                
        self.bind("<Control-d>", choose_download_mode)
        self.bind("<Control-D>", choose_download_mode)
        self.bind("<F6>", choose_download_mode)
        
        def add_video_playlist(_event):
            self.add_video_playlist()
        self.bind("<Return>", add_video_playlist)
        
        def toggle_full_screen(_event):
            if not self.is_in_full_screen_mode: 
                self.is_in_full_screen_mode = True
                self.attributes("-fullscreen", True)
                self.run_geometry_changes_tracker("_event")
            else:
                self.is_in_full_screen_mode = False
                self.attributes("-fullscreen", False)
                # Had to reset titlebar color because of customtkinter has some issue with when fullscreen toggle
                self._windows_set_titlebar_color(self._get_appearance_mode())
                self.run_geometry_changes_tracker("_event")
    
        self.bind("<F11>", toggle_full_screen)
        self.bind("<Alt-Return>", toggle_full_screen)
        
        def minimize(_event):
            self.iconify()
            
        self.bind("<Control-n>", minimize)
        self.bind("<Control-N>", minimize)
        self.bind("<F9>", minimize)
        self.bind("<Control-Down>", minimize)
        
        def toggle_maximize(_event):
            if not self.is_maximized:
                self.is_maximized = True
                self.root_geometry = self.geometry()
                self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+{0}+{0}")
                self.run_geometry_changes_tracker("_event")
            else:
                self.is_maximized = False
                self.geometry(self.root_geometry)
                self.run_geometry_changes_tracker("_event")
        
        self.bind("<Control-m>", toggle_maximize)
        self.bind("<Control-M>", toggle_maximize)
        self.bind("<F10>", toggle_maximize)
        self.bind("<Control-Up>", toggle_maximize)
        
        def terminate(_event):
            self.on_app_closing()
            
        self.bind("<Control-Alt-q>", terminate)
        self.bind("<Control-Alt-Q>", terminate)
        self.bind("<Control-Alt-F4>", terminate)
        
        def quick_exit(_event):
            self.show_close_confirmation_dialog()
            
        self.bind("<Control-q>", quick_exit)
        self.bind("<Control-Q>", quick_exit)
        
        def minimize_to_tray_icon(_event):
            self.minimize_to_tray()
            
        self.bind("<F12>", minimize_to_tray_icon)
        self.bind("<Control-Shift-m>", minimize_to_tray_icon)
        self.bind("<Control-Shift-M>", minimize_to_tray_icon)
        self.bind("<Control-Shift-n>", minimize_to_tray_icon)
        self.bind("<Control-Shift-N>", minimize_to_tray_icon)
        
    def configure_app_previous_state(self) -> None:
        """Configures the application to its previous state."""
        if GeneralSettings.settings["display_download_speed_info"]:
            self.net_speed_switch_state.set(True)
            self.net_speed_switch.select()
            self.show_net_speed_info()
        else:
            self.net_speed_switch_state.set(False)
            self.net_speed_switch.deselect()
            self.hide_net_speed_info()

    def show_app_logo(self) -> None:
        
        """
        Show the application logo.
        """
        self.logo_frame.place(relwidth=1, relheight=1)

    def hide_app_logo(self) -> None:
        """
        Hide the application logo.
        """
        self.logo_frame.place_forget()

    def update_widgets(self) -> None:
        """
        Update all the widgets in the application.
        """
        for widget in self.winfo_children():
            widget.update()
            try:
                for sub_widget in widget.winfo_children():
                    sub_widget.update()
                    sub_widget.focus_set()
                    try:
                        for sub_sub_widget in sub_widget.winfo_children():
                            sub_sub_widget.update()
                            sub_widget.focus_set()
                            try:
                                for sub_sub_sub_widget in sub_sub_widget.winfo_children():
                                    sub_sub_sub_widget.update()
                                    sub_widget.focus_set()
                            except Exception as error:
                                print(f"app.py L-657 : {error}")
                    except Exception as error:
                        print(f"app.py L-659 : {error}")
            except Exception as error:
                print(f"app.py L-661 : {error}")
        self.update()
        self.focus_set()

    def geometry_changes_tracker(self) -> None:
        """
        Track changes in the geometry of the window and adjust accordingly.
        """
        try:
            self.is_geometry_changes_tracker_running = True
            update_delay = 0.5
            # Check if the old window width or height is different from the current width or height
            if self.root_width != self.winfo_width() or self.root_height != self.winfo_height():
                # If the window size changed, show the logo on full screen
                self.show_app_logo()
                self.root_width = self.winfo_width()
                self.root_height = self.winfo_height()
                time.sleep(update_delay)
                # Wait until the user stops changing the window size
                while self.root_width != self.winfo_width() or self.root_height != self.winfo_height():
                    # Keep updating the old window size to track if the user changed the window size or not
                    self.root_width = self.winfo_width()
                    self.root_height = self.winfo_height()
                    # Set delay to 1 sec
                    time.sleep(update_delay)
                self.configure_widgets_size()
                self.update_idletasks()
                self.update_widgets()
                self.history_content_frame.configure_panel()
                self.hide_app_logo()
            self.is_geometry_changes_tracker_running = False
        except Exception as error:
            print(f"geometry_changes_tracker L-1219 : {error}")

    def run_geometry_changes_tracker(self, _event: tk.Event | str) -> None:
        """
        Run the geometry changes tracker in a separate thread.
        """
        if not self.is_geometry_changes_tracker_running:
            threading.Thread(target=self.geometry_changes_tracker).start()
            # self.after(100, self.geometry_changes_tracker)
            ...
            
    def select_download_mode(self, download_mode: Literal["video", "playlist"]) -> None:
        """
        Select the download mode (either "video" or "playlist").
        """
        self.selected_download_mode = download_mode
        if download_mode == "playlist":
            self.playlist_radio_btn.select()
            self.video_radio_btn.deselect()
            self.video_radio_btn.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))
        else:
            self.video_radio_btn.select()
            self.playlist_radio_btn.deselect()
            self.playlist_radio_btn.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))

    def update_active_videos_count_status(self) -> None:
        """
        Update the status label with the count of active loading and active downloading videos.
        """
        self.videos_status_count_label.configure(
            text=f"{LanguageManager.data['loading']} : {LoadManager.queued_load_count + LoadManager.active_load_count}"
                 f" | "
                 f"{LanguageManager.data['downloading']} : {DownloadManager.queued_download_count + 
                                                            DownloadManager.active_download_count}"
                 f" | "
                 f" {LanguageManager.data['converting']} : {VideoConvertManager.active_convert_count + 
                                                            VideoConvertManager.queued_convert_count}"
        )
    
    def update_total_videos_count_status(self, added_video_count, downloading_video_count, downloaded_video_count) -> None:
        """
        Update the status label with the count of added loading and added downloading and downloaded videos.
        """
        self.navigate_added_btn.configure(text=LanguageManager.data["added"] + f" ({str(added_video_count)})")
        self.navigate_downloading_btn.configure(text=LanguageManager.data["downloading"] + f" ({str(downloading_video_count)})")
        self.navigate_downloaded_btn.configure(text=LanguageManager.data["downloaded"] + f" ({str(downloaded_video_count)})")

    def fade_effect(self) -> None:
        """
        Apply a fade effect to the application.
        """
        fade_out_to = AppearanceSettings.get_opacity("decimal") - 0.15
        
        def fade_out(alpha):
            if alpha > fade_out_to:
                self.attributes("-alpha", alpha)
                self.after(25, fade_out, alpha - 0.025)
            else:
                fade_in(fade_out_to)

        def fade_in(alpha):
            if AppearanceSettings.get_opacity("decimal") >= alpha:
                self.attributes("-alpha", alpha)
                self.after(25, fade_in, alpha + 0.025)
            else:
                self.attributes("-alpha", AppearanceSettings.get_opacity("decimal"))
            
        fade_out(AppearanceSettings.get_opacity("decimal"))
        
    def scroll_frame_to_bottom(self, frame: ctk.CTkScrollableFrame):
        """
        Scroll the frame to the bottom.
        """
        frame.after(10, frame._parent_canvas.yview_moveto, 1.0)
    
    
    def add_video(self, url: str = None)-> None:
        if url is None:
            yt_url = self.url_entry.get()
        else:
            yt_url = url
            self.fade_effect()

        self.added_frame_info_label.place_forget()
        self.is_content_added = True
        
        AddedVideo(
            root=self,
            master=self.added_content_scroll_frame,
            height=int(70 * AppearanceSettings.get_scale("decimal")),
            width=self.added_content_scroll_frame.winfo_width(),
            # video url
            video_url=yt_url,
            # download btn callback
            video_download_button_click_callback=self.download_video,
        ).pack(fill="x", pady=2)
        
    def add_playlist(self, url: str = None) -> None:
        if url is None:
            yt_url = self.url_entry.get()
        else:
            yt_url = url
            self.fade_effect()
        
        self.added_frame_info_label.place_forget()
        self.is_content_added = True
        
        AddedPlayList(
            root=self,
            master=self.added_content_scroll_frame,
            height=int(86 * AppearanceSettings.get_scale("decimal")),
            width=self.added_content_scroll_frame.winfo_width(),

            playlist_download_button_click_callback=self.download_playlist,
            video_download_button_click_callback=self.download_video,
            playlist_url=yt_url
        ).pack(fill="x", pady=2)

    def add_video_playlist(self) -> None:
        """
        Add a video or playlist to the content.
        """
        yt_url = self.url_entry.get()
        
        # if url entry is nothing just do nothing
        if yt_url.replace(" ", "") == "":
            return    
                
        # Show fade effect
        self.fade_effect()
        
        if self.selected_download_mode == "video":
            self.add_video()
        else:
            self.add_playlist()
        
        # Automatically navigate to added frame when new video added
        self.place_nav_frame(self.added_content_scroll_frame, "added")
        # auot scroll to bottom
        self.scroll_frame_to_bottom(self.added_content_scroll_frame)

    def download_video(self, video: AddedVideo) -> None:
        """
        Download a video.

        Args:
            video (AddedVideo): The video to be downloaded.
        """
        self.is_content_downloading = True
        self.downloading_frame_info_label.place_forget()
        
        DownloadingVideo(
            root=self,
            master=self.downloading_content_scroll_frame,
            height=int(70 * AppearanceSettings.get_scale("decimal")),
            width=self.downloading_content_scroll_frame.winfo_width(),
            # video info
            channel_url=video.channel_url,
            video_url=video.video_url,
            channel=video.channel,
            video_title=video.video_title,
            video_stream_data=video.video_stream_data,
            length=video.length,
            thumbnails=video.thumbnails,
            notification_thumbnail_image_path=video.notification_thumbnail_image_path,
            original_thumbnail_image_path=video.original_thumbnail_image_path,
            # History thumbnail image paths
            history_normal_thumbnail_image_path=video.history_normal_thumbnail_image_path,
            history_hover_thumbnail_image_path=video.history_hover_thumbnail_image_path,
            # download info
            download_quality=video.download_quality,
            download_type=video.download_type,
            download_type_info=video.selected_download_type_info,
            video_download_complete_callback=self.downloaded_video,
        ).pack(fill="x", pady=2)
        
        self.scroll_frame_to_bottom(self.downloading_content_scroll_frame)

    def download_playlist(self, playlist: AddedPlayList) -> None:
        """
        Download a playlist.

        Args:
            playlist (AddedPlayList): The playlist to be downloaded.
        """
        self.is_content_downloading = True
        self.downloading_frame_info_label.place_forget()
        DownloadingPlayList(
            root=self,
            master=self.downloading_content_scroll_frame,
            height=int(86 * AppearanceSettings.get_scale("decimal")),
            width=self.downloading_content_scroll_frame.winfo_width(),
            # video info
            channel_url=playlist.channel_url,
            channel=playlist.channel,
            playlist_title=playlist.playlist_title,
            playlist_video_count=len(playlist.loaded_videos),
            playlist_url=playlist.playlist_url,
            playlist_original_video_count=playlist.playlist_original_video_count,
            # play list videos
            videos=playlist.loaded_videos,
            # download directory
            # playlist download completed callback utils
            playlist_download_complete_callback=self.downloaded_playlist,
        ).pack(fill="x", pady=2)

        self.scroll_frame_to_bottom(self.downloading_content_scroll_frame)
        
    def downloaded_video(self, video: DownloadingVideo) -> None:
        """
        Handle downloaded video.

        Args:
            video (DownloadingVideo): The downloaded video.
        """
        self.is_content_downloaded = True
        self.downloaded_frame_info_label.place_forget()
        DownloadedVideo(
            root=self,
            master=self.downloaded_content_scroll_frame,
            height=int(70 * AppearanceSettings.get_scale("decimal")),
            width=self.downloaded_content_scroll_frame.winfo_width(),

            thumbnails=video.thumbnails,
            video_title=video.video_title,
            channel=video.channel,
            channel_url=video.channel_url,
            video_url=video.video_url,
            file_size=video.file_size,
            length=video.length,
            original_thumbnail_image_path=video.original_thumbnail_image_path,
            # History thumbnail image paths
            history_normal_thumbnail_image_path=video.history_normal_thumbnail_image_path,
            history_hover_thumbnail_image_path=video.history_hover_thumbnail_image_path,
            downloaded_file_name=video.download_file_name,
            download_quality=video.download_quality,
            download_type=video.download_type
        ).pack(fill="x", pady=2)
        
        self.scroll_frame_to_bottom(self.downloaded_content_scroll_frame)

    def downloaded_playlist(self, playlist: DownloadingPlayList) -> None:
        """
        Handle downloaded playlist.

        Args:
            playlist (DownloadingPlayList): The downloaded playlist.
        """
        self.is_content_downloaded = True
        self.downloaded_frame_info_label.place_forget()
        DownloadedPlayList(
            root=self,
            master=self.downloaded_content_scroll_frame,
            height=86 * AppearanceSettings.get_scale("decimal"),
            width=self.downloaded_content_scroll_frame.winfo_width(),
            # playlist url
            channel_url=playlist.channel_url,
            channel=playlist.channel,
            playlist_title=playlist.playlist_title,
            playlist_original_video_count=playlist.playlist_original_video_count,
            playlist_video_count=len(playlist.downloaded_videos),
            playlist_url=playlist.playlist_url,
            videos=playlist.downloaded_videos
        ).pack(fill="x", pady=2)
        
        self.scroll_frame_to_bottom(self.downloaded_content_scroll_frame)
        
    def update_download_speed_status(self, download_speed_bytes_per_sec: int) -> None:
        if download_speed_bytes_per_sec > self.current_max_download_speed_bytes:
            self.current_max_download_speed_bytes = download_speed_bytes_per_sec
            self.confgiure_chart_y_axis_values()
        else:
            if len(self.net_speed_line.get_data()) > 100:
                max_ = max(self.net_speed_line.get_data()[-100::])
                if max_ < self.current_max_download_speed_bytes:
                    if max_ == 0:
                        max_ = 0.0001
                    self.current_max_download_speed_bytes = max_
                    self.confgiure_chart_y_axis_values()
        
        if len(self.net_speed_line.get_data()) > 3600:
            self.net_speed_chart.clear_data()
            
        self.current_download_speed_bytes = download_speed_bytes_per_sec
        
        self.net_speed_label.configure(
            text=f"{LanguageManager.data["download_speed"]} : {ValueConvertUtility.convert_size(download_speed_bytes_per_sec, decimal_points=3)}/s"
        )
        
        self.net_speed_temp_label.configure(
            text=f"{LanguageManager.data["download_speed"]} : {ValueConvertUtility.convert_size(download_speed_bytes_per_sec, decimal_points=3)}/s"
        )
        
        self.net_speed_chart.show_data(line=self.net_speed_line, data=[download_speed_bytes_per_sec])    
        
    def confgiure_chart_y_axis_values(self):
        converted_speed = ValueConvertUtility.convert_size(self.current_max_download_speed_bytes, decimal_points=2)
        y_axis_data = f"{LanguageManager.data["peak"]} : {converted_speed}/s"
       
        self.net_speed_chart.configure(y_axis_data=y_axis_data, y_axis_values=(0, self.current_max_download_speed_bytes))
        
    def confgiure_chart_x_axis_values(self):
        scale = AppearanceSettings.get_scale("decimal")
        if self.net_speed_chart.cget("width") / 10 * scale >= 60:
            x_axis_point_count = 61
        else:
            x_axis_point_count = 31
        
        
        style_type= (int(scale * 4), int(6 * scale))
        self.net_speed_chart.configure(
            x_axis_values=tuple([x for x in range(1, x_axis_point_count)]),
            )
        self.net_speed_line.configure(style_type=style_type)

    def open_context_menu(self, _event: tk.Event) -> None:
        """
        Open the context menu at the current pointer position.

        Args:
            _event: The event triggering the context menu opening.
        """
        pointer_x = self.winfo_pointerx() - self.winfo_rootx()
        pointer_y = self.winfo_pointery() - self.winfo_rooty()

        self.context_menu.place(x=pointer_x, y=pointer_y)

    def close_context_menu(self, _event: tk.Event) -> None:
        """
        Close the context menu if the pointer is not over the entry widget.

        Args:
            _event: The event triggering the context menu closing.
        """
        pointer_x = self.winfo_pointerx() - self.winfo_rootx()
        pointer_y = self.winfo_pointery() - self.winfo_rooty()

        if (pointer_x < self.url_entry.winfo_x() or pointer_y < self.url_entry.winfo_y() or
                pointer_x > (self.url_entry.winfo_x() + self.url_entry.winfo_width()) or
                pointer_y > (self.url_entry.winfo_y() + self.url_entry.winfo_height())):
            self.context_menu.place_forget()

    def close_context_menu_directly(self, _event: tk.Event) -> None:
        """
        Close the context menu directly.

        Args:
            _event: The event triggering the context menu closing.
        """
        self.context_menu.place_forget()

    def update_general_settings(self, updated: Literal["language"] = None) -> None:
        """
        Update the general settings of the application and save them.
        """
        if updated == "language":
            LanguageManager.update_language()
            self.update_widgets_text()

        GeneralSettings.save_settings()

    def update_appearance_settings(
            self,
            updated: Literal["accent_color", "theme", "opacity"] = None) -> None:
        """
        Update the theme settings based on the specified update.

        Args:
            updated (Literal["accent_color", "theme", "opacity"], optional):
                The type of theme setting that was updated.
        """
        if updated == "accent_color":
            ThemeManager.update_accent_color()
        if updated == "theme":
            ThemeManager.update_theme()
            ThemeManager.set_title_bar_style(self)
        if updated == "opacity":
            self.attributes("-alpha", AppearanceSettings.get_opacity("decimal"))
        # print(AppearanceSettings.get_opacity("percentage"))
        AppearanceSettings.save_settings()

    def open_settings(self) -> None:
        """
        Open the settings panel and configure the settings button to close the settings.

        """
        self.is_settings_open = True
        ContextMenu.close_all_menus()
        self.settings_panel.place(relwidth=1, relheight=1)
        self.settings_btn.configure(command=self.close_settings)

    def close_settings(self) -> None:
        """
        Close the settings panel and configure the settings button to open the settings.

        """
        self.is_settings_open = False
        self.settings_panel.place_forget()
        self.settings_btn.configure(command=self.open_settings)

    def on_app_closing(self, restart: bool = False) -> None:
        """
        Handle the application closing event.

        Args:
            restart (bool, optional): Whether to restart the application. Defaults to False.
        """
        if self.is_accessible_to_required_dirs :
            try:
                GeneralSettings.settings['window_geometry'] = self.geometry()
                GeneralSettings.save_settings()
                self.clear_temporally_saved_files()
                App.maintain_history()
            except Exception as error:
                print("app.py L-1577 : ", error)
        self.destroy()
        self.is_app_running = False
        if not restart:
            os._exit(0)

    def cancel_app_closing(self) -> None:
        """
        Cancel the application closing action.

        """
        self.bind_widgets_events()

    def restart(self) -> None:
        """
        Restart the application.

        """
        self.on_app_closing(restart=True)
        if os.path.exists("main.py"):
            os.startfile("main.py")
        if os.path.exists("PyTube Downloader.exe"):
            os.startfile("PyTube Downloader.exe")
        os._exit(0)
        
    def confirm_quit(self):
        self.restore_from_tray()
        self.show_close_confirmation_dialog()

    def show_close_confirmation_dialog(self) -> None:
        """
        Show a confirmation dialog before closing the application.

        """
        scale = AppearanceSettings.get_scale("decimal")
        AlertWindow(
            master=self,
            original_configure_callback=self.run_geometry_changes_tracker,
            alert_msg="exit_confirmation",
            ok_button_display=True,
            cancel_button_display=True,
            ok_button_callback=self.on_app_closing,
            cancel_button_callback=self.cancel_app_closing,
            callback=self.cancel_app_closing,
            wait_for_previous=True,
            width=int(450 * scale),
            height=int(130 * scale),
        )

    def restore_from_tray(self) -> None:
        """
        Restore the application window from the system tray.
        """
        self.tray_menu.stop()
        self.deiconify()

    def minimize_to_tray(self) -> None:
        """
        Minimize the application window to the system tray.
        """
        self.iconify()
        self.tray_menu = TrayMenu(
            open_command=self.restore_from_tray,
            quit_command=self.confirm_quit,
        )
        self.withdraw()
        # self.after(1, self.tray_menu.run)
        threading.Thread(target=self.tray_menu.run, daemon=True).start()

    def run(self) -> None:
        """
        Run the application.
        """
        self.mainloop()

    @classmethod
    def clear_temporally_saved_files(self) -> None:
        """
        Clears temporarily saved files, such as thumbnails.
        """
        FileUtility.delete_files("temp\\thumbnails", ["this directory is necessary"])
        
    @staticmethod
    def maintain_history() -> None:
        HistoryManager.clear_invalid_history()
    
    def open_update_download_page(self) -> None:
        """
        Open website for download latest version
        """
        webbrowser.open("https://sourceforge.net/projects/pytube-downloader/files/latest/download")
    
    
    def show_update_alert(self, latest_version, current_version) -> None:
        scale = AppearanceSettings.get_scale("decimal")
        if latest_version is not None:
            if latest_version != current_version:
                AlertWindow(
                    master=self,
                    original_configure_callback=self.run_geometry_changes_tracker,
                    alert_msg="update_alert",
                    more_details=f"v{current_version} ➝ v{latest_version}",
                    ok_button_display=True,
                    ok_button_callback=self.open_update_download_page,
                    cancel_button_display=True,
                    wait_for_previous=True,
                    width=int(450 * scale),
                    height=int(150 * scale)
                )
    
    def check_for_updates(self) -> None:
        """
        Update the version of the application.
        """
        # Check the app is updated or not
        latest_version = DataRetrieveUtility.get_latest_version()
        current_version = DataRetrieveUtility.get_current_version()
        
        threading.Thread(target=self.show_update_alert, args=(latest_version, current_version), daemon=True).start()
                
    def run_update_check(self):
        """
        Run the update check in a separate thread.
        """
        # self.after(1, self.check_for_updates)
        self.check_for_updates()

    def manage_history_videos(self, no, channel, title, url, thumbnail_normal_path, thumbnail_hover_path, video_length, download_date, is_playlist_duplicated):
        """
        Manage the history videos.
        """
        self.history_content_frame.add_hisory_video(no, channel, title, url, thumbnail_normal_path, thumbnail_hover_path, video_length, download_date, is_playlist_duplicated)
        
    def manage_history_playlists(self, no, channel, title, url, thumbnail_normal_path, thumbnail_hover_path, video_count, download_date, is_playlist_duplicated):
        """
        Manage the history playlists.
        """
        self.history_content_frame.add_hisory_playlist(no, channel, title, url, thumbnail_normal_path, thumbnail_hover_path, video_count, download_date, is_playlist_duplicated)
        