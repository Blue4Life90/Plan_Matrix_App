# PEP8 Compliant Guidance
# Standard Library Imports
import time
import tkinter as tk

# Third-Party Library Imports
import customtkinter as ctk # type: ignore

# Local Application/Library Specific Imports
from functions.json_functions import save_legend_job_codes
from constants import APP_BG_COLOR, PANE_BG_COLOR, TEXT_COLOR
from constants import ASKING_HRS_FG_COLOR, ASKING_HRS_BG_COLOR
from constants import WORKING_HRS_FG_COLOR, WORKING_HRS_BG_COLOR
from constants import SCROLLBAR_FG_COLOR, SCROLLBAR_HOVER_COLOR
from constants import BUTTON_FG_COLOR, BUTTON_HOVER_BG_COLOR
from TL_WSLegendFrame import WSLegendWindow

class RankingFrame(ctk.CTkFrame):
    def __init__(self, parent, schedule_hrs_frame):
        super().__init__(parent, bg_color=PANE_BG_COLOR, fg_color=PANE_BG_COLOR)
        self.schedule_hrs_frame = schedule_hrs_frame
        self.build_frame()
        # Create a main frame to hold everything
        #self.main_frame = ctk.CTkFrame(self, fg_color=APP_BG_COLOR)
        #self.main_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        #self.main_frame.grid_propagate(False)

    def build_frame(self):
        self.clear_content()

        # Create a main frame to hold everything
        self.main_frame = ctk.CTkFrame(self, fg_color=APP_BG_COLOR)
        self.main_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        if self.schedule_hrs_frame.schedule_type == "Overtime":
            self.build_overtime_frame()
        else:
            self.build_work_schedule_frame()
    
    def build_overtime_frame(self):   
        # Create a canvas and inner frame
        self.canvas = tk.Canvas(self, bg=PANE_BG_COLOR, width=200, height=460, highlightthickness=0)
        self.inner_frame = tk.Frame(self.canvas, bg=PANE_BG_COLOR)

        # Create a scrollbar and configure it
        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview,
                                        fg_color=PANE_BG_COLOR, button_color=SCROLLBAR_FG_COLOR,
                                        button_hover_color=SCROLLBAR_HOVER_COLOR)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the scrollbar and canvas
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.canvas.grid(row=1, column=0, sticky="nsew")

        # Create a window in the canvas for the inner frame
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Create header row
        self.inner_frame.rowconfigure(0, weight=0)  # Don't allow the switch frame to expand
        self.inner_frame.rowconfigure(1, weight=1)  # Don't allow the header row to expand
        self.inner_frame.rowconfigure(2, weight=1)  # Allow the ranking rows to expand
        self.inner_frame.columnconfigure(0, weight=1)  # Allow the header columns to expand horizontally
        self.inner_frame.columnconfigure(1, weight=1)
        self.inner_frame.columnconfigure(2, weight=1)

        self.rowconfigure(0, weight=0)  # Don't allow the switch frame to expand
        self.rowconfigure(1, weight=0)  # Don't allow the header row to expand
        self.rowconfigure(2, weight=0)  # Allow the ranking rows to expand
        self.columnconfigure(0, weight=1)  # Allow the header columns to expand horizontally
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        
        # Create a top frame for the switch label and sort switch
        self.top_frame = ctk.CTkFrame(self.main_frame, fg_color=APP_BG_COLOR)
        self.top_frame.pack(fill="x", padx=5, pady=(5, 2))

        self.switch_label = ctk.CTkLabel(
            self.top_frame, text="Sort by Asking/Working Hours", 
            bg_color=APP_BG_COLOR, text_color=TEXT_COLOR, 
            font=("Calibri", 12)
        )
        self.switch_label.pack(side="left", padx=(0, 5))

        self.sort_switch_var = ctk.StringVar(value="asking") 
        self.sort_switch = ctk.CTkSwitch(
            self.top_frame, text="", command=self.sort_switch_event, 
            variable=self.sort_switch_var, 
            onvalue="asking", offvalue="working", 
            fg_color=WORKING_HRS_FG_COLOR, 
            progress_color=ASKING_HRS_FG_COLOR,
            width=40, height=20
        )
        self.sort_switch.pack(side="left")

        # Create a bottom frame for the "Lowest Asking" label
        self.bottom_frame = ctk.CTkFrame(
            self.main_frame, fg_color=APP_BG_COLOR,
            corner_radius=10
        )
        self.bottom_frame.pack(fill="x", padx=5, pady=(2, 5))

        self.lowest_asking_label = ctk.CTkLabel(
            self.bottom_frame, text="Lowest Asking:",
            bg_color=APP_BG_COLOR, text_color=TEXT_COLOR,
            font=("Calibri", 12, "bold"),
            justify="center"
        )
        self.lowest_asking_label.pack(expand=True, fill="both", padx=10)

        self.create_ranking_labels()
        self.sort_ranking_labels()
        
        for i in range(3):
            self.inner_frame.columnconfigure(i, weight=1)
            
        self.update_idletasks()
        self.update_scrollbar()
        self.delayed_layout_update()
            
    def build_work_schedule_frame(self):
        # Configure the main frame to expand the columns equally
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        self.view_legend_button = ctk.CTkButton(
            self.main_frame,
            text="View Legend",
            command=self.view_legend,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_BG_COLOR,
            text_color=TEXT_COLOR
        )
        self.view_legend_button.grid(row=0, column=0, columnspan=3, padx=20, pady=(10, 5), sticky="ew")
        
        self.define_job_codes_button = ctk.CTkButton(
            self.main_frame,
            text="Define Job Codes",
            command=self.open_define_job_codes_window,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_BG_COLOR,
            text_color=TEXT_COLOR
        )
        self.define_job_codes_button.grid(row=1, column=0, columnspan=3, padx=20, pady=(5, 10), sticky="ew")

    def clear_content(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.main_frame = None
        self.inner_frame = None
        self.canvas = None
        self.scrollbar = None
    
    def view_legend(self):
        self.legend_window = WSLegendWindow(self)
        self.after(100, lambda: center_window(self.legend_window))

    def open_define_job_codes_window(self):
        self.define_job_codes_window = DefineJobCodesWindow(self)
        self.after(100, lambda: center_window(self.define_job_codes_window))
    
    def create_label_frame(self, parent, text, is_working_hours=False, is_name=False):
        frame = ctk.CTkFrame(
            parent, width=30, height=20, 
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
        label.grid(sticky="nsew")
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
            name_frame.grid(row=i, column=0, padx=2, pady=5, sticky="ew", in_=self.inner_frame)

            tw_frame = self.create_label_frame(
                self, total_working_hours, is_working_hours=True
            )
            tw_frame.grid(row=i, column=1, padx=2, pady=5, sticky="ew", in_=self.inner_frame)

            ta_frame = self.create_label_frame(
                self, total_asking_hours, 
                is_name=False, is_working_hours=False
            )
            ta_frame.grid(row=i, column=2, padx=2, pady=5, sticky="ew", in_=self.inner_frame)
            
        self.update_scrollbar()
            
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
        name_frame = self.inner_frame.grid_slaves(row=row_index, column=0)
        if name_frame:
            name_frame[0].winfo_children()[0].configure(text=member_name)
        else:
            name_frame = self.create_label_frame(
                self, member_name, is_name=True
            )
            name_frame.grid(row=row_index, column=0, padx=2, pady=5, sticky="ew", in_=self.inner_frame)

        # Check if the tw frame exists, create it if not
        tw_frame = self.inner_frame.grid_slaves(row=row_index, column=1)
        if tw_frame:
            tw_frame[0].winfo_children()[0].configure(
                text=total_working_hours
            )
        else:
            tw_frame = self.create_label_frame(
                self, total_working_hours, 
                is_working_hours=True
            )
            tw_frame.grid(row=row_index, column=1, padx=2, pady=5, sticky="ew", in_=self.inner_frame)

        # Check if the ta frame exists, create it if not
        ta_frame = self.inner_frame.grid_slaves(row=row_index, column=2)
        if ta_frame:
            ta_frame[0].winfo_children()[0].configure(text=total_asking_hours)
        else:
            ta_frame = self.create_label_frame(
                self, total_asking_hours, 
                is_name=False, is_working_hours=False
            )
            ta_frame.grid(row=row_index, column=2, padx=2, pady=5, sticky="ew", in_=self.inner_frame)

        self.sort_ranking_labels
        
    def update_scrollbar(self):
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            if hasattr(self, 'inner_frame') and self.inner_frame:
                self.inner_frame.update_idletasks()
                canvas_width = self.canvas.winfo_width()
                self.canvas.itemconfig(
                    self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw"),
                    width=canvas_width
                )
                self.inner_frame.config(width=canvas_width)
        
    def delayed_layout_update(self):
        self.after(100, self.update_scrollbar)
    
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

    def sort_ranking_labels(self, sort_key=None, update_lowest=True):
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

        # Find the person with the lowest asking hours and lowest working hours
        if update_lowest and ranking_data:
            lowest_asking_person = min(ranking_data, key=lambda x: x[2])
            lowest_working_person = min(ranking_data, key=lambda x: x[1])

            if self.schedule_hrs_frame.schedule_type == "Work Schedule":
                self.lowest_asking_label.configure(text="")
            else:
                if self.sort_switch_var.get() == "asking":
                    self.lowest_asking_label.configure(text=f"Lowest Asking: {lowest_asking_person[0]}")
                else:
                    self.lowest_asking_label.configure(text=f"Lowest Working: {lowest_working_person[0]}")
        else:
            self.lowest_asking_label.configure(text="")

        # Clear the existing ranking labels
        for widget in self.inner_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:  # Skip the header row
                widget.destroy()

        # Create new ranking labels based on the sorted data
        for i, (member_name, total_working_hours, total_asking_hours) in enumerate(ranking_data, start=2):
            name_frame = self.create_label_frame(
                self, member_name, is_name=True
            )
            name_frame.grid(row=i, column=0, padx=2, pady=5, sticky="ew", in_=self.inner_frame)

            tw_frame = self.create_label_frame(
                self, total_working_hours, is_working_hours=True
            )
            tw_frame.grid(row=i, column=1, padx=2, pady=5, sticky="ew", in_=self.inner_frame)

            ta_frame = self.create_label_frame(
                self, total_asking_hours, 
                is_name=False, is_working_hours=False
            )
            ta_frame.grid(row=i, column=2, padx=2, pady=5, sticky="ew", in_=self.inner_frame)
            
        self.update_scrollbar()
            
    def rebuild_ranking_system(self):
        self.build_frame()
        # Clear the existing ranking labels
        if self.schedule_hrs_frame.schedule_type == "Overtime":
        #for widget in self.inner_frame.grid_slaves():
        #    if int(widget.grid_info()["row"]) > 0:  # Skip the header row
        #        widget.destroy()

            # Create new ranking labels
            self.create_ranking_labels()
            self.sort_ranking_labels()

            # Toggle the sort switch to update the ranking
            current_sort_state = self.sort_switch_var.get()
            new_sort_state = "working" if current_sort_state == "asking" else "asking"
            self.sort_switch_var.set(new_sort_state)
            self.sort_switch_event()
        

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'+{x}+{y}')
    
    # Make multiple attempts to lift the window
    for _ in range(5):
        window.lift()
        window.attributes('-topmost', True)
        window.update()
        time.sleep(0.1)
    window.attributes('-topmost', False)
    window.focus_force()
        
class DefineJobCodesWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent, fg_color=APP_BG_COLOR)
        self.parent = parent
        self.title("Define Legend Job Codes")
        self.configure(bg=APP_BG_COLOR)
        
        self.job_code_entries = []
        self.job_code_numbers = []
        
        self.create_widgets()
        self.bind_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.grab_set()  # This prevents interaction with the main window

    def on_closing(self):
        self.grab_release()
        self.destroy()
    
    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        add_label = ctk.CTkLabel(
            self, text="Enter Job Codes below.", 
            font=("Calibri", 14, "bold"), 
            text_color=TEXT_COLOR
        )
        add_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.add_frame = ctk.CTkFrame(self, fg_color=PANE_BG_COLOR)
        self.add_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.add_frame.columnconfigure(1, weight=1)

        self.add_job_code_entry()  # Add the first entry field

        button_frame = ctk.CTkFrame(self, fg_color=APP_BG_COLOR)
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        add_another_button = ctk.CTkButton(
            button_frame, text="+ (Tab)", command=self.add_job_code_entry, 
            font=("Calibri", 14, "bold"),
            fg_color="#047a1b", 
            hover_color="#02a120", 
            text_color="white"
        )
        add_another_button.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        
        remove_last_button = ctk.CTkButton(
            button_frame, text="- (Ctrl+z)", 
            command=self.remove_job_code_entry,
            font=("Calibri", 14, "bold"),
            fg_color="#7a0404", 
            hover_color="#a10202", 
            text_color="white"
        )
        remove_last_button.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")

        confirm_button = ctk.CTkButton(
            button_frame, text="Save", command=self.save_job_codes, 
            fg_color=BUTTON_FG_COLOR, 
            hover_color=BUTTON_HOVER_BG_COLOR, 
            text_color=TEXT_COLOR
        )
        confirm_button.grid(row=1, column=0, padx=(0, 5), pady=5, sticky="ew")
        
        cancel_button = ctk.CTkButton(
            button_frame, text="Cancel", command=self.cancel, 
            fg_color=BUTTON_FG_COLOR, 
            hover_color=BUTTON_HOVER_BG_COLOR, 
            text_color=TEXT_COLOR
        )
        cancel_button.grid(row=1, column=1, padx=(5, 0), pady=5, sticky="ew")
        
    def bind_shortcuts(self):
        self.bind("<Tab>", lambda event: self.add_job_code_entry())
        self.bind("<Control-z>", lambda event: self.remove_job_code_entry())
    
    def add_job_code_entry(self):
        index = len(self.job_code_entries) + 1
        
        number_label = ctk.CTkLabel(
            self.add_frame, 
            text=str(index), 
            width=30, 
            text_color="white",
            font=("Calibri", 14, "bold")
        )
        number_label.grid(row=index-1, column=0, padx=(0, 10), pady=5, sticky="e")
        self.job_code_numbers.append(number_label)
        
        entry = ctk.CTkEntry(self.add_frame, width=200)
        entry.grid(row=index-1, column=1, padx=(0, 5), pady=5, sticky="ew")
        self.job_code_entries.append(entry)
        
    def remove_job_code_entry(self):
        if len(self.job_code_entries) > 1:
            entry = self.job_code_entries.pop()
            number = self.job_code_numbers.pop()
            entry.destroy()
            number.destroy()
        
    def save_job_codes(self):
        job_codes = {}
        for number, entry in zip(self.job_code_numbers, self.job_code_entries):
            job_code_id = number.cget("text")
            job_code_name = entry.get()
            if job_code_name:  # Only save non-empty job codes
                job_codes[job_code_id] = job_code_name
        
        save_legend_job_codes(job_codes)
        self.destroy()
        self.parent.view_legend()  # Open the legend window with updated job codes
    
    def cancel(self):
        self.destroy()
     
        
# Mock ScheduleHrsFrame
class MockScheduleHrsFrame:
    def __init__(self):
        #self.schedule_type = "work_schedule"
        self.schedule_type = "Overtime"
        self.frames = [MockMemberFrame() for _ in range(5)]  # Create 5 mock member frames

class MockMemberFrame:
    def __init__(self):
        self.labels = [ctk.CTkLabel(None, text="Mock Member")]
        self.starting_working_hours = 40
        self.working_hours_entries = [ctk.CTkEntry(None) for _ in range(7)]
        self.asking_hours_tracking = [ctk.CTkLabel(None, text="50")]

# Main application
class TestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RankingFrame Test")
        self.geometry("300x500")

        self.schedule_hrs_frame = MockScheduleHrsFrame()
        self.ranking_frame = RankingFrame(self, self.schedule_hrs_frame)
        self.ranking_frame.pack(expand=True, fill="both", padx=10, pady=10)

if __name__ == "__main__":
    app = TestApp()
    app.mainloop()