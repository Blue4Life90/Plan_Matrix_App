# PEP8 Compliant Guidance
# Standard Library Imports
import tkinter as tk

# Third-Party Library Imports

# Local Application/Library Specific Imports
import functions.header_functions as header_functions
from constants import FG_COLOR, APP_BG_COLOR, FG_SECONDARY_COLOR

# Schedule Header: Includes - Title, Calendar, Shifts, Crew Name, and Crew ID
class HeaderFrame(tk.Frame):
    """
    The frame displaying the title, calendar, shifts, crew name, and crew ID.

    Attributes:
        parent (App): The parent application window.
        user_selections (dict): The user's selected schedule date and crew.

    Methods:
        update_calendar(crew: str, month: datetime.datetime, year: datetime.datetime): Updates the calendar display.
    """
    def __init__(self, parent, user_selections):
        super().__init__(parent, borderwidth=1, relief="flat", bg=APP_BG_COLOR)
        self.parent = parent
        self.user_selections = user_selections

        self.grid(column=0, row=0, padx=10, sticky="ew")

        self.create_title_label()
        self.create_calendar_month_header()
        self.create_calendar_month_label()
        self.create_calendar_year_label()
        self.create_id_detection_label()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(34, weight=1)

    def update_labels(self, schedule_type):
        if schedule_type == "work_schedule":
            self.title_label.config(text="Work Schedule")
            self.calendar_month_hdr.config(text=f"{self.user_selections['selected_crew']} Crew Work Schedule")
        else:  # Assume "overtime" if not "work_schedule"
            self.title_label.config(text="Overtime Schedule")
            self.calendar_month_hdr.config(text=f"{self.user_selections['selected_crew']} Crew Scheduled Overtime")
    
    def create_title_label(self):
        self.title_label = tk.Label(self, text="Overtime Schedule", 
                                    font=("Calibri", 30, "bold"), fg=FG_COLOR, bg=APP_BG_COLOR,
                                    anchor="center", justify="center")
        self.title_label.config(padx=10)
        self.title_label.grid(column=0, row=0, columnspan=35, sticky="nsew")

    def create_calendar_month_header(self):
        self.calendar_month_hdr = tk.Label(self, text="Schedule Calendar", 
                                        font=("Calibri", 12, "bold"), fg=FG_COLOR, bg=APP_BG_COLOR)
        self.calendar_month_hdr.grid(column=0, row=1, columnspan=35, sticky="nsew")

    def create_calendar_month_label(self):
        self.calendar_month_label = tk.Label(self, text="", 
                                            font=("Calibri", 12, "bold"), fg=FG_COLOR, bg=APP_BG_COLOR)
        self.calendar_month_label.grid(column=0, row=2, columnspan=35, sticky="nsew")

    def create_calendar_year_label(self):
        self.calendar_year_label = tk.Label(self, text="", 
                                            font=("Calibri", 12, "bold"), fg=FG_COLOR, bg=APP_BG_COLOR)
        # self.calendar_year_label.grid(column=0, row=3, columnspan=35, sticky="nsew")

    def create_id_detection_label(self):
        self.ID_detection_label = tk.Label(self, 
                                        text=f"Current User: {header_functions.get_user_id()}", 
                                        font=("Calibri", 12), fg=FG_SECONDARY_COLOR, bg=APP_BG_COLOR)
        self.ID_detection_label.grid(column=34, row=2, sticky="e")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(34, weight=1)
    
    def update_calendar(self, crew, month, year):
        """
        Updates the calendar display.

        Args:
            crew (str): The selected crew.
            month (datetime.datetime): The selected month.
            year (datetime.datetime): The selected year.
        """
        self.calendar_month_hdr.config(text=f"{crew} Crew Scheduled Overtime")
        self.calendar_year_label.config(text=year.year)
        self.calendar_month_label.config(text=f"{month.strftime("%B")} {year.year}")
        
# For testing
if __name__ == "__main__":
    root = tk.Tk()
    user_selections = {"crew": "A", "month": "January", "year": "2022"}
    header_frame = HeaderFrame(root, user_selections)
    header_frame.pack()
    root.mainloop()