# PEP8 Compliant Guidance
# Standard Library Imports
import os
import logging
import tkinter as tk
from PIL import Image, ImageTk  # Import for handling images

# Third-Party Library Imports
import customtkinter as ctk #type: ignore

# Local Application/Library Specific Imports
from constants import PANE_BG_COLOR, log_file
from constants import BUTTON_FG_COLOR, BUTTON_HOVER_BG_COLOR

# Logging Format
logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file, 
                    filemode='a'
)

class LeftPaneButtonFrame(ctk.CTkFrame):
    def __init__(
        self, parent, open_schedule_manager_method, 
        save_member_data_method, open_schedule_selection_menu, schedule_type
    ):
        super().__init__(parent, bg_color=PANE_BG_COLOR, fg_color=PANE_BG_COLOR)
        self.parent = parent
        self.open_schedule_manager_method = open_schedule_manager_method
        self.save_member_data_method = save_member_data_method
        self.open_schedule_selection_menu = open_schedule_selection_menu
        self.schedule_type = schedule_type
        
        self.configure(bg_color=PANE_BG_COLOR)
        
        self.nav_title_frame()
        self.button_frame()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
    
    def nav_title_frame(self):
        self.nav_pane_title_frame = ctk.CTkFrame(
            self, 
            bg_color=PANE_BG_COLOR, 
            fg_color=PANE_BG_COLOR
        )
        self.nav_pane_title_frame.pack(padx=10, pady=5, side="top", fill="x")  # Add fill="x" here

        # Title image
        image_path = os.path.normpath(os.path.join("images/background_images/", "Plan_Matrix_title.png"))
        image = Image.open(image_path)  # Open the image file directly
        photo = ImageTk.PhotoImage(image)  # Convert to PhotoImage

        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)

        # Create a label with the image
        self.nav_pane_title_image = tk.Label(
            self.nav_pane_title_frame, image=photo, 
            bg=PANE_BG_COLOR
        )
        self.nav_pane_title_image.image = photo  # Keep a reference to the image
        self.nav_pane_title_image.pack(padx=10, pady=5, side="left", fill="x", expand=True)
    
    def button_frame(self):
        self.frame_for_nav_pane_buttons = tk.Frame(self, bg=PANE_BG_COLOR)
        self.frame_for_nav_pane_buttons.pack(side="top", pady=10)

        # Create a button widget
        self.select_new_schedule_button = ctk.CTkButton(self.frame_for_nav_pane_buttons, text="Select Schedule Menu",
                                                    width=200, height=40,
                                                    font=("Calibri", 16, "bold"),
                                                    fg_color=BUTTON_FG_COLOR,
                                                    hover_color=BUTTON_HOVER_BG_COLOR, 
                                                    command=self.open_schedule_selection_menu)
        self.select_new_schedule_button.pack(padx=10, pady=5)
        
        # Create a button widget
        self.schedule_manager_button = ctk.CTkButton(self.frame_for_nav_pane_buttons, text="Open Schedule Manager",
                                                    width=200, height=40,
                                                    font=("Calibri", 16, "bold"),
                                                    fg_color=BUTTON_FG_COLOR,
                                                    hover_color=BUTTON_HOVER_BG_COLOR, 
                                                    command=self.open_schedule_manager_method)
        self.schedule_manager_button.pack(padx=10, pady=5)
        
        if self.schedule_type == "Overtime":
            switch_command = self.parent.master.select_work_schedule
            switch_text = "Overtime Schedule"
        else:
            switch_command = self.parent.master.select_overtime_schedule
            switch_text = "Work Schedule"   
        
        # Create a button widget
        self.switch_schedules_button = ctk.CTkButton(self.frame_for_nav_pane_buttons, text=switch_text, 
                                                width=200, height=40,
                                                font=("Calibri", 16, "bold"),
                                                fg_color=BUTTON_FG_COLOR, 
                                                hover_color=BUTTON_HOVER_BG_COLOR, 
                                                command=switch_command)
        self.switch_schedules_button.pack(padx=10, pady=5)
        
        self.save_entries_button = ctk.CTkButton(self.frame_for_nav_pane_buttons, text="Save", 
                                                 width=200, height=40, 
                                                 font=("Calibri", 16, "bold"), 
                                                 fg_color=BUTTON_FG_COLOR, 
                                                 hover_color=BUTTON_HOVER_BG_COLOR, 
                                                 command=self.save_member_data_method)
        self.save_entries_button.pack(padx=10, pady=5)
        
        self.print_schedule_button = ctk.CTkButton(
            self.frame_for_nav_pane_buttons, 
            text="Print", 
            width=200, height=40,
            font=("Calibri", 16, "bold"),
            fg_color=BUTTON_FG_COLOR, 
            hover_color=BUTTON_HOVER_BG_COLOR, 
            command=self.print_current_schedule
        )
        self.print_schedule_button.pack(padx=10, pady=5)
        
    def print_current_schedule(self):
        self.parent.master.print_current_schedule()
    
    def update_switch_button(self, schedule_type, switch_command):
        if schedule_type == "Overtime":
            switch_text = "Overtime Schedule"
        else:
            switch_text = "Work Schedule"

        if hasattr(self, 'switch_schedules_button'):
            try:
                self.switch_schedules_button.configure(text=switch_text, command=switch_command)
            except Exception as e:
                logging.error(f"Error updating switch button: {str(e)}")
                # Add any additional error handling or logging here
        else:
            logging.warning("switch_schedules_button does not exist.")