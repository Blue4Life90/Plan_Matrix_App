# PEP8 Compliant Guidance
# Standard Library Imports
import os
import sys
import csv
import time
import logging
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from datetime import datetime
from tkinter import messagebox
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Third-Party Library Imports
import customtkinter as ctk # type: ignore

# Local Application/Library Specific Imports
import constants
from constants import log_file
from constants import prompt_shared_path
from PathConfig import save_shared_path
import functions.header_functions as header_functions
from functions.app_functions import lock_widgets
from functions.header_functions import get_user_id
from functions.login_functions import load_user_access_levels
from functions.app_functions import center_toplevel_window, forward_outlook_email
from HeaderFrame import HeaderFrame
from HdrDateGrid import HdrDateGrid
from ScrolledFrame import ScrolledFrame
from RankingFrame import RankingFrame
from UserAccess import User, LoginWindow
from ScheduleHrsFrame import ScheduleHrsFrame
from AppButtonsFrame import LeftPaneButtonFrame
from AccessLevelManager import AccessLevelManager
from TLSelectScheduleDate import TLSelectScheduleDate

shared_path = prompt_shared_path()

registry_directory = os.path.normpath(os.path.join(shared_path, "SaveFiles", "UserRegistry"))
ACCESS_LEVEL_ENCRYPTION = os.path.normpath(os.path.join(registry_directory, "access_levels.enc"))
USER_REGISTRY_DIR = os.path.normpath(os.path.join(shared_path, "SaveFiles", "UserRegistry"))
USER_ID_FILE = os.path.normpath(os.path.join(USER_REGISTRY_DIR, "user_id.csv"))

log_directory = os.path.normpath(os.path.join(shared_path, "SaveFiles", "TrackingLogs"))

# Create directories if they don't exist
try:
    os.makedirs(log_directory, exist_ok=True)
    os.makedirs(registry_directory, exist_ok=True)
    
    if not os.path.exists(log_file):
        open(log_file, 'w').close()
    if not os.path.exists(ACCESS_LEVEL_ENCRYPTION):
        open(ACCESS_LEVEL_ENCRYPTION, 'w').close()
    if not os.path.exists(USER_ID_FILE):
        with open(USER_ID_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password_hash', 'remember_me'])  # Write header row
except OSError as e:
    messagebox.showerror("Error", f"Failed to create files: {str(e)}")
    logging.error(f"Failed to create files: {str(e)}")
    exit(1)

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file,
                    filemode='a')

