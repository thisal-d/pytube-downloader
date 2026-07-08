import customtkinter as ctk


class SettingNavigateButton(ctk.CTkButton):
    def __init__(self, is_clicked: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.is_clicked = is_clicked

    def set_clicked_state(self, is_clicked: bool):
        self.is_clicked = is_clicked
