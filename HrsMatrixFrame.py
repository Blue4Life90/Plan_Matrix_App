# PEP8 Compliant Guidance
# Standard Library Imports
import os
import logging
import tkinter as tk
from tkinter import messagebox

# Third-Party Library Imports

# Local Application/Library Specific Imports
import functions.logging_config as logging_config
from functions.header_functions import get_user_id
from constants import TRACKING_LOGS_DIR
from constants import ASKING_HRS_BG_COLOR, ASKING_HRS_FG_COLOR
from constants import WORKING_HRS_BG_COLOR, WORKING_HRS_FG_COLOR
from constants import BG_COLOR, FG_COLOR, APP_BG_COLOR, FG_SECONDARY_COLOR

class HrsMatrixFrame(tk.Frame):
    def __init__(self, parent, name, hdr_date_grid, 
                 ranking_frame, starting_asking_hours, starting_working_hours,
                 user_selections, 
                 cols=31
    ):
        super().__init__(parent, bg=APP_BG_COLOR)
        self.name = name
        self.hdr_date_grid = hdr_date_grid
        self.ranking_frame = ranking_frame
        self.starting_asking_hours = starting_asking_hours
        self.starting_working_hours = starting_working_hours
        self.user_selections = user_selections
        
        # Configure logging with the correct log file path
        self.tracking_file = self.get_tracking_file_path()
        logging_config.setup_logging(entry_log_file=self.tracking_file)
        
        # Get the loggers
        self.entry_logger = logging.getLogger('entry_logger')
        self.error_logger = logging.getLogger('error_logger')
        
        self.member_hours = {}   
        
        self.working_hours_entries = []  # List to store the created entries
        self.asking_hours_entries = []  # List to store the created entries
        self.asking_hours_tracking = []  # List to store the tracked asking hour labels
        self.labels = []  # List to store the created labels
        
        self.cols = cols
        
        # Create a frame for the total working hours label
        self.total_working_hours_frame = tk.Frame(self, bg=APP_BG_COLOR)
        self.total_working_hours_frame.grid(row=3, column=self.cols + 1, sticky="nsew")

        # Create a frame for the total asking hours label
        self.total_asking_hours_frame = tk.Frame(self, bg=APP_BG_COLOR)
        self.total_asking_hours_frame.grid(row=4, column=self.cols + 1, sticky="nsew")
        
        # Initialize labels for total hours; they will be updated later
        self.total_working_hours_label = tk.Label(
            self.total_working_hours_frame, text="0",
            bg=APP_BG_COLOR, fg=WORKING_HRS_BG_COLOR,
            font=("Calibri", 12, "bold"), relief="ridge", bd=1, justify="center",
            width=5, height=1
        )
        self.total_working_hours_label.pack(fill="both", expand=True)

        self.total_asking_hours_label = tk.Label(
            self.total_asking_hours_frame, text="0",
            bg=APP_BG_COLOR, fg=ASKING_HRS_BG_COLOR,
            font=("Calibri", 12, "bold"), relief="ridge", bd=1, justify="center",
            width=5
        )  

        self.total_asking_hours_label.pack(fill="both", expand=True)
        
        self.create_labels_and_entries()  # Create the labels and entries    

    def get_tracking_file_path(self):
        crew_folder =os.path.normpath(os.path.join(TRACKING_LOGS_DIR, self.user_selections["selected_crew"]))
        if not os.path.exists(os.path.normpath(crew_folder)):
            os.makedirs(crew_folder)
        selected_year = self.user_selections["selected_year"].strftime("%Y")  # Extract year as string
        selected_month = self.user_selections["selected_month"].strftime("%m")  # Extract month as string
        tracking_file = os.path.normpath(os.path.join(crew_folder, f'{self.user_selections["selected_crew"]}_{selected_year}_{selected_month}.log'))
        return tracking_file
    
    def update_tracking_file(self, user_selections):
        self.user_selections = user_selections
        self.tracking_file = self.get_tracking_file_path()
        logging_config.setup_logging(entry_log_file=self.tracking_file)
        self.entry_logger = logging.getLogger('entry_logger')
        self.error_logger = logging.getLogger('error_logger')
    
    def create_labels_and_entries(self):
        name_label = tk.Label(
            self, 
            text=self.name,
            font=("Calibri", 10, "bold"), 
            bg=APP_BG_COLOR, fg=FG_COLOR,
            width=20
        )
        name_label.grid(row=3, column=0, padx=10)

        starting_working_hours_tip_label = tk.Label(
            self, 
            text="Starting Worked:",
            font=("Calibri", 10, "bold"),
            bg=APP_BG_COLOR, fg=WORKING_HRS_BG_COLOR
        )
        starting_working_hours_tip_label.grid(row=4, column=0, sticky="w")

        starting_working_hours_label = tk.Label(
            self, 
            text=self.starting_working_hours,
            font=("Calibri", 10, "bold"),
            bg=APP_BG_COLOR, fg=WORKING_HRS_BG_COLOR
        )
        starting_working_hours_label.grid(row=4, column=0, sticky="e")

        starting_asking_hours_tip_label = tk.Label(
            self, 
            text="Starting Asked:", 
            font=("Calibri", 10, "bold"), 
            bg=APP_BG_COLOR, fg=ASKING_HRS_BG_COLOR
        )
        starting_asking_hours_tip_label.grid(row=5, column=0, sticky="w")

        starting_asking_hours_label = tk.Label(
            self, 
            text=self.starting_asking_hours,
            font=("Calibri", 10, "bold"),
            bg=APP_BG_COLOR, fg=ASKING_HRS_BG_COLOR
        )
        starting_asking_hours_label.grid(row=5, column=0, sticky="e")

        name_label.grid_propagate(False)
        self.labels.append(name_label)

        for j in range(self.cols):
            if j < len(self.hdr_date_grid.dates):
                date_str = self.hdr_date_grid.dates[j].strftime('%Y%m%d')
            else:
                date_str = ''

            column_frame = tk.Frame(
                self, bg=BG_COLOR, relief="flat", borderwidth=1
            )
            column_frame.grid(row=3, column=j + 1, padx=0, pady=0, rowspan=3)

            working_hours_entry = tk.Entry(
                column_frame, width=4,
                font=('Calibri', 12, "bold"), 
                relief="raised", bd=1,
                bg=WORKING_HRS_BG_COLOR, fg=WORKING_HRS_FG_COLOR, 
                justify="center",
                name=f"w_{self.name} {date_str}"
            )
            working_hours_entry.pack(fill="both", expand=True)
            working_hours_entry.bind(
                "<FocusOut>", 
                lambda event, 
                entry=working_hours_entry: [self.update_column_sums(event), self.entry_modified(entry)]
            )
            self.working_hours_entries.append(working_hours_entry)

            asking_hours_entry = tk.Entry(
                column_frame, width=4,
                font=('Calibri', 12, "bold"), 
                relief="raised", bd=1,
                bg=ASKING_HRS_BG_COLOR, fg=ASKING_HRS_FG_COLOR, 
                justify="center",
                name=f"a_{self.name} {date_str}"
            )
            asking_hours_entry.pack(fill="both", expand=True)
            asking_hours_entry.bind(
                "<FocusOut>", 
                lambda event, 
                entry=asking_hours_entry: [self.update_column_sums(event), self.entry_modified(entry)]
            )
            self.asking_hours_entries.append(asking_hours_entry)

            working_hours_entry.bind("<FocusIn>", self.on_entry_focus)
            asking_hours_entry.bind("<FocusIn>", self.on_entry_focus)
            
            asking_hours_tracking_label = tk.Label(
                column_frame, text=self.starting_asking_hours,
                relief="ridge", bd=1,
                font=('Calibri', 12, "bold"), 
                bg=FG_SECONDARY_COLOR,
                justify="center"
            )
            asking_hours_tracking_label.pack(fill="both", expand=True)
            self.asking_hours_tracking.append(asking_hours_tracking_label)

            
    def on_entry_focus(self, event):
        entry = event.widget
        entry.selection_range(0, tk.END)
    
    def ot_get_names_from_labels(self):
        label_values = []
        for label in self.labels:
            label_values.append(label.cget("text"))
        return label_values

    def update_rows(self, num_rows):
        for label in self.labels:
            label.grid_forget()
        for entry in self.working_hours_entries:
            entry.grid_forget()
        for entry in self.asking_hours_entries:
            entry.grid_forget()
        
        self.labels.clear()
        self.working_hours_entries.clear()
        self.asking_hours_entries.clear()
        
        # Create new labels and entries based on the updated number of rows
        for i in range(num_rows):
            label = tk.Label(self, text=f"Label {i+1}", width=20, height=1)
            label.grid(row=i*2, column=0, padx=10, pady=(5, 0))
            label.grid_propagate(False)
            self.labels.append(label)
            
            for j in range(self.cols):
                working_hours_entry = tk.Entry(
                    self, width=3, 
                    font=('Calibri', 12), 
                    bg='lightgreen'
                )
                working_hours_entry.grid(row=i*2, column=j+1, padx=5, pady=0)
                self.working_hours_entries.append(working_hours_entry)
                
                asking_hours_entry = tk.Entry(
                    self, width=3, 
                    font=('Calibri', 12), 
                    bg='lightpink'
                )
                asking_hours_entry.grid(row=i*2+1, column=j+1, padx=5, pady=0)
                self.asking_hours_entries.append(asking_hours_entry)
                
    def update_column_sums(self, event):
        total_working_hours = 0
        total_asking_hours = 0
        for col in range(self.cols):
            working_hours_sum = 0
            asking_hours_sum = 0

            for row in range(len(self.labels)):
                working_hours_entry = self.working_hours_entries[row * self.cols + col]
                asking_hours_entry = self.asking_hours_entries[row * self.cols + col]

                working_hours_value = working_hours_entry.get()
                asking_hours_value = asking_hours_entry.get()

                if working_hours_value:
                    try:
                        working_hours_sum += int(working_hours_value)
                    except ValueError:
                        pass

                if asking_hours_value:
                    try:
                        asking_hours_sum += int(asking_hours_value)
                    except ValueError:
                        pass

            # Update total sums
            total_working_hours += working_hours_sum
            total_asking_hours += asking_hours_sum

            if col == 0:
                # For the first column, use the starting asking hours as the base value
                cumulative_sum = self.starting_asking_hours + working_hours_sum + asking_hours_sum
            else:
                # For subsequent columns, use the previous column's cumulative sum as the base value
                previous_sum = int(self.asking_hours_tracking[col - 1].cget("text"))
                cumulative_sum = previous_sum + working_hours_sum + asking_hours_sum

            self.asking_hours_tracking[col].config(text=str(cumulative_sum))

        # Use the value from the last asking_hours_tracking label for total asking hours
        if self.asking_hours_tracking:
            last_asking_hours_value = self.asking_hours_tracking[-1].cget("text")
        else:
            last_asking_hours_value = "0"  # Default to "0" if the list is empty

        self.total_working_hours_value = total_working_hours + self.starting_working_hours
        
        # Update the total hours labels
        self.total_working_hours_label.config(text=str(self.total_working_hours_value))
        self.total_asking_hours_label.config(text=last_asking_hours_value)
            
    def entry_modified(self, modified_entry):
        try:
            # Validate the input
            input_value = modified_entry.get()
            
            if not input_value:
                # If the input is empty, allow it
                pass
            elif not input_value.isdigit() or int(input_value) < 0:
                # If the input is not a non-negative integer, show an error message and clear the entry
                messagebox.showerror("Invalid Input", "Please enter a non-negative integer.")
                modified_entry.delete(0, tk.END)
                return
            
            entry_name = modified_entry.winfo_name()
            username = get_user_id()
            schedule_type = "Overtime" if isinstance(self, HrsMatrixFrame) else "work_schedule"
            log_message = f"{schedule_type} - {username} - {entry_name} - Entered: {input_value}"
            self.entry_logger.info(log_message)
            
            # Check if the ranking frame exists
            if self.ranking_frame:
                # Check if the ranking frame is visible
                if self.ranking_frame.winfo_viewable():
                    # Call the update function in RankingFrame, passing relevant data
                    self.ranking_frame.update_ranking(self, modified_entry)
                else:
                    self.error_logger.error("HrsMatrixFrame.entry_modified: self.ranking_frame is not visible")
            else:
                self.error_logger.error("HrsMatrixFrame.entry_modified: self.ranking_frame does not exist")
        
        except Exception as e:
            # Log the error
            self.error_logger.error(f"An error occurred in entry_modified: {str(e)}")
            # Show an error message to the user
            messagebox.showerror("Error", "An unexpected error occurred. Please try again.")