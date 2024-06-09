# PEP8 Compliant Guidance
# Standard Library Imports
import os
import pickle
import tkinter as tk
from tkinter import messagebox

# Third-Party Library Imports

# Local Application/Library Specific Imports
from constants import ACCESS_LEVEL_ENCRYPTION
from functions.login_functions import register_or_update_user, get_user_access_level
from functions.header_functions import get_user_id, test_get_user_id

# Use the fixed 256-bit AES key
key = b'S)\xba\xe4\xaf\x7f\x08\xf1\xe9\xd5\xb6\xdb\xe9\x89\xcc=\x0b\x92)6F\xc14\x19p\x88\xa3\x07\t\xacq\x01'

# Load user access levels from the access_levels.enc file
def load_user_access_levels():
    try:
        if os.path.exists(ACCESS_LEVEL_ENCRYPTION):
            with open(ACCESS_LEVEL_ENCRYPTION, "rb") as f:
                user_access_levels = pickle.load(f)
        else:
            user_access_levels = {}
    except Exception as e:
        print(f"Error loading user access levels: {e}")
        user_access_levels = {}

    return user_access_levels

# Save user access levels to the access_levels.enc file
def save_user_access_levels(user_access_levels):
    try:
        with open(ACCESS_LEVEL_ENCRYPTION, "wb") as f:
            pickle.dump(user_access_levels, f)
    except Exception as e:
        print(f"Error saving user access levels: {e}")

# Grant privileged access to the current user
def grant_privileged_access():
    current_user_id = test_get_user_id()
    user_access_levels = load_user_access_levels()
    
    if current_user_id in user_access_levels:
        access_level = get_user_access_level(current_user_id, user_access_levels)
        if access_level == "privileged":
            messagebox.showinfo("Info", f"User {current_user_id} already has privileged access.")
            return
    register_or_update_user(current_user_id, "privileged")
    user_access_levels = load_user_access_levels()
    save_user_access_levels(user_access_levels)
    messagebox.showinfo("Success", f"Granted privileged access to user: {current_user_id}")

# GUI class to provide the access grant interface
class AccessGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grant Privileged Access")
        self.configure(background="white")

        self.user_id = test_get_user_id()

        self.label_user = tk.Label(self, text=f"User: {self.user_id}", bg="white", fg="black", font=("Helvetica", 12))
        self.label_user.pack(pady=10)

        self.label_instruction = tk.Label(self, text="Click the button below to gain 'privileged' access to the schedule", bg="white", fg="black", font=("Helvetica", 12))
        self.label_instruction.pack(pady=10)

        self.button_grant_access = tk.Button(self, text="Grant Privileged Access", command=self.grant_access, bg="blue", fg="white", font=("Helvetica", 12))
        self.button_grant_access.pack(pady=20)

    def grant_access(self):
        grant_privileged_access()

# Main function to run the GUI
def main():
    app = AccessGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
