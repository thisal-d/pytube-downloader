import customtkinter as ctk
import time
from PIL import Image
from typing import Callable
from settings import AppearanceSettings
from services import LanguageManager, ThemeManager

class AlertWindow(ctk.CTkToplevel):
    """
    Use to track any alert windows running or not
    """
    Running = False
    
    def __init__(
            self,
            master: ctk.CTk = None,
            original_configure_callback : Callable = None,
            alert_msg: str = "something_went_wrong",
            ok_button_display: bool = None,
            ok_button_callback: Callable = None,
            cancel_button_display: bool = None,
            cancel_button_callback: Callable = None,
            callback: Callable = None,
            wait_for_previous: bool = False,
            more_details: str = None,
            width: int = 400,
            height: int = 200):

        super().__init__(
            master=master,
            width=width,
            height=height,
            fg_color=ThemeManager.get_color_based_on_theme("background")
        )

        # If ensure_previous_closed is true, wait until the previous alert window is closed
        if wait_for_previous:
            while AlertWindow.Running :
                time.sleep(0.5)
                
        if not master.is_app_running:
            return
        
        # Start the alert window
        AlertWindow.Running = True
        
        scale = AppearanceSettings.get_scale("decimal")

        self.master: ctk.CTk = master
        self.original_configure_callback  = original_configure_callback 
        self.more_details = more_details
        self.alert_msg = alert_msg
        self.is_cancel_button_displayed = cancel_button_display
        self.is_ok_button_displayed = ok_button_display
        self.width = width
        self.height = height
        self.callback = callback
        self.geometry(f"{self.width}x{self.height}")
        self.attributes("-alpha", AppearanceSettings.get_opacity("decimal"))
        self.configure(width=self.width),
        self.configure(height=self.height)
        self.resizable(False, False)
        self.iconbitmap("assets\\main icon\\512x512.ico")
        self.title("PytubeDownloader")
        self.transient(master)
        self.grab_set()

        self.info_image = ctk.CTkImage(Image.open("assets\\ui images\\info.png"), size=(70 * scale, 70 * scale))
        self.info_image_label = ctk.CTkLabel(
            master=self,
            text="",
            image=self.info_image,
            width=70 * scale, height=70*scale
        )

        self.error_msg_label = ctk.CTkLabel(
            master=self,
            text=LanguageManager.data[self.alert_msg],
            font=("Arial", 13 * scale, "bold"),
            text_color=ThemeManager.get_color_based_on_theme("text_warning")
        )
        
        if more_details is not None:
            self.more_details_label = ctk.CTkLabel(
                master=self,
                text=self.more_details,
                font=("Arial", 12 * scale, "bold"),
                text_color=ThemeManager.get_color_based_on_theme("text_normal")
            )

        if cancel_button_display is True:
            self.cancel_button = ctk.CTkButton(
                master=self,
                command=self.on_click_cancel_button,
                text=LanguageManager.data["cancel"],
                font=("Arial", 12 * scale, "bold"),
                width=100 * scale, height=28 * scale,
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
                fg_color=ThemeManager.get_color_based_on_theme("background_warning"),
                hover_color=ThemeManager.get_color_based_on_theme("background_warning_hover"),
            )

        if ok_button_display is True:
            self.ok_button = ctk.CTkButton(
                master=self,
                command=self.on_click_ok_button,
                text=LanguageManager.data["ok"],
                font=("Arial", 12 * scale, "bold"),
                width=100 * scale, height=28 * scale,
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
                fg_color=ThemeManager.get_accent_color("normal"),
                hover_color=ThemeManager.get_accent_color("hover"),
            )

        self.ok_button_callback = ok_button_callback
        self.cancel_button_callback = cancel_button_callback

        self.master.bind("<Configure>", self.move)
        self.bind("<Configure>", self.move)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.move("event")

        self.place_widgets()
        
        # self.set_widgets_sizes()
        # self.set_widgets_texts()
        # self.set_widgets_fonts()
        # self.set_widgets_colors()
        # self.set_widgets_accent_color()

        ThemeManager.set_title_bar_style(self)

    def move(self, _event):
        geometry_x = int(self.master.winfo_width() * 0.5 + self.master.winfo_x() - 0.5 * self.width)
        geometry_y = int(self.master.winfo_height() * 0.5 + self.master.winfo_y() - 0.5 * self.height)
        self.geometry(f"{self.width}x{self.height}+{geometry_x}+{geometry_y}")

    def on_closing(self):
        self.transient(None)
        self.grab_release()
        self.unbind("<Configure>")
        self.master.unbind("<Configure>")
        self.destroy()
        AlertWindow.Running = False
        if self.callback is not None:
            self.callback()
            
        if self.original_configure_callback  is not None:
            self.master.bind("<Configure>", self.original_configure_callback )

    def on_click_ok_button(self):
        if self.ok_button_callback is not None:
            self.ok_button_callback()
        self.on_closing()

    def on_click_cancel_button(self):
        if self.cancel_button_callback is not None:
            self.cancel_button_callback()
        self.on_closing()

    def set_widgets_accent_color(self):
        self.ok_button.configure(
            fg_color=ThemeManager.get_accent_color("normal"),
            hover_color=ThemeManager.get_accent_color("hover"),
        )

    def update_widgets_accent_color(self):
        self.set_widgets_accent_color()

    def set_widgets_colors(self):
        """Set colors for the widgets."""
        self.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))
        
        if self.is_ok_button_displayed:
            self.ok_button.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            )
        
        if self.is_cancel_button_displayed:
            self.cancel_button.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
                fg_color=ThemeManager.get_color_based_on_theme("background_warning"),
                hover_color=ThemeManager.get_color_based_on_theme("background_warning_hover"),
            )
        
        self.error_msg_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_warning")
        )

        if self.more_details is not None:
            self.more_details_label.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal")
            )

    def update_widgets_colors(self):
        """Update colors for the widgets."""
        self.set_widgets_colors()

    def place_widgets(self):
        scale = AppearanceSettings.get_scale("decimal")
        self.info_image_label.pack(side="left", fill="y", padx=(30 * scale, 10 * scale))

        if self.more_details is None:
            self.error_msg_label.pack(pady=(20 * scale, 15 * scale), padx=(0, 30 * scale))
        else:
            self.error_msg_label.pack(pady=(10 * scale, 0 * scale), padx=(0, 30 * scale))
            self.more_details_label.pack(pady=(8 * scale, 15 * scale), padx=(0, 30 * scale))

        if self.is_cancel_button_displayed:
            self.ok_button.pack(side="right", padx=(0, 20 * scale))

        if self.is_cancel_button_displayed:
            self.cancel_button.pack(side="right", padx=(20 * scale, 40 * scale))

    def set_widgets_texts(self):
        scale = AppearanceSettings.get_scale("decimal")
        
        self.info_image = ctk.CTkImage(Image.open("assets\\ui images\\info.png"), size=(70 * scale, 70 * scale))
        self.info_image_label.configure(image=self.info_image)

        self.error_msg_label.configure(text=LanguageManager.data[self.alert_msg])

        if self.more_details is not None:
            self.more_details_label.configure(text=self.more_details)
        
        if self.is_cancel_button_displayed:
            self.cancel_button.configure(text=LanguageManager.data["cancel"])

        if self.is_ok_button_displayed:
            self.ok_button.configure(text=LanguageManager.data["ok"])

    def set_widgets_fonts(self):
        scale = AppearanceSettings.get_scale("decimal")

        self.error_msg_label.configure(font=("Arial", 13 * scale, "bold"))
        if self.more_details is not None:
            self.more_details_label.configure(font=("Arial", 12 * scale, "bold"))
        
        if self.is_cancel_button_displayed:
            self.cancel_button.configure(font=("Arial", 12 * scale, "bold"))
        
        if self.is_ok_button_displayed:
            self.ok_button.configure(font=("Arial", 12 * scale, "bold"))

    def set_widgets_sizes(self):
        scale = AppearanceSettings.get_scale("decimal")

        self.info_image_label.configure(width=70 * scale, height=70*scale)
        if self.is_cancel_button_displayed:
            self.cancel_button.configure(width=100 * scale, height=28 * scale)
        
        if self.is_ok_button_displayed:
            self.ok_button.configure(width=100 * scale, height=28 * scale)