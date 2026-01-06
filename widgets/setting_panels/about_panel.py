import os
import threading
import webbrowser
from typing import Any, Dict
import random
import customtkinter as ctk
from PIL import Image
from utils import (
    DataRetrieveUtility,
    JsonUtility,
    FileUtility,
    ImageUtility,
)
from services import ThemeManager, LanguageManager, InformationManager
from settings import (
    AppearanceSettings,
)
from ..components.contributor_profile_widget import ContributorProfileWidget


class AboutPanel(ctk.CTkFrame):
    def __init__(
            self,
            master: Any = None):

        super().__init__(
            master=master,
        )

        self.logo_name_version_frame = ctk.CTkFrame(
            master=self
        )
        
        self.logo_label = ctk.CTkLabel(
            master=self.logo_name_version_frame,
            text="⚡",
        )

        self.name_label = ctk.CTkLabel(
            master=self.logo_name_version_frame,
            text=""
        )

        self.version_label = ctk.CTkButton(
            master=self.logo_name_version_frame,
            hover=False,
            text=""
        )

        self.developed_by__label = ctk.CTkLabel(
            master=self,
            text="Contributors"
        )
        self.dash4_label = ctk.CTkLabel(
            master=self,
            text=":"
        )
        self.contributors_status_label = ctk.CTkLabel(
            master=self,
            text="Retrieving contributors data...!",
        )

        self.contributors_frame = ctk.CTkScrollableFrame(
            master=self,
        )
   
    
        self.explore_title_label = ctk.CTkLabel(
            master=self,
            anchor="w",
            text=""
        )

        self.explore_btns_frame = ctk.CTkScrollableFrame(
            master=self,
        )
        self.explore_buttons = []

        self.disclaimer_label = ctk.CTkLabel(
            master=self,
            justify="left",
            text="",
        )

        self.contribute_data_retrieve_status = None

        self.create_explore_buttons()
        self.place_widgets()
        self.set_widgets_fonts()
        self.set_widgets_texts()
        self.set_widgets_sizes()
        self.configure_values()
        self.set_widgets_accent_color()
        self.set_widgets_colors()
        self.bind_widgets_events()

        ThemeManager.register_widget(self)
        LanguageManager.register_widget(self)

    def configure_values(self):
        self.logo_label.configure(text=InformationManager.info["logo"])
        self.name_label.configure(text=InformationManager.info["name"])
        self.version_label.configure(text= f"v{InformationManager.info["version"]}")
        # self.site_button.configure(text=InformationManager.info["site"], command=lambda: webbrowser.open(InformationManager.info["site"]))
        # self.after(100, self.configure_contributors_info)
        threading.Thread(target=self.configure_contributors_info, daemon=True).start()

    def create_explore_buttons(self):
        for explore_info in InformationManager.info["explore_links"]:
            btn = ctk.CTkButton(
                master=self.explore_btns_frame,
                text=explore_info["name"],
                width=200,
                height=30,
                command=lambda url=explore_info["url"]: webbrowser.open(url)
            )
            self.explore_buttons.append(btn)

    def update_contributors_info(self, contributors_data):
        # retrieve links of contributors as list[dict] -> GitHub.com
        # iterate contributors list[dict] and generate
        InformationManager.info["contributors"] = {}
        for i, contributor_data in enumerate(contributors_data):
            InformationManager.info["contributors"][i] = {
                "profile_url": contributor_data["profile_url"],
                "user_name": contributor_data["user_name"]
            }

    def configure_contributors_info(self):
        # randomly choose to update info :D
        if random.choice((False,) * 15 + (True,)*5):
            # delete old profile images
            FileUtility.delete_files("assets//profile images//", ["this directory is necessary"])
            InformationManager.info["contributors"] = {}

        # retrieve contributors data from GitHub repo as list[dict]
        contributors_data = DataRetrieveUtility.get_contributors_data()
        # if it success -> return Dict
        # if it fails -> return None
        if contributors_data is not None:
            # if old contributors data list length is different from new contributors data list length,
            # that means contributors data is changed
            if len(InformationManager.info["contributors"]) != len(contributors_data):
                # if contributors data is changed, call update_contributors_info function to update old data dict
                self.update_contributors_info(contributors_data)
        else:
            if len(InformationManager.info["contributors"]) == 0:
                self.contribute_data_retrieve_status = "Failed"
                self.contributors_status_label.configure(
                    text=LanguageManager.data["contribute_data_retrieve_failed"],
                    text_color=ThemeManager.get_color_based_on_theme("text_warning")
                )

        if len(InformationManager.info["contributors"]) != 0:
            # place forget the loading label
            self.contributors_status_label.grid_forget()
            self.dash4_label.grid_forget()
            self.contribute_data_retrieve_status = "Success"
            # place frame for show  contributors info
            self.contributors_frame.grid(
                row=3,
                column=0,
                pady=(5 * AppearanceSettings.get_scale("decimal"), 0),
                sticky="w",
                columnspan=10,
                padx=(150, 0)
            )
        # iterate through contributors
        profile_images_directory = "assets//profile images//"
        row = 0
        for i in InformationManager.info["contributors"].keys():
            contributor = InformationManager.info["contributors"][i]
            # check if profile image saved or if not create image path
            # check profile image is already downloaded if it's not download profile image right now
            if contributor.get("profile_images_paths", None) is not None:
                profile_images_paths = contributor["profile_images_paths"]
            else:
                profile_normal_image_path = FileUtility.sanitize_filename(f"{contributor["profile_url"]}-normal.png")
                profile_normal_image_path = profile_images_directory + profile_normal_image_path

                profile_hover_image_path = FileUtility.sanitize_filename(f"{contributor["profile_url"]}-hover.png")
                profile_hover_image_path = profile_images_directory + profile_hover_image_path
                profile_images_paths = (
                    FileUtility.get_available_file_name(profile_normal_image_path),
                    FileUtility.get_available_file_name(profile_hover_image_path)
                )
                # update images path
                InformationManager.info["contributors"][i]["profile_images_paths"] = profile_images_paths

            # check if profile image is already downloaded if it's not download profile image
            if not os.path.exists(profile_images_paths[0]):
                try:
                    # download image from GitHub
                    ImageUtility.download_image(
                        image_url=f"{contributor["profile_url"]}.png",
                        output_image_path=profile_images_paths[0]
                    )
                    # add corner radius to download image
                    profile_image = Image.open(profile_images_paths[0])
                    profile_image = ImageUtility.create_image_with_rounded_corners(
                        image=profile_image,
                        radius=int(profile_image.width/2),
                    )
                    profile_image.save(profile_images_paths[0])
                    profile_image.close()
                except Exception as error:
                    print(f"about_panel.py : {error}")
            # check if  hover profile image is already generated if not generate
            if not os.path.exists(profile_images_paths[1]) and os.path.exists(profile_images_paths[0]):
                profile_image = Image.open(profile_images_paths[0])
                profile_image_hover = ImageUtility.create_image_with_rounded_corners(
                    ImageUtility.create_image_with_hover_effect(
                        image=profile_image,
                        intensity_increase=40
                    ),
                    radius=int(profile_image.width/2)
                )
                profile_image_hover.save(profile_images_paths[1])

            if os.path.exists(profile_images_paths[1]) and os.path.exists(profile_images_paths[0]):
                # create contributor
                ContributorProfileWidget(
                    master=self.contributors_frame,
                    width=35,
                    height=35,
                    user_name=contributor["user_name"],
                    profile_url=contributor["profile_url"],
                    profile_images_paths=profile_images_paths,
                ).grid(
                    row=row,
                    pady=0,
                    padx=(15, 15, 15)
                )
                row += 2

        # save info to json
        InformationManager.save_info()

    def bind_widgets_events(self):
        for explore_btn in self.explore_buttons:
            explore_btn.bind("<Enter>", lambda event, btn=explore_btn: btn.configure(
                    fg_color=ThemeManager.get_color_based_on_theme("primary_hover")
                )
            )
            explore_btn.bind("<Leave>", lambda event, btn=explore_btn: btn.configure(
                    fg_color=ThemeManager.get_color_based_on_theme("primary")
                )
            )

    def set_widgets_accent_color(self):
        self.name_label.configure(text_color=ThemeManager.get_accent_color("normal"))
        self.logo_label.configure(text_color=ThemeManager.get_accent_color("normal"))

    def update_widgets_accent_color(self):
        self.set_widgets_accent_color()

    def set_widgets_colors(self):
        self.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))

        self.logo_name_version_frame.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))

        self.version_label.configure(
            text_color=ThemeManager.get_color_based_on_theme("text_normal"),
            fg_color=ThemeManager.get_color_based_on_theme("primary"),
            border_color=ThemeManager.get_color_based_on_theme("border"),
        )

        self.developed_by__label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))

        if  self.contribute_data_retrieve_status == "Failed":
            self.contributors_status_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_warning"))
        else:
            self.contributors_status_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_muted"))


        self.contributors_frame.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))

        self.explore_btns_frame.configure(fg_color=ThemeManager.get_color_based_on_theme("background"))
        self.explore_title_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_normal"))
        
        for explore_btn in self.explore_buttons:
            explore_btn.configure(
                text_color=ThemeManager.get_color_based_on_theme("text_normal"),
                fg_color=ThemeManager.get_color_based_on_theme("primary"),
                border_color=ThemeManager.get_color_based_on_theme("border")
            )
        
        self.disclaimer_label.configure(text_color=ThemeManager.get_color_based_on_theme("text_warning"))
        
    def update_widgets_colors(self):
        """Update colors for the widgets."""
        self.set_widgets_colors()

    def place_widgets(self):
        scale = AppearanceSettings.get_scale("decimal")
        pady = 16 * scale

        self.logo_name_version_frame.grid(row=0, column=0, columnspan=3, pady=(50, 0), padx=(100, 0),)
        self.logo_label.grid(row=0, column=0, sticky="e")
        self.name_label.grid(row=0, column=1, sticky="e")
        self.version_label.grid(row=0, column=2, sticky="sw", padx=(8 * scale, 0))

        self.developed_by__label.grid(row=2, column=0, padx=(100, 0), pady=(pady, 0), sticky="w")
        self.dash4_label.grid(row=2, column=1, pady=(pady, 0), sticky="w")
        self.contributors_status_label.grid(row=2, column=2, pady=(pady, 0), sticky="w")

       
        self.explore_title_label.grid(row=4, column=0, padx=(100, 0), pady=(pady, 0), sticky="w")
        self.explore_btns_frame.grid(
                row=5,
                column=0,
                pady=(5 * AppearanceSettings.get_scale("decimal"), 0),
                sticky="w",
                columnspan=10,
                padx=(150, 0)
            )
        self.explore_btns_frame._scrollbar.grid_forget()

        column_ = 0
        row_ = 0
        for explore_btn in self.explore_buttons:
            explore_btn.grid(padx=10, row=row_, column=column_)
            if column_ > 4:
                column_ = 0
                row_ += 1
            else:
                column_ += 1

        self.disclaimer_label.place(x=100, rely=1, y=-50 * scale)
        
    def set_widgets_sizes(self):
        scale = AppearanceSettings.get_scale("decimal")
        self.contributors_frame.configure(height=200 * scale, width=500 * scale)
        self.contributors_frame._scrollbar.grid_forget()

        self.version_label.configure(width=1 * scale, height=1 * scale)

        self.explore_btns_frame.configure(height=30 * scale, width=500 * scale)
        for explore_btn in self.explore_buttons:
            explore_btn.configure(width=1 * scale, height=28 * scale, border_width=1 * scale)
    
    def set_widgets_texts(self):
        self.developed_by__label.configure(text=LanguageManager.data["developed_by"])
        # print("self.contribute_data_retrieve_status :",self.contribute_data_retrieve_status)
        if self.contribute_data_retrieve_status == "Failed":
            self.contributors_status_label.configure(text=LanguageManager.data["contribute_data_retrieve_failed"])
        elif self.contribute_data_retrieve_status is None:
            self.contributors_status_label.configure(text=LanguageManager.data["contribute_data_retrieving"])
        
        self.explore_title_label.configure(text=LanguageManager.data["explore_the_project"])
        self.disclaimer_label.configure(text="  " + LanguageManager.data["disclaimer"])
        

    def update_widgets_text(self):
        self.set_widgets_texts()

    def set_widgets_fonts(self):
        scale = AppearanceSettings.get_scale("decimal")

        self.logo_label.configure(font=("Segoe UI", 30 * scale, "bold"))

        self.name_label.configure(font=("Segoe UI", 24 * scale, "bold"))
        self.version_label.configure(font=("Segoe UI", 10 * scale, "bold"))

        # self.site_button.configure(font=title_font)
        title_font = ("Segoe UI", 13 * scale, "bold")
        self.developed_by__label.configure(font=title_font)
        self.dash4_label.configure(font=title_font)
        self.contributors_status_label.configure(font=title_font)

        value_font = ("Segoe UI", int(13 * scale), "normal")
        self.disclaimer_label.configure(font=value_font)

        self.explore_title_label.configure(font=title_font)
        self.explore_button_font = ("Segoe UI", 11 * scale, "bold")
        for explore_btn in self.explore_buttons:
            explore_btn.configure(font=self.explore_button_font)