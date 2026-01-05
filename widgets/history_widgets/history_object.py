import customtkinter as ctk
from tkinter import PhotoImage
import tkinter as tk
from settings import AppearanceSettings
from services import ThemeManager, LanguageManager
from utils import ImageUtility, FileUtility
from typing import Callable
from PIL import Image
import webbrowser
import os


class HistoryObject(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkFrame = None,
        width: int = 130,
        no: int = None,
        channel: str = None,
        title: str = None,
        url: str = None,
        thumbnail_path_normal: str = None,
        thumbnail_path_hover: str = None,
        add_to_download_callback: Callable = None,
        remove_callback: Callable = None,
        download_date: str = None):
        
        super().__init__(master=master, width=width, border_width=1)
        
        self.thumbnail_button: tk.Button = None
        self.label_frame: ctk.CTkFrame = None
        self.title_label: ctk.CTkLabel = None
        self.channel_label: ctk.CTkLabel = None
        self.download_date_label: ctk.CTkLabel = None
        self.remove_callback: Callable = remove_callback
        
        self.width = width
        self.height = width / 16 * 9 + 15 * 3 + 20
        
        self.no = no
        self.channel = channel
        self.title = title
        self.url = url
        self.thumbnail_path_normal = thumbnail_path_normal
        self.thumbnail_path_hover = thumbnail_path_hover
        self.download_date = download_date
        self.thumbnail_normal: PhotoImage = None 
        self.thumbnail_hover: PhotoImage = None
        self.default_thumbnail_used = False
        self.add_to_download_callback = add_to_download_callback
        
        self.create_widgets()
        self.place_widgets()
        self.set_data()
        self.set_widgets_texts()
        
        self.set_widgets_sizes()
        self.set_widgets_fonts()
        
        self.set_widgets_accent_color()
        self.tk_widgets_colors()
        self.set_widgets_colors()
        
        self.bind_widgets_events()
        LanguageManager.register_widget(self)
        ThemeManager.register_widget(self)
        
    def get_resized_thumbnail(self, thumbnail_path: str):
        thumbnail_size_for_video_history_object = (
            int(self.width) - 5,
            int((self.width/ 16*9))
        )
        
        thumbnail_image = Image.open(thumbnail_path)
        thumbnail_image = ImageUtility.resize_image(
            image=thumbnail_image,
            new_size=thumbnail_size_for_video_history_object
        )
        
        thumbnail_path = FileUtility.get_available_file_name("temp\\thumbnails\\history.png")
        thumbnail_image.save(FileUtility.get_available_file_name(thumbnail_path))

        return thumbnail_path
    
    def get_default_thumbnail(self):
        ...
        
    def configure_default_thumbnails(self):
        ...
    
    def set_data(self):
        if os.path.exists(self.thumbnail_path_normal) and self.thumbnail_path_normal != "":
            self.thumbnail_normal = PhotoImage(file=self.get_resized_thumbnail(self.thumbnail_path_normal))
            self.thumbnail_hover = PhotoImage(file=self.get_resized_thumbnail(self.thumbnail_path_hover))
        else:
            self.default_thumbnail_used = True
            self.get_default_thumbnail()
        
        self.thumbnail_button.configure(image=self.thumbnail_normal)
        self.title_label.configure(text=self.title)
        self.channel_label.configure(text=self.channel)
        self.download_date_label.configure(text=self.download_date)
        
    def bind_widgets_events(self):
        def on_mouse_enter_self(event):
            try:
                self.configure(border_color=ThemeManager.get_accent_color("hover"))
                self.thumbnail_button.configure(image=self.thumbnail_hover)
            except:
                pass
        def on_mouse_leave_self(event):
            try:
                self.configure(border_color=ThemeManager.get_accent_color("normal"))
                self.thumbnail_button.configure(image=self.thumbnail_normal)
            except:
                pass
            
        self.bind("<Enter>", on_mouse_enter_self)
        self.bind("<Leave>", on_mouse_leave_self)
        
        self.thumbnail_button.bind("<Enter>", on_mouse_enter_self)
        self.thumbnail_button.bind("<Leave>", on_mouse_leave_self)
        
        self.title_label.bind("<Enter>", on_mouse_enter_self)
        self.title_label.bind("<Leave>", on_mouse_leave_self)
        
        self.channel_label.bind("<Enter>", on_mouse_enter_self)
        self.channel_label.bind("<Leave>", on_mouse_leave_self)
        
        self.download_date_label.bind("<Enter>", on_mouse_enter_self)
        self.download_date_label.bind("<Leave>", on_mouse_leave_self)

        """
        def on_mouse_enter_remove_btn(_event):
            try:
                self.remove_btn.configure(
                    fg_color=ThemeManager.get_color_based_on_theme("background_Warning_hover"),
                )
            except Exception as error:
                pass

        def on_mouse_leave_remove_btn(_event):
            try:
                self.remove_btn.configure(
                    fg_color=ThemeManager.get_color_based_on_theme("background_Warning"),
                )
            except Exception as error:
                pass

        self.remove_btn.bind("<Enter>", on_mouse_enter_remove_btn)
        self.remove_btn.bind("<Leave>", on_mouse_leave_remove_btn)
        """

    def create_widgets(self):
        self.thumbnail_button = tk.Button(master=self, text="", relief="sunken", bd=0, cursor="hand2", command=lambda: webbrowser.open(self.url))
        self.remove_btn = ctk.CTkButton(master=self, text="X", command=self.kill, hover=False, corner_radius=4)
        self.label_frame = ctk.CTkFrame(master=self)
        self.title_label = ctk.CTkLabel(master=self.label_frame, text="", justify="left", anchor="w")
        self.channel_label = ctk.CTkLabel(master=self.label_frame, text="", justify="left", anchor="w")
        self.download_date_label = ctk.CTkLabel(master=self.label_frame, text="", justify="left", anchor="e")
        self.download_btn = ctk.CTkButton(master=self.label_frame, text="Download", command=lambda: self.add_to_download_callback(self.url))
        
    def place_widgets(self):
        scale = AppearanceSettings.get_scale("decimal")
        self.remove_btn.place(x=self.width-2, y=5 , anchor="ne")
        self.thumbnail_button.place(x=1, y=3)
            
        y = (self.width) / 16 * 9 + 10
        self.label_frame.place(x=4, y=y)
        
        y=0
        self.title_label.place(x=0, y=y)
        self.channel_label.place(x=0, y=(y + 15) * scale)
        self.download_date_label.place(x=0, y=(y + 30) * scale)
        self.download_btn.place(x=0, y=(y + 45) * scale)
    
    def set_widgets_colors(self):
        """Set colors for widgets."""
        self.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"))
        self.label_frame.configure(fg_color=ThemeManager.get_color_based_on_theme("primary"))
        self.remove_btn.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background_warning"),
            hover_color=ThemeManager.get_color_based_on_theme("background_warning_hover"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
        )
        self.title_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))
        self.channel_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))
        self.download_date_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))
        self.download_btn.configure(
            text_color=ThemeManager.get_color_based_on_theme("background"),
        )
    
    def tk_widgets_colors(self):
        self.thumbnail_button.configure(
            bg=ThemeManager.get_color_based_on_theme("primary"),
            disabledforeground=ThemeManager.get_color_based_on_theme("text_muted"),
            activebackground=ThemeManager.get_color_based_on_theme("primary")
        )
        
    def update_widgets_colors(self):
        """Update colors for widgets."""
        self.tk_widgets_colors()
        self.set_widgets_colors()
        if self.default_thumbnail_used:
            self.configure_default_thumbnails()
        
    def set_widgets_accent_color(self):
        """Set accent color for widgets."""

        self.configure(border_color=ThemeManager.get_accent_color("normal"))
        self.download_btn.configure(
            fg_color=ThemeManager.get_accent_color("normal"),
            hover_color=ThemeManager.get_accent_color("hover")
        )

    def update_widgets_accent_color(self):
        """Update accent color for widgets."""
        self.set_widgets_accent_color()

    def set_widgets_texts(self):
        self.download_btn.configure(text=LanguageManager.data["download"])
        
    def update_widgets_text(self):
        self.set_widgets_texts()

    def set_widgets_sizes(self):
        """Set sizes for widgets."""
        scale = AppearanceSettings.get_scale("decimal")
        
        width = self.width
        height = 15 * scale
        
        self.remove_btn.configure(width=20 * scale, height=20 * scale, border_spacing=0)
        self.title_label.configure(height=height, width=width - 8)
        self.channel_label.configure(height=height, width=width - 8)
        self.download_date_label.configure(height=height, width=width - 8)
        
        self.download_btn.configure(
            width = width - 8,
            height = 20 * scale
        )
        
        self.label_frame.configure(width=width-8, height=65*scale)
        
        widget_height = ((self.width/ 16*9)) + (3 * (15 * scale)) + (20 * scale) + 14
        self.configure(
            width = self.width,
            height = widget_height
        )
        
    def set_widgets_fonts(self):
        """Set fonts for widgets."""
        scale = AppearanceSettings.get_scale("decimal")
        self.remove_btn.configure(font=("Segoe UI", 10 * scale, "bold"))
        self.title_label.configure(font=('Segoe UI', int(11 * scale), 'bold'))
        self.channel_label.configure(font=('Segoe UI', int(10 * scale), 'bold'))
        self.download_date_label.configure(font=('Segoe UI', int(10 * scale), 'normal'))
        
        self.download_btn.configure(font=('Segoe UI', int(11 * scale), 'bold'))
        
    def kill(self):
        if self.remove_callback is not None:
            self.remove_callback(self)
        
    def __del__(self):
          
        # Unregister widget from ThemeManager
        ThemeManager.unregister_widget(self)

        # Clean up all attributes by setting them to None or deleting them
        del self.thumbnail_button
        del self.label_frame
        del self.title_label
        del self.channel_label
        del self.download_date_label
        del self.remove_btn
        del self.thumbnail_normal
        del self.thumbnail_hover
        del self.default_thumbnail_used
        del self.add_to_download_callback
        del self.remove_callback
        del self.no
        del self.channel
        del self.title
        del self.url
        del self.thumbnail_path_normal
        del self.thumbnail_path_hover
        del self.download_date
        
        del self.width
        del self.height

    def destroy(self):
        try:
            self.thumbnail_button.destroy()
            self.label_frame.destroy()
            self.title_label.destroy()
            self.channel_label.destroy()
            self.download_date_label.destroy()
            self.__del__()
            return super().destroy()
        except Exception as error:
            print("history_object.py L-284", error)
        