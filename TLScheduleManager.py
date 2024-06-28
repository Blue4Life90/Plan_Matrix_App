# PEP8 Compliant Guidance
# Standard Library Imports
import logging
import tkinter as tk
import datetime as datetime
from tkinter import ttk
from tkinter import messagebox

# Third-Party Library Imports
import customtkinter as ctk # type: ignore

# Local Application/Library Specific Imports  
from functions.json_functions import adjust_crew_member_starting_hours
from functions.json_functions import load_hours_data_from_json, save_new_crew_member
from functions.json_functions import remove_crew_member, change_crew_member_name, move_person_data
from constants import log_file
from constants import load_icons
from constants import BUTTON_FG_COLOR, BUTTON_HOVER_BG_COLOR
from constants import APP_BG_COLOR, FILE_MENU_BG_COLOR, TEXT_COLOR
from constants import ASKING_HRS_FG_COLOR, WORKING_HRS_FG_COLOR
from constants import ASKING_HRS_BG_COLOR, WORKING_HRS_BG_COLOR
from constants import TREEVIEW_EVEN, TREEVIEW_ODD, TREEVIEW_TEXT, TREEVIEW_SELECTED

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    filename=log_file, filemode='a'
)

class TLScheduleManager(tk.Toplevel):
    """
    A Toplevel window for managing crew members.

    Args:
        parent (tk.Tk): The parent window.
        initial_names (list): A list of initial crew member names.
        app (App): The main application instance.
        user_selections (dict): A dictionary containing user selections.
        schedule_type (str): The type of schedule ("Overtime" or "work_schedule").
    """
    def __init__(self, parent, initial_names, app, user_selections, schedule_type, crew_member_count):
        super().__init__(parent)
        self.title("Schedule Manager")
        self.iconpath_0, self.iconpath_1, self.iconpath_2 = load_icons()
        self.iconphoto(False, self.iconpath_0)  # Set the icon for the main window
        self.configure(background=APP_BG_COLOR)
        
        self.initial_names = initial_names
        self.app = app
        self.user_selections = user_selections
        self.schedule_type = schedule_type
        self.crew_member_count = crew_member_count
        
        # Center the toplevel window over the parent window
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        self_width = self.winfo_reqwidth()
        self_height = self.winfo_reqheight()
        position_x = parent_x + (parent_width - self_width) // 2
        position_y = parent_y + (parent_height - self_height) // 2
        self.geometry(f"+{position_x}+{position_y}")
        
        self.configure_button_frame()
        self.button_frame.grid(row=0, column=0, rowspan=50, sticky="nsew")
        
        self.configure_treeview()
        self.tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=0)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
                
        self.selected_num_rows_var = tk.StringVar()
        self.num_rows_label = ctk.CTkLabel(
            self, 
            text=f"{self.crew_member_count} Crew Members", 
            font=("Calibri", 12), 
            text_color=TEXT_COLOR
        )
        
        self.selected_num_rows_var.set(self.crew_member_count)
        self.edited_crew_members = None
        self.removed_crew_members = None
        self.moved_personnel = []
        
        self.num_rows_label.grid(row=1, column=1, sticky="ew", padx=10, pady=0)
        
        apply_member_count_btn = ctk.CTkButton(
            self, text="Confirm All Changes", 
            fg_color="#047a1b", hover_color="#02a120", text_color="white", 
            command=self.confirm_changes
        )
        apply_member_count_btn.grid(row=2, column=1, sticky="ew", padx=10, pady=10)
        
        # Create an entry box with the old name
        edit_entry_frame = tk.LabelFrame(
            self, text="use this for editing", 
            font=("Calibri", 10, "italic"), fg=TEXT_COLOR, 
            padx=10, pady=10, bg=APP_BG_COLOR
        )
        edit_entry_frame.grid(row=4, column=1, sticky="ew", padx=10, pady=10)
        
        self.new_name_entry = tk.Entry(edit_entry_frame, state="disabled")
        self.new_name_entry.grid(row=4, column=1, sticky="ew")
        edit_entry_frame.grid_columnconfigure(1, weight=1)
        
        if user_selections['selected_month'].month == 1:
            self.configure_hours_frame()
            self.starting_hours_frame.grid(row=0, column=2, rowspan=50, sticky="nsew")
        
        for i in range(50):
            self.grid_rowconfigure(i, weight=1)
            
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
    def configure_hours_frame(self):
        """
        Configure the frame widget containing all starting hour adjustment options.
        """
        self.starting_hours_frame = tk.Frame(
            self, bg=APP_BG_COLOR, relief="flat", borderwidth=1
        )

        # Crew Member Name Selected
        #TODO: Name configures to selected tree item
        self.crew_member_name_label = ctk.CTkLabel(
            self.starting_hours_frame, text="", 
            font=("Calibri", 14, "bold"),
            text_color=TEXT_COLOR
        )
        self.crew_member_name_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Starting Working Hours
        #TODO: Hours configure to selected tree item
        self.crew_member_starting_working_hours_label = ctk.CTkLabel(
            self.starting_hours_frame, text="Starting Working Hours: ", 
            font=("Calibri", 14, "bold"),
            text_color=WORKING_HRS_BG_COLOR
        )
        self.crew_member_starting_working_hours_label.grid(row=1, column=0, padx=10, pady=(10, 0))
        
        self.crew_member_starting_working_hours = ctk.CTkEntry(
            self.starting_hours_frame, 
            font=("Calibri", 14),
            text_color=WORKING_HRS_FG_COLOR,
            fg_color=WORKING_HRS_BG_COLOR,
            border_color=WORKING_HRS_FG_COLOR,
            state="disabled"
        )
        self.crew_member_starting_working_hours.grid(row=2, column=0, padx=10, pady=10)

        # Starting Asking Hours
        #TODO: Hours configure to selected tree item
        self.crew_member_starting_asking_hours_label = ctk.CTkLabel(
            self.starting_hours_frame, text="Starting Asking Hours: ", 
            font=("Calibri", 14, "bold"),
            text_color=ASKING_HRS_BG_COLOR
        )
        self.crew_member_starting_asking_hours_label.grid(row=3, column=0, padx=10, pady=(10, 0))
        
        self.crew_member_starting_asking_hours = ctk.CTkEntry(
            self.starting_hours_frame, 
            font=("Calibri", 14),
            text_color=ASKING_HRS_FG_COLOR,
            fg_color=ASKING_HRS_BG_COLOR,
            border_color=ASKING_HRS_FG_COLOR,
            state="disabled"
        )
        self.crew_member_starting_asking_hours.grid(row=4, column=0, padx=10, pady=10)
        
        self.confirm_new_starting_hours_button = ctk.CTkButton(
            self.starting_hours_frame, text="Change Hours", 
            fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_BG_COLOR, 
            command=self.change_starting_hours,
            state="disabled"
        )
        self.confirm_new_starting_hours_button.grid(row=5, column=0, sticky="ew", padx=10, pady=10)

        self.button_frame.grid_columnconfigure(0, weight=1)
        
        # Push the "Edit Selected Name" button to the bottom
        #TODO: May not be needed...
        #self.button_frame.grid_rowconfigure(5, weight=1)

    #TODO: Test Once Ready
    def change_starting_hours(self):
        if self.schedule_type != "Overtime":
            messagebox.showinfo("Error", "Starting hours can only be changed in the Overtime Schedule.")
            return
        
        if self.user_selections['selected_month'].month != 1:
            messagebox.showinfo("Error", "Starting hours can only be changed in January.")
            return

        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Selection Error", "No crew member selected.")
            return

        selected_name = self.tree.item(selected_items[0])['values'][0]
        new_starting_working_hours = self.crew_member_starting_working_hours.get()
        new_starting_asking_hours = self.crew_member_starting_asking_hours.get()

        try:
            if not new_starting_working_hours.isdigit() or not new_starting_asking_hours.isdigit():
                messagebox.showerror("Entry Error", "Starting hours must be a number.")

            new_starting_working_hours = int(new_starting_working_hours)
            new_starting_asking_hours = int(new_starting_asking_hours)

            crew = self.user_selections['selected_crew']
            year = self.user_selections['selected_year'].year

            # Call the function to adjust the crew member's starting hours
            adjust_crew_member_starting_hours(selected_name, crew, year, new_starting_working_hours, new_starting_asking_hours)

            messagebox.showinfo("Success", "Starting hours updated successfully.")

        except ValueError as e:
            messagebox.showerror("Error", str(e))
            logging.error(f"ValueError applying changes.\nException: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logging.error(f"ValueError applying changes.\nException: {str(e)}")

    def configure_button_frame(self):
        """
        Configure the frame widget containing all button options in the TL window.
        """
        self.button_frame = tk.Frame(
            self, bg=FILE_MENU_BG_COLOR, relief="flat", borderwidth=1
        )

        self.close_schedule_manager_btn = ctk.CTkButton(
            self.button_frame, text="Close", 
            fg_color="#730110", hover_color="#940115", 
            command=lambda: self.destroy()
        )
        self.close_schedule_manager_btn.grid(row=0, column=0, sticky="ew", 
                                             padx=10, pady=10)
        
        add_name_btn = ctk.CTkButton(
            self.button_frame, text="Add New Name", 
            fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_BG_COLOR, 
            command=self.add_name
        )
        add_name_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        remove_name_btn = ctk.CTkButton(
            self.button_frame, text="Remove Selected Name", 
            fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_BG_COLOR, 
            command=self.remove_name
        )
        remove_name_btn.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        move_up_btn = ctk.CTkButton(
            self.button_frame, text="Move Up",
            fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_BG_COLOR,
            command=self.move_up
        )
        move_up_btn.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        move_down_btn = ctk.CTkButton(
            self.button_frame, text="Move Down",
            fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_BG_COLOR,
            command=self.move_down
        )
        move_down_btn.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        
        # Add empty space between the "Remove Selected Name" and "Edit Selected Name" buttons
        empty_space = tk.Frame(self.button_frame, bg=FILE_MENU_BG_COLOR, height=50)
        empty_space.grid(row=5, column=0, sticky="nsew")

        edit_name_btn = ctk.CTkButton(
            self.button_frame, text="Edit Selected Name", 
            fg_color=BUTTON_FG_COLOR, hover_color=BUTTON_HOVER_BG_COLOR, 
            command=self.edit_name
        )
        edit_name_btn.grid(row=6, column=0, sticky="sew", padx=10, pady=17)

        self.button_frame.grid_columnconfigure(0, weight=1)
        
        # Push the "Edit Selected Name" button to the bottom
        self.button_frame.grid_rowconfigure(5, weight=1)

    def move_up(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        selected_item = selected_items[0]
        index = self.tree.index(selected_item)
        if index > 0:
            self.tree.move(selected_item, "", index - 1)
            self.tree.selection_set(selected_item)
            self.tree.focus(selected_item)
            
            moved_name = self.tree.item(selected_item)['values'][0]
            self.moved_personnel.append((moved_name, index - 1))

    def move_down(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        selected_item = selected_items[0]
        index = self.tree.index(selected_item)
        if index < len(self.tree.get_children()) - 1:
            self.tree.move(selected_item, "", index + 1)
            self.tree.selection_set(selected_item)
            self.tree.focus(selected_item)

            # Store the moved personnel name and new position
            moved_name = self.tree.item(selected_item)['values'][0]
            self.moved_personnel.append((moved_name, index + 1))
        
    def configure_treeview(self):
        """
        Configure the Treeview widget to display crew member names.
        """
        self.tree = ttk.Treeview(self)
        self.tree["columns"] = ("Name")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Name", width=270, minwidth=270)
        self.tree.heading("Name", text="Name", anchor=tk.W)

        # Remove the current list
        self.tree.delete(*self.tree.get_children())
        
        # Add the new names from labels with alternating row colors
        for i, name in enumerate(self.initial_names):
            if i % 2 == 0:
                self.tree.insert("", tk.END, values=(name,), tags=("evenrow",))
            else:
                self.tree.insert("", tk.END, values=(name,), tags=("oddrow",))
        
        self.tree.update()

        # Set the Treeview style
        self.set_tree_style()
    
    def set_tree_style(self):
        """
        Set the style of the Treeview widget.
        """
        style = ttk.Style()
        
        style.theme_use("clam")
        
        # Configure the Treeview style
        style.configure("Custom.Treeview",
                        background=TREEVIEW_EVEN,
                        fieldbackground=TREEVIEW_EVEN,
                        foreground=TREEVIEW_TEXT, highlightthickness=0
        )
        
        style.configure("Custom.Treeview.Heading",
                        background="black",
                        foreground="white",
                        relief="flat"
        )
        
        # Configure the selected item style
        style.map("Custom.Treeview",
                background=[('selected', TREEVIEW_SELECTED)],
                foreground=[('selected', "white")])
        
        # Apply the "Custom.Treeview" style to the Treeview widget
        self.tree.configure(style="Custom.Treeview")
        
        # Configure alternating row colors
        self.tree.tag_configure(
            "evenrow", background=TREEVIEW_EVEN, foreground=TREEVIEW_TEXT
        )
        self.tree.tag_configure(
            "oddrow", background=TREEVIEW_ODD, foreground=TREEVIEW_TEXT
        )

    def on_tree_select(self, event):
        """
        Called when the selection in the Treeview changes.
        Enables editing of the selected crew member name.

        Args:
            event: The event object triggered by the selection change.
        """
        # Get the selected item
        selected_items = self.tree.selection()
        if not selected_items:
            # No item selected, disable the entry box
            self.new_name_entry.config(state="disabled")
            if hasattr(self, 'starting_hours_frame') and self.starting_hours_frame.winfo_viewable():
                self.confirm_new_starting_hours_button.configure(state="disabled")
                self.crew_member_starting_working_hours.configure(placeholder_text="", state="disabled")
                self.crew_member_starting_asking_hours.configure(placeholder_text="", state="disabled")
            return
        elif len(selected_items) > 1:
            # Multiple items selected, disable the entry box and clear the name label
            self.new_name_entry.config(state="disabled")
            
            if hasattr(self, 'starting_hours_frame') and self.starting_hours_frame.winfo_viewable():
                self.crew_member_name_label.configure(text="")
                self.confirm_new_starting_hours_button.configure(state="disabled")
                self.crew_member_starting_working_hours.configure(placeholder_text="", state="disabled")
                self.crew_member_starting_asking_hours.configure(placeholder_text="", state="disabled")
        else:
            selected_name_to_edit = selected_items[0]
            selected_name = self.tree.item(selected_name_to_edit)['values'][0]
            
            if hasattr(self, 'starting_hours_frame') and self.starting_hours_frame.winfo_viewable():
                if self.schedule_type == "Overtime":
                    self.crew_member_name_label.configure(text=selected_name)
                    
                    # Load the data from JSON
                    crew = self.user_selections['selected_crew']
                    month = self.user_selections['selected_month'].month
                    year = self.user_selections['selected_year'].year
                    schedule_type = self.schedule_type
                    
                    data = load_hours_data_from_json(crew, month, year, schedule_type)
                    member_data = data.get(selected_name, None)
                    
                    if member_data:
                        self.selected_name_working_hours = member_data.monthly_hours.get('starting_working_hours', 0)
                        self.selected_name_asking_hours = member_data.monthly_hours.get('starting_asking_hours', 0)

                        self.crew_member_starting_working_hours.configure(placeholder_text=self.selected_name_working_hours, state="normal")
                        self.crew_member_starting_asking_hours.configure(placeholder_text=self.selected_name_asking_hours, state="normal")
                        self.confirm_new_starting_hours_button.configure(state="normal")
                    else:
                        self.crew_member_starting_working_hours.configure(placeholder_text="", state="disabled")
                        self.crew_member_starting_asking_hours.configure(placeholder_text="", state="disabled")
                        self.confirm_new_starting_hours_button.configure(state="disabled")

            # Get the name of the selected item
            old_name = self.tree.item(selected_name_to_edit)['values'][0]

            # Enable the entry box and set its value to the old name
            self.new_name_entry.config(state="normal")
            self.new_name_entry.delete(0, "end")
            self.new_name_entry.insert(0, old_name)

    
    def confirm_changes(self):
        """
        Confirm the changes made to crew member names and apply the changes.
        Update the member count and names in the application.
        Handle and log any exceptions that occur during the process.
        """
        try:
            self.apply_member_count()
            self.app.create_frames()
            
            # Update the scrollbar after updating the member count
            self.app.update_scrollbar()
            messagebox.showinfo("Success", "Member count and names updated successfully.")
        except Exception as e:
            logging.error(f"Error applying changes.\nException: {str(e)}")
            messagebox.showinfo("Error", "There was an error please view the log file.")
    
    def apply_member_count(self):
        """
        Apply the updated member count and names to the corresponding workbooks.
        Create new workbooks if they don't exist.
        Update the app's member count and retrieve the updated names from the frames.
        Handle and display any exceptions that occur during the process.
        """
        num_rows = int(self.selected_num_rows_var.get())
        
        try:
            # Load existing data to determine the preexisting names
            overtime_data = load_hours_data_from_json(self.user_selections['selected_crew'], self.user_selections['selected_month'].month, self.user_selections['selected_year'].year, "Overtime")
            work_schedule_data = load_hours_data_from_json(self.user_selections['selected_crew'], self.user_selections['selected_month'].month, self.user_selections['selected_year'].year, "work_schedule")
            
            # Remove placeholder if it exists from the list is applicable
            if "[placeholder]" in overtime_data:
                del overtime_data["[placeholder]"]
            if "[placeholder]" in work_schedule_data:
                del work_schedule_data["[placeholder]"]
            
            # Get the current crew member names from the Treeview
            current_crew_member_names = [self.tree.item(name)['values'][0] for name in self.tree.get_children()]
            
            # Handle new and existing crew members for the selected month and future months
            for month in range(self.user_selections['selected_month'].month, 13):
                for name in current_crew_member_names:
                    if name not in overtime_data:
                        save_new_crew_member(name, self.user_selections['selected_crew'], month, self.user_selections['selected_year'].year, "Overtime")
                    
                    if name not in work_schedule_data:
                        save_new_crew_member(name, self.user_selections['selected_crew'], month, self.user_selections['selected_year'].year, "work_schedule")
            
            # Move the personnel data in the JSON files if they were moved
            if self.moved_personnel:
                for month in range(self.user_selections['selected_month'].month, 13):
                    move_person_data(self.user_selections, self.moved_personnel, "Overtime")
                    move_person_data(self.user_selections, self.moved_personnel, "work_schedule")
                self.moved_personnel = []
            
            # Remove the crew members from the JSON files if they were removed from the Treeview
            if self.removed_crew_members:
                for month in range(self.user_selections['selected_month'].month, 13):
                    for name in self.removed_crew_members:
                        remove_crew_member(name, self.user_selections['selected_crew'], month, self.user_selections['selected_year'].year, "Overtime")
                        remove_crew_member(name, self.user_selections['selected_crew'], month, self.user_selections['selected_year'].year, "work_schedule")
                
            # Update the crew member names in the JSON files if they were edited
            if self.edited_crew_members:
                for month in range(self.user_selections['selected_month'].month, 13):
                    for old_name, new_name in self.edited_crew_members.items():
                        change_crew_member_name(old_name, new_name, self.user_selections['selected_crew'], month, self.user_selections['selected_year'].year, "Overtime")
                        change_crew_member_name(old_name, new_name, self.user_selections['selected_crew'], month, self.user_selections['selected_year'].year, "work_schedule")
            
            # Clear the edited and removed crew member lists
            self.edited_crew_members = {}
            self.removed_crew_members = []
            
            self.app.crew_member_count = num_rows
            self.app.get_labels()

        except Exception as e:
            logging.error(f"Error applying changes.\nException: {str(e)}")
            messagebox.showerror("Error", str(e))

    def add_name(self):
        """
        Open a new window to add new crew member names.
        Update the Treeview and the selected number of rows variable with the added names.
        """
        # Add a new name to the Treeview and the Schedule Labels
        def confirm_add():
            new_names = [entry.get() for entry in name_entries]
            
            for new_name in new_names:
                if new_name:
                    self.tree.insert("", tk.END, values=(new_name,))
            
            self.selected_num_rows_var.set(len(self.tree.get_children()))
            self.num_rows_label.configure(text=f"{self.selected_num_rows_var.get()} Crew Members")
            add_window.destroy()
        
        def add_entry():
            name_label = tk.Label(
                add_window, text="Member Name:", 
                font=("Calibri", 12),
                background=APP_BG_COLOR, fg=TEXT_COLOR
            )
            name_label.grid(row=len(name_entries)+1, column=0, padx=10, pady=5)

            name_entry = tk.Entry(add_window)
            name_entry.grid(row=len(name_entries)+1, column=1, padx=10, pady=5)
            name_entries.append(name_entry)
            name_entry.focus_set()  # Set focus to the new entry

        def remove_entry():
            if name_entries:
                last_entry = name_entries.pop()
                last_entry.destroy()
                last_label = add_window.grid_slaves(row=len(name_entries)+1, column=0)[0]
                last_label.destroy()
                if name_entries:
                    name_entries[-1].focus_set()

        def on_tab(event):
            add_entry()
            return "break"  # Prevent default Tab behavior

        def on_ctrl_z(event):
            if len(name_entries) > 1:
                remove_entry()
            return "break"  # Prevent default Ctrl+Z behavior
        
        def on_enter(event):
            confirm_add()
            return "break"  # Prevent default Enter behavior
        
        name_entries = []

        add_window = tk.Toplevel(self)
        add_window.overrideredirect(True)
        add_window.title("Add New Crew Members")
        add_window.configure(bg=APP_BG_COLOR)
        
        # Bind the hotkeys
        add_window.bind("<Tab>", on_tab)
        add_window.bind("<Control-z>", on_ctrl_z)
        add_window.bind("<Return>", on_enter)

        # Calculate the center position
        app_window_width = self.winfo_width()
        app_window_height = self.winfo_height()
        app_window_x = self.winfo_x()
        app_window_y = self.winfo_y()

        add_window_width = add_window.winfo_reqwidth()
        add_window_height = add_window.winfo_reqheight()

        center_x = app_window_x + (app_window_width - add_window_width) // 2
        center_y = app_window_y + (app_window_height - add_window_height) // 2

        # Set the position of the window to the center of the application window
        add_window.geometry(f"+{center_x}+{center_y}")

        add_label = tk.Label(
            add_window, text="Enter member names below.", 
            font=("Calibri", 14, "bold"), 
            bg=APP_BG_COLOR, fg=TEXT_COLOR
        )
        add_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="ew")

        add_entry()  # Add the first entry field

        confirm_button = ctk.CTkButton(
            add_window, text="Confirm", command=confirm_add, 
            fg_color=BUTTON_FG_COLOR, 
            hover_color=BUTTON_HOVER_BG_COLOR, 
            text_color=TEXT_COLOR
        )
        confirm_button.grid(row=101, column=0, padx=10, pady=10, sticky="ew")
        
        cancel_button = ctk.CTkButton(
            add_window, text="Cancel", command=lambda: add_window.destroy(), 
            fg_color=BUTTON_FG_COLOR, 
            hover_color=BUTTON_HOVER_BG_COLOR, 
            text_color=TEXT_COLOR
        )
        cancel_button.grid(row=101, column=1, padx=10, pady=10, sticky="ew")

        # Modify the add_entry and remove_last buttons to use the new functions
        add_another_button = ctk.CTkButton(
            add_window, text="+ (Tab)", command=add_entry, 
            font=("Calibri", 14, "bold"),
            fg_color="#047a1b", 
            hover_color="#02a120", 
            text_color="white"
        )
        add_another_button.grid(row=100, column=0, columnspan=1, padx=10, pady=10, sticky="ew")
        
        remove_last_button = ctk.CTkButton(
            add_window, text="- (Ctrl+z)", 
            command=lambda: remove_entry() if len(name_entries) > 1 else None,
            font=("Calibri", 14, "bold"),
            fg_color="#7a0404", 
            hover_color="#a10202", 
            text_color="white"
        )
        remove_last_button.grid(row=100, column=1, columnspan=1, padx=10, pady=10, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def edit_name(self):
        """
        Edit the selected crew member name in the Treeview.
        Update the name in the Treeview based on the entry box value.
        Disable the entry box after editing.
        Store the old and new crew member names for later updating in the JSON files.
        """
        # init edited_crew_members
        self.edited_crew_members = {}
        
        # Get the new name from the entry box
        new_name = self.new_name_entry.get()
        
        # Get the selected item
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Editing Error", "You didn't select anything to edit")
            return
        elif new_name == selected_items:
            messagebox.showinfo("Editing Error", "No change made to existing name.")
        elif new_name == "":
            messagebox.showinfo("Editing Error", "Selected item cannot be blank")

        selected_name_to_edit = selected_items[0]
        
        # Store the old and new crew member names
        old_name = self.tree.item(selected_name_to_edit, 'values')[0]
        self.edited_crew_members[old_name] = new_name
        
        # Update the name in the treeview
        self.tree.item(selected_name_to_edit, values=(new_name,))

        # Disable the entry box
        self.new_name_entry.config(state="disabled")

    def remove_name(self):
        """
        Remove the selected crew member name from the Treeview.
        Update the selected number of rows variable and the label displaying the crew member count.
        """
        # Get the selected item
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Selection Error", "Selected item cannot be blank")
            return

        # Store the removed crew member names
        self.removed_crew_members = []
        
        # Remove the selected item from the tree
        for item in selected_items:
            crew_member_name = self.tree.item(item)['values'][0]
            self.removed_crew_members.append(crew_member_name)
            self.tree.delete(item)
            
        self.selected_num_rows_var.set(len(self.tree.get_children()))
        self.num_rows_label.configure(text=f"{self.selected_num_rows_var} Crew Members")



class MockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mock Application")
        self.geometry("400x300")
        self.configure(bg="white")

        self.member_count = 0
        self.initial_names = ["John", "Jane", "Doe"]

        self.open_manager_button = tk.Button(
            self,
            text="Open Schedule Manager",
            command=self.open_schedule_manager
        )
        self.open_manager_button.pack(pady=20)


if __name__ == "__main__":
    app = MockApp()
    app.mainloop()