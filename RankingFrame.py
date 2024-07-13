# PEP8 Compliant Guidance
# Standard Library Imports

# Third-Party Library Imports
import customtkinter as ctk # type: ignore

# Local Application/Library Specific Imports
from constants import APP_BG_COLOR, PANE_BG_COLOR, TEXT_COLOR
from constants import ASKING_HRS_FG_COLOR, ASKING_HRS_BG_COLOR
from constants import WORKING_HRS_FG_COLOR, WORKING_HRS_BG_COLOR

class RankingFrame(ctk.CTkFrame):
    def __init__(self, parent, schedule_hrs_frame):
        super().__init__(parent, bg_color=PANE_BG_COLOR, fg_color=PANE_BG_COLOR)
        self.schedule_hrs_frame = schedule_hrs_frame

        # Create header row
        self.rowconfigure(0, weight=0)  # Don't allow the switch frame to expand
        self.rowconfigure(1, weight=0)  # Don't allow the header row to expand
        self.rowconfigure(2, weight=1)  # Allow the ranking rows to expand
        self.columnconfigure(0, weight=1)  # Allow the header columns to expand horizontally
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Create a frame to hold the switch and its label
        self.switch_frame = ctk.CTkFrame(self, fg_color=APP_BG_COLOR)
        self.switch_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.switch_label = ctk.CTkLabel(
            self.switch_frame, text="Sort by Asking/Working Hours", 
            bg_color=APP_BG_COLOR, text_color=TEXT_COLOR, 
            font=("Calibri", 12)
        )
        self.switch_label.pack(side="left", padx=5)
        
        self.sort_switch_var = ctk.StringVar(value="asking") 
        self.sort_switch = ctk.CTkSwitch(
            self.switch_frame, text="", command=self.sort_switch_event, 
            variable=self.sort_switch_var, 
            onvalue="asking", offvalue="working", 
            fg_color=WORKING_HRS_FG_COLOR, 
            progress_color=ASKING_HRS_FG_COLOR,
            width=40, height=20
        )
        self.sort_switch.pack(side="left", padx=5)

        self.create_ranking_labels()
        self.sort_ranking_labels()

    def create_label_frame(self, parent, text, is_working_hours=False, is_name=False):
        frame = ctk.CTkFrame(
            parent, width=40, height=20, 
            bg_color=PANE_BG_COLOR, 
            fg_color=PANE_BG_COLOR
        )
        if is_name:
            label_color = TEXT_COLOR
        elif is_working_hours:
            label_color = WORKING_HRS_BG_COLOR
        else:
            label_color = ASKING_HRS_BG_COLOR
        
        label = ctk.CTkLabel(
            frame, text=text, 
            bg_color=PANE_BG_COLOR, 
            fg_color=PANE_BG_COLOR, 
            font=("Calibri", 12, "bold"), 
            text_color=label_color
        )
        label.pack(expand=True, fill="both")
        return frame
    
    def calculate_total_working_hours(self, member_frame):
        total_working_hours = int(member_frame.starting_working_hours)
        for entry in member_frame.working_hours_entries:
            try:
                total_working_hours += int(entry.get() or 0)
            except ValueError:
                # Skip the entry if it is not a valid integer
                pass
        return total_working_hours

    def calculate_total_asking_hours(self, member_frame):
        return int(member_frame.asking_hours_tracking[-1].cget("text"))

    def create_ranking_labels(self):
        if not self.schedule_hrs_frame.frames:
            return  # Exit if frames attribute is empty or None
        
        for i, member_frame in enumerate(
            self.schedule_hrs_frame.frames, start=1
        ):
            member_name = member_frame.labels[0].cget("text")
            total_working_hours = self.calculate_total_working_hours(member_frame)
            total_asking_hours = self.calculate_total_asking_hours(member_frame)

            name_frame = self.create_label_frame(
                self, member_name, is_name=True
            )
            name_frame.grid(row=i, column=0, padx=5, pady=5)

            tw_frame = self.create_label_frame(
                self, total_working_hours, is_working_hours=True
            )
            tw_frame.grid(row=i, column=1, padx=5, pady=5)

            ta_frame = self.create_label_frame(
                self, total_asking_hours, 
                is_name=False, is_working_hours=False
            )
            ta_frame.grid(row=i, column=2, padx=5, pady=5)
            
    def update_ranking(self, member_frame, modified_entry):
        # Check if the modified entry value is valid
        entry_value = modified_entry.get()
        if not entry_value.isdigit() or len(entry_value) > 4:
            # Skip the update if the entry value is invalid
            return

        # Update the totals and labels
        member_name = member_frame.labels[0].cget("text")
        total_working_hours = self.calculate_total_working_hours(member_frame)
        total_asking_hours = self.calculate_total_asking_hours(member_frame)

        row_index = self.schedule_hrs_frame.frames.index(member_frame) + 1

        # Check if the name frame exists, create it if not
        name_frame = self.grid_slaves(row=row_index, column=0)
        if name_frame:
            name_frame[0].winfo_children()[0].configure(text=member_name)
        else:
            name_frame = self.create_label_frame(
                self, member_name, is_name=True
            )
            name_frame.grid(row=row_index, column=0, padx=5, pady=5)

        # Check if the tw frame exists, create it if not
        tw_frame = self.grid_slaves(row=row_index, column=1)
        if tw_frame:
            tw_frame[0].winfo_children()[0].configure(
                text=total_working_hours
            )
        else:
            tw_frame = self.create_label_frame(
                self, total_working_hours, 
                is_working_hours=True
            )
            tw_frame.grid(row=row_index, column=1, padx=5, pady=5)

        # Check if the ta frame exists, create it if not
        ta_frame = self.grid_slaves(row=row_index, column=2)
        if ta_frame:
            ta_frame[0].winfo_children()[0].configure(text=total_asking_hours)
        else:
            ta_frame = self.create_label_frame(
                self, total_asking_hours, 
                is_name=False, is_working_hours=False
            )
            ta_frame.grid(row=row_index, column=2, padx=5, pady=5)

        self.sort_ranking_labels()
            
    def sort_switch_event(self):
        if self.sort_switch_var.get() == "asking":
            self.sort_ranking_labels(sort_key=self.sort_by_asking_hours_key)
        else:
            self.sort_ranking_labels(sort_key=self.sort_by_working_hours_key)
    
    def sort_by_asking_hours_key(self, x):
        return x[2]

    def sort_by_working_hours_key(self, x):
        return x[1]

    def sort_by_asking_hours(self):
        self.sort_ranking_labels(
            sort_key=self.sort_by_asking_hours_key, reverse=True
        )

    def sort_by_working_hours(self):
        self.sort_ranking_labels(
            sort_key=self.sort_by_working_hours_key, reverse=True
        )

    def sort_ranking_labels(self, sort_key=None):
        # Get the current ranking data
        ranking_data = []
        for i, member_frame in enumerate(
            self.schedule_hrs_frame.frames, start=1
            ):
            member_name = member_frame.labels[0].cget("text")
            total_working_hours = self.calculate_total_working_hours(member_frame)
            total_asking_hours = self.calculate_total_asking_hours(member_frame)
            ranking_data.append((member_name, total_working_hours, total_asking_hours))

        # Sort the ranking data based on the switch state
        if self.sort_switch_var.get() == "asking":
            sort_key = self.sort_by_asking_hours_key
        else:
            sort_key = self.sort_by_working_hours_key
        
        ranking_data.sort(key=sort_key, reverse=True)

        # Clear the existing ranking labels
        for widget in self.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:  # Skip the header row
                widget.destroy()

        # Create new ranking labels based on the sorted data
        for i, (member_name, total_working_hours, total_asking_hours) in enumerate(ranking_data, start=2):
            name_frame = self.create_label_frame(
                self, member_name, is_name=True
            )
            name_frame.grid(row=i, column=0, padx=5, pady=5)

            tw_frame = self.create_label_frame(
                self, total_working_hours, is_working_hours=True
            )
            tw_frame.grid(row=i, column=1, padx=5, pady=5)

            ta_frame = self.create_label_frame(
                self, total_asking_hours, 
                is_name=False, is_working_hours=False
            )
            ta_frame.grid(row=i, column=2, padx=5, pady=5)
            
    def rebuild_ranking_system(self):
        # Clear the existing ranking labels
        for widget in self.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:  # Skip the header row
                widget.destroy()

        # Create new ranking labels
        self.create_ranking_labels()

        # Toggle the sort switch to update the ranking
        current_sort_state = self.sort_switch_var.get()
        new_sort_state = "working" if current_sort_state == "asking" else "asking"
        self.sort_switch_var.set(new_sort_state)
        self.sort_switch_event()