from collections.abc import Callable
from typing import Any, Literal

import customtkinter as ctk

from services import LanguageManager, ThemeManager
from settings import AppearanceSettings
from utils import JsonUtility, SettingsValidateUtility
from widgets.components.accent_color_button import AccentColorButton


class AppearancePanel(ctk.CTkFrame):
    def __init__(
        self, master: Any = None, theme_settings_change_callback: Callable = None, restart_callback: Callable = None
    ):

        super().__init__(
            master=master,
        )

        self.theme_label = ctk.CTkLabel(
            master=self,
        )
        self.dash1_label = ctk.CTkLabel(
            master=self,
            text=":",
        )

        self.theme_data = JsonUtility.read_from_file("data\\themes.json")
        self.theme_names = [language_name for language_name in self.theme_data.keys()]
        self.theme_combo_box = ctk.CTkComboBox(
            master=self,
            values=self.theme_names,
            command=self.apply_theme_mode,
            width=140 * AppearanceSettings.get_scale("decimal"),
            height=28 * AppearanceSettings.get_scale("decimal"),
        )

        """
        self.system_theme_check_box = ctk.CTkCheckBox(
            master=self,
            command=self.sync_theme_with_os,
        )
        """

        self.accent_color_label = ctk.CTkLabel(
            master=self,
        )
        self.dash2_label = ctk.CTkLabel(
            master=self,
            text=":",
        )
        self.accent_color_frame = ctk.CTkFrame(
            master=self,
        )

        # add accent  color buttons
        self.accent_color_buttons: list[AccentColorButton] = []
        for accent_color in AppearanceSettings.settings["accent"]["colors"]:
            button = AccentColorButton(
                master=self.accent_color_frame,
                text="",
                fg_color=accent_color[0],
                hover_color=accent_color[1],
                size_change=4,
                corner_radius=8,
            )
            button.configure(command=lambda btn=button: self.apply_accent_color(btn))
            self.accent_color_buttons.append(button)

        # add user custom accent color
        self.custom_accent_color_label = ctk.CTkLabel(
            master=self,
        )

        self.dash3_label = ctk.CTkLabel(
            master=self,
            text=":",
        )

        self.custom_accent_color_entry = ctk.CTkEntry(
            master=self,
        )

        self.custom_accent_color_display_btn = ctk.CTkButton(
            master=self,
            text="",
        )

        self.custom_accent_color_apply_btn = ctk.CTkButton(
            master=self, state="disabled", command=self.apply_custom_accent_color
        )

        self.custom_accent_color_alert_text = ctk.CTkTextbox(
            master=self,
            activate_scrollbars=False,
        )

        self.scale_label = ctk.CTkLabel(
            master=self,
        )

        self.dash4_label = ctk.CTkLabel(
            master=self,
            text=":",
        )

        self.scale_change_slider = ctk.CTkSlider(
            master=self,
            command=self.change_scale,
            number_of_steps=100,
            from_=100,
            to=200,
        )

        self.scale_apply_btn = ctk.CTkButton(master=self, state="disabled", command=self.ask_to_restart)

        self.scale_value_entry = ctk.CTkEntry(
            master=self,
        )

        self.opacity_label = ctk.CTkLabel(
            master=self,
        )

        self.dash5_label = ctk.CTkLabel(
            master=self,
            text=":",
        )

        self.opacity_change_slider = ctk.CTkSlider(
            master=self,
            command=self.apply_opacity,
            from_=60,
            number_of_steps=320,
            to=100,
        )

        self.opacity_value_entry = ctk.CTkEntry(
            master=self,
        )

        self.settings_reset_button = ctk.CTkButton(master=self, command=self.reset_settings)

        # callbacks for settings changes
        self.restart_callback = restart_callback
        self.theme_settings_change_callback = theme_settings_change_callback

        self.scale_entry_previous_value: str = ""
        self.opacity_entry_previous_value: str = ""

        self.set_widgets_fonts()
        self.set_widgets_texts()
        self.set_widgets_sizes()
        self.set_widgets_colors()
        self.set_widgets_accent_color()
        self.place_widgets()
        self.bind_widgets_events()
        self.set_widgets_values()

        # Register widget with ThemeManager
        ThemeManager.register_widget(self)
        LanguageManager.register_widget(self)

    def set_value_to_entry(self, entry: ctk.CTkEntry, value: str) -> None:
        entry.delete(0, "end")
        entry.insert(0, value)

    def cancel_scale_settings_resetting(self):
        self.scale_change_slider.set(AppearanceSettings.get_scale("perentage"))
        self.set_value_to_entry(self.scale_value_entry, f"{AppearanceSettings.get_scale('perentage')} %")

    def reset_settings(self):
        self.apply_theme_mode("Dark Default")
        self.theme_combo_box.set("Dark Default")

        if not self.accent_color_buttons[0].pressed:
            self.accent_color_buttons[0].on_mouse_enter_self("event")
            self.apply_accent_color(self.accent_color_buttons[0])

        self.scale_change_slider.set(100)
        self.apply_opacity(100)

        self.opacity_change_slider.set(100)
        self.set_value_to_entry(self.scale_value_entry, f"{100.0} %")

        if AppearanceSettings.get_scale("perentage") != 100:
            from widgets import AlertWindow

            scale = AppearanceSettings.get_scale("decimal")
            AlertWindow(
                master=self.master.master,
                original_configure_callback=self.master.master.run_geometry_changes_tracker,
                alert_msg="scale_settings_reset_confirmation",
                more_details="This changes happen in low level",
                width=int(450 * scale),
                height=int(130 * scale),
                ok_button_display=True,
                cancel_button_display=True,
                ok_button_callback=self.apply_scale,
                cancel_button_callback=self.cancel_scale_settings_resetting,
            )

    def release_all_accent_color_buttons(self):
        """
        Release all pressed accent color buttons.
        """
        for accent_button in self.accent_color_buttons:
            if accent_button.pressed:
                accent_button.set_unpressed()

    def apply_accent_color(self, button: AccentColorButton):
        """
        Apply selected accent color.
        """
        AppearanceSettings.settings["accent"]["selected"]["color"] = [button.fg_color, button.hover_color]
        AppearanceSettings.settings["accent"]["selected"]["is_custom"] = False

        self.theme_settings_change_callback("accent_color")
        self.release_all_accent_color_buttons()
        button.set_pressed()
        self.validate_custom_accent_color("event")

    def apply_custom_accent_color(self):
        """
        Apply custom accent color.
        """
        colors = self.custom_accent_color_entry.get().strip().replace(" ", "").split(",")
        AppearanceSettings.settings["accent"]["selected"]["color"] = [colors[0], colors[1]]
        AppearanceSettings.settings["accent"]["selected"]["is_custom"] = True
        self.release_all_accent_color_buttons()
        self.theme_settings_change_callback("accent_color")
        self.custom_accent_color_apply_btn.configure(state="disabled")

    def apply_theme_mode(self, theme: Literal["Dark", "Light", None]):
        """
        Apply selected theme mode. Dark / Light
        """
        theme_name = self.theme_data[theme]
        if theme_name != AppearanceSettings.settings["theme"]["name"]:
            AppearanceSettings.settings["theme"]["name"] = theme_name
            AppearanceSettings.settings["theme"]["display_name"] = theme
            self.theme_settings_change_callback(updated="theme")

    """
    def sync_theme_with_os(self):
        Synchronize theme with the OS.
        self.system_theme_check_box.configure(command=self.disable_sync_theme_with_os)
        self.theme_combo_box.configure(state="disabled")
        AppearanceSettings.settings["root"]["theme_mode"] = 2
        self.theme_settings_change_callback("theme_mode")
    """

    def disable_sync_theme_with_os(self):
        """
        Disable synchronization with the OS.
        """

        # self.system_theme_check_box.configure(command=self.sync_theme_with_os)

        self.theme_combo_box.configure(state="normal")
        AppearanceSettings.settings["root"]["theme_mode"] = AppearanceSettings.themes.index(
            ctk.get_appearance_mode().lower()
        )
        self.theme_settings_change_callback("theme_mode")

    def apply_opacity(self, opacity_value: float):
        """
        Apply selected opacity value.
        """
        self.set_value_to_entry(self.opacity_value_entry, f"{opacity_value} %")
        AppearanceSettings.settings["window"]["opacity"]["percentage"] = opacity_value
        AppearanceSettings.settings["window"]["opacity"]["decimal"] = opacity_value / 100
        # print(AppearanceSettings.settings)
        self.theme_settings_change_callback("opacity")

    def change_scale(self, scale_value: int):
        """
        Change the scale value.
        """
        self.set_value_to_entry(self.scale_value_entry, f"{scale_value} %")
        if scale_value != AppearanceSettings.get_scale("percentage"):
            self.scale_apply_btn.configure(state="normal")
        else:
            self.scale_apply_btn.configure(state="disabled")

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
            ok_button_callback=self.apply_scale,
        )

    def apply_scale(self):
        scale_value = self.scale_change_slider.get()
        AppearanceSettings.set_scale("percentage", scale_value)
        AppearanceSettings.set_scale("decimal", scale_value / 100)
        self.theme_settings_change_callback()
        self.restart_callback()

    def validate_custom_accent_color(self, _event):
        """
        Validate custom accent color entry.
        """
        text = self.custom_accent_color_entry.get()
        colors = text.strip().replace(" ", "")
        if SettingsValidateUtility.validate_accent_color(colors):
            fg_color = colors.split(",")[0]
            hover_color = colors.split(",")[1]
            self.custom_accent_color_display_btn.configure(fg_color=fg_color, hover_color=hover_color)
            self.custom_accent_color_entry.delete(0, "end")
            self.custom_accent_color_entry.insert("end", f"{fg_color}, {hover_color}")
            self.custom_accent_color_apply_btn.configure(state="normal")
        else:
            self.custom_accent_color_display_btn.configure(
                fg_color=ThemeManager.get_color_based_on_theme("background"),
                hover_color=ThemeManager.get_color_based_on_theme("background"),
            )
            self.custom_accent_color_apply_btn.configure(state="disabled")

    def validate_scale_value(self, _event):
        """
        Validate scale value
        """
        if self.scale_entry_previous_value == self.scale_value_entry.get():
            return

        self.scale_entry_previous_value = self.scale_value_entry.get()
        text = self.scale_value_entry.get()
        value = text.strip().replace(" ", "")
        if SettingsValidateUtility.validate_scale_value(value):
            value = value[0:-1]
            value = float(int(float(value)))
            self.scale_change_slider.set(value)
            self.change_scale(value)

    def validate_opacity_value(self, _event):
        """
        Validate opacity value
        """
        if self.opacity_entry_previous_value == self.opacity_value_entry.get():
            return

        self.opacity_entry_previous_value = self.opacity_value_entry.get()
        text = self.opacity_value_entry.get()
        value = text.strip().replace(" ", "")
        if SettingsValidateUtility.validate_opacity_value(value):
            value = value[0:-1]
            value = float(value)
            self.opacity_change_slider.set(value)
            self.apply_opacity(value)

    def set_widgets_colors(self):
        """
        Set colors for the widgets.
        """
        self.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))

        self.theme_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.dash1_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.theme_combo_box.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            border_color=ThemeManager.get_color_based_on_theme("border"),
            dropdown_fg_color=ThemeManager.get_color_based_on_theme("primary"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            dropdown_text_color=ThemeManager.get_color_based_on_theme("text_muted"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
        )

        """
        self.system_theme_check_box.configure(
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            border_color=ThemeManager.get_color_based_on_theme("border")
        )
        """

        self.accent_color_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.dash2_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.accent_color_frame.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))

        self.custom_accent_color_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.dash3_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.custom_accent_color_entry.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            border_color=ThemeManager.get_color_based_on_theme("border"),
        )
        self.custom_accent_color_display_btn.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background"),
        )
        self.custom_accent_color_apply_btn.configure(
            text_color=ThemeManager.get_color_based_on_theme("background"),
        )
        self.custom_accent_color_alert_text.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background"),
            text_color=ThemeManager.get_color_based_on_theme("text_warning"),
        )

        self.scale_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.dash4_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.scale_change_slider.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            button_hover_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
        )
        self.scale_value_entry.configure(
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            border_color=ThemeManager.get_color_based_on_theme("border"),
        )
        self.scale_apply_btn.configure(
            text_color=ThemeManager.get_color_based_on_theme("background"),
        )

        self.opacity_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.dash5_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        self.opacity_change_slider.configure(
            button_color=ThemeManager.get_color_based_on_theme("secondary"),
            button_hover_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
        )
        self.opacity_value_entry.configure(
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            border_color=ThemeManager.get_color_based_on_theme("border"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
        )

        self.settings_reset_button.configure(
            fg_color=ThemeManager.get_color_based_on_theme("background_warning"),
            hover_color=ThemeManager.get_color_based_on_theme("background_warning_hover"),
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
        )

    def update_widgets_colors(self):
        """Update colors for the widgets."""
        self.set_widgets_colors()

    def set_widgets_accent_color(self):
        """
        Update accent color.
        """
        self.theme_combo_box.configure(dropdown_hover_color=ThemeManager.get_accent_color("hover"))
        self.custom_accent_color_apply_btn.configure(
            fg_color=ThemeManager.get_accent_color("normal"),
            hover_color=ThemeManager.get_accent_color("hover"),
        )

        """
        self.system_theme_check_box.configure(
            checkmark_color=ThemeManager.get_accent_color("normal")
        )
        """

        self.scale_change_slider.configure(
            progress_color=ThemeManager.get_accent_color("normal"),
        )
        self.scale_apply_btn.configure(
            fg_color=ThemeManager.get_accent_color("normal"),
            hover_color=ThemeManager.get_accent_color("hover"),
        )

        self.opacity_change_slider.configure(
            progress_color=ThemeManager.get_accent_color("normal"),
        )

    def update_widgets_accent_color(self):
        """
        Update accent color.
        """
        self.set_widgets_accent_color()

    def place_widgets(self):
        """
        Place widgets on the frame.
        """
        scale = AppearanceSettings.get_scale("decimal")
        pady = 16 * scale
        self.theme_label.grid(row=0, column=0, padx=(100, 0), pady=(50, 0), sticky="w")
        self.dash1_label.grid(row=0, column=1, padx=(30, 30), pady=(50, 0), sticky="w")
        self.theme_combo_box.grid(row=0, column=2, pady=(50, 0), sticky="w")
        # self.system_theme_check_box.grid(row=0, column=3, padx=(20, 0), pady=(50, 0), sticky="w")

        self.accent_color_label.grid(row=1, column=0, padx=(100, 0), pady=(pady, 0), sticky="nw")
        self.dash2_label.grid(row=1, column=1, padx=(30, 30), pady=(pady, 0), sticky="nw")
        self.accent_color_frame.grid(row=1, column=2, pady=(pady, 0), sticky="w")

        # place accent color buttons
        max_columns = 3
        row = 0
        column = 0
        for button in self.accent_color_buttons:
            button.grid(row=row, column=column, padx=6, pady=6)
            column += 1
            if column > max_columns:
                column = 0
                row += 1
            button.bind_event()

        self.custom_accent_color_label.grid(row=2, column=0, padx=(100, 0), pady=(pady, 0), sticky="w")
        self.dash3_label.grid(row=2, column=1, padx=(30, 30), pady=(pady, 0), sticky="w")
        self.custom_accent_color_entry.grid(row=2, column=2, pady=(pady, 0), sticky="w")
        self.custom_accent_color_display_btn.grid(row=2, column=3, padx=(20, 0), pady=(pady, 0), sticky="w")
        self.custom_accent_color_apply_btn.grid(row=2, column=3, padx=(100 * scale, 0), pady=(pady, 0), sticky="w")
        self.custom_accent_color_alert_text.grid(row=3, column=0, columnspan=9, padx=(100, 0), pady=(10, 0), sticky="w")

        self.scale_label.grid(row=4, column=0, padx=(100, 0), pady=(pady, 0), sticky="w")
        self.dash4_label.grid(row=4, column=1, padx=(30, 30), pady=(pady, 0), sticky="w")
        self.scale_change_slider.grid(row=4, column=2, pady=(pady, 0), sticky="w")
        self.scale_value_entry.grid(row=4, column=3, padx=(20, 0), pady=(pady, 0), sticky="w")
        self.scale_apply_btn.grid(row=4, column=3, padx=(100 * scale, 0), pady=(pady, 0), sticky="w")

        self.opacity_label.grid(row=5, column=0, padx=(100, 0), pady=(pady, 0), sticky="w")
        self.dash5_label.grid(row=5, column=1, padx=(30, 30), pady=(pady, 0), sticky="w")
        self.opacity_change_slider.grid(row=5, column=2, pady=(pady, 0), sticky="sw")
        self.opacity_value_entry.grid(row=5, column=3, padx=(20, 0), pady=(pady, 0), sticky="w")

        self.settings_reset_button.grid(row=5, column=3, pady=(pady, 0), padx=(100 * scale, 0), sticky="w")

    def set_widgets_sizes(self):
        scale = AppearanceSettings.get_scale("decimal")
        self.theme_combo_box.configure(width=140 * scale, height=28 * scale)
        # self.system_theme_check_box.configure(checkbox_width=24 * scale, checkbox_height=24 * scale)

        for accent_color_button in self.accent_color_buttons:
            accent_color_button.configure(width=30 * scale, height=30 * scale, corner_radius=6 * scale)
        self.custom_accent_color_display_btn.configure(width=30 * scale, height=30 * scale, corner_radius=6 * scale)
        self.custom_accent_color_entry.configure(width=140 * scale, height=28 * scale)
        self.custom_accent_color_apply_btn.configure(width=80 * scale, height=24 * scale)
        self.custom_accent_color_alert_text.configure(width=590 * scale, height=85 * scale)

        self.scale_change_slider.configure(width=180 * scale, height=18 * scale)
        self.scale_value_entry.configure(width=70 * scale, height=24 * scale)
        self.scale_apply_btn.configure(width=80 * scale, height=24 * scale)
        self.opacity_change_slider.configure(width=180 * scale, height=18 * scale)
        self.opacity_value_entry.configure(width=70 * scale, height=24 * scale)

        self.settings_reset_button.configure(width=80 * scale, height=24 * scale)

    def set_widgets_texts(self):
        self.theme_label.configure(text=LanguageManager.data["theme"])

        self.theme_combo_box.configure(values=self.theme_names)

        self.theme_combo_box.set(AppearanceSettings.settings["theme"]["display_name"])

        # self.system_theme_check_box.configure(text=LanguageManager.data["sync_with_os"])
        self.accent_color_label.configure(text=LanguageManager.data["accent_color"])
        self.custom_accent_color_label.configure(text=LanguageManager.data["custom_accent_color"])
        self.custom_accent_color_apply_btn.configure(text=LanguageManager.data["apply"])
        self.custom_accent_color_alert_text.delete(1.0, "end")
        self.custom_accent_color_alert_text.insert("end", LanguageManager.data["custom_accent_color_alert_text"])
        self.scale_label.configure(text=LanguageManager.data["scale"])
        self.scale_apply_btn.configure(text=LanguageManager.data["apply"])
        self.opacity_label.configure(text=LanguageManager.data["transparent"])
        self.settings_reset_button.configure(text=LanguageManager.data["reset"])

    def update_widgets_text(self):
        self.set_widgets_texts()

    def set_widgets_fonts(self):
        # Segoe UI, Open Sans
        scale = AppearanceSettings.get_scale("decimal")
        title_font = ("Segoe UI", 13 * scale, "bold")
        self.theme_label.configure(font=title_font)
        self.dash1_label.configure(font=title_font)
        self.accent_color_label.configure(font=title_font)
        self.dash2_label.configure(font=title_font)
        self.custom_accent_color_label.configure(font=title_font)
        self.dash3_label.configure(font=title_font)
        self.scale_label.configure(font=title_font)
        self.dash4_label.configure(font=title_font)
        self.opacity_label.configure(font=title_font)
        self.dash5_label.configure(font=title_font)

        value_font = ("Segoe UI", 13 * scale, "normal")
        self.theme_combo_box.configure(font=value_font, dropdown_font=value_font)
        # self.system_theme_check_box.configure(font=value_font)
        self.custom_accent_color_entry.configure(font=value_font)
        self.custom_accent_color_alert_text.configure(font=value_font)
        self.scale_value_entry.configure(font=value_font)
        self.opacity_value_entry.configure(font=value_font)

        button_font = ("Segoe UI", 11 * scale, "bold")
        self.custom_accent_color_apply_btn.configure(font=button_font)
        self.scale_apply_btn.configure(font=button_font)
        self.settings_reset_button.configure(font=button_font)

    # set default values to widgets
    def set_widgets_values(self):
        """
        set values for widgets using saved settings.
        """
        self.custom_accent_color_alert_text.bind("<Key>", lambda e: "break")
        if AppearanceSettings.settings["accent"]["selected"]["is_custom"] == False:
            for button in self.accent_color_buttons:
                if (
                    button.fg_color == AppearanceSettings.settings["accent"]["selected"]["color"][0]
                    and button.hover_color == AppearanceSettings.settings["accent"]["selected"]["color"][1]
                ):
                    button.on_mouse_enter_self("event")
                    button.set_pressed()
        else:
            # add default value to entry using data
            self.custom_accent_color_entry.insert(
                "end",
                AppearanceSettings.settings["accent"]["selected"]["color"][0]
                + ", "
                + AppearanceSettings.settings["accent"]["selected"]["color"][1],
            )
            self.validate_custom_accent_color("event")
            self.custom_accent_color_apply_btn.configure(state="disabled")

        self.theme_combo_box.set(AppearanceSettings.settings["theme"]["display_name"])

        self.opacity_change_slider.set(AppearanceSettings.get_opacity("percentage"))

        self.scale_change_slider.set(AppearanceSettings.get_scale("percentage"))
        self.scale_entry_previous_value = f"{AppearanceSettings.get_scale('percentage')} %"

        self.set_value_to_entry(self.scale_value_entry, f"{AppearanceSettings.get_scale('percentage')} %")
        self.set_value_to_entry(self.opacity_value_entry, f"{AppearanceSettings.get_opacity('percentage')} %")

    def bind_widgets_events(self):
        """
        Bind events to widgets.
        """
        self.custom_accent_color_entry.bind("<KeyRelease>", self.validate_custom_accent_color)
        self.scale_value_entry.bind("<KeyRelease>", self.validate_scale_value)
        self.opacity_value_entry.bind("<KeyRelease>", self.validate_opacity_value)
        self.validate_custom_accent_color("event")

        # Theme-based hover color functions
        def on_mouse_enter_theme_combo_box(event_):
            self.theme_combo_box.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
                button_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
            )

        def on_mouse_leave_theme_combo_box(event_):
            self.theme_combo_box.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
                button_color=ThemeManager.get_color_based_on_theme("secondary"),
            )

        self.theme_combo_box.bind("<Enter>", on_mouse_enter_theme_combo_box)
        self.theme_combo_box.bind("<Leave>", on_mouse_leave_theme_combo_box)

        """
        def on_mouse_enter_system_theme_check_box(event_):
            print("Enter Mouse")
            self.system_theme_check_box.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
            )
        def on_mouse_leave_system_theme_check_box(event_):
            print("Leave Mouse")
            self.system_theme_check_box.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
            )
        self.system_theme_check_box.bind("<Enter>", on_mouse_enter_system_theme_check_box)
        self.system_theme_check_box.bind("<Leave>", on_mouse_leave_system_theme_check_box)
        """

        def on_mouse_enter_custom_accent_color_entry(event_):
            self.custom_accent_color_entry.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
            )

        def on_mouse_leave_custom_accent_color_entry(event_):
            self.custom_accent_color_entry.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
            )

        self.custom_accent_color_entry.bind("<Enter>", on_mouse_enter_custom_accent_color_entry)
        self.custom_accent_color_entry.bind("<Leave>", on_mouse_leave_custom_accent_color_entry)

        def on_mouse_enter_scale_value_entry(event_):
            self.scale_value_entry.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
            )

        def on_mouse_leave_scale_value_entry(event_):
            self.scale_value_entry.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
            )

        self.scale_value_entry.bind("<Enter>", on_mouse_enter_scale_value_entry)
        self.scale_value_entry.bind("<Leave>", on_mouse_leave_scale_value_entry)

        def on_mouse_enter_opacity_value_entry(event_):
            self.opacity_value_entry.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary_hover"),
            )

        def on_mouse_leave_opacity_value_entry(event_):
            self.opacity_value_entry.configure(
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
            )

        self.opacity_value_entry.bind("<Enter>", on_mouse_enter_opacity_value_entry)
        self.opacity_value_entry.bind("<Leave>", on_mouse_leave_opacity_value_entry)
