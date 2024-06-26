# PEP8 Compliant Guidance
# Standard Library Imports
import datetime
import calendar
import tkinter as tk

# Third-Party Library Imports

# Local Application/Library Specific Imports
import functions.header_functions as header_functions
from constants import BG_COLOR, FG_COLOR, FG_SECONDARY_COLOR

"""
This module contains the HdrDateGrid class for displaying the date grid and shift hours.

Classes:
    HdrDateGrid(tk.Frame): The frame displaying the date grid and shift hours.
"""

class HdrDateGrid(tk.Frame):
    """
    The frame displaying the date grid and shift hours.

    Attributes:
        parent (App): The parent application window.
        user_selections (dict): The user's selected schedule date and crew.
        crew (str): The selected crew.
        month (int): The selected month.
        year (int): The selected year.
        days_of_week (list): The list of days of the week.
        starting_day_index (int): The index of the starting day of the month.
        num_days_in_month (int): The number of days in the selected month.
        date_range (list): The range of dates for the selected month.
        column_frames (list): The list of frames representing each date column.

    Methods:
        None
    """
    DAYS_OF_WEEK = ["S", "M", "T", "W", "T", "F", "S"]
    MAX_DAYS_IN_MONTH = 31
    DAYS_IN_WEEK = 7
    
    def __init__(self, parent, user_selections):
        super().__init__(parent, relief=tk.FLAT, borderwidth=2, padx=10, pady=10)
        self.parent = parent
        self.configure(bg=BG_COLOR)
        self.user_selections = user_selections
        self.dates = self.generate_dates()  # Generate the dates attribute

        self.crew = self.user_selections["selected_crew"]
        self.month = self.user_selections["selected_month"].month
        self.year = self.user_selections["selected_year"].year

        self.days_of_week = self.DAYS_OF_WEEK

        self.starting_day_index = header_functions.get_weekday(self.month, self.year) % self.DAYS_IN_WEEK
        self.num_days_in_month = header_functions.month_range(self.month, self.year)
        self.date_range = list(range(1, self.num_days_in_month + 1)) + [""] * (self.MAX_DAYS_IN_MONTH - self.num_days_in_month)
        self.actual_date_range = list(range(1, self.num_days_in_month + 1))

        # Create a label in column 0 with the specified dimensions and position
        label = tk.Label(self, text="", width=20, height=1, bg=BG_COLOR, fg=FG_COLOR)
        label.grid(row=0, column=0, padx=10, pady=5, rowspan=3)

        self.date_column_frames = [tk.Frame(self, borderwidth=0, relief="solid", bg=BG_COLOR) for _ in range(31)]
            
        for column_index, column_frame in enumerate(self.date_column_frames):
            column_frame.grid(row=0, column=column_index+1, padx=0, pady=0)
            column_frame.grid_propagate(False)

        for column_index in range(31):
            day_index = (self.starting_day_index + column_index) % 7
            day_label = self.days_of_week[day_index] if column_index < self.num_days_in_month else ""
            tk.Label(self.date_column_frames[column_index], text=day_label, 
                     width=4, font=('Calibri', 12, "bold"), bg=BG_COLOR, fg=FG_SECONDARY_COLOR
                     ).pack(fill='both', expand=True)
            tk.Label(self.date_column_frames[column_index], text=str(self.date_range[column_index]), 
                     font=('Calibri', 12, "bold"), bg=BG_COLOR, fg=FG_SECONDARY_COLOR
                     ).pack(fill='both', expand=True)

        date_to_find = datetime.datetime(self.year, self.month, 1)
        crew_shift_list = header_functions.get_crew_shifts(self.crew, date_to_find)
        crew_shift_list = crew_shift_list[:31] + [" "] * (31 - len(crew_shift_list))
        for column_index in range(31):
            tk.Label(self.date_column_frames[column_index], text=crew_shift_list[column_index], 
                     font=("Calibri", 12, "bold"), bg=BG_COLOR, fg=FG_SECONDARY_COLOR
                     ).pack(fill="both", expand=True)
            
    def generate_dates(self):
        selected_month = self.user_selections['selected_month'].month
        selected_year = self.user_selections['selected_year'].year
        num_days = calendar.monthrange(selected_year, selected_month)[1]
        return [datetime.datetime(selected_year, selected_month, day) for day in range(1, num_days + 1)]
