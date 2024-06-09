# PEP8 Compliant Guidance
# Standard Library Imports
import tkinter as tk
from tkinter import messagebox

# Third-Party Library Imports
import customtkinter as ctk # type: ignore

# Local Application/Library Specific Imports
from functions.login_functions import register_or_update_user, ACCESS_LEVELS
from functions.login_functions import get_user_ids
from constants import load_icons
from constants import APP_BG_COLOR, BUTTON_FG_COLOR, BUTTON_HOVER_BG_COLOR, TEXT_COLOR

class AccessLevelManager(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Access Level Manager")
        # Load icons after the root window is initialized
        self.iconpath_0, self.iconpath_1, self.iconpath_2 = load_icons()
        self.iconphoto(False, self.iconpath_0)  # Set the icon for the main window
        
        self.configure(bg=APP_BG_COLOR)

        # Create comboboxes and button
        self.user_label = ctk.CTkLabel(
            self, 
            font=("Calibri", 14), text_color="white", 
            text="User:", 
            fg_color=APP_BG_COLOR
        )
        self.user_label.grid(row=0, column=0, padx=10, pady=10)

        self.user_combobox = ctk.CTkComboBox(
            self, values=get_user_ids(), 
            font=("Calibri", 14)
        )
        self.user_combobox.grid(row=0, column=1, padx=10, pady=10)

        self.access_level_label = ctk.CTkLabel(
            self, 
            text="Access Level:",
            font=("Calibri", 14), 
            text_color="white", 
            fg_color=APP_BG_COLOR
        )
        self.access_level_label.grid(row=1, column=0, padx=10, pady=10)

        # Determine the available access levels based on the user's access level
        if self.parent.current_user.access_level == "admin":
            available_access_levels = ACCESS_LEVELS
        else:
            available_access_levels = [level for level in ACCESS_LEVELS if level != "admin"]

        self.access_level_combobox = ctk.CTkComboBox(
            self, 
            values=available_access_levels, 
            font=("Calibri", 14)
        )
        self.access_level_combobox.grid(row=1, column=1, padx=10, pady=10)

        self.confirm_button = ctk.CTkButton(
            self, 
            text="Confirm", 
            command=self.update_access_level,
            font=("Calibri", 14, "bold"), 
            fg_color=BUTTON_FG_COLOR, 
            hover_color=BUTTON_HOVER_BG_COLOR, 
            text_color=TEXT_COLOR
        )
        self.confirm_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def update_access_level(self):
        user_id = self.user_combobox.get()
        access_level = self.access_level_combobox.get()

        if user_id and access_level:
            try:
                register_or_update_user(user_id, access_level)
                messagebox.showinfo("Success", f"Access level for {user_id} updated to {access_level}")
            except PermissionError:
                messagebox.showinfo("Info", f"User {user_id} already has {access_level} access.")
        else:
            messagebox.showerror("Error", "Please select a user and an access level.")