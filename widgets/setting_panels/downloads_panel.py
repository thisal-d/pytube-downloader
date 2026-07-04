from collections.abc import Callable
from tkinter import filedialog
from typing import Any

import customtkinter as ctk

from services import DownloadManager, LanguageManager, ThemeManager
from settings import AppearanceSettings, GeneralSettings
from utils import FileUtility, SettingsValidateUtility, ValueConvertUtility


class DownloadsPanel(ctk.CTkFrame):
    def __init__(
        self, master: Any = None, general_settings_change_callback: Callable = None, restart_callback: Callable = None
    ):

        super().__init__(
            master=master,
        )

        self.download_path_label = ctk.CTkLabel(
            master=self,
        )
        self.dash1_label = ctk.CTkLabel(
            master=self,
            text=":",
        )
        self.download_path_entry = ctk.CTkEntry(
            master=self,
            justify="left",
        )

        self.download_path_choose_button = ctk.CTkButton(
            master=self,
            text="📂",  # 📁, 📂, 🗂️
            hover=False,
            command=self.select_download_path,
        )

        # ---------------------------------------------------------------------------
        self.create_sep_path_for_videos_audios_label = ctk.CTkLabel(
            master=self,
        )

        self.dash2_label = ctk.CTkLabel(
            master=self,
            text=":",
        )
        self.create_sep_path_for_videos_audios_switch_state = ctk.BooleanVar(value=None)
        self.create_sep_path_for_videos_audios_switch = ctk.CTkSwitch(
            master=self,
            text="",
            command=self.change_create_sep_path_for_audios_videos,
            onvalue=True,
            offvalue=False,
            variable=self.create_sep_path_for_videos_audios_switch_state,
        )
        self.create_sep_path_for_videos_audios_info_label = ctk.CTkLabel(master=self)

        # ---------------------------------------------------------------------------
        self.create_sep_path_for_qualities_label = ctk.CTkLabel(
            master=self,
        )

        self.dash3_label = ctk.CTkLabel(
            master=self,
            text=":",
        )
        self.create_sep_path_for_qualities_switch_state = ctk.BooleanVar(value=None)
        self.create_sep_path_for_qualities_switch = ctk.CTkSwitch(
            master=self,
            text="",
            command=self.change_create_sep_path_for_qualities,
            onvalue=True,
            offvalue=False,
            variable=self.create_sep_path_for_qualities_switch_state,
        )
        self.create_sep_path_for_qualities_info_label = ctk.CTkLabel(
            master=self,
            text="",
        )

        # ---------------------------------------------------------------------------
        self.create_sep_path_for_playlists_label = ctk.CTkLabel(
            master=self,
            text="Playlist-Specific Directories",
        )
        self.dash4_label = ctk.CTkLabel(
            master=self,
            text=":",
        )

        self.create_sep_path_for_playlists_switch_state = ctk.BooleanVar(value=None)
        self.create_sep_path_for_playlists_switch = ctk.CTkSwitch(
            master=self,
            text="",
            command=self.change_create_sep_path_for_playlists,
            onvalue=True,
            offvalue=False,
            variable=self.create_sep_path_for_playlists_switch_state,
        )
        self.create_sep_path_for_playlists_info_label = ctk.CTkLabel(
            master=self,
            justify="left",
        )

        # ---------------------------------------------------------------------------

        # -------------------------------------------------------------
        self.chunk_size_label = ctk.CTkLabel(
            master=self,
            text="Chunk Size",
        )

        self.dash5_label = ctk.CTkLabel(
            master=self,
            text=":",
        )

        self.chunk_size_change_slider = ctk.CTkSlider(
            master=self,
            command=self.change_chunk_size,
            from_=51200,  # 50KB
            to=11534336,
        )

        self.chunk_size_value_entry = ctk.CTkEntry(
            master=self,
        )

        # -------------------------------------------------------------

        self.apply_changes_button = ctk.CTkButton(
            master=self,
            state="disabled",
            command=self.apply_downloads_settings,
        )

        self.settings_reset_button = ctk.CTkButton(master=self, command=self.reset_settings)

        self.restart_callback = restart_callback

        self.download_path_changed: bool = False
        self.create_sep_path_for_qualities_state_changed: bool = False
        self.create_sep_path_for_videos_audios_state_changed: bool = False
        self.create_sep_path_for_playlists_state_changed: bool = False
        self.chunk_size_changed: bool = False

        # track values validity
        self.download_path_valid: bool = True
        self.chunk_size_valid: bool = True

        self.chunk_size_entry_previous_value: str = ""

        self.general_settings_change_callback = general_settings_change_callback
        self.configure_values()
        self.set_widgets_accent_color()
        self.set_widgets_colors()
        self.set_widgets_texts()
        self.set_widgets_sizes()
        self.set_widgets_fonts()
        self.place_widgets()
        self.bind_widgets_events()

        ThemeManager.register_widget(self)
        LanguageManager.register_widget(self)

    def reset_settings(self):
        self.download_path_entry.delete(0, "end")
        self.download_path_entry.insert("end", GeneralSettings.get_default_download_dir())

        self.create_sep_path_for_videos_audios_switch.deselect()
        self.create_sep_path_for_qualities_switch.deselect()
        self.create_sep_path_for_playlists_switch.deselect()

        self.change_chunk_size(DownloadManager.default_chunk_size)
        self.chunk_size_change_slider.set(DownloadManager.default_chunk_size)

        self.apply_downloads_settings()

    def apply_downloads_settings(self):
        if self.chunk_size_changed:
            self.ask_to_restart()
        else:
            self.set_downloads_settings()

    def set_value_to_entry(self, entry: ctk.CTkEntry, value: str) -> None:
        entry.delete(0, "end")
        entry.insert(0, value)

    def cancel_chunk_size_settings_resetting(self):
        self.chunk_size_change_slider.set(GeneralSettings.settings["chunk_size"])
        self.set_value_to_entry(
            self.chunk_size_value_entry,
            f"{ValueConvertUtility.convert_size(GeneralSettings.settings['chunk_size'], decimal_points=3)}",
        )
        self.chunk_size_changed = False

    def set_downloads_settings(self):
        GeneralSettings.settings["download_directory"] = FileUtility.format_path(self.download_path_entry.get())
        GeneralSettings.settings["create_sep_path_for_qualities"] = self.create_sep_path_for_qualities_switch.get()
        GeneralSettings.settings["create_sep_path_for_videos_audios"] = (
            self.create_sep_path_for_videos_audios_switch.get()
        )
        GeneralSettings.settings["create_sep_path_for_playlists"] = self.create_sep_path_for_playlists_switch.get()
        GeneralSettings.settings["chunk_size"] = int(self.chunk_size_change_slider.get())
        self.general_settings_change_callback()
        self.apply_changes_button.configure(state="disabled")
        if self.chunk_size_changed:
            self.restart_callback()

    def ask_to_restart(self):
        from widgets import AlertWindow

        scale = AppearanceSettings.get_scale("decimal")
        AlertWindow(
            master=self.master.master,
            original_configure_callback=self.master.master.run_geometry_changes_tracker,
            alert_msg="restart_confirmation",
            width=int(450 * scale),
            height=int(130 * scale),
            ok_button_display=True,
            cancel_button_display=True,
            ok_button_callback=self.set_downloads_settings,
            cancel_button_callback=self.cancel_chunk_size_settings_resetting,
        )

    def set_apply_button_state(self):
        if any(
            (
                self.download_path_changed,
                self.create_sep_path_for_videos_audios_state_changed,
                self.create_sep_path_for_playlists_state_changed,
                self.create_sep_path_for_qualities_state_changed,
                self.chunk_size_changed,
            )
        ) and all((self.download_path_valid, self.chunk_size_valid)):
            self.apply_changes_button.configure(state="normal")
        else:
            self.apply_changes_button.configure(state="disabled")

    def change_chunk_size(self, chunk_size: int | float) -> None:
        self.chunk_size_valid = True
        self.set_value_to_entry(
            self.chunk_size_value_entry, f"{ValueConvertUtility.convert_size(chunk_size, decimal_points=3)}"
        )
        if chunk_size != GeneralSettings.settings["chunk_size"]:
            self.chunk_size_changed = True
        else:
            self.chunk_size_changed = False
        self.set_apply_button_state()

    def validate_chunk_size_value(self, _event):
        if self.chunk_size_entry_previous_value == self.chunk_size_value_entry.get():
            return

        self.chunk_size_entry_previous_value = self.chunk_size_value_entry.get()
        text = self.chunk_size_value_entry.get()
        value = text.strip().replace(" ", "")
        if SettingsValidateUtility.validate_chunk_size_value(value):
            self.chunk_size_valid = True
            value = ValueConvertUtility.MB_KB_to_Bytes(value)
            self.chunk_size_change_slider.set(value)
            self.change_chunk_size(value)
        else:
            self.chunk_size_valid = False
            self.set_apply_button_state()

    def download_path_validate(self, _event):
        path = FileUtility.format_path(self.download_path_entry.get())
        if path != GeneralSettings.settings["download_directory"]:
            self.download_path_changed = True
            if SettingsValidateUtility.validate_download_path(path):
                self.download_path_valid = True
            else:
                self.download_path_valid = False
        else:
            self.download_path_changed = False
        self.set_apply_button_state()

    def select_download_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path_entry.delete(0, "end")
            self.download_path_entry.insert(0, directory)
            self.download_path_validate("event")
        else:
            self.download_path_valid = False
        self.set_apply_button_state()

    def change_create_sep_path_for_audios_videos(self):
        if (
            GeneralSettings.settings["create_sep_path_for_videos_audios"]
            != self.create_sep_path_for_videos_audios_switch.get()
        ):
            self.create_sep_path_for_videos_audios_state_changed = True
        else:
            self.create_sep_path_for_videos_audios_state_changed = False
        self.set_apply_button_state()

    def change_create_sep_path_for_playlists(self):
        if GeneralSettings.settings["create_sep_path_for_playlists"] != self.create_sep_path_for_playlists_switch.get():
            self.create_sep_path_for_playlists_state_changed = True
        else:
            self.create_sep_path_for_playlists_state_changed = False
        self.set_apply_button_state()

    def change_create_sep_path_for_qualities(self):
        if GeneralSettings.settings["create_sep_path_for_qualities"] != self.create_sep_path_for_qualities_switch.get():
            self.create_sep_path_for_qualities_state_changed = True
        else:
            self.create_sep_path_for_qualities_state_changed = False
        self.set_apply_button_state()

    def configure_values(self):
        self.download_path_entry.insert(0, GeneralSettings.settings["download_directory"])

        if GeneralSettings.settings["create_sep_path_for_videos_audios"]:
            self.create_sep_path_for_videos_audios_switch.select()
            self.create_sep_path_for_videos_audios_switch_state.set(True)
        else:
            self.create_sep_path_for_videos_audios_switch_state.set(False)

        if GeneralSettings.settings["create_sep_path_for_qualities"]:
            self.create_sep_path_for_qualities_switch.select()
            self.create_sep_path_for_qualities_switch_state.set(True)
        else:
            self.create_sep_path_for_qualities_switch_state.set(False)

        if GeneralSettings.settings["create_sep_path_for_playlists"]:
            self.create_sep_path_for_playlists_switch.select()
            self.create_sep_path_for_playlists_switch_state.set(True)
        else:
            self.create_sep_path_for_playlists_switch_state.set(False)

        self.chunk_size_change_slider.set(GeneralSettings.settings["chunk_size"])
        self.set_value_to_entry(
            self.chunk_size_value_entry,
            f"{ValueConvertUtility.convert_size(GeneralSettings.settings['chunk_size'], decimal_points=3)}",
        )

    def bind_widgets_events(self):
        self.download_path_entry.bind("<KeyRelease>", self.download_path_validate)
        self.chunk_size_value_entry.bind("<KeyRelease>", self.validate_chunk_size_value)

        def on_mouse_enter_download_path_entry(event_):
            self.download_path_entry.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
            )

        def on_mouse_leave_download_path_entry(event_):
            self.download_path_entry.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
            )

        self.download_path_entry.bind("<Enter>", on_mouse_enter_download_path_entry)
        self.download_path_entry.bind("<Leave>", on_mouse_leave_download_path_entry)

        def on_mouse_enter_download_path_button(_event):
            self.download_path_choose_button.configure(text_color=ThemeManager.get_accent_color("hover"))

        def on_mouse_leave_download_path_button(_event):
            self.download_path_choose_button.configure(text_color=ThemeManager.get_accent_color("normal"))

        self.download_path_choose_button.bind("<Enter>", on_mouse_enter_download_path_button)
        self.download_path_choose_button.bind("<Leave>", on_mouse_leave_download_path_button)
        # ---------------------------------------------------------------------------

        def on_mouse_enter_create_sep_path_for_videos_audios_switch(event_):
            self.create_sep_path_for_videos_audios_switch.configure(
                button_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            )

        def on_mouse_leave_create_sep_path_for_videos_audios_switch(event_):
            self.create_sep_path_for_videos_audios_switch.configure(
                button_color=ThemeManager.get_color_based_on_theme("secondary"),
            )

        self.create_sep_path_for_videos_audios_switch.bind(
            "<Enter>", on_mouse_enter_create_sep_path_for_videos_audios_switch
        )
        self.create_sep_path_for_videos_audios_switch.bind(
            "<Leave>", on_mouse_leave_create_sep_path_for_videos_audios_switch
        )
        # ---------------------------------------------------------------------------

        def on_mouse_enter_create_sep_path_for_qualities_switch(event_):
            self.create_sep_path_for_qualities_switch.configure(
                button_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            )

        def on_mouse_leave_create_sep_path_for_qualities_switch(event_):
            self.create_sep_path_for_qualities_switch.configure(
                button_color=ThemeManager.get_color_based_on_theme("secondary"),
            )

        self.create_sep_path_for_qualities_switch.bind("<Enter>", on_mouse_enter_create_sep_path_for_qualities_switch)
        self.create_sep_path_for_qualities_switch.bind("<Leave>", on_mouse_leave_create_sep_path_for_qualities_switch)
        # ---------------------------------------------------------------------------

        def on_mouse_enter_create_sep_path_for_playlists_switch(event_):
            self.create_sep_path_for_playlists_switch.configure(
                button_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            )

        def on_mouse_leave_create_sep_path_for_playlists_switch(event_):
            self.create_sep_path_for_playlists_switch.configure(
                button_color=ThemeManager.get_color_based_on_theme("secondary"),
            )

        self.create_sep_path_for_playlists_switch.bind("<Enter>", on_mouse_enter_create_sep_path_for_playlists_switch)
        self.create_sep_path_for_playlists_switch.bind("<Leave>", on_mouse_leave_create_sep_path_for_playlists_switch)

    def set_widgets_colors(self):
        self.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))

        self.download_path_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.dash1_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.download_path_entry.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            border_color=ThemeManager.get_color_based_on_theme("border"),
        )
        self.download_path_choose_button.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background"),
        )

        self.create_sep_path_for_videos_audios_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal")
        )
        self.dash2_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.create_sep_path_for_videos_audios_switch.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            button_hover_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
        )
        self.create_sep_path_for_videos_audios_info_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )

        self.create_sep_path_for_qualities_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal")
        )
        self.dash3_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.create_sep_path_for_qualities_switch.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            button_hover_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
        )
        self.create_sep_path_for_qualities_info_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )

        self.create_sep_path_for_playlists_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal")
        )
        self.dash4_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.create_sep_path_for_playlists_switch.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            button_hover_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
        )
        self.create_sep_path_for_playlists_info_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_muted")
        )

        self.chunk_size_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.dash5_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.chunk_size_change_slider.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            button_hover_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
        )
        self.chunk_size_value_entry.configure(
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            border_color=ThemeManager.get_color_based_on_theme("border"),
        )

        self.apply_changes_button.configure(
            text_color=ThemeManager.get_color_based_on_theme("background"),
        )
        self.settings_reset_button.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background_warning"),
            hover_color=ThemeManager.get_color_based_on_theme("background_warning_hover"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
        )

    def update_widgets_colors(self):
        self.set_widgets_colors()

    def set_widgets_accent_color(self):
        self.download_path_choose_button.configure(text_color=ThemeManager.get_accent_color("normal"))
        self.create_sep_path_for_videos_audios_switch.configure(progress_color=ThemeManager.get_accent_color("normal"))
        self.create_sep_path_for_qualities_switch.configure(progress_color=ThemeManager.get_accent_color("normal"))
        self.create_sep_path_for_playlists_switch.configure(progress_color=ThemeManager.get_accent_color("normal"))
        self.chunk_size_change_slider.configure(
            progress_color=ThemeManager.get_accent_color("normal"),
        )

        self.apply_changes_button.configure(
            fg_color=ThemeManager.get_accent_color("normal"),
            hover_color=ThemeManager.get_accent_color("hover"),
        )

    def update_widgets_accent_color(self):
        self.set_widgets_accent_color()

    def place_widgets(self):
        scale = AppearanceSettings.get_scale("decimal")
        pady = 16 * scale

        self.download_path_label.grid(row=0, column=0, padx=(100, 0), pady=(50, 0), sticky="w")
        self.dash1_label.grid(row=0, column=1, padx=(30, 30), pady=(50, 0), sticky="w")
        self.download_path_entry.grid(row=0, column=2, pady=(50, 0), sticky="w")
        self.download_path_choose_button.grid(row=0, column=2, pady=(43, 0), padx=(270 * scale, 0), sticky="w")

        self.create_sep_path_for_videos_audios_label.grid(row=1, column=0, padx=(100, 0), pady=(pady, 0), sticky="w")
        self.dash2_label.grid(row=1, column=1, padx=(30, 30), pady=(pady, 0), sticky="w")
        self.create_sep_path_for_videos_audios_switch.grid(row=1, column=2, padx=(0, 0), pady=(pady, 0), sticky="w")
        self.create_sep_path_for_videos_audios_info_label.grid(
            row=2, column=0, columnspan=4, padx=(100 + (20 * scale), 0), pady=(10, 0), sticky="w"
        )

        self.create_sep_path_for_qualities_label.grid(row=3, column=0, padx=(100, 0), pady=(pady, 0), sticky="w")
        self.dash3_label.grid(row=3, column=1, padx=(30, 30), pady=(pady, 0), sticky="w")
        self.create_sep_path_for_qualities_switch.grid(row=3, column=2, padx=(0, 0), pady=(pady, 0), sticky="w")
        self.create_sep_path_for_qualities_info_label.grid(
            row=4, column=0, columnspan=4, padx=(100 + (20 * scale), 0), pady=(10, 0), sticky="w"
        )

        self.create_sep_path_for_playlists_label.grid(row=5, column=0, padx=(100, 0), pady=(pady, 0), sticky="w")
        self.dash4_label.grid(row=5, column=1, padx=(30, 30), pady=(pady, 0), sticky="w")
        self.create_sep_path_for_playlists_switch.grid(row=5, column=2, padx=(0, 0), pady=(pady, 0), sticky="w")
        self.create_sep_path_for_playlists_info_label.grid(
            row=6, column=0, columnspan=4, padx=(100 + (20 * scale), 0), pady=(10, 0), sticky="w"
        )

        self.chunk_size_label.grid(row=7, column=0, padx=(100, 0), pady=(pady, 0), sticky="w")
        self.dash5_label.grid(row=7, column=1, padx=(30, 30), pady=(pady, 0), sticky="w")
        self.chunk_size_change_slider.grid(row=7, column=2, pady=(pady, 0), sticky="w")
        self.chunk_size_value_entry.grid(row=7, column=2, padx=(200 * scale, 0), pady=(pady, 0), sticky="w")

        self.apply_changes_button.grid(
            row=8, column=2, columnspan=2, pady=(pady, 0), padx=(20 + 200 * scale, 0), sticky="w"
        )

        self.settings_reset_button.grid(
            row=9, column=2, columnspan=2, pady=(pady + 20 * scale, 0), padx=(20 + 200 * scale, 0), sticky="w"
        )

    def set_widgets_sizes(self):
        scale = AppearanceSettings.get_scale("decimal")

        self.download_path_entry.configure(width=250 * scale, height=28 * scale)
        # have no fore ground width and height not important
        self.download_path_choose_button.configure(width=1 * scale, height=1 * scale)
        self.create_sep_path_for_videos_audios_switch.configure(switch_width=36 * scale, switch_height=18 * scale)
        self.create_sep_path_for_qualities_switch.configure(switch_width=36 * scale, switch_height=18 * scale)
        self.create_sep_path_for_playlists_switch.configure(switch_width=36 * scale, switch_height=18 * scale)
        self.chunk_size_change_slider.configure(width=180 * scale, height=18 * scale)
        self.chunk_size_value_entry.configure(width=80 * scale, height=24 * scale)

        self.apply_changes_button.configure(width=80 * scale, height=24 * scale)
        self.settings_reset_button.configure(width=80 * scale, height=24 * scale)

    def set_widgets_texts(self):
        self.download_path_label.configure(text=LanguageManager.data["download_path"])
        self.create_sep_path_for_videos_audios_label.configure(
            text=LanguageManager.data["separate_folders_for_audio_&_video"]
        )
        self.create_sep_path_for_videos_audios_info_label.configure(
            text=LanguageManager.data["separate_folders_for_audio_&_video_info"]
        )
        self.create_sep_path_for_qualities_label.configure(
            text=LanguageManager.data["quality-based_folder_organization"]
        )
        self.create_sep_path_for_qualities_info_label.configure(
            text=LanguageManager.data["quality-based_folder_organization_info"]
        )
        self.create_sep_path_for_playlists_label.configure(text=LanguageManager.data["playlist-specific_directories"])
        self.create_sep_path_for_playlists_info_label.configure(
            text=LanguageManager.data["playlist-specific_directories_info"]
        )
        self.chunk_size_label.configure(text=LanguageManager.data["chunk_size"])
        self.apply_changes_button.configure(text=LanguageManager.data["apply"])
        self.settings_reset_button.configure(text=LanguageManager.data["reset"])

    def update_widgets_text(self):
        self.set_widgets_texts()

    def set_widgets_fonts(self):
        scale = AppearanceSettings.get_scale("decimal")

        title_font = ("Segoe UI", 13 * scale, "bold")
        self.download_path_label.configure(font=title_font)
        self.dash1_label.configure(font=title_font)
        self.create_sep_path_for_videos_audios_label.configure(font=title_font)
        self.dash2_label.configure(font=title_font)
        self.create_sep_path_for_qualities_label.configure(font=title_font)
        self.dash3_label.configure(font=title_font)
        self.create_sep_path_for_playlists_label.configure(font=title_font)
        self.dash4_label.configure(font=title_font)
        self.chunk_size_label.configure(font=title_font)
        self.dash5_label.configure(font=title_font)

        value_font = ("Segoe UI", 13 * scale, "normal")
        self.download_path_entry.configure(font=value_font)
        self.create_sep_path_for_videos_audios_info_label.configure(font=value_font)
        self.create_sep_path_for_qualities_info_label.configure(font=value_font)
        self.create_sep_path_for_playlists_info_label.configure(font=value_font)
        self.chunk_size_value_entry.configure(font=value_font)

        button_font2 = ("Segoe UI", 30 * scale, "bold")
        self.download_path_choose_button.configure(font=button_font2)

        button_font = ("Segoe UI", 11 * scale, "bold")
        self.apply_changes_button.configure(font=button_font)
        self.settings_reset_button.configure(font=button_font)

