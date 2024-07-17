# PEP8 Compliant Guidance
# Standard Library Imports
import os
import json
import logging
import tkinter as tk

# Third-Party Library Imports

# Local Application/Library Specific Imports
from PathConfig import get_shared_path
from constants import APP_BG_COLOR, FG_COLOR
from functions.header_functions import get_user_id
from functions.app_functions import apply_entry_color_specs

def save_overtime_slots(data, crew, month, year, num_slots):
    shared_path = get_shared_path() or os.getcwd()
    json_dir = os.path.normpath(os.path.join(shared_path, "SaveFiles", "OT_Slots"))
    os.makedirs(json_dir, exist_ok=True)  # Ensure the directory exists
    json_filepath = os.path.normpath(os.path.join(json_dir, f"OT_{crew}_{year}.json"))

    if not os.path.exists(json_filepath):
        # If the file does not exist, create an initial structure
        existing_data = {'month': {}}
    else:
        with open(json_filepath, 'r') as file:
            existing_data = json.load(file)

    if str(month) not in existing_data['month']:
        existing_data['month'][str(month)] = {}

    existing_data['month'][str(month)]['count'] = num_slots

    for slot, hours in data.items():
        existing_data['month'][str(month)][slot] = hours

    with open(json_filepath, 'w') as file:
        json.dump(existing_data, file, indent=4)

def load_overtime_slots(crew, month, year):
    shared_path = get_shared_path() or os.getcwd()
    json_dir = os.path.normpath(os.path.join(shared_path, "SaveFiles", "OT_Slots"))
    os.makedirs(json_dir, exist_ok=True)  # Ensure the directory exists
    json_filepath = os.path.normpath(os.path.join(json_dir, f"OT_{crew}_{year}.json"))

    if not os.path.exists(json_filepath):
        return {}, 3  # Return an empty dictionary and default to 3 slots if the file does not exist

    with open(json_filepath, 'r') as file:
        data = json.load(file)

    num_slots = data['month'].get(str(month), {}).get('count', 3)
    return data['month'].get(str(month), {}), num_slots


class OvertimeSlots(tk.Frame):
    def __init__(self, parent, hdr_date_grid, user_selections, num_slots, cols=31):
        super().__init__(parent, bg=APP_BG_COLOR)
        self.hdr_date_grid = hdr_date_grid
        self.user_selections = user_selections
        self.cols = cols
        self.num_slots = num_slots

        self.tracking_file = self.get_tracking_file_path()
        self.setup_logging()

        self.labels = []
        self.entries = []

        self.load_overtime_data()
        self.create_overtime_entries()

    def get_tracking_file_path(self):
        crew_folder = os.path.join("tracking_logs", self.user_selections["selected_crew"])
        if not os.path.exists(crew_folder):
            os.makedirs(crew_folder)
        selected_year = self.user_selections["selected_year"].strftime("%Y")
        selected_month = self.user_selections["selected_month"].strftime("%m")
        tracking_file = os.path.join(crew_folder, f'{self.user_selections["selected_crew"]}_{selected_year}_{selected_month}.log')
        return tracking_file

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.entry_logger = logging.getLogger('entry_logger')
        self.error_logger = logging.getLogger('error_logger')
        handler = logging.FileHandler(self.tracking_file)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.entry_logger.addHandler(handler)
        self.error_logger.addHandler(handler)

    def create_overtime_entries(self):
        for label in self.labels:
            label.destroy()
        for entry_row in self.entries:
            for entry in entry_row:
                entry.destroy()

        self.labels = []
        self.entries = []

        overtime_names = [f"Overtime {i+1}" for i in range(self.num_slots)]

        for i, overtime_name in enumerate(overtime_names):
            row = i
            label = tk.Label(self, text=overtime_name, font=("Calibri", 10, "bold"), width=20, height=1, bg=APP_BG_COLOR, fg=FG_COLOR)
            label.grid(row=row, column=0, padx=10, pady=7)
            self.labels.append(label)

            entry_row = []
            for j in range(self.cols):
                if j < len(self.hdr_date_grid.dates):
                    date_str = self.hdr_date_grid.dates[j].strftime('%Y%m%d')
                else:
                    date_str = ''
                column_frame = tk.Frame(self, bg=APP_BG_COLOR, relief="flat", borderwidth=1)
                column_frame.grid(row=row, column=j + 1, padx=0, pady=7)

                overtime_entry = tk.Entry(column_frame, width=4, font=('Calibri', 12, "bold"), relief="raised", bd=1, bg="white", fg="black", justify="center", name=f"o_{overtime_name} {date_str}")
                overtime_entry.pack(fill="both", expand=True)
                overtime_entry.bind("<KeyRelease>", lambda event, entry=overtime_entry: self.entry_modified(entry, event))
                overtime_entry.bind("<FocusIn>", self.on_entry_focus)
                entry_row.append(overtime_entry)

            self.entries.append(entry_row)

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
        log_message = f"Overtime - {username} - {entry_name[2:]} - Entered: {entry_text}"
        self.entry_logger.info(log_message)

    def on_entry_focus(self, event):
        entry = event.widget
        entry.selection_range(0, tk.END)

    def update_overtime_slots(self, num_slots):
        old_data = {}
        for label, entry_row in zip(self.labels, self.entries):
            slot_name = label.cget("text")
            old_data[slot_name] = [entry.get() for entry in entry_row]

        self.num_slots = max(3, num_slots)
        self.labels.clear()
        self.entries.clear()
        self.create_overtime_entries()

        for label, entry_row in zip(self.labels, self.entries):
            slot_name = label.cget("text")
            if slot_name in old_data:
                for entry, value in zip(entry_row, old_data[slot_name]):
                    entry.delete(0, tk.END)
                    entry.insert(0, value)

        self.save_overtime_data()
    
    def load_overtime_data(self):
        overtime_data, self.num_slots = load_overtime_slots(self.user_selections["selected_crew"], self.user_selections["selected_month"].month, self.user_selections["selected_year"].year)
        for label, entry_row in zip(self.labels, self.entries):
            slot_name = label.cget("text")
            if slot_name in overtime_data:
                for entry, value in zip(entry_row, overtime_data[slot_name]):
                    entry.delete(0, tk.END)
                    entry.insert(0, value)

    def save_overtime_data(self):
        overtime_data = {}
        for label, entry_row in zip(self.labels, self.entries):
            slot_name = label.cget("text")
            overtime_data[slot_name] = [entry.get() for entry in entry_row]
        
        existing_data, _ = load_overtime_slots(self.user_selections["selected_crew"], self.user_selections["selected_month"].month, self.user_selections["selected_year"].year)
        current_slots = [label.cget("text") for label in self.labels]
        for slot in list(existing_data.keys()):
            if slot.startswith("Overtime") and slot not in current_slots:
                del existing_data[slot]
        
        save_overtime_slots(overtime_data, self.user_selections["selected_crew"], self.user_selections["selected_month"].month, self.user_selections["selected_year"].year, self.num_slots)