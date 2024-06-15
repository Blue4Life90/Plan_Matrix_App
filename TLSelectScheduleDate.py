# PEP8 Compliant Guidance
# Standard Library Imports
import logging
import calendar
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Third-Party Library Imports
from PIL import Image
import customtkinter as ctk # type: ignore

# Local Application/Library Specific Imports
import functions.header_functions as header_functions
from constants import log_file
from constants import load_icons
from constants import APP_BG_COLOR, SELECT_SCHEDULE_BANNER_IMAGE
from constants import BUTTON_FG_COLOR, BUTTON_HOVER_BG_COLOR, TEXT_COLOR


logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file, 
                    filemode='a'
)

class TLSelectScheduleDate(tk.Toplevel):
    """
    _summary_
    
    Parent: Schedule_GUI 
    A toplevel window for selecting the schedule date and crew.

    Attributes:
        parent (tk.Tk): The parent window.
        user_selections (dict): The user's selected schedule date and crew.
        currentdate (datetime.datetime): The current date.
        currentmonth (int): The current month.
        currentyear (int): The current year.
    
    Methods:
        confirm_selections(): Confirms the user's selections and opens the main application window.
        selections_are_valid() -> bool: Checks if the user's selections are valid.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Schedule Selection")
        self.overrideredirect(True)
        self.iconpath_0, self.iconpath_1, self.iconpath_2 = load_icons()
        self.iconphoto(False, self.iconpath_0)  # Set the icon for the main window
        self.configure(background=APP_BG_COLOR)
        
        self.attributes("-topmost", True)  # Keep the window on top of others
        self.attributes("-toolwindow", True)  # Remove the minimize/maximize buttons
        
        self.user_selections = {}
        
        self.currentdate = datetime.datetime.now()
        self.currentmonth = self.currentdate.month
        self.currentyear = self.currentdate.year
        self.schedule_type = tk.StringVar()
        self.selected_schedule_type = "Overtime"
        
        """Picture Frame"""
        self.picture_frame = ctk.CTkFrame(self)
        self.picture_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")
        
        self.image = ctk.CTkImage(light_image=Image.open(SELECT_SCHEDULE_BANNER_IMAGE),
                                  dark_image=Image.open(SELECT_SCHEDULE_BANNER_IMAGE),
                                  size=(250, 500))
        self.image_label = ctk.CTkLabel(
            self.picture_frame,
            text="",
            image=self.image
        )
        self.image_label.grid(row=0, column=0, sticky="nsew")
        
        """Selection Frame"""
        self.selection_frame = ctk.CTkFrame(self, fg_color=APP_BG_COLOR)
        self.selection_frame.grid(row=0, column=1, padx=(20, 20), pady=(40, 0), sticky="nsew")
        
        
        # Crew Selection
        self.step_label = ctk.CTkLabel(
            self.selection_frame, 
            text="Please select the schedule via the\ncomboboxes below:",
            font=("Calibri", 14), text_color="white", 
            justify="left"
        )
        self.step_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 30), sticky="ew")
        
        # Crew Selection
        self.select_schedule_crew_label = ctk.CTkLabel(
            self.selection_frame, text="Select Crew:", 
            font=("Calibri", 14, "bold"), text_color="white",
            fg_color=APP_BG_COLOR
        )
        self.select_schedule_crew_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")        
        
        self.select_schedule_crew = ctk.CTkComboBox(self.selection_frame, values=header_functions.crews_list())
        #self.select_schedule_crew.set("A")
        self.select_schedule_crew.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Month Selection
        self.select_schedule_month_label = ctk.CTkLabel(
            self.selection_frame, text="Select Month:", 
            font=("Calibri", 14, "bold"), text_color="white",
            fg_color=APP_BG_COLOR
        )
        self.select_schedule_month_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.select_schedule_month = ctk.CTkComboBox(self.selection_frame, values=list(calendar.month_name)[1:])
        #self.select_schedule_month.set(calendar.month_name[self.currentmonth])
        self.select_schedule_month.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # Year Selection
        self.select_schedule_year_label = ctk.CTkLabel(
            self.selection_frame, text="Select Year:", 
            font=("Calibri", 14, "bold"), 
            fg_color=APP_BG_COLOR,
            text_color="white"
        )
        self.select_schedule_year_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.select_schedule_year = ctk.CTkComboBox(self.selection_frame, values=[str(year) for year in range(self.currentyear - 30, self.currentyear + 31)])
        self.select_schedule_year.set(str(self.currentyear))
        self.select_schedule_year.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        # Button to confirm selections and open the main application window
        self.confirm_button = ctk.CTkButton(
            self.selection_frame, text="Confirm", 
            font=("Calibri", 16, "bold"), 
            fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_BG_COLOR, 
            command=self.confirm_selections)
        self.confirm_button.grid(row=5, column=0, columnspan=2, padx=10, pady=(30,5), sticky="ew")
        
        # Button to close the application
        self.close_button = ctk.CTkButton(
            self.selection_frame,
            text="Close App",
            font=("Calibri", 16, "bold"), 
            command=self.close_app,
            fg_color="#730110",
            hover_color="#940115",
            text_color="white"
        )
        self.close_button.grid(row=6, column=0, columnspan=2, padx=10, pady=(5, 60), sticky="ew")
        
        self.trademark_info_label = ctk.CTkLabel(
            self.selection_frame,
            text="Created April 2024 @ MDGL",
            font=("Calibri", 8), text_color=TEXT_COLOR, 
            justify="right",
            anchor="e"
        )
        self.trademark_info_label.grid(row=10, column=0, columnspan=2, sticky="ew")
        
        self.create_schedule_type_combo()

    def create_schedule_type_combo(self):
        self.schedule_type_label = ctk.CTkLabel(
            self.selection_frame, text="Schedule Type:", 
            font=("Calibri", 14, "bold"), 
            text_color="white",
            fg_color=APP_BG_COLOR
        )
        self.schedule_type_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        schedule_type_combo = ctk.CTkComboBox(
            self.selection_frame, 
            values=["Overtime", "Work Schedule"], 
            variable=self.schedule_type 
        )
        schedule_type_combo.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        schedule_type_combo.set("Overtime")  # Set the default value
        self.schedule_type.trace_add("write", self.update_schedule_type)

    def update_schedule_type(self, *args):
        selected_type = self.schedule_type.get()
        if selected_type == "Overtime":
            self.selected_schedule_type = "overtime"
        elif selected_type == "Work Schedule":
            self.selected_schedule_type = "work_schedule"
    
    def confirm_selections(self) -> None:
        if self.selections_are_valid():
            selected_month = datetime.datetime.strptime(
                self.select_schedule_month.get(), "%B"
            )
            selected_year = datetime.datetime(int(self.select_schedule_year.get()), 1, 1)
            self.user_selections = header_functions.get_selected_values(
                self.select_schedule_crew.get(), selected_month, selected_year
            )

            self.parent.pass_values(self.user_selections, self.selected_schedule_type)
            
            # Check if the main application window still exists
            if self.parent.winfo_exists():
                self.withdraw()
                self.parent.deiconify()
            else:
                # Handle the case when the main application window has been destroyed
                logging.error("Main application window has been destroyed.")
                # You can add additional logic here, such as closing the TLSelectScheduleDate window
                self.destroy()

    def selections_are_valid(self) -> bool:
        try:
            selected_year = int(self.select_schedule_year.get())
            if selected_year > self.currentyear + 1 or str(self.select_schedule_crew.get()) == "":
                messagebox.showerror("Invalid Selection", "Year > than current year was selected. Please select a valid year.")
                logging.error("Invalid Selection", "User selection was >1 year past the current year")
                return False
            return True
        except ValueError:
            messagebox.showerror("Invalid Selection", "Please select a valid year.")
            logging.error("Invalid Selection", "Somehow user made an invalid selection when selecting schedule data to view.")
            return False
    
    def close_app(self):
        self.parent.destroy()