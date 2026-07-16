from collections.abc import Callable

import customtkinter as ctk

from services import LanguageManager, ThemeManager
from settings import AppearanceSettings


class ContextMenu(ctk.CTkFrame):
    child_widgets: list["ContextMenu"] = []

    @staticmethod
    def close_all_menus():
        for child_widget in ContextMenu.child_widgets:
            if child_widget.is_open:
                child_widget.place_forget()

    def __init__(
        self,
        master=None,
        width: int = 70,
        height: int = 100,
        font: tuple[str, int, str] = ("Segoe UI", 10, "bold"),
        options_texts: list[str] = None,
        options_commands: list[Callable] = None,
    ):

        super().__init__(master=master, corner_radius=0)

        self.width = width
        self.height = height
        self.font = font
        self.options_texts = options_texts
        self.options_commands = options_commands
        self.option_buttons: list[ctk.CTkButton] = []

        self.create_widgets()
        self.set_widgets_accent_color()
        self.set_widgets_colors()
        self.set_widgets_fonts()
        self.set_widgets_texts()
        self.set_widgets_sizes()
        self.place_widgets()

        self.is_open = False

        ThemeManager.register_widget(self)
        LanguageManager.register_widget(self)
        ContextMenu.child_widgets.append(self)

    def bind_widgets_events(self, event: str, event_command: Callable):
        self.bind(event, event_command)
        self._canvas.bind(event, event_command)
        for option_button in self.option_buttons:
            option_button.bind(event, event_command)

    def set_open(self):
        self.is_open = True

    def set_closed(self):
        self.is_open = False

    def create_widgets(self):
        for i, _option_text in enumerate(self.options_texts):
            button = ctk.CTkButton(self, text="", command=self.options_commands[i])
            self.option_buttons.append(button)

    def set_widgets_accent_color(self):
        self.configure(border_color=ThemeManager.get_accent_color("normal"))

    def update_widgets_accent_color(self):
        self.set_widgets_accent_color()

    def set_widgets_colors(self):
        super().configure(fg_color=ThemeManager.get_color_based_on_theme("secondary"))
        for option_button in self.option_buttons:
            option_button.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
                hover_color=ThemeManager.get_color_based_on_theme("secondary_hover"),
                fg_color=ThemeManager.get_color_based_on_theme("secondary"),
            )

    def update_widgets_colors(self):
        """Update colors for the widgets."""
        self.set_widgets_colors()

    def set_widgets_fonts(self):
        for option_button in self.option_buttons:
            option_button.configure(font=(self.font[0], self.font[1], self.font[2]))

    def set_widgets_texts(self):
        for i, button in enumerate(self.option_buttons):
            button.configure(text=LanguageManager.data[self.options_texts[i]])

    def update_widgets_text(self):
        self.set_widgets_texts()

    def set_widgets_sizes(self):
        AppearanceSettings.get_scale("decimal")
        super().configure(width=self.width, height=self.height, border_width=1)
        button_height = int((self.height - 2) / len(self.options_texts))
        for option_button in self.option_buttons:
            option_button.configure(width=self.width, height=button_height, corner_radius=0)

    def place_widgets(self):
        self.option_buttons[0].pack(pady=1, padx=1)
        for button in self.option_buttons[1:-1]:
            button.pack(pady=(0, 0), padx=1)
        self.option_buttons[-1].pack(pady=1, padx=1)

    def configure(self, **kwargs):
        if "font" in kwargs:
            self.font = kwargs["font"]
            self.set_widgets_fonts()
        elif "width" in kwargs and "height" in kwargs:
            self.width = kwargs["width"]
            self.height = kwargs["height"]
            super().configure(**kwargs)
            self.set_widgets_sizes()
        else:
            super().configure(**kwargs)

    def __del__(self):
        ContextMenu.child_widgets.remove(self)
        self.unregister_from_services()

        del self.width
        del self.height
        del self.font
        del self.options_texts
        del self.options_commands
        del self.option_buttons
        del self.is_open

        self.destroy()
        del self

    def unregister_from_services(self):
        ThemeManager.unregister_widget(self)
        LanguageManager.unregister_widget(self)
