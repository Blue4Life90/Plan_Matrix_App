# PEP8 Compliant Guidance
# Standard Library Imports
import os
import logging
import tkinter as tk

# Third-Party Library Imports

# Local Application/Library Specific Imports
import functions.logging_config as logging_config
from functions.header_functions import get_user_id
from constants import TRACKING_LOGS_DIR
from constants import FG_COLOR, APP_BG_COLOR
from functions.app_functions import apply_entry_color_specs 

class WorkScheduleMatrixFrame(tk.Frame):
    def __init__(self, parent, name, hdr_date_grid, 
                 ranking_frame, user_selections, cols=31
    ):
        super().__init__(parent, bg=APP_BG_COLOR)
        self.name = name
        self.hdr_date_grid = hdr_date_grid
        self.ranking_frame = ranking_frame
        self.user_selections = user_selections
        
        self.tracking_file = self.get_tracking_file_path()
        logging_config.setup_logging(entry_log_file=self.tracking_file)
        self.entry_logger = logging.getLogger('entry_logger')
        self.error_logger = logging.getLogger('error_logger')
        
        self.member_hours = {}   
        self.crew_member_role_entries = []  # List to store the created entries
        self.labels = []  # List to store the created labels
        
        self.cols = cols
        
        self.create_labels_and_entries()  # Create the labels and entries
    
    def get_tracking_file_path(self):
        crew_folder = os.path.join(TRACKING_LOGS_DIR, self.user_selections["selected_crew"])
        if not os.path.exists(crew_folder):
            os.makedirs(crew_folder)
        selected_year = self.user_selections["selected_year"].strftime("%Y")  # Extract year as string
        selected_month = self.user_selections["selected_month"].strftime("%m")  # Extract month as string
        tracking_file = os.path.join(crew_folder, f'{self.user_selections["selected_crew"]}_{selected_year}_{selected_month}.log')
        return tracking_file
    
    def update_tracking_file(self, user_selections):
        self.user_selections = user_selections
        self.tracking_file = self.get_tracking_file_path()
        logging_config.setup_logging(entry_log_file=self.tracking_file)
        self.entry_logger = logging.getLogger('entry_logger')
        self.error_logger = logging.getLogger('error_logger')
    
    def create_labels_and_entries(self):
        # Create a label in column 0 with the specified dimensions and position
        name_label = tk.Label(self, 
                              text=self.name, 
                              font=("Calibri", 10, "bold"), 
                              width=20, 
                              height=1, 
                              bg=APP_BG_COLOR, 
                              fg=FG_COLOR)
        name_label.grid(row=0, column=0, padx=10, pady=5, rowspan=3)

        self.labels.append(name_label)

        for j in range(self.cols):
            if j < len(self.hdr_date_grid.dates):
                date_str = self.hdr_date_grid.dates[j].strftime('%Y%m%d')
            else:
                date_str = ''
            column_frame = tk.Frame(
                self, bg=APP_BG_COLOR, relief="flat", borderwidth=1
            )
            column_frame.grid(row=0, column=j + 1, padx=0, pady=0)

            crew_member_role_entry = tk.Entry(
                column_frame, width=4,
                font=('Calibri', 12, "bold"), 
                relief="raised", bd=1,
                bg="white", fg="black", 
                justify="center",
                name=f"r_{self.name} {date_str}"  # Add this line
            )
            crew_member_role_entry.pack(fill="both", expand=True)
            crew_member_role_entry.bind(
                "<KeyRelease>", 
                lambda event, 
                entry=crew_member_role_entry: self.entry_modified(entry, event)
            )
            self.crew_member_role_entries.append(crew_member_role_entry)
            crew_member_role_entry.bind("<FocusIn>", self.on_entry_focus)
            
    def on_entry_focus(self, event):
        entry = event.widget
        entry.selection_range(0, tk.END)
    
    def ws_get_names_from_labels(self):
        label_values = []
        for label in self.labels:
            label_values.append(label.cget("text"))
        return label_values

    def update_rows(self, num_rows):
        # Remove existing labels and entries from the grid
        for label in self.labels:
            label.grid_forget()
        for entry in self.crew_member_role_entries:
            entry.grid_forget()
        
        self.labels.clear()
        self.crew_member_role_entries.clear()
        
        # Create new labels and entries based on the updated number of rows
        for i in range(num_rows):
            label = tk.Label(self, text=f"Label {i+1}", width=20, height=1)
            label.grid(row=i, column=0, padx=10, pady=(5, 0))  # Add vertical padding only at the top
            label.grid_propagate(False)
            self.labels.append(label)
            
            for j in range(self.cols):
                crew_member_role_entry = tk.Entry(
                    self, width=3, 
                    font=('Calibri', 12), 
                    bg='lightgreen'
                )
                crew_member_role_entry.grid(row=i, column=j+1, padx=5, pady=0)  # Remove vertical padding
                self.crew_member_role_entries.append(crew_member_role_entry)
            
    def entry_modified(self, modified_entry, event):
        entry_text = modified_entry.get()
        
        if entry_text.isdigit():
            pass
        
        elif entry_text.upper() != entry_text:
            modified_entry.delete(0, tk.END)
            modified_entry.insert(0, entry_text.upper())
        
        entry = event.widget
        entry_text = modified_entry.get().upper()
        apply_entry_color_specs(entry, entry_text)
        entry_name = modified_entry.winfo_name()
        username = get_user_id()
        schedule_type = "Work Schedule" if isinstance(self, WorkScheduleMatrixFrame) else "Overtime"
        log_message = f"{schedule_type} - {username} - {entry_name[2:]} - Entered: {entry_text}"
        self.entry_logger.info(log_message)