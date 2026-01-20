import webbrowser
import customtkinter as ctk
from typing import Union, List
from services import ThemeManager, LanguageManager
from settings import AppearanceSettings
from widgets.video.video import Video
import math


class PlayList(ctk.CTkFrame):
    """
    A custom Tkinter frame for displaying information about a playlist.

    Args:
        master (Optional): The parent widget.
        width (int): The width of the frame.
        height (int): The height of the frame.
        channel_url (str): The URL of the channel.
        playlist_url (str): The URL of the playlist.
        playlist_title (str): The title of the playlist.
        channel (str): The name of the channel.
        playlist_video_count (int): The number of videos in the playlist.
    """
    
    max_videos_per_page: int = 5

    def __init__(
            self,
            root: ctk.CTk = None,
            master: ctk.CTkScrollableFrame = None,
            width: int = 0,
            height: int = 0,
            # playlist info
            channel_url: str = "-------",
            playlist_url: str = "-------",
            playlist_title: str = "-------",
            channel: str = "-------",
            playlist_video_count: int = 0,
            playlist_original_video_count: int = 0):

        super().__init__(
            master=master,
            width=width,
        )        
        
        # Initialize attributes
        self.root = root
        self.master_frame = master
        self.height: int = height
        self.width: int = width
        
        # playlist info
        self.channel_url: str = channel_url
        self.channel: str = channel
        self.playlist_url: str = playlist_url
        self.playlist_title: str = playlist_title
        self.playlist_video_count: int = playlist_video_count
        self.playlist_original_video_count: int = playlist_original_video_count

        # widgets
        self.view_btn: Union[ctk.CTkButton, None] = None
        self.last_viewed_index: int = 0
        self.current_viewing_page: int = 0
        self.total_videos_tab_count: int = 0
        
        self.info_frame: Union[ctk.CTkFrame, None] = None
        self.playlist_title_label: Union[ctk.CTkLabel, None] = None
        self.channel_btn: Union[ctk.CTkButton, None] = None
        self.url_label: Union[ctk.CTkLabel, None] = None

        self.playlist_main_frame: Union[ctk.CTkFrame, None] = None

        self.remove_btn: Union[ctk.CTkButton, None] = None
        self.playlist_video_count_label: Union[ctk.CTkLabel, None] = None
        self.playlist_item_frame: Union[ctk.CTkFrame, None] = None

        self.playlist_videos_frame: Union[ctk.CTkFrame, None] = None
        self.previous_btn: Union[ctk.CTkButton, None] = None
        self.next_btn: Union[ctk.CTkButton, None] = None
        self.tab_info_label: Union[ctk.CTkLabel, None] = None

        self.videos: List[Video] = []
        # Create and configure widgets
        self.create_widgets()
        self.set_widgets_texts()
        self.set_widgets_sizes()
        self.set_widgets_fonts()
        self.set_widgets_colors()
        self.set_tk_widgets_colors()
        self.set_widgets_accent_color()
        self.place_widgets()
        self.bind_widgets_events()

        # Register to Theme Manager for accent color updates & widgets colors updates
        ThemeManager.register_widget(self)
        LanguageManager.register_widget(self)

    def hide_videos(self):
        """Hide the videos in the playlist."""
        self.view_btn.configure(
            command=self.view_videos,
            text="⯈",
        )
        self.playlist_item_frame.pack_forget()

    def view_videos(self):
        """View the videos in the playlist."""
        self.view_btn.configure(
            command=self.hide_videos,
            text="⯆",
        )
        self.playlist_item_frame.pack(padx=10, fill="x", pady=2)

    def set_playlist_data(self):
        """Set the data of the playlist."""
        self.playlist_video_count_label.configure(text=f"{self.playlist_video_count}")
        self.playlist_title_label.configure(text=f"{LanguageManager.data['title']} : {self.playlist_title}")
        self.channel_btn.configure(text=f"{LanguageManager.data['channel']} : {self.channel}")
        self.url_label.configure(text=self.playlist_url)
        self.channel_btn.configure(state="normal")

    def create_widgets(self):
        """Create widgets for the playlist."""
        self.playlist_main_frame = ctk.CTkFrame(master=self)
        self.view_btn = ctk.CTkButton(
            master=self.playlist_main_frame,
            text="⯈",
            hover=False,
            command=self.view_videos,
            state="disabled",
            cursor="hand2",
        )
        self.info_frame = ctk.CTkFrame(master=self.playlist_main_frame)
        self.playlist_title_label = ctk.CTkLabel(
            master=self.info_frame, anchor="w"
        )
        self.channel_btn = ctk.CTkButton(
            master=self.info_frame,
            anchor="w",
            command=lambda: webbrowser.open(self.channel_url),
            state="disabled",
            hover=False,
        )
        self.url_label = ctk.CTkLabel(master=self.info_frame, anchor="w", text=self.playlist_url)
        
        self.remove_btn = ctk.CTkButton(master=self.playlist_main_frame, command=self.kill, text="X", hover=False)
        self.playlist_video_count_label = ctk.CTkLabel(
            master=self.playlist_main_frame,
            justify="right",
            text=f"{self.playlist_video_count}"
        )
        self.playlist_item_frame = ctk.CTkFrame(master=self, height=0)
        self.playlist_videos_frame = ctk.CTkFrame(master=self.playlist_item_frame, height=0)
        self.previous_btn = ctk.CTkButton(
            master=self.playlist_item_frame,
            command=self.view_previous_videos,
            text="⯇",
            hover=False
        )
        self.next_btn = ctk.CTkButton(
            master=self.playlist_item_frame,
            command=self.view_next_videos,
            text="⯈",
            hover=False
        )
        self.tab_info_label = ctk.CTkLabel(master=self.playlist_item_frame, text='999 | 999')
    
    def pack_forgot_videos(self):
        for i in range(
                self.current_viewing_page * PlayList.max_videos_per_page,
                (self.current_viewing_page * PlayList.max_videos_per_page) + PlayList.max_videos_per_page
        ):
            try:
                self.videos[i].pack_forget()
            except Exception as error:
                print(f"play_list.py L165 : {error}")
        """print("Place Forgets Start:",self.last_viewed_index, end="")
        self.last_viewed_index -= PlayList.max_videos_per_page
        for i in range(self.last_viewed_index, self.last_viewed_index + PlayList.max_videos_per_page , 1):
            try:
                self.videos[i].pack_forget()
            except Exception as error:
                print(f"play_list.py L154 : {error}")
            self.last_viewed_index += 1
        print(" End :",self.last_viewed_index)
        """
        
    def configure_videos_tab_view(self):
        self.current_viewing_page -= 1
        self.total_videos_tab_count = math.ceil(len(self.videos) / PlayList.max_videos_per_page) - 1
        
        if len(self.videos) <= PlayList.max_videos_per_page:
            self.previous_btn.place_forget()
            self.next_btn.place_forget()
            self.tab_info_label.place_forget()
        if self.current_viewing_page > self.total_videos_tab_count:
            self.current_viewing_page = self.total_videos_tab_count - 1
            
        if len(self.videos) > PlayList.max_videos_per_page:
            self.playlist_item_frame.configure(
                height=5 * (self.videos[0].height + 1) + 1 + 40 * AppearanceSettings.get_scale("decimal")
            )
            self.playlist_videos_frame.configure(height=5 * (self.videos[0].height + 1))
        elif len(self.videos) != 0:
            self.playlist_item_frame.configure(height=len(self.videos) * (self.videos[0].height + 1))
            self.playlist_videos_frame.configure(height=len(self.videos) * (self.videos[0].height + 1))
        
        self.view_next_videos()
                        
    def view_next_videos(self):
        self.pack_forgot_videos()

        if self.current_viewing_page == self.total_videos_tab_count:
            self.current_viewing_page = 0
        else:
            self.current_viewing_page += 1
            
        for i in range(
                self.current_viewing_page * PlayList.max_videos_per_page,
                (self.current_viewing_page * PlayList.max_videos_per_page) + PlayList.max_videos_per_page):
            try:
                self.videos[i].pack(fill="x", padx=(20, 0), pady=(1, 0))
            except Exception as error:
                print(f"play_list.py L202 : {error}")
        
        self.tab_info_label.configure(text=f"{self.current_viewing_page + 1} | {self.total_videos_tab_count + 1}")
         
        """self.pack_forgot_videos()
        print("View next Start:",self.last_viewed_index, end="")
        for i in range(self.last_viewed_index, self.last_viewed_index + PlayList.max_videos_per_page):
            try:
                self.videos[i].pack(fill="x", padx=(20, 0), pady=(1, 0))
            except Exception as error:
                print(f"play_list.py L165 : {error}")
            self.last_viewed_index += 1
        print(" End:",self.last_viewed_index)
        """
        
    def view_previous_videos(self):
        self.pack_forgot_videos()
        
        if self.current_viewing_page == 0:
            self.current_viewing_page = self.total_videos_tab_count
        else:    
            self.current_viewing_page -= 1
        
        for i in range(
                self.current_viewing_page * PlayList.max_videos_per_page,
                self.current_viewing_page * PlayList.max_videos_per_page + PlayList.max_videos_per_page):
            try:
                self.videos[i].pack(fill="x", padx=(20, 0), pady=(1, 0))
            except Exception as error:
                print(f"play_list.py L227 : {error}")
        
        self.tab_info_label.configure(text=f"{self.current_viewing_page + 1} | {self.total_videos_tab_count + 1}")
        
        """print("View before Start:",self.last_viewed_index, end="")
        for i in range(
                self.last_viewed_index - PlayList.max_videos_per_page * 2, 
                self.last_viewed_index - PlayList.max_videos_per_page * 2 + PlayList.max_videos_per_page):
            try:
                self.videos[i].pack(fill="x", padx=(20, 0), pady=(1, 0))
            except Exception as error:
                print(f"play_list.py L176 : {error}")
        print(" End :",self.last_viewed_index, i)
        self.last_viewed_index = i
        """
        
    def set_widgets_texts(self):
        self.playlist_title_label.configure(text=f"{LanguageManager.data['title']} : {self.playlist_title}")
        self.channel_btn.configure(text=f"{LanguageManager.data['channel']} : {self.channel}")

    def update_widgets_text(self):
        self.set_widgets_texts()

    def set_widgets_fonts(self):
        """Set fonts for the widgets."""
        scale = AppearanceSettings.get_scale("decimal")

        self.view_btn.configure(font=('Segoe UI', 17 * scale),)
        self.playlist_title_label.configure(font=('Segoe UI', int(14 * scale), 'bold'))
        self.channel_btn.configure(font=('Segoe UI', int(14 * scale), 'bold'))
        font_style = ctk.CTkFont(family="Segoe UI", size=int(14 * scale), slant="italic", underline=True)
        self.url_label.configure(font=font_style)
        self.remove_btn.configure(font=("Segoe UI", 12 * scale, "bold"),)
        self.playlist_video_count_label.configure(font=("Segoe UI", 13 * scale, "bold"))
        
        navigate_btn_font_style = ("Segoe UI", 12 * scale, "bold")
        self.next_btn.configure(font=navigate_btn_font_style)
        self.previous_btn.configure(font=navigate_btn_font_style)
        self.tab_info_label.configure(font=navigate_btn_font_style)

    def set_widgets_sizes(self):
        """Set sizes for the widgets."""
        scale = AppearanceSettings.get_scale("decimal")

        self.playlist_main_frame.configure(border_width=1, height=self.height, width=self.width)
        self.view_btn.configure(width=1, height=1)
        self.info_frame.configure(height=self.height-3)
        label_height = int((self.height - 2) / 3)
        self.playlist_title_label.configure(height=label_height)
        self.channel_btn.configure(height=label_height)
        self.url_label.configure(height=label_height)
        self.remove_btn.configure(width=22 * scale, height=22 * scale, border_spacing=0)
        self.playlist_video_count_label.configure(width=15 * scale, height=15 * scale)
        
        self.next_btn.configure(width=30 * scale, height=30 * scale)
        self.previous_btn.configure(width=30 * scale, height=30 * scale)
        self.tab_info_label.configure(width=70 * scale, height=30 * scale)

    def set_widgets_accent_color(self):
        """Set accent color for the widgets."""
        self.playlist_main_frame.configure(
            border_color=ThemeManager.get_accent_color("normal")
        )
        self.view_btn.configure(
            text_color=ThemeManager.get_accent_color("normal")
        )
        self.url_label.configure(text_color=ThemeManager.get_accent_color("normal"))
        self.next_btn.configure(
            fg_color=ThemeManager.get_accent_color("normal"),
            hover_color=ThemeManager.get_accent_color("hover"),
        )
        self.previous_btn.configure(
            fg_color=ThemeManager.get_accent_color("normal"),
            hover_color=ThemeManager.get_accent_color("hover"),
        )

    def update_widgets_accent_color(self):
        """Update accent color for the widgets."""
        self.set_widgets_accent_color()

    def set_tk_widgets_colors(self):
        """Set colors for the Tk widgets."""
        self.playlist_title_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )
        self.channel_btn.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_muted"),
            fg_color=ThemeManager.get_color_based_on_theme("primary")
        )

    def update_widgets_colors(self):
        """Update colors for the widgets."""
        self.set_tk_widgets_colors()
        self.set_widgets_colors()

    def set_widgets_colors(self):
        """Set colors for the widgets."""
        self.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background")
        )
        self.playlist_item_frame.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background")
        )
        self.playlist_main_frame.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background")
        )
        self.info_frame.configure(
            fg_color=ThemeManager.get_color_based_on_theme("primary")
        )
        self.view_btn.configure(
            fg_color=ThemeManager.get_color_based_on_theme("primary")
        )
        self.playlist_main_frame.configure(
            fg_color=ThemeManager.get_color_based_on_theme("primary")
        )
        self.remove_btn.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background_warning"),
            hover_color=ThemeManager.get_color_based_on_theme("background_warning_hover"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal")
        )
        self.playlist_video_count_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )
        self.playlist_videos_frame.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background")
        )
        self.next_btn.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal")
        )
        self.previous_btn.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal")
        )
        self.tab_info_label.configure(
           text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )

    def on_mouse_enter_self(self, event):
        """Handle mouse enter event for the widget."""
        """
        self.playlist_main_frame.configure(
            fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["hover"],
            border_color=AppearanceSettings.settings["root"]["accent_color"]["hover"]
        )
        self.info_frame.configure(
            fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["hover"]
        )
        self.view_btn.configure(
            fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["hover"],
        )
        self.channel_btn.configure(
            fg_color=ThemeManager.get_color_based_on_theme_mode(
                AppearanceSettings.settings["video_object"]["fg_color"]["hover"]
            )
        )
        """
        # disable due to ui performance issue
        """def on_mouse_enter_videos():
            video_object: AddedVideo
            for video_object in self.playlist_item_frame.winfo_children():
                if type(video_object) is AddedVideo or \
                        type(video_object) is DownloadingVideo or \
                        type(video_object) is DownloadedVideo:
                    if self.on_mouse_state == "enter":
                        video_object.on_mouse_enter_self(event)
                    else:
                        break
        threading.Thread(target=on_mouse_enter_videos).start()"""

    def on_mouse_leave_self(self, event):
        """Handle mouse leave event for the widget."""
        """
        self.playlist_main_frame.configure(
            fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["normal"],
            border_color=AppearanceSettings.settings["root"]["accent_color"]["normal"]
        )
        self.info_frame.configure(
            fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["normal"]
        )
        self.view_btn.configure(
            fg_color=AppearanceSettings.settings["video_object"]["fg_color"]["normal"],
        )
        self.channel_btn.configure(
            fg_color=ThemeManager.get_color_based_on_theme_mode(
                AppearanceSettings.settings["video_object"]["fg_color"]["normal"]
            )
        )
        """

        # disable due to ui performance down
        """def on_mouse_leave_videos():
            video_object: AddedVideo
            for video_object in self.playlist_item_frame.winfo_children():
                if type(video_object) is AddedVideo or \
                        type(video_object) is DownloadingVideo or \
                        type(video_object) is DownloadedVideo:
                    if self.on_mouse_state == "leave":
                        video_object.on_mouse_leave_self(event)
                    else:
                        break
        threading.Thread(target=on_mouse_leave_videos).start()"""

    def bind_widgets_events(self):
        """Bind events for the widgets."""
        # self.playlist_main_frame.bind("<Enter>", self.on_mouse_enter_self)
        # self.playlist_main_frame.bind("<Leave>", self.on_mouse_leave_self)

        self.bind("<Configure>", self.configure_widget_sizes)

        """
        for child_widgets in self.playlist_main_frame.winfo_children() + self.playlist_item_frame.winfo_children():
            child_widgets.bind("<Enter>", self.on_mouse_enter_self)
            child_widgets.bind("<Leave>", self.on_mouse_leave_self)
            try:
                for sub_child_widgets in child_widgets.winfo_children():
                    sub_child_widgets.bind("<Enter>", self.on_mouse_enter_self)
                    sub_child_widgets.bind("<Leave>", self.on_mouse_leave_self)
            except Exception as error:
                print(f"1@PlayList.py > Err : {error}")
                pass
        """
        
        def on_mouse_enter_channel_btn(_event):
            self.channel_btn.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal")
            )
            # self.on_mouse_enter_self(event)

        def on_mouse_leave_channel_btn(_event):
            self.channel_btn.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_muted"),
            )

        self.channel_btn.bind("<Enter>", on_mouse_enter_channel_btn)
        self.channel_btn.bind("<Leave>", on_mouse_leave_channel_btn)

        #-----------------------------------------------------------------

        def on_mouse_enter_view_btn(_event):
            self.view_btn.configure(
                text_color=ThemeManager.get_accent_color("hover")
            )
            # self.on_mouse_enter_self(event)

        def on_mouse_leave_view_btn(_event):
            self.view_btn.configure(
                text_color=ThemeManager.get_accent_color("normal"),
            )

        self.view_btn.bind("<Enter>", on_mouse_enter_view_btn)
        self.view_btn.bind("<Leave>", on_mouse_leave_view_btn)

        """
        def on_mouse_enter_remove_btn(_event):
            self.remove_btn.configure(
                fg_color=ThemeManager.get_color_based_on_theme("background_warning_hover")
            )
            # self.on_mouse_enter_self(event)

        def on_mouse_leave_remove_btn(_event):
            self.remove_btn.configure(
                fg_color=ThemeManager.get_color_based_on_theme("background_warning")
            )

        self.remove_btn.bind("<Enter>", on_mouse_enter_remove_btn)
        self.remove_btn.bind("<Leave>", on_mouse_leave_remove_btn)
        """
        
    # place widgets
    def place_widgets(self):
        """Place the widgets."""
        scale = AppearanceSettings.get_scale("decimal")

        self.playlist_main_frame.pack(fill="x")
        self.view_btn.place(rely=0.7, x=15 * scale, anchor="w")

        self.info_frame.place(x=50*scale + 15 * scale, y=1)
        self.playlist_title_label.place(x=0, rely=0.2, anchor="w")
        self.channel_btn.place(x=0, rely=0.5, anchor="w")
        self.url_label.place(x=0, rely=0.8, anchor="w")

        self.playlist_video_count_label.place(relx=1, x=-40 * scale, rely=0.8, anchor="w")
        self.remove_btn.place(relx=1, x=-25 * scale, y=3 * scale)
        
        self.playlist_videos_frame.place(x=0, y=0, relwidth=1)
        
        self.previous_btn.place(rely=1, y=-20 * scale, relx=0.5, anchor="e", x=-40 * scale)
        self.next_btn.place(rely=1, y=-20 * scale, relx=0.5, anchor="w", x=40 * scale)
        self.tab_info_label.place(rely=1, y=-20 * scale, relx=0.5, anchor="center")

    def configure_widget_sizes(self, _event):
        ...
        
    def __del__(self):
        """Clear the Memory."""
        self.root = None
        self.master_frame = None
        
        del self.height
        del self.width
        
        # playlist info
        del self.channel_url
        del self.channel
        del self.playlist_url
        del self.playlist_title
        del self.playlist_video_count

        # widgets
        del self.view_btn
        del self.info_frame
        del self.playlist_title_label
        del self.channel_btn
        del self.url_label
        del self.playlist_main_frame
        del self.remove_btn
        del self.playlist_video_count_label
        del self.playlist_item_frame
        
        del self.total_download_size_progress_label
        del self.videos
        
        del self.last_viewed_index
        del self.playlist_videos_frame
        del self.previous_btn
        del self.next_btn
        del self.tab_info_label
        
        del self

    def destroy_widgets(self):
        """Destroy the child widget."""
        self.playlist_main_frame.destroy()
        self.view_btn.destroy()
        self.info_frame.destroy()
        self.playlist_title_label.destroy()
        self.channel_btn.destroy()
        self.url_label.destroy()
        self.remove_btn.destroy()
        self.playlist_video_count_label.destroy()
        self.playlist_item_frame.destroy()
        self.playlist_videos_frame.destroy()
        self.previous_btn.destroy()
        self.next_btn.destroy()
        self.tab_info_label.destroy()
        self.self.total_download_size_progress_label.destroy()
        
        super().destroy()

    def kill(self):
        """Destroy the playlist widget."""
        ThemeManager.unregister_widget(self)
        LanguageManager.unregister_widget(self)
        self.destroy_widgets()
        self.__del__()
        