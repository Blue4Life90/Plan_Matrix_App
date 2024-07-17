# PEP8 Compliant Guidance
# Standard Library Imports
import logging
import datetime
import tkinter as tk
from tkinter import messagebox

# Third-Party Library Imports
import customtkinter as ctk # type: ignore

# Local Application/Library Specific Imports
from functions.app_functions import lock_widgets
from functions.app_functions import apply_entry_color_specs
from functions.app_functions import lock_and_color_entry_widgets
from functions.json_functions import load_hours_data_from_json, save_hours_data_to_json
from constants import log_file
from constants import APP_BG_COLOR, TEXT_COLOR
from constants import SCROLLBAR_FG_COLOR, SCROLLBAR_HOVER_COLOR
from HdrDateGrid import HdrDateGrid
from OvertimeSlots import OvertimeSlots
from OvertimeSlots import load_overtime_slots
from CrewMemberHours import CrewMemberHours
from HrsMatrixFrame import HrsMatrixFrame
from TLScheduleManager import TLScheduleManager
from WorkbookDataLoader import WorkbookDataLoader
from WorkScheduleMatrixFrame import WorkScheduleMatrixFrame

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    filename=log_file, filemode='a'
)

class ScheduleHrsFrame(tk.Frame):
    """
    A frame that displays and manages the schedule hours for crew members.

    This class creates a grid of frames, each representing a crew member and their
    working and asking hours for each day of the month. It provides functionality to
    load and save data from/to an Excel workbook, update the display based on user
    selections, and allow editing of member data through the schedule manager.

    The frame includes a canvas with a scrollbar to accommodate a large number of crew
    members and ensure proper visibility and navigation.

    Attributes:
        parent (tk.Tk): The parent window.
        hdr_date_grid (HdrDateGrid): The header date grid.
        ranking_frame (RankingFrame): The frame displaying the ranking system.
        member_count_file (str): The path to the file storing the member count.
        member_data_file (str): The path to the file storing the member data.
        member_count (int): The number of crew members.
        initial_names (list): The list of initial crew member names.
        frames (list): The list of frames representing each crew member.
        user_selections (dict): The user's selected schedule date and crew.
        canvas (tk.Canvas): The canvas widget for displaying the frames.
        inner_frame (tk.Frame): The inner frame within the canvas.
        scrollbar (tk.Scrollbar): The scrollbar widget for the canvas.

    Methods:
        load_workbook_data(workbook_filename, worksheet_name): Load data from the specified workbook and worksheet.
        save_workbook_data(workbook_filename, worksheet_name): Save the current data to the specified workbook and worksheet.
        create_frames(): Create the frames for displaying member data.
        save_member_data(): Save the member data to the workbook.
        update_scrollbar(): Update the scrollbar and canvas configuration.
        get_labels(): Retrieve the labels from the frames and store them in initial_names.
        open_window(): Open the schedule manager window.
        on_mousewheel(event): Handle the mousewheel event to scroll the canvas.
        on_canvas_configure(event): Update the canvas configuration when the window is resized.
    """
    
    def __init__(self, parent, hdr_date_grid, ranking_frame, user_selections, schedule_type, access_level, app):
        """
        Initialize the ScheduleHrsFrame.

        Args:
            parent (tk.Tk): The parent window.
            hdr_date_grid (HdrDateGrid): The header date grid.
            ranking_frame (RankingFrame): The frame displaying the ranking system.
            user_selections (dict): The user's selected schedule date and crew.
        """    
        super().__init__(parent, relief="flat", borderwidth=2, 
                         bg=APP_BG_COLOR, padx=10, pady=10)
        self.parent = parent
        self.hdr_date_grid = hdr_date_grid
        self.ranking_frame = ranking_frame
        self.user_selections = user_selections
        self.schedule_type = schedule_type
        self.crew_member_hours = {}
        crew_data = load_hours_data_from_json(self.user_selections['selected_crew'], self.user_selections['selected_month'].month, self.user_selections['selected_year'].year, schedule_type)
        self.crew_member_count = len(crew_data)
        self.initial_names = []
        self.frames = []
        self.work_schedule_frames = []
        self.access_level = access_level
        self.app = app
        self.frames_created = tk.BooleanVar(value=False)
        
        # Create a canvas and inner frame
        self.canvas = tk.Canvas(self, bg=APP_BG_COLOR, 
                                width=800, height=650,  # Add initial width and height
                                highlightthickness=0)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.inner_frame = tk.Frame(self.canvas, bg=APP_BG_COLOR)

        # Create a scrollbar and configure it
        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview, 
                                          fg_color=APP_BG_COLOR, button_color=SCROLLBAR_FG_COLOR, 
                                          button_hover_color=SCROLLBAR_HOVER_COLOR)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a window in the canvas for the inner frame
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.create_frames()
        self.get_labels()

        # Configure the canvas to expand and fill
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def destroy_overtime_section(self):
        if hasattr(self, 'overtime_slot_title_frame'):
            self.overtime_slot_title_frame.destroy()
            self.overtime_slot_title_frame = None
        if hasattr(self, 'overtime_frame'):
            self.overtime_frame.destroy()
            self.overtime_frame = None
    
    def load_workbook_data(self, json_filename, worksheet_name, schedule_type):
        """
        Load data from the JSON file.

        Args:
            json_filename (str): The filename of the JSON file.
            worksheet_name (str): The name of the worksheet (used to extract the month number).
            schedule_type (str): The schedule type ("Overtime" or "work_schedule").

        Returns:
            list[tuple]: A list of tuples containing the loaded data for each member.
        """
        try:
            self.crew_member_hours = load_hours_data_from_json(self.user_selections['selected_crew'], self.user_selections['selected_month'].month, self.user_selections['selected_year'].year, schedule_type)

            month_number = int(worksheet_name.split(" ")[1])

            if schedule_type == "Overtime":
                data = []
                for name, crew_member in self.crew_member_hours.items():
                    hours_data = crew_member.get_hours(month_number)
                    starting_asking_hours = hours_data.get('starting_asking_hours', 0)
                    starting_working_hours = hours_data.get('starting_working_hours', 0)
                    entry_data = hours_data.get('entry_data', [('', '')] * 31)
                    data.append((name, starting_asking_hours, starting_working_hours, entry_data))
                return data
            
            elif schedule_type == "work_schedule":
                data = []
                for name, crew_member in self.crew_member_hours.items():
                    hours_data = crew_member.get_hours(month_number)
                    role_data = hours_data.get('role_data', [''] * 31)  # Default to empty roles if missing
                    data.append((name, role_data))
                if not data:
                    # Return default data if no data is found
                    data = [("", [''] * 31)]
                return data
        except Exception as e:
            logging.error(f"An error occurred while loading data from JSON file: {str(e)}")
            return []
    
    def save_workbook_data(self, worksheet_name):
        """
        Save the current data to the JSON file.

        Args:
            worksheet_name (str): The name of the worksheet (used to extract the month number).
        """
        try:
            month_number = worksheet_name
            month_str = str(month_number)

            if self.schedule_type == "Overtime":
                for i, frame in enumerate(self.frames, start=2):
                    name = frame.labels[0].cget("text")
                    if name not in self.crew_member_hours:
                        self.crew_member_hours[name] = CrewMemberHours(name)
                    
                    member = self.crew_member_hours[name]

                    # Retrieve the existing starting hours and total hours from the JSON file
                    existing_data = load_hours_data_from_json(self.user_selections['selected_crew'], self.user_selections['selected_month'].month, self.user_selections['selected_year'].year, self.schedule_type)
                    existing_member_data = existing_data.get(name)
                    if existing_member_data:
                        existing_monthly_hours = existing_member_data.monthly_hours
                        starting_asking_hours = existing_monthly_hours.get('starting_asking_hours', 0)
                        starting_working_hours = existing_monthly_hours.get('starting_working_hours', 0)
                        total_asking_hours = existing_monthly_hours.get('total_asking_hours', 0)
                        total_working_hours = existing_monthly_hours.get('total_working_hours', 0)
                    else:
                        starting_asking_hours = 0
                        starting_working_hours = 0
                        total_asking_hours = 0
                        total_working_hours = 0

                    member.monthly_hours = {
                        'starting_asking_hours': starting_asking_hours,
                        'starting_working_hours': starting_working_hours,
                        'total_asking_hours': total_asking_hours,
                        'total_working_hours': total_working_hours,
                        'asking_hours_data': [],
                        'working_hours_data': []
                    }

                    monthly_hours = member.monthly_hours
                    working_hours_data = [entry.get() for entry in frame.working_hours_entries]
                    asking_hours_data = [entry.get() for entry in frame.asking_hours_entries]

                    monthly_hours['working_hours_data'] = working_hours_data
                    monthly_hours['asking_hours_data'] = asking_hours_data

                    #TODO: Revise so that it adds the actual starting hours to the total
                    #The value of 'member.monthly_hours' will always keep starting hours at 0 so
                    #it can't work.
                    monthly_hours['total_working_hours'] = sum(
                        int(hours) for hours in working_hours_data if hours.isdigit()
                    ) + int(monthly_hours['starting_working_hours'])
                    
                    monthly_hours['total_asking_hours'] = (
                        sum(int(hours) for hours in asking_hours_data if hours.strip()) +
                        sum(int(hours) for hours in working_hours_data if hours.strip()) +
                        int(monthly_hours['starting_asking_hours'])
)
                save_hours_data_to_json(self.crew_member_hours, self.user_selections['selected_crew'], self.user_selections['selected_year'].year, self.schedule_type, month_number)
                
            elif self.schedule_type == "work_schedule":
                for i, frame in enumerate(self.work_schedule_frames, start=2):
                    name = frame.labels[0].cget("text")
                    if name not in self.crew_member_hours:
                        self.crew_member_hours[name] = CrewMemberHours(name)

                    member = self.crew_member_hours[name]

                    # Ensure monthly hours are initialized
                    if month_str not in member.monthly_hours:
                        member.monthly_hours[month_str] = {
                            'entry_data': []
                        }

                    role_data = [entry.get() for entry in frame.crew_member_role_entries]
                    member.monthly_hours[month_str]['entry_data'] = role_data

                save_hours_data_to_json(self.crew_member_hours, self.user_selections['selected_crew'], self.user_selections['selected_year'].year, self.schedule_type, month_number)
                self.overtime_frame.save_overtime_data()

        except Exception as e:
            logging.error(f"An error occurred while saving data to JSON file: {str(e)}")
            messagebox.showerror("Error", "An error occurred while saving the data.")

    
    #TODO: Testing Phase
    def reset_hours_for_new_year(self):
        if self.schedule_type == "Overtime":
            prev_year = self.user_selections['selected_year'].year - 1
            prev_crew = self.user_selections['selected_crew']
            prev_year_data = load_hours_data_from_json(prev_crew, prev_year, self.schedule_type)
            ranking_data = [(name, member.monthly_hours[12]['total_working_hours'], member.monthly_hours[12]['total_asking_hours'])
                            for name, member in prev_year_data.items()]
            ranking_data.sort(key=lambda x: x[1])
            working_hours_ranks = {name: rank for rank, (name, _, _) in enumerate(ranking_data)}
            ranking_data.sort(key=lambda x: x[2])
            asking_hours_ranks = {name: rank for rank, (name, _, _) in enumerate(ranking_data)}
            
            current_year = self.user_selections['selected_year'].year
            current_crew = self.user_selections['selected_crew']
            current_year_data = self.crew_member_hours
            
            for name, member in current_year_data.items():
                member.monthly_hours[1]['starting_working_hours'] = working_hours_ranks[name]
                member.monthly_hours[1]['starting_asking_hours'] = asking_hours_ranks[name]
                member.monthly_hours[1]['total_working_hours'] = working_hours_ranks[name]
                member.monthly_hours[1]['total_asking_hours'] = asking_hours_ranks[name]
            
            save_hours_data_to_json(current_year_data, current_crew, current_year, self.schedule_type, 1)
                
    def recalculate_hours(self, name, start_month, adjustment):
        # Recalculate starting hours and total hours for subsequent months
        crew_member = self.crew_member_hours.get(name)
        if crew_member:
            for month in range(start_month, 13):
                # Retrieve the hours data for the current month
                hours_data = crew_member.get_hours(month)
                
                # Update the total hours based on the adjustment
                updated_total_asking_hours = hours_data['total_asking_hours'] + adjustment
                updated_total_working_hours = hours_data['total_working_hours'] + adjustment
                
                # Update the starting hours for the next month
                if month < 12:
                    next_month_data = crew_member.get_hours(month + 1)
                    next_month_data['starting_asking_hours'] = updated_total_asking_hours
                    next_month_data['starting_working_hours'] = updated_total_working_hours
                
                # Update the hours data in the crew_member_hours dictionary
                crew_member.update_hours(month, hours_data['starting_asking_hours'], hours_data['starting_working_hours'],
                                        updated_total_asking_hours, updated_total_working_hours)
    
    def create_frames(self):
        """
        Create or update the frames for displaying member data.

        This method starts a separate thread to load the workbook data and updates
        the existing frames with the loaded data. If no frames exist, it creates new frames.

        If an exception occurs during the process, an error message is logged and displayed
        to the user.
        """
        self.frames_created.set(False)
        data_loader = WorkbookDataLoader(self)
        data_loader.start()
    
    def update_frames(self, user_selections):
        if self.schedule_type == "Overtime":
            for frame in self.frames:
                frame.update_tracking_file(user_selections)
        elif self.schedule_type == "work_schedule":
            for frame in self.work_schedule_frames:
                frame.update_tracking_file(user_selections)
    
    def create_overtime_section(self):
        self.overtime_slot_title_frame = tk.Frame(self.inner_frame, bg=APP_BG_COLOR)
        self.overtime_slot_title_frame.pack(fill="x", pady=(10, 0))
        title_label = tk.Label(self.overtime_slot_title_frame, text="Scheduled Overtime", font=("Calibri", 14, "bold"), bg=APP_BG_COLOR, fg=TEXT_COLOR)
        title_label.pack()

        overtime_data, num_slots = load_overtime_slots(
            self.user_selections["selected_crew"], 
            self.user_selections["selected_month"].month, 
            self.user_selections["selected_year"].year
        )
        self.overtime_frame = OvertimeSlots(self.inner_frame, self.hdr_date_grid, self.user_selections, num_slots)
        self.overtime_frame.pack(fill="x", expand=False, pady=(5, 10))
        self.overtime_frame.load_overtime_data()

    def data_loaded(self, data, exception):
        if exception:
            messagebox.showerror("Error", "An error occurred while loading member data.")
            return

        if data is None or len(data) == 0:
            messagebox.showinfo("No Data", "No crew data archived, please use Schedule Manager\nto begin adding data.")

        self.destroy_frames()

        if self.schedule_type == "Overtime":
            self.frames = []
            for name, item in data.items():
                monthly_hours = item.monthly_hours
                starting_asking_hours = monthly_hours.get('starting_asking_hours')
                starting_working_hours = monthly_hours.get('starting_working_hours')
                working_hours_data = monthly_hours.get('working_hours_data', [])
                asking_hours_data = monthly_hours.get('asking_hours_data', [])

                frame = HrsMatrixFrame(self.inner_frame, name, self.hdr_date_grid, self.ranking_frame, starting_asking_hours, starting_working_hours, self.user_selections)
                frame.pack(pady=5, fill="x")
                self.frames.append(frame)

                for j, working_hours in enumerate(working_hours_data):
                    working_hours_entry = frame.working_hours_entries[j]
                    working_hours_entry.delete(0, tk.END)
                    working_hours_entry.insert(0, working_hours)

                for j, asking_hours in enumerate(asking_hours_data):
                    asking_hours_entry = frame.asking_hours_entries[j]
                    asking_hours_entry.delete(0, tk.END)
                    asking_hours_entry.insert(0, asking_hours)

                frame.update_column_sums(None)
                frame.labels[0].config(text=name)

            if self.access_level == "read-only":
                for frame in self.frames:
                    lock_widgets(frame)
        else:
            self.work_schedule_frames = []
            for name, item in data.items():
                monthly_hours = item.monthly_hours
                entry_data = monthly_hours.get('entry_data', [])

                frame = WorkScheduleMatrixFrame(self.inner_frame, name, self.hdr_date_grid, self.ranking_frame, self.user_selections)
                frame.pack(pady=5, fill="x")
                self.work_schedule_frames.append(frame)

                for j, role in enumerate(entry_data):
                    entry = frame.crew_member_role_entries[j]
                    entry.delete(0, tk.END)
                    entry.insert(0, role)
                    apply_entry_color_specs(entry, role)

            self.destroy_overtime_section()
            self.create_overtime_section()

            if self.access_level == "read-only":
                for frame in self.work_schedule_frames:
                    lock_and_color_entry_widgets(frame)

        self.update_scrollbar()
        self.get_labels()
        self.adjust_canvas_size()

        if self.ranking_frame:
            self.ranking_frame.rebuild_ranking_system()

        def check_frames_created():
            if self.schedule_type == "Overtime":
                if len(self.frames) == self.crew_member_count:
                    self.frames_created.set(True)
                else:
                    self.after(100, check_frames_created)
            elif self.schedule_type == "work_schedule":
                if len(self.work_schedule_frames) == self.crew_member_count:
                    self.frames_created.set(True)
                else:
                    self.after(100, check_frames_created)

        check_frames_created()

    def destroy_frames(self):
        # Destroy existing HrsMatrixFrame instances
        if self.frames:
            for frame in self.frames:
                frame.destroy()
            self.frames.clear()

        # Destroy existing WorkScheduleMatrixFrame instances
        if self.work_schedule_frames:
            for frame in self.work_schedule_frames:
                frame.destroy()
                self.overtime_frame.destroy()
                self.overtime_slot_title_frame.destroy()
                
            self.work_schedule_frames.clear()
    
    def adjust_canvas_size(self):
        self.update_idletasks()
        self.canvas.configure(width=self.inner_frame.winfo_reqwidth() + 25)
        self.canvas.configure(height=min(self.inner_frame.winfo_reqheight(), 650))
    
    def save_member_data(self):
        """
        Save the member data to the workbook.

        This method retrieves the workbook and worksheet information based on the user's
        selections and calls the `save_workbook_data` method to save the current data.

        If an exception occurs during the process, an error message is logged and displayed
        to the user.
        """

        self.selected_month = self.user_selections['selected_month'].month
        self.save_workbook_data(self.selected_month)
        if self.schedule_type == "work_schedule":
            self.overtime_frame.save_overtime_data()
        self.app.display_save_status()  # Ensure the save status is displayed

    def update_scrollbar(self):
        """
        Update the scrollbar and canvas configuration.

        This method updates the scrollbar and canvas configuration based on the current
        size of the inner frame. It adjusts the scroll region and the size of the canvas
        window to accommodate the content of the inner frame.
        """
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

    def get_labels(self):
        """
        Retrieve the labels from the frames and store them in initial_names.
        """        
        if self.schedule_type == "Overtime":
            self.initial_names = [
                name 
                for frame in self.frames 
                for name in frame.ot_get_names_from_labels()
            ]
        elif self.schedule_type == "work_schedule":
            self.initial_names = [
                name 
                for frame in self.work_schedule_frames 
                for name in frame.ws_get_names_from_labels()
            ]

    def open_window(self):
        """
        Open the schedule manager window.
        """
        self.schedule_manager = TLScheduleManager(self.parent, 
                                             self.initial_names, 
                                             self, 
                                             self.user_selections,
                                             self.schedule_type, 
                                             self.crew_member_count
        )
        self.schedule_manager.transient(self.parent)  # Set the schedule manager window as transient
        self.schedule_manager.grab_set()  # Grab the focus to keep the schedule manager window in front

        # Retrieve listed names from the schedules
        self.get_labels()
        
        # Update the ranking labels
        if self.ranking_frame:
            self.ranking_frame.create_ranking_labels()
        
    def on_mousewheel(self, event):
        """
        Handle the mousewheel event to scroll the canvas.

        This method is triggered when the user scrolls the mousewheel within the canvas.
        It adjusts the canvas view based on the scroll direction and speed.

        Args:
            event (tk.Event): The mousewheel event object.
        """
        try:
            # Check if the canvas is active and not a top-level window
            if self.canvas.winfo_exists() and self.canvas.winfo_viewable():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            # Handle the TclError exception
            pass
    
    def on_canvas_configure(self, event):
        """
        Update the canvas configuration when the window is resized.

        This method is triggered when the canvas is resized due to window resizing.
        It adjusts the scroll region and the size of the inner frame to match the new canvas size.

        Args:
            event (tk.Event): The canvas configure event object.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(
            self.canvas.create_window((0, 0), 
                                      window=self.inner_frame, 
                                      anchor="nw"
                                      ),
                            width=self.canvas.winfo_width() - self.scrollbar.winfo_width() - 5,
                            height=self.inner_frame.winfo_reqheight()
        )
        self.adjust_canvas_size() 




# For testing...
class TestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Schedule Hours Frame Test")

        # Create instances of the required objects (replace with your own instances)
        ranking_frame = None
        user_selections = {
            'selected_crew': 'A',
            'selected_month': datetime.datetime(2023, 6, 1),  # Provide the month as a datetime object
            'selected_year': datetime.datetime(2023, 1, 1)  # Provide the year as a datetime object
        }
        self.schedule_type = "Overtime"  # Change to "work_schedule" if needed

        # Create an instance of the HdrDateGrid
        self.hdr_date_grid = HdrDateGrid(
            self, user_selections
        )
        self.hdr_date_grid.pack(expand=True, fill="both")
        
        self.access_level = "admin"

        # Create an instance of the ScheduleHrsFrame
        self.schedule_hrs_frame = ScheduleHrsFrame(
            self,
            hdr_date_grid=self.hdr_date_grid,
            ranking_frame=ranking_frame,
            user_selections=user_selections,
            schedule_type=self.schedule_type,
            access_level=self.access_level
        )
        self.schedule_hrs_frame.pack(expand=True, fill="both")

        # Adjust the canvas size after the app is displayed
        self.after(0, self.adjust_canvas_size)

        # Create a button to open the schedule manager window
        open_window_button = tk.Button(
            self,
            text="Open Schedule Manager",
            command=self.schedule_hrs_frame.open_window
        )
        open_window_button.pack()

        # Create a button to save the member data
        save_button = tk.Button(
            self,
            text="Save Member Data",
            command=self.schedule_hrs_frame.save_member_data
        )
        save_button.pack()

        # Test loading data
        self.test_load_data()

    def adjust_canvas_size(self):
        self.update_idletasks()
        required_width = self.schedule_hrs_frame.inner_frame.winfo_reqwidth() + 25
        self.schedule_hrs_frame.canvas.configure(width=max(required_width, self.hdr_date_grid.winfo_reqwidth()))
        self.schedule_hrs_frame.canvas.configure(height=min(self.schedule_hrs_frame.inner_frame.winfo_reqheight(), 650))

    def test_load_data(self):
        crew = self.schedule_hrs_frame.user_selections['selected_crew']
        month = self.schedule_hrs_frame.user_selections['selected_month'].month
        year = self.schedule_hrs_frame.user_selections['selected_year'].year
        schedule_type = self.schedule_hrs_frame.schedule_type

        data = load_hours_data_from_json(crew, month, year, schedule_type)

        # Simulate passing this data to ScheduleHrsFrame
        self.schedule_hrs_frame.data_loaded(data, None)


if __name__ == "__main__":
    app = TestApp()
    app.mainloop()