class App(tk.Tk):
    """
    The main application window.

    This class represents the main window of the scheduling application. It is responsible for
    creating and managing the various frames and widgets that make up the user interface.

    Attributes:
        member_count_file (str): The path to the file containing member count data.

        title_frame (HeaderFrame): The frame displaying the header information.
        schedule_hrs_frame (ScheduleHrsFrame): The frame displaying the schedule hours.
        ranking_frame (RankingFrame): The frame displaying the ranking system.
        hdr_date_grid (HdrDateGrid): The widget displaying the date grid in the header.
        user_selections (dict): The user's selected schedule date and crew.

    Methods:
        configure_app_menu_bar(): Configures the application menu bar.
        pass_values(user_selections: dict): Passes the selected values and updates the UI.
        add_left_pane_frame(): Adds the left pane frame and buttons to the main window.
        get_open_schedule_manager_method(): Returns the method to open the schedule manager.
        get_save_member_data_method(): Returns the method to save member data.
        get_schedule_selection_menu_method(): Returns the method to open the schedule selection menu.
        set_title_frame(user_selections: dict): Sets up the title frame.
        set_hours_frame(user_selections: dict): Sets up the hours frame.
        load_ranking_system(): Loads the ranking system.
        open_input_window(): Opens the input window for selecting the schedule date and crew.
        load_schedule_from_file(): Loads the schedule from a file.
        select_schedule_type(): Opens the menu to switch between overtime and work schedules.
        save_schedule_data(): Saves the schedule data.
        open_schedule_manager(): Opens the schedule manager.
        show_about(): Displays the about information.
        contact_for_help(): Opens an email to contact for help.
    """
    def __init__(self):
        """
        Initialize the main application window.

        This method sets up the main window, configures the layout, and initializes the
        necessary attributes and widgets.
        """
        super().__init__()
        self.title("Plan_Matrix")
        
        self.configure(background=constants.APP_BG_COLOR)
        self.iconify()
        
        # Load icons after the root window is initialized
        self.iconpath_0, self.iconpath_1, self.iconpath_2 = constants.load_icons()
        self.iconphoto(False, self.iconpath_0)  # Set the icon for the main window
        
        self.title_frame = None
        
        self.schedule_hrs_frame = None
        self.ranking_frame = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Check if the current user is a verified user
        self.current_user_id = get_user_id()
        
        # Initialize self.current_user with a default User instance
        self.current_user = User("", "", "read-only")
        
        # Create a loading overlay
        self.loading_overlay = tk.Frame(self, bg="white")
        self.loading_overlay.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        loading_label = tk.Label(self.loading_overlay, text="Loading, please wait...")
        loading_label.pack(pady=20)
        
        # Schedule the login process to run after the main window is displayed
        self.after(0, self.show_login_window)
        
        self.autosave_var = tk.BooleanVar(value=False)
            
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.bottom_frame = ctk.CTkFrame(self, fg_color=constants.APP_BG_COLOR)
        self.bottom_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        self.clock_label = ctk.CTkLabel(self.bottom_frame, text="Clock: ", font=("Calibri", 12), text_color=constants.TEXT_COLOR)
        self.clock_label.pack(side=tk.RIGHT, padx=10)
        
        self.autosave_label = ctk.CTkLabel(self.bottom_frame, text="Autosave: Off", font=("Calibri", 12), text_color=constants.TEXT_COLOR)
        self.autosave_label.pack(side=tk.RIGHT, padx=10)
        
        self.save_status_label = ctk.CTkLabel(self.bottom_frame, text="", font=("Calibri", 12), text_color="green")
        self.save_status_label.pack(side=tk.LEFT, padx=10)
        
        self.start_clock_thread()  # Start the clock thread
        
    def start_clock_thread(self):
        clock_thread = threading.Thread(target=self.update_clock)
        clock_thread.daemon = True
        clock_thread.start()
    
    def update_clock(self):
        while True:
            current_time = datetime.now().strftime("%B %d, %Y %H:%M:%S")
            try:
                self.clock_label.configure(text=f"{current_time}")
            except tk.TclError:
                # Handle the case when the label is no longer accessible
                break
            time.sleep(1) # Pause for 1 second before the next update
    
    def display_save_status(self):
        self.save_status_label.configure(text="Schedule AutoSaved Successfully")
        self.after(5000, self.clear_save_status)

    def clear_save_status(self):
        self.save_status_label.configure(text="")
    
    def hide_loading_overlay(self):
        if hasattr(self, 'loading_overlay') and self.loading_overlay.winfo_exists():
            self.loading_overlay.destroy()
    
    def load_user_access_levels(self):
        load_user_access_levels()
    
    def update_header_frame_labels(self, schedule_type):
        if self.title_frame:
            self.title_frame.update_labels(schedule_type)
               
    def initialize_application(self):
        """
        Initialize the main application window components.
        """
        # Allow child widgets to expand and contract to fit the grid
        for child in self.winfo_children():
            if not isinstance(child, LoginWindow):  # Skip LoginWindow instances
                child.grid_configure(sticky="nsew")
        
        self.add_left_pane_frame()
        self.configure_app_menu_bar()
        self.open_input_window()
        
        # Ensure all widgets are fully loaded
        self.update_idletasks()
    
    def show_login_window(self):
        """
        Show the login window for the user to log in or register.
        """
        self.login_window = LoginWindow(self)
        self.wait_window(self.login_window)
        
    def create_admin_menu(self):
        self.admin_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.admin_menu.add_command(label="Log File", command=self.open_log_file)
        self.admin_menu.add_command(label="UserID CSV", command=self.open_user_id_csv)
        self.menu_bar.add_cascade(label="Administrator", menu=self.admin_menu)
        
    def open_log_file(self):
        log_file_path = constants.log_file
        os.startfile(log_file_path)

    def open_user_id_csv(self):
        user_id_file_path = constants.USER_ID_FILE
        os.startfile(user_id_file_path)
    
    def disable_menu_options(self):
        # Disable menu options based on access level
        self.file_menu.entryconfig("Save", state="disabled")
        self.file_menu.entryconfig("Auto Save", state="disabled")
        self.edit_menu.entryconfig("Open Schedule Manager", state="disabled")
        self.edit_menu.entryconfig("Manage Access Levels", state="disabled")
        self.view_menu.entryconfig("Navigation Pane", state="disabled")

    def enable_menu_options(self):
        # Enable menu options based on access level
        self.file_menu.entryconfig("Save", state="normal")
        self.autosave_var.set(True)
        self.file_menu.entryconfig("Auto Save", state="normal", variable=self.autosave_var, onvalue=True, offvalue=False)
        self.update_autosave_label()
        self.edit_menu.entryconfig("Open Schedule Manager", state="normal")

    def toggle_nav_pane(self):
        if self.left_pane_frame.winfo_viewable():
            self.left_pane_frame.grid_forget()
            if hasattr(self, 'left_pane_button_frame') and self.left_pane_button_frame.winfo_exists():
                self.left_pane_button_frame.destroy()
        else:
            self.left_pane_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")
            self.left_pane_button_frame = LeftPaneButtonFrame(
                self.left_pane_frame,
                self.get_open_schedule_manager_method(),
                self.get_save_member_data_method(),
                self.get_schedule_selection_menu_method(),
                self.schedule_hrs_frame.schedule_type if self.schedule_hrs_frame else None
            )
            self.left_pane_button_frame.grid(row=0, column=0, sticky="nsew")
    
    def configure_app_menu_bar(self):
        """
        Configure the application menu bar.

        This method sets up the menu bar with File, Edit, and Help menus, and their respective
        menu items and associated commands.
        """
        self.menu_bar = tk.Menu(self)
        
        # Create a File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        
        self.file_menu.add_command(label="Select Schedule Date", command=self.load_schedule_from_file)
        
        # Create a submenu for Schedule Type
        self.schedule_type_menu = tk.Menu(self.file_menu, tearoff=0)
        self.schedule_type_menu.add_command(label="Overtime", command=self.select_overtime_schedule)
        self.schedule_type_menu.add_command(label="Work Schedule", command=self.select_work_schedule)

        # Add the Schedule Type submenu to the File menu
        self.file_menu.add_cascade(label="Schedule Type", menu=self.schedule_type_menu)
        
        self.file_menu.add_command(label="Save", command=self.save_schedule_data)
        self.file_menu.add_checkbutton(label="Auto Save", variable=self.autosave_var, command=self.update_autosave_label)
        self.file_menu.add_command(label="Print", command=self.print_current_schedule)
        self.file_menu.add_command(label="Select New Shared Save Path", command=self.select_new_shared_path)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.destroy)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Create an Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Open Schedule Manager", command=self.open_schedule_manager)
        self.edit_menu.add_command(label="Manage Access Levels", command=self.open_access_level_manager)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        
        # Create a View menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_checkbutton(label="Navigation Pane", command=self.toggle_nav_pane)
        self.view_menu.add_command(label="View Tracking Log", command=self.view_tracking_log)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        # Create a Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.contact_for_help)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        
        # Create an Administrator menu if the user has admin access
        if self.current_user.access_level == "admin":
            self.create_admin_menu()
            
        self.config(menu=self.menu_bar)

    def select_new_shared_path(self):
        new_shared_path = filedialog.askdirectory(title="Select New Shared Path")
        if new_shared_path:
            save_shared_path(new_shared_path)
            messagebox.showinfo("Success", "New shared path selected. Please restart the application for the changes to take effect.")    
    
    def view_tracking_log(self):
        if self.schedule_hrs_frame:
            crew_folder = os.path.join(constants.TRACKING_LOGS_DIR, self.user_selections["selected_crew"])
            selected_year = self.user_selections["selected_year"].strftime("%Y")
            selected_month = self.user_selections["selected_month"].strftime("%m")
            log_file = os.path.join(crew_folder, f'{self.user_selections["selected_crew"]}_{selected_year}_{selected_month}.log')

            if os.path.exists(log_file):
                if sys.platform == "win32":
                    os.system(f'start cmd /c "type {log_file} & pause"')
            else:
                messagebox.showinfo("Tracking Log", "No tracking log found for the selected schedule.")
        else:
            messagebox.showinfo("Tracking Log", "No schedule is currently loaded.")
    
    def update_autosave_label(self):
        if self.autosave_var.get():
            self.autosave_label.configure(text="Autosave: On")
        else:
            self.autosave_label.configure(text="Autosave: Off")
    
    def add_left_pane_frame(self):
        """
        Add the left pane frame and buttons to the main window.

        This method creates the left pane frame and adds the necessary buttons to it.
        """
        self.left_pane_frame = ctk.CTkFrame(
            self, 
            bg_color=constants.PANE_BG_COLOR, 
            fg_color=constants.PANE_BG_COLOR
        )
        self.left_pane_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")

        self.left_pane_button_frame = LeftPaneButtonFrame(
            self.left_pane_frame, 
            self.get_open_schedule_manager_method(), 
            self.get_save_member_data_method(), 
            self.get_schedule_selection_menu_method(),
            self.schedule_hrs_frame.schedule_type if self.schedule_hrs_frame else None
        )
        self.left_pane_button_frame.grid(row=0, column=0, sticky="nsew")

    def get_open_schedule_manager_method(self):
        """
        Get the method to open the schedule manager. 
        Needed for ButtonFrame as a dependancy.

        Returns:
            function: The method to open the schedule manager.
        """
        return self.open_schedule_manager
    
    def get_save_member_data_method(self):
        """
        Get the method to save member data.

        Returns:
            function: The method to save member data (placeholder).
        """
        return lambda: None

    def load_ranking_system(self):
        """
        Load the ranking system.

        This method creates and configures the ranking system frame if it 
        doesn't exist.
        """
        if self.ranking_frame is None and self.schedule_hrs_frame is not None:
            
            self.ranking_frame = RankingFrame(self.left_pane_frame, 
                                              self.schedule_hrs_frame)
            self.ranking_frame.grid(row=4, column=0, padx=10, pady=10, 
                                    sticky="new")       

    def get_schedule_selection_menu_method(self):
        """
        Get the method to open the schedule selection menu.

        Returns:
            function: The method to open the schedule selection menu 
            (placeholder).
            Needed as a ButtonFrame dependancy.
        """
        return lambda: None
    
    def set_title_frame(self, user_selections, schedule_type):
        """
        Set up the title frame.

        This method creates and configures the title frame based on the user's 
        selections.

        Args:
            user_selections (dict): The user's selected schedule date and crew.
        """
        if self.title_frame is None:
            self.scrolled_frame = ScrolledFrame(self)
            self.scrolled_frame.grid(column=2, row=0, padx=10, sticky="ew")
            self.title_frame = HeaderFrame(self.scrolled_frame.scrollable_frame, user_selections)
            self.title_frame.grid(column=0, row=0, padx=10, sticky="ew")
            self.grid_rowconfigure(2, weight=1)  # Title frame row

        self.title_frame.update_calendar(user_selections["selected_crew"],
                                        user_selections["selected_month"],
                                        user_selections["selected_year"])
        self.title_frame.update_labels(schedule_type)  # Add this line
    
    def set_hours_frame(self, user_selections, schedule_type):
        """
        Set up the hours frame.

        This method creates and configures the hours frame based on the user's 
        selections.

        Args:
            user_selections (dict): The user's selected schedule date and crew.
        """
        if self.schedule_hrs_frame is None:
            self.hdr_date_grid = HdrDateGrid(self.scrolled_frame.scrollable_frame, user_selections)
            self.hdr_date_grid.grid(column=0, row=1, padx=10, pady=0, sticky="ew")

            self.schedule_hrs_frame = ScheduleHrsFrame(
                self.scrolled_frame.scrollable_frame,
                self.hdr_date_grid,
                self.ranking_frame,
                user_selections,
                schedule_type,
                self.current_user.access_level, 
                self
            )
            self.schedule_hrs_frame.grid(column=0, row=2, padx=10, pady=0, sticky="nsew")

            # Store a reference to all HrsMatrixFrame instances
            if self.schedule_hrs_frame.frames:
                self.hrs_matrix_frame = self.schedule_hrs_frame.frames

            self.grid_rowconfigure(1, weight=0)  # Hours frame row
            self.grid_rowconfigure(2, weight=1)  # Hours frame row

            self.after(100, self.configure_save_button)

    def configure_save_button(self):
        try:
            if hasattr(self, 'left_pane_button_frame') and self.left_pane_button_frame.winfo_exists():
                self.left_pane_button_frame.save_entries_button.configure(
                    command=self.schedule_hrs_frame.save_member_data
                )
            else:
                logging.warning("left_pane_button_frame or save_entries_button is not accessible.")
        except tk.TclError as e:
            logging.error(f"Error configuring save_entries_button: {str(e)}")
    
    def update_schedule_hrs_frame(self, schedule_type):
        if self.schedule_hrs_frame:
            self.show_loading_overlay()
            self.schedule_hrs_frame.schedule_type = schedule_type
            self.schedule_hrs_frame.create_frames()
            self.hide_loading_overlay()
    
    def pass_values(self, user_selections, selected_schedule_type):
        """
        Pass the selected values and update the user interface.

        This method receives the user's selected schedule date and crew, updates the
        title frame, hours frame, and ranking system, and centers the main window on the screen.

        Args:
            user_selections (dict): The user's selected schedule date and crew.
        """

        self.user_selections = user_selections
        self.set_title_frame(self.user_selections, selected_schedule_type)
        
        if not hasattr(self, 'loading_overlay') or not self.loading_overlay.winfo_exists():
            self.init_loading_overlay()
            self.update_idletasks()
        
        self.set_hours_frame(self.user_selections, selected_schedule_type)
        
        # Update the tracking file for all frames
        if self.schedule_hrs_frame:
            self.schedule_hrs_frame.update_frames(self.user_selections)
        
        self.show_loading_overlay() 

        def update_ui():
            if self.ranking_frame:
                self.ranking_frame.destroy()

            self.load_ranking_system()

            # Update the ranking_frame attribute of ScheduleHrsFrame and HrsMatrixFrame
            if self.schedule_hrs_frame:
                self.schedule_hrs_frame.ranking_frame = self.ranking_frame
                for frame in self.schedule_hrs_frame.frames:
                    frame.ranking_frame = self.ranking_frame
            
            self.scrolled_frame.update_scroll_region()

            if self.current_user is not None:
                if self.current_user.access_level == "read-only":
                    self.toggle_nav_pane()
                    lock_widgets(self)
                    self.disable_menu_options()
                    
                    try:
                        if selected_schedule_type == "Overtime":
                            for frame in self.schedule_hrs_frame.frames:
                                lock_widgets(frame)
                                
                        elif selected_schedule_type == "work_schedule":
                            for frame in self.schedule_hrs_frame.work_schedule_frames:
                                lock_widgets(frame)
                    except Exception as e:
                        logging.error(f"Error from widget lock: pass_values.update_ui(): {str(e)}")
                            
                elif self.current_user.access_level == "privileged":
                    self.enable_menu_options()
                elif self.current_user.access_level == "admin":
                    self.enable_menu_options()
            else:
                # Handle the case when self.current_user is None
                # You can show an error message or take appropriate action
                messagebox.showerror("Access Error", "User access level not set.")
                self.destroy()
                return
        
            # Center the main window on the screen
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            window_width = self.winfo_reqwidth()
            window_height = self.winfo_reqheight()
            position_x = (screen_width // 2) - (window_width // 2)
            position_y = (screen_height // 2) - (window_height // 2)

            # Should be called following the creation of all widgets and frames
            self.geometry(f"+{position_x}+{position_y}")
            
            if selected_schedule_type == "Overtime":
                self.update_switch_button("work_schedule", self.select_work_schedule)
            else:
                self.update_switch_button("Overtime", self.select_overtime_schedule)

        def wait_for_frames_created():
            if self.schedule_hrs_frame and hasattr(self.schedule_hrs_frame, 'frames_created'):
                if not self.schedule_hrs_frame.frames_created.get():
                    self.after(0, self.loading_process)  # Schedule loading_process if frames are not created
                self.wait_variable(self.schedule_hrs_frame.frames_created)
                self.after(0, self.hide_loading_overlay)  # Hide the loading overlay after frames are created
                self.after(0, update_ui)
            else:
                self.after(100, wait_for_frames_created)

        wait_for_frames_created()
        
    def show_loading_overlay(self):
        if self.schedule_hrs_frame and (not hasattr(self, 'loading_overlay') or not self.loading_overlay.winfo_exists()):
            self.init_loading_overlay()
            self.update_idletasks()

    def init_loading_overlay(self):
        self.loading_overlay = tk.Frame(self, bg=constants.APP_BG_COLOR)
        self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        loading_frame = tk.Frame(self.loading_overlay, bg=constants.APP_BG_COLOR)
        loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        loading_label = tk.Label(
            loading_frame,
            text="Loading, please wait...",
            bg=constants.APP_BG_COLOR,
            font=("Calibri", 22),
            fg="white"
        )
        loading_label.pack(pady=(0, 20))

        progressbar_style = ttk.Style()
        progressbar_style.theme_use('clam')
        progressbar_style.configure(
            "red.Horizontal.TProgressbar",
            bordercolor='#0d00ff',
            troughcolor=constants.PANE_BG_COLOR,
            foreground='#06039c',
            background='#0400d6',
            darkcolor="#05015c",
            lightcolor="#3d34ed"
        )

        self.progress_bar = ttk.Progressbar(loading_frame, style="red.Horizontal.TProgressbar", length=200, mode='determinate')
        self.progress_bar.pack(pady=(0, 20))

        image_path = os.path.join("images/background_images/", "Loading_Screen_image.png")
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)

        self.loading_screen_tree_image = tk.Label(
            loading_frame, image=photo,
            bg=constants.APP_BG_COLOR
        )
        self.loading_screen_tree_image.image = photo
        self.loading_screen_tree_image.pack()
        
        if self.autosave_var.get():
            schedule_autosave_notif_label = tk.Label(
                loading_frame,
                text="AutoSave: Your schedule was saved before the swap.",
                bg=constants.APP_BG_COLOR,
                font=("Calibri", 14),
                fg="white"
            )
            schedule_autosave_notif_label.pack(pady=20)

        self.after(0, self.loading_process)

    def loading_process(self):
        # Check if a loading process is already running
        if hasattr(self, 'loading_process_running') and self.loading_process_running:
            return

        self.loading_process_running = True  # Set the flag to indicate loading process is running

        if hasattr(self, 'progress_bar'):
            self.progress_bar['value'] = 0
            self.update_idletasks()

            for i in range(1, 11):
                if self.schedule_hrs_frame and hasattr(self.schedule_hrs_frame, 'frames_created') and self.schedule_hrs_frame.frames_created.get():
                    break  # Break out of the loop if frames are created
                elif not self.schedule_hrs_frame or not hasattr(self.schedule_hrs_frame, 'frames_created') or not self.schedule_hrs_frame.frames_created.get():
                    progress = i * 10
                    self.progress_bar['value'] = progress
                    self.update_idletasks()
                    time.sleep(0.1)  # Adjust the delay as needed
                else:
                    break

            self.progress_bar['value'] = 100
            self.update_idletasks()

        self.after(300, self.destroy_loading_overlay)
        self.loading_process_running = False  # Reset the flag after the loading process is completed

    def destroy_loading_overlay(self):
        if hasattr(self, 'loading_overlay') and self.loading_overlay.winfo_exists():
            self.loading_overlay.destroy()
            del self.loading_overlay

    def destroy(self):
        # if access level is less than privileged or admin
        if self.current_user.access_level == "read-only":
            super().destroy()
        else:
            # If there is anything to save..
            if self.schedule_hrs_frame:
                if self.autosave_var.get():
                    self.save_schedule_data()
                    self.display_save_status()
                super().destroy()
            else:
                super().destroy()
    
    """
    Menu Bar Options
    
    """
    
    def open_access_level_manager(self):
        """
        File menu option:
        
        Opens the access level manager for assigning crew access levels.
        """
        self.access_level_manager_window = AccessLevelManager(self)
        center_toplevel_window(self.access_level_manager_window)
    
    def open_input_window(self):
        """
        File menu option / On __init__:
        
        Opens the input window for selecting the schedule date and crew.
        """
        try:
            self.input_window = TLSelectScheduleDate(self)
            
            if hasattr(self, 'left_pane_button_frame') and self.left_pane_button_frame.winfo_exists():
                if hasattr(self.left_pane_button_frame, 'select_new_schedule_button'):
                    try:
                        self.left_pane_button_frame.select_new_schedule_button.configure(
                            command=self.load_schedule_from_file
                        )
                    except tk.TclError as e:
                        logging.error(f"Error configuring select_new_schedule_button: {str(e)}")
                else:
                    logging.warning("select_new_schedule_button does not exist.")
            else:
                logging.warning("left_pane_button_frame does not exist or has been destroyed.")
            
            self.wait_window(self.input_window) # Wait for the input window to be visible
            center_toplevel_window(self.input_window)
        except Exception as e:
            logging.error("Error occurring at open_input_window")
    
    def load_schedule_from_file(self):
        """
        File Menu Option: Load the schedule from a file.

        This method closes the current schedule window, resets the title and 
        hours frames, and opens the input window to select a new schedule date 
        and crew.
        """
        if self.current_user.access_level != "read-only":
            if self.autosave_var.get():
                self.save_schedule_data()
                self.display_save_status()
        
        self.iconify()
        if self.schedule_hrs_frame:
            self.schedule_hrs_frame.destroy()
            
        if self.ranking_frame:
            self.ranking_frame.destroy()
            
        self.title_frame = None
        self.schedule_hrs_frame = None
        self.ranking_frame = None
        
        # Temporarily unhide the navigation pane if it was hidden
        if not self.left_pane_frame.winfo_viewable():
            self.toggle_nav_pane()
        
        self.open_input_window()
        
        # Update the HdrDateGrid instance with the new user selections
        if hasattr(self, 'hdr_date_grid') and self.hdr_date_grid.winfo_exists():
            self.hdr_date_grid.destroy()
        self.hdr_date_grid = HdrDateGrid(self.scrolled_frame.scrollable_frame, self.user_selections)
        self.hdr_date_grid.grid(column=0, row=1, padx=10, pady=0, sticky="ew")
        
        if self.schedule_hrs_frame:
            self.schedule_hrs_frame.update_frames(self.user_selections)
            if self.schedule_hrs_frame.schedule_type == "Overtime":
                self.update_switch_button("work_schedule", self.select_work_schedule)
            else:
                self.update_switch_button("Overtime", self.select_overtime_schedule)
    
    def select_overtime_schedule(self):
        """
        Helper Methods for Select Schedule Type:
        Select the overtime schedule by passing to ScheduleHrsFrame
        """
        if self.current_user.access_level != "read-only":
            if self.autosave_var.get():
                self.save_schedule_data()
                self.display_save_status
        self.set_hours_frame(self.user_selections, "overtime")
        self.update_header_frame_labels("overtime")
        self.update_schedule_hrs_frame("Overtime")
        self.update_switch_button("work_schedule", self.select_work_schedule)
        
        self.show_loading_overlay()
        self.after(0, lambda: self.hide_loading_overlay())

    def select_work_schedule(self):
        """
        Helper Methods for Select Schedule Type:
        Select the work schedule by passing to ScheduleHrsFrame
        """
        if self.current_user.access_level != "read-only":
            if self.autosave_var.get():
                self.save_schedule_data()
                self.display_save_status()
        self.set_hours_frame(self.user_selections, "work_schedule")
        self.update_header_frame_labels("work_schedule")
        self.update_schedule_hrs_frame("work_schedule")
        self.update_switch_button("Overtime", self.select_overtime_schedule)
        
        self.show_loading_overlay()
        self.after(0, lambda: self.hide_loading_overlay())
    
    def update_switch_button(self, schedule_type, switch_command):
        if hasattr(self, 'left_pane_button_frame'):
            try:
                self.left_pane_button_frame.update_switch_button(schedule_type, switch_command)
            except Exception as e:
                logging.error(f"Error updating switch button: {str(e)}")
                # Add any additional error handling or logging here
        else:
            logging.warning("left_pane_button_frame does not exist.")
    
    def save_schedule_data(self):
        """
        File menu option: Save the schedule data.
        
        This method saves the member data from the hours frame.
        """
        if self.schedule_hrs_frame:
            self.schedule_hrs_frame.save_member_data()
            self.display_save_status()
        else:
            logging.warning("No schedule data to save.")
    
    def open_schedule_manager(self):
        """
        Edit menu option: Open the schedule manager.

        This method opens the schedule manager window from the hours frame.
        """
        if self.schedule_hrs_frame:
            self.schedule_hrs_frame.open_window()
        
        self.show_loading_overlay()
        self.wait_window(self.schedule_hrs_frame.schedule_manager)
        self.hide_loading_overlay()
            
    def show_about(self):
        """
        Help Menu Option: Display the about information.

        This method opens the "Plan_Matrix_Doc.pdf" file when the user selects the "About" option from the Help menu.
        It includes error handling for different scenarios.
        """
        pdf_path = "Plan_Matrix_Doc.pdf"
        
        if os.path.exists(pdf_path):
            try:
                if sys.platform == "win32":
                    os.startfile(pdf_path)
                else:
                    subprocess.run(["open", pdf_path], check=True)
            except Exception as e:
                logging.error(f"Error occurred while opening the PDF file: {str(e)}")
                messagebox.showerror("Error", "Failed to open the PDF file. Please check the application logs for more details.")
        else:
            logging.error(f"The 'Plan_Matrix_Doc.pdf' file was not found at path: {pdf_path}")
            messagebox.showerror("File Not Found", "The 'Plan_Matrix_Doc.pdf' file was not found. Please ensure the file exists in the specified location.")
            
    def contact_for_help(self):
        """
        Help Menu Option: Open an email to contact for help.

        This method is a placeholder for future implementation.
        Opens an outlook email to forward to developer
        """
        current_date = datetime.now().strftime("%m/%d/%Y")
        subject = f"{current_date} Schedule Support Request"
        body = """I need assistance or have found an issue with the Schedule App.\n\n[please outline your concern here]\n\nThank you.\n\n"""
        
        body = f"{body}User ID: {get_user_id()}"
            
        recipient = "matthewdunaway@chevron.com"

        forward_outlook_email(subject, body, recipient)

    def get_schedule_data(self, schedule_type):
        """
        Extract schedule data based on the user's selected schedule type.

        This method retrieves the schedule data from the respective frames based on the selected
        schedule type. If the schedule type is "Overtime", it extracts the name, starting working hours,
        starting asking hours, working hours data, and asking hours data from each frame in the
        `schedule_hrs_frame.frames` list and appends them to the `schedule_data` list. If the schedule
        type is "work_schedule", it extracts the name and row data from each frame in the
        `schedule_hrs_frame.work_schedule_frames` list and appends them to the `schedule_data` list.

        Args:
            schedule_type (str): The type of schedule selected, either "Overtime" or "work_schedule".

        Returns:
            list: A list of tuples containing the extracted schedule data.
                - For "Overtime" schedule:
                    - Each tuple contains (name, starting_working_hours, working_hours_data) and
                        ("", starting_asking_hours, asking_hours_data).
                - For "work_schedule":
                    - Each tuple contains (name, row_data).
                - If an invalid schedule type is provided, an empty list is returned.
        """
        if schedule_type == "Overtime":
            schedule_data = []
            for frame in self.schedule_hrs_frame.frames:
                name = frame.labels[0].cget("text")
                starting_working_hours = str(frame.starting_working_hours)
                starting_asking_hours = str(frame.starting_asking_hours)
                working_hours_data = [working_entry.get() for working_entry in frame.working_hours_entries]
                asking_hours_data = [asking_entry.get() for asking_entry in frame.asking_hours_entries]
                
                schedule_data.append((name, starting_working_hours, working_hours_data))
                schedule_data.append(("", starting_asking_hours, asking_hours_data))
        elif schedule_type == "work_schedule":
            # Personnel Schedule Data
            schedule_data = []
            for frame in self.schedule_hrs_frame.work_schedule_frames:
                name = frame.labels[0].cget("text")
                row_data = [str(entry.get()) for entry in frame.crew_member_role_entries]
                schedule_data.append((name, row_data))

            # Overtime Personnel Data    
            overtime_data = []
            for label, entry_row in zip(self.schedule_hrs_frame.overtime_frame.labels, self.schedule_hrs_frame.overtime_frame.entries):
                slot_name = label.cget("text")
                slot_data = [entry.get() for entry in entry_row]
                overtime_data.append((slot_name, slot_data))
            
            return schedule_data, overtime_data
        else:
            schedule_data = []
            
        return schedule_data
    
    def print_current_schedule(self):
        """
        Print the current schedule to a PDF file and open it.

        This method generates a PDF file of the current schedule based on the selected schedule type
        (Overtime or Work Schedule). It saves the PDF file to the user's desktop and automatically opens
        it using the default PDF viewer on their operating system.

        If the PDF file is successfully generated and saved, a success message is displayed using a
        message box. If there is an error generating the PDF file, an error message is displayed.
        """
        if self.schedule_hrs_frame:
            schedule_type = self.schedule_hrs_frame.schedule_type
            
            schedule_data = self.get_schedule_data(schedule_type)
            filename = self.generate_filename(schedule_type)

            # Generate the PDF
            pdf_file = self.generate_schedule_pdf(schedule_data, filename)
            
            if pdf_file is not None:
                messagebox.showinfo('Export', 'Schedule exported to PDF successfully!')
                
                # Open the PDF file
                if sys.platform == "win32":
                    try:
                        os.startfile(pdf_file.filename)
                    except FileNotFoundError as e:
                        logging.error(f"Error occurred opening the file.\nLogged Error: {e}")
                        messagebox.showerror("FileError", "The file could not be opened.")
                    
            else:
                messagebox.showerror('Error', 'Failed to generate the PDF file.')

    def generate_overtime_schedule_pdf(self):
        """
        Generate the overtime schedule data and filename for PDF export.

        This method retrieves the overtime schedule data from the frames and generates the filename
        based on the selected schedule date and crew.

        Returns:
            tuple: A tuple containing the schedule data and the generated filename.
                - schedule_data (list): A list of tuples representing the overtime schedule data.
                - filename (str): The generated filename for the PDF file.
        """
        schedule_data = []
        for frame in self.schedule_hrs_frame.frames:
            name = frame.labels[0].cget("text")
            starting_working_hours = str(frame.starting_working_hours)
            starting_asking_hours = str(frame.starting_asking_hours)
            working_hours_data = [working_entry.get() for working_entry in frame.working_hours_entries]
            asking_hours_data = [asking_entry.get() for asking_entry in frame.asking_hours_entries]
            
            schedule_data.append((name, starting_working_hours, working_hours_data))
            schedule_data.append(("", starting_asking_hours, asking_hours_data))

        # Generate the PDF filename based on the schedule date and crew
        selected_date = self.user_selections['selected_month']
        selected_year = self.user_selections['selected_year'].year
        selected_crew = self.user_selections['selected_crew']
        month_name = selected_date.strftime("%B")  # Get the full month name

        filename = f"{selected_crew} Crew OT - {month_name} {selected_year}.pdf"

        return schedule_data, filename

    def generate_work_schedule_pdf(self):
        """
        Generate the work schedule data and filename for PDF export.

        This method retrieves the work schedule data from the frames and generates the filename
        based on the selected schedule date and crew.

        Returns:
            tuple: A tuple containing the schedule data and the generated filename.
                - schedule_data (list): A list of tuples representing the work schedule data.
                - filename (str): The generated filename for the PDF file.
        """
        schedule_data = []
        for frame in self.schedule_hrs_frame.work_schedule_frames:
            name = frame.labels[0].cget("text")
            row_data = [str(entry.get()) for entry in frame.crew_member_role_entries]
            schedule_data.append((name, row_data))

        # Generate the PDF filename based on the schedule date and crew
        selected_date = self.user_selections['selected_month']
        selected_year = self.user_selections['selected_year'].year
        selected_crew = self.user_selections['selected_crew']
        month_name = selected_date.strftime("%B")  # Get the full month name

        filename = f"{selected_crew} Crew WS - {month_name} {selected_year}.pdf"

        return schedule_data, filename

    def generate_filename(self, schedule_type):
        """
        Generate a filename for the PDF based on the selected schedule type, date, and crew.

        Args:
            schedule_type (str): The type of schedule ("Overtime" or "work_schedule").

        Returns:
            str: The generated filename for the PDF.
        """
        selected_date = self.user_selections['selected_month']
        selected_year = self.user_selections['selected_year'].year
        selected_crew = self.user_selections['selected_crew']
        month_name = selected_date.strftime("%B")  # Get the full month name

        if schedule_type == "Overtime":
            filename = f"{selected_crew} Crew OT - {month_name} {selected_year}.pdf"
        elif schedule_type == "work_schedule":
            filename = f"{selected_crew} Crew WS - {month_name} {selected_year}.pdf"
        else:
            filename = ""
            
        return filename
    
    def generate_schedule_pdf(self, schedule_data, filename):
        """
        Generate the schedule PDF file.

        This method generates a PDF file based on the provided schedule data and filename. It creates
        a table with the schedule data, applies styling to the table, and builds the PDF document.
        The generated PDF file is saved to the user's desktop.

        Args:
            schedule_data (list): A list of tuples representing the schedule data.
            filename (str): The filename for the generated PDF file.

        Returns:
            SimpleDocTemplate: The generated PDF file object, or None if there was an error.
        """
        if not schedule_data or not filename:
            logging.error("schedule_data or filename is empty or None")
            logging.error(f"Filename: {filename}\nSchedule Data: {schedule_data}")
            return None

        # Register the custom font for the PDF
        pdfmetrics.registerFont(TTFont('Calibri', 'C:/Windows/Fonts/Calibri.ttf'))
        
        # Define the paragraph styles
        HEADER_STYLE = ParagraphStyle(
            name='report_style', 
            fontName='Calibri',
            fontSize=10,
            textColor=colors.HexColor("#ffffff"),
            alignment=TA_CENTER
        )
        
        DATA_STYLE = ParagraphStyle(
            name='data_style', 
            fontName='Calibri',
            fontSize=10,
            alignment=TA_CENTER
        )        

        # Define the file path for saving the PDF
        DESKTOP_PATH = os.path.expanduser("~\\Desktop")
        if not os.path.exists(DESKTOP_PATH):
            os.makedirs(DESKTOP_PATH)

        file_path = os.path.join(DESKTOP_PATH, filename)
        file_path = os.path.normpath(file_path)

        try:
            # Create a new PDF document
            pdf_file = SimpleDocTemplate(file_path, pagesize=landscape(letter))

            # Generate the table data and span commands based on the schedule type
            if "OT" in filename:
                header_text = self.generate_header_text("Overtime")
                table_data = self.generate_overtime_table_data(schedule_data, HEADER_STYLE, DATA_STYLE)
                span_commands = self.generate_overtime_span_commands(schedule_data)
            elif "WS" in filename:
                header_text = self.generate_header_text("Work Schedule")
                regular_schedule, overtime_data = schedule_data
                table_data, cell_styles = self.generate_work_schedule_table_data(regular_schedule, overtime_data, HEADER_STYLE, DATA_STYLE)
                span_commands = []
            else:
                logging.error("Invalid schedule type. Check filename in generate_schedule_pdf method")
                return None

            # Define the table style based on the schedule type
            table_style = self.generate_table_style(span_commands, "OT" in filename)

            # Create the custom header
            header = self.generate_header(header_text)

            # Create a table for the header
            header_table = self.generate_header_table(header, pdf_file.width)

            # Create the table and apply the styles
            table = Table(table_data)
            table.setStyle(table_style)
            
            # Apply cell styles only for work schedule
            if "WS" in filename:
                table.setStyle(TableStyle(cell_styles))

            # Build the PDF document with the header and table
            elements = [header_table, table]
            pdf_file.build(elements)

            return pdf_file

        except Exception as e:
            logging.error(f"Failed to generate or save PDF: {str(e)}")
            return None

    def generate_header_text(self, schedule_type):
        """
        Generate the header text for the PDF based on the schedule type, selected crew, month, and year.

        Args:
            schedule_type (str): The type of schedule ("Overtime" or "Work Schedule").

        Returns:
            str: The generated header text.
        """
        return (
            f"{schedule_type}<br/>"
            f"{self.user_selections['selected_crew']} Crew "
            f"| {self.user_selections['selected_month'].strftime('%B')} "
            f"| {self.user_selections['selected_year'].year}"
        )

    def generate_overtime_table_data(self, schedule_data, header_style, data_style):
        """
        Generate the table data for the overtime schedule PDF.

        Args:
            schedule_data (list): A list of tuples representing the overtime schedule data.
            header_style (ParagraphStyle): The style for the header cells.
            data_style (ParagraphStyle): The style for the data cells.

        Returns:
            list: The generated table data for the overtime schedule.
        """
        selected_month = self.user_selections["selected_month"].month
        selected_year = self.user_selections["selected_year"].year
        selected_crew = self.user_selections["selected_crew"]

        num_days_in_month = header_functions.month_range(selected_month, selected_year)
        starting_day_index = header_functions.get_weekday(selected_month, selected_year)

        days_of_week = ["S", "M", "T", "W", "T", "F", "S"]
        day_labels = [days_of_week[(starting_day_index + i) % 7] for i in range(num_days_in_month)]

        date_to_find = datetime(selected_year, selected_month, 1)
        crew_shift_list = header_functions.get_crew_shifts(selected_crew, date_to_find)[:num_days_in_month]

        table_data = [
            ['Name', 'Starting\nHours'] + [
                Paragraph(f'{i+1}<br/>{day_labels[i]}<br/>{crew_shift_list[i]}', header_style)
                for i in range(num_days_in_month)
            ]
        ]
        for name, starting_hours, hours_data in schedule_data:
            if name:
                table_data.append([Paragraph(name, data_style), Paragraph(starting_hours, data_style)] + [Paragraph(data, data_style) for data in hours_data])
            else:
                table_data.append(['', Paragraph(starting_hours, data_style)] + [Paragraph(data, data_style) for data in hours_data])
        return table_data

    def generate_work_schedule_table_data(self, schedule_data, overtime_data, header_style, data_style):
        """
        Generate the table data for the work schedule PDF.

        Args:
            schedule_data (list): A list of tuples representing the work schedule data.
            header_style (ParagraphStyle): The style for the header cells.
            data_style (ParagraphStyle): The style for the data cells.

        Returns:
            list: The generated table data for the work schedule.
        """
        selected_month = self.user_selections["selected_month"].month
        selected_year = self.user_selections["selected_year"].year
        selected_crew = self.user_selections["selected_crew"]

        num_days_in_month = header_functions.month_range(selected_month, selected_year)
        starting_day_index = header_functions.get_weekday(selected_month, selected_year)

        days_of_week = ["S", "M", "T", "W", "T", "F", "S"]
        day_labels = [days_of_week[(starting_day_index + i) % 7] for i in range(num_days_in_month)]

        date_to_find = datetime(selected_year, selected_month, 1)
        crew_shift_list = header_functions.get_crew_shifts(selected_crew, date_to_find)[:num_days_in_month]

        table_data = [
            ['Name'] + [
                Paragraph(f'{i+1}<br/>{day_labels[i]}<br/>{crew_shift_list[i]}', header_style)
                for i in range(num_days_in_month)
            ]
        ]
        
        cell_styles = []
        
        for name, row_data in schedule_data:
            row = [Paragraph(name, data_style)]
            for data in row_data:
                if data in constants.COLOR_SPECS:
                    bg_color = constants.COLOR_SPECS[data]["label_bg"]
                    text_color = constants.COLOR_SPECS[data]["label_text"]
                    cell_style = ParagraphStyle(
                        f'colored_cell_{data}',
                        parent=data_style,
                        textColor=colors.HexColor(text_color),
                        backColor=colors.HexColor(bg_color)
                    )
                    row.append(Paragraph(data, cell_style))
                    cell_styles.append(('BACKGROUND', (len(row)-1, len(table_data)), (len(row)-1, len(table_data)), colors.HexColor(bg_color)))
                else:
                    row.append(Paragraph(data, data_style))
            table_data.append(row)
            
        # Add a separator row with "Overtime" title
        separator_style = ParagraphStyle(
            'separator',
            parent=header_style,
            fontSize=12,
            textColor=colors.HexColor("#FFFFFF"),
            backColor=colors.HexColor("#05016e"),
            alignment=TA_CENTER
        )
        separator_row = [Paragraph("Overtime", separator_style)]
        table_data.append(separator_row)

        # Add style for the separator row
        separator_row_index = len(table_data) - 1
        cell_styles.append(('BACKGROUND', (0, separator_row_index), (-1, separator_row_index), colors.HexColor("#05016e")))
        cell_styles.append(('SPAN', (0, separator_row_index), (-1, separator_row_index)))
        cell_styles.append(('ALIGN', (0, separator_row_index), (-1, separator_row_index), 'CENTER'))
        cell_styles.append(('VALIGN', (0, separator_row_index), (-1, separator_row_index), 'MIDDLE'))

        # Add overtime slots data
        for slot_name, slot_data in overtime_data:
            row = [Paragraph(slot_name, data_style)] + [Paragraph(data, data_style) if data else '' for data in slot_data]
            table_data.append(row)
            for col, data in enumerate(slot_data):
                if data in constants.COLOR_SPECS:
                    bg_color = constants.COLOR_SPECS[data]["label_bg"]
                    text_color = constants.COLOR_SPECS[data]["label_text"]
                    cell_styles.append(('BACKGROUND', (col+1, len(table_data)-1), (col+1, len(table_data)-1), colors.HexColor(bg_color)))
                    cell_styles.append(('TEXTCOLOR', (col+1, len(table_data)-1), (col+1, len(table_data)-1), colors.HexColor(text_color)))

        return table_data, cell_styles

    def generate_overtime_span_commands(self, schedule_data):
        """
        Generate the span commands for merging name column rows in the overtime schedule.

        Args:
            schedule_data (list): A list of tuples representing the overtime schedule data.

        Returns:
            list: The generated span commands for merging name column rows.
        """
        name_row_indices = [idx for idx, (name, _, _) in enumerate(schedule_data, start=1) if name]
        return [('SPAN', (0, idx), (0, idx+1)) for idx in name_row_indices]

    def generate_table_style(self, span_commands, is_overtime):
        """
        Generate the table style for the PDF based on the span commands and schedule type.

        Args:
            span_commands (list): The span commands for merging name column rows.
            is_overtime (bool): Indicates whether the schedule is an overtime schedule.

        Returns:
            TableStyle: The generated table style for the PDF.
        """
        base_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#05016e")),  # Header row background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header row text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment for all cells
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Vertical alignment for all cells
            ('FONTNAME', (0, 0), (-1, 0), 'Calibri'),  # Header row font
            ('FONTSIZE', (0, 0), (-1, 0), 12),  # Header row font size
            ('BOTTOMPADDING', (0, 0), (-1, 0), 2),  # Header row bottom padding
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Data rows background
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor("#ceccfc")),  # Name column background
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Data rows text color
            ('LEFTPADDING', (0, 0), (-1, -1), 2),  # Cell left padding
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),  # Cell right padding
            ('FONTNAME', (0, 1), (-1, -1), 'Calibri'),  # Data row font
            ('FONTSIZE', (0, 1), (-1, -1), 10),  # Data row font size
            ('TOPPADDING', (0, 1), (-1, -1), 2),  # Data row top padding
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),  # Data row bottom padding
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),  # Inner grid lines
            ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Border around the entire table
        ]

        if is_overtime:
            overtime_style = [
                ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),  # Vertical alignment for header cells
                
                *[('BACKGROUND', (1, idx), (-1, idx), colors.HexColor("#C6EFCE")) for idx in range(1, len(span_commands)*2, 2)],  # Working hours row colors
                *[('TEXTCOLOR', (1, idx), (-1, idx), colors.HexColor("#006100")) for idx in range(1, len(span_commands)*2, 2)],  # Working hours row text colors
                *[('BACKGROUND', (1, idx), (-1, idx), colors.HexColor("#FFC7CE")) for idx in range(2, len(span_commands)*2+1, 2)],  # Asking hours row colors
                *[('TEXTCOLOR', (1, idx), (-1, idx), colors.HexColor("#9C0006")) for idx in range(2, len(span_commands)*2+1, 2)],  # Asking hours row text colors
                ('TEXTCOLOR', (0, 1), (0, -1), colors.white),  # Name column text color
            ]
            base_style.extend(overtime_style)

        base_style.extend(span_commands)

        return TableStyle(base_style)

    def generate_header(self, header_text):
        """
        Generate the header for the PDF.

        Args:
            header_text (str): The text for the header.

        Returns:
            Paragraph: The generated header paragraph.
        """
        header_style = ParagraphStyle(
            name='header_style',
            fontName='Calibri',
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        return Paragraph(header_text, header_style)

    def generate_header_table(self, header, width):
        """
        Generate the header table for the PDF.

        Args:
            header (Paragraph): The header paragraph.
            width (float): The width of the PDF document.

        Returns:
            Table: The generated header table.
        """
        header_table = Table([[header]], colWidths=[width])
        header_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        return header_table
      
app = App() # Create an instance of the App class

app.mainloop() # Run the application main loop