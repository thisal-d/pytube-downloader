import customtkinter as ctk


class AccentColorButton(ctk.CTkButton):
    def __init__(
        self,
        master=None,
        width=1,
        height=1,
        border_width=0,
        corner_radius=0,
        text="",
        hover_color=None,
        fg_color=None,
        size_change=0,
    ):

        super().__init__(
            master=master,
            width=width,
            height=height,
            border_width=border_width,
            corner_radius=corner_radius,
            text=text,
            fg_color=fg_color,
        )
        self.size_change = size_change
        self.height = height
        self.width = width
        self.pressed = False
        self.hover_color = hover_color
        self.fg_color = fg_color

    def on_mouse_enter_self(self, _event):
        self.configure(
            width=self.cget("width") + self.size_change,
            height=self.cget("height") + self.size_change,
            fg_color=self.hover_color,
        )
        self.grid(padx=self.grid_info()["padx"] - self.size_change, pady=self.grid_info()["pady"] - self.size_change)

    def on_mouse_leave_self(self, _event):
        self.configure(
            width=self.cget("width") - self.size_change,
            height=self.cget("height") - self.size_change,
            fg_color=self.fg_color,
        )
        self.grid(padx=self.grid_info()["padx"] + self.size_change, pady=self.grid_info()["pady"] + self.size_change)

    def set_pressed(self):
        self.pressed = True
        self.configure(state="disabled")
        self.unbind("<Enter>")
        self.unbind("<Leave>")
        # self.reset_other_buttons()

    def set_unpressed(self):
        self.pressed = False
        self.configure(state="normal")
        self.bind("<Enter>", self.on_mouse_enter_self)
        self.bind("<Leave>", self.on_mouse_leave_self)
        self.on_mouse_leave_self("event")

    def bind_event(self):
        self.bind("<Enter>", self.on_mouse_enter_self)
        self.bind("<Leave>", self.on_mouse_leave_self)
