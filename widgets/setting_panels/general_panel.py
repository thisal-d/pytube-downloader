from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from services import LanguageManager, ThemeManager
from settings import AppearanceSettings, GeneralSettings
from utils import JsonUtility


class GeneralPanel(ctk.CTkFrame):
    def __init__(self, master: Any = None, general_settings_change_callback: Callable = None):

        super().__init__(master=master)

        self.language_label = ctk.CTkLabel(
            master=self,
        )
        self.dash1_label = ctk.CTkLabel(
            master=self,
            text=":",
        )

        self.language_data = JsonUtility.read_from_file("data/languages.json")
        self.language_names = [language_name for language_name in self.language_data]
        self.languages_combo_box = ctk.CTkComboBox(
            master=self,
            values=self.language_names,
            command=self.apply_language,
            width=140 * AppearanceSettings.get_scale("decimal"),
            height=28 * AppearanceSettings.get_scale("decimal"),
        )

        self.shortcut_label = ctk.CTkLabel(
            master=self,
        )
        self.dash2_label = ctk.CTkLabel(
            master=self,
            text=":",
        )
        self.shortcut_frame = ctk.CTkScrollableFrame(
            master=self,
        )
        self.shortcut_keys_data = [
            {"desc": "toggle_settings", "key_strokes": [("Ctrl", ",")]},
            {"desc": "exit_settings", "key_strokes": [("Esc",)]},
            {"desc": "change_download_mode", "key_strokes": [("F6",), ("Ctrl", "d")]},
            {"desc": "add_video_/_playlist", "key_strokes": [("Enter",)]},
            {"desc": "toggle_fullscreen", "key_strokes": [("F11",), ("Alt", "Enter")]},
            {"desc": "minimize", "key_strokes": [("F9",), ("Ctrl", "n"), ("Ctrl", "↓")]},
            {"desc": "toggle_maximize", "key_strokes": [("F10",), ("Ctrl", "m"), ("Ctrl", "↑")]},
            {"desc": "quick_exit", "key_strokes": [("Ctrl", "q")]},
            {"desc": "force_exit", "key_strokes": [("Ctrl", "Alt", "q"), ("Ctrl", "Alt", "F4")]},
            {"desc": "minimize_to_tray", "key_strokes": [("F12",), ("Ctrl", "Shift", "m"), ("Ctrl", "Shift", "n")]},
        ]

        self.shortcut_keys_widgets_info = []
        for skd in self.shortcut_keys_data:
            shortcut_keys_widgets_info_dict = {
                "label": ctk.CTkLabel(
                    master=self.shortcut_frame,
                ),
                "dash": ctk.CTkLabel(master=self.shortcut_frame, text=":"),
                "key_frame": ctk.CTkFrame(master=self.shortcut_frame, fg_color="transparent"),
                "buttons": [],
            }
            for key_stroke in skd["key_strokes"]:
                shortcut_keys_widgets_info_dict["buttons"].append(
                    ctk.CTkButton(
                        master=shortcut_keys_widgets_info_dict["key_frame"],
                        fg_color="transparent",
                        border_width=1,
                        hover=False,
                        text=" + ".join(key_stroke),
                        corner_radius=8,
                    )
                )
            self.shortcut_keys_widgets_info.append(shortcut_keys_widgets_info_dict)

        self.alerts_state_label = ctk.CTkLabel(
            master=self,
        )

        self.dash3_label = ctk.CTkLabel(
            master=self,
            text=":",
        )

        self.alerts_state_switch_state = ctk.BooleanVar(value=None)
        self.alerts_state_change_switch = ctk.CTkSwitch(
            master=self,
            text="",
            command=self.change_alerts_state,
            onvalue=True,
            offvalue=False,
            variable=self.alerts_state_switch_state,
        )

        self.settings_reset_button = ctk.CTkButton(master=self, command=self.reset_settings)

        # callbacks for settings changes
        self.general_settings_change_callback = general_settings_change_callback

        self.set_widgets_fonts()
        self.set_widgets_texts()
        self.set_widgets_sizes()
        self.set_widgets_colors()
        self.set_widgets_accent_color()
        self.place_widgets()
        self.set_widgets_values()
        self.bind_widgets_events()

        # Register widget with ThemeManager
        ThemeManager.register_widget(self)
        LanguageManager.register_widget(self)

    def reset_settings(self):
        # Reset language to english and apply it
        self.languages_combo_box.set("English")
        self.alerts_state_change_switch.select()
        self.change_alerts_state()

        self.apply_language("English")

    def change_alerts_state(self):
        GeneralSettings.settings["alerts"] = self.alerts_state_switch_state.get()
        self.general_settings_change_callback()

    def apply_language(self, language: str) -> None:
        lang_code = self.language_data[language]
        if lang_code != GeneralSettings.settings["lang_code"]:
            GeneralSettings.settings["lang_code"] = lang_code
            GeneralSettings.settings["language"] = language
            self.general_settings_change_callback(updated="language")

    def set_widgets_accent_color(self):
        """
        Set accent color for widgets.
        """

        self.languages_combo_box.configure(dropdown_hover_color=ThemeManager.get_accent_color("hover"))

        self.alerts_state_change_switch.configure(
            progress_color=ThemeManager.get_accent_color("normal"),
        )

    def update_widgets_accent_color(self):
        """
        Update accent color.
        """
        self.set_widgets_accent_color()

    def set_widgets_colors(self):
        """
        Set colors for the widgets.
        """
        self.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))

        self.language_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.dash1_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.languages_combo_box.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            border_color=ThemeManager.get_color_based_on_theme("border"),
            dropdown_fg_color=ThemeManager.get_color_based_on_theme("primary"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            dropdown_text_color=ThemeManager.get_color_based_on_theme("text_muted"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
        )

        self.shortcut_frame.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))
        self.shortcut_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.dash2_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))

        for _key, value in enumerate(self.shortcut_keys_widgets_info):
            value["label"].configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
            value["dash"].configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
            for button in value["buttons"]:
                button.configure(
                    fg_color=ThemeManager.get_color_based_on_theme("primary"),
                    border_color=ThemeManager.get_color_based_on_theme("border"),
                    text_color=ThemeManager.get_color_based_on_theme("text_normal"),
                )

        self.settings_reset_button.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background_warning"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
        )

        self.alerts_state_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.alerts_state_change_switch.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            button_hover_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
        )

    def update_widgets_colors(self):
        """Update colors for the widgets."""
        self.set_widgets_colors()

    def place_widgets(self):
        """
        Place widgets on the frame.
        """
        scale = AppearanceSettings.get_scale("decimal")
        pady = 16 * scale

        self.language_label.grid(row=0, column=0, padx=(100, 0), pady=(50, 0), sticky="w")
        self.dash1_label.grid(row=0, column=1, padx=(30, 30), pady=(50, 0), sticky="w")
        self.languages_combo_box.grid(row=0, column=2, pady=(50, 0), sticky="w")

        self.shortcut_label.grid(row=1, column=0, padx=(100, 0), pady=(pady, 0), sticky="nw")
        self.dash2_label.grid(row=1, column=1, padx=(30, 30), pady=(pady, 0), sticky="nw")
        self.shortcut_frame.grid(row=1, column=2, pady=(2, 0), sticky="w")

        for i, shortcut_widget_info in enumerate(self.shortcut_keys_widgets_info):
            shortcut_widget_info["label"].grid(row=i, column=0, pady=(4 * scale, 0), sticky="e")
            shortcut_widget_info["dash"].grid(
                row=i, column=1, padx=(15 * scale, 15 * scale), pady=(4 * scale, 0), sticky="w"
            )
            shortcut_widget_info["key_frame"].grid(row=i, column=2, pady=(4 * scale, 0), sticky="w")
            for button in shortcut_widget_info["buttons"]:
                button.pack(side="left", padx=(2 * scale, 0))

        self.alerts_state_label.grid(row=2, column=0, padx=(100, 0), pady=(pady, 0), sticky="w")
        self.dash3_label.grid(row=2, column=1, padx=(30, 30), pady=(pady, 0), sticky="w")
        self.alerts_state_change_switch.grid(row=2, column=2, padx=(0, 0), pady=(pady, 0), sticky="w")

        self.settings_reset_button.grid(row=3, column=2, padx=(100, 0), pady=(pady, 0), sticky="s")

    def set_widgets_sizes(self):
        scale = AppearanceSettings.get_scale("decimal")
        self.languages_combo_box.configure(width=140 * scale, height=28 * scale)
        self.shortcut_frame.configure(width=450 * scale, height=252 * scale)
        self.shortcut_frame._scrollbar.grid_forget()

        for shortcut_widget_info in self.shortcut_keys_widgets_info:
            for button in shortcut_widget_info["buttons"]:
                button.configure(width=1, height=24 * scale)

        self.alerts_state_change_switch.configure(switch_width=36 * scale, switch_height=18 * scale)

        self.settings_reset_button.configure(width=80 * scale, height=24 * scale)

    def set_widgets_texts(self):
        self.language_label.configure(text=LanguageManager.data["language"])
        self.shortcut_label.configure(text=LanguageManager.data["shortcuts"])

        for i, shortcut_widget_info in enumerate(self.shortcut_keys_widgets_info):
            shortcut_widget_info["label"].configure(text=LanguageManager.data[self.shortcut_keys_data[i]["desc"]])

        self.settings_reset_button.configure(text=LanguageManager.data["reset"])

        self.alerts_state_label.configure(text=LanguageManager.data["alerts"])

    def update_widgets_text(self):
        self.set_widgets_texts()

    def set_widgets_fonts(self):
        # Segoe UI, Open Sans
        scale = AppearanceSettings.get_scale("decimal")
        title_font = ("Segoe UI", 13 * scale, "bold")
        self.language_label.configure(font=title_font)
        self.dash1_label.configure(font=title_font)
        self.shortcut_label.configure(font=title_font)
        self.dash2_label.configure(font=title_font)
        self.alerts_state_label.configure(font=title_font)

        value_font = ("Segoe UI", 13 * scale, "normal")
        self.languages_combo_box.configure(font=value_font, dropdown_font=value_font)

        value_font = ("Segoe UI", 11 * scale, "bold")
        for shortcut_widget_info in self.shortcut_keys_widgets_info:
            shortcut_widget_info["label"].configure(font=value_font)
            shortcut_widget_info["dash"].configure(font=value_font)

        value_font = ("Segoe UI", 11 * scale, "normal")
        for shortcut_widget_info in self.shortcut_keys_widgets_info:
            for button in shortcut_widget_info["buttons"]:
                button.configure(font=value_font)

        self.settings_reset_button.configure(font=("Segoe UI", 11 * scale, "bold"))

    # set default values to widgets
    def set_widgets_values(self):
        """
        set values for widgets using saved settings.
        """
        self.languages_combo_box.set(GeneralSettings.settings["language"])

        if GeneralSettings.settings["alerts"]:
            self.alerts_state_change_switch.select()
            self.alerts_state_switch_state.set(True)

    def bind_widgets_events(self):
        # ----------------------------------------------------------

        def on_mouse_enter_languages_combo_box(event_):
            self.languages_combo_box.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
                button_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            )

        def on_mouse_leave_languages_combo_box(event_):
            self.languages_combo_box.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
                button_color=ThemeManager.get_color_based_on_theme("secondary"),
            )

        self.languages_combo_box.bind("<Enter>", on_mouse_enter_languages_combo_box)
        self.languages_combo_box.bind("<Leave>", on_mouse_leave_languages_combo_box)

        # ----------------------------------------------------------

        def on_mouse_enter_reset_button(event_):
            self.settings_reset_button.configure(
                fg_color=ThemeManager.get_color_based_on_theme("background_warning_hover"),
            )

        def on_mouse_leave_reset_button(event_):
            self.settings_reset_button.configure(
                fg_color=ThemeManager.get_color_based_on_theme("background_warning"),
            )

        self.settings_reset_button.bind("<Enter>", on_mouse_enter_reset_button)
        self.settings_reset_button.bind("<Leave>", on_mouse_leave_reset_button)

        # ----------------------------------------------------------

        def on_mouse_enter_alerts_state_change_switch(event_):
            self.alerts_state_change_switch.configure(
                button_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            )

        def on_mouse_leave_alerts_state_change_switch(event_):
            self.alerts_state_change_switch.configure(
                button_color=ThemeManager.get_color_based_on_theme("secondary"),
            )

        self.alerts_state_change_switch.bind("<Enter>", on_mouse_enter_alerts_state_change_switch)
        self.alerts_state_change_switch.bind("<Leave>", on_mouse_leave_alerts_state_change_switch)
