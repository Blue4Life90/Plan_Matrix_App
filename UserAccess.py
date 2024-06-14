# PEP8 Compliant Guidance
# Standard Library Imports
import logging
import tkinter as tk
from tkinter import messagebox

# Third-Party Library Imports
from PIL import Image
import customtkinter as ctk #type: ignore

# Local Application/Library Specific Imports
from constants import log_file
from constants import APP_BG_COLOR, TEXT_COLOR
from constants import BUTTON_HOVER_BG_COLOR, BUTTON_FG_COLOR
from constants import REGISTRATION_BANNER_IMAGE, LOGIN_BANNER_IMAGE, RESET_PASS_BANNER_IMAGE
from functions.header_functions import get_user_id
from functions.login_functions import update_remember_me
from functions.login_functions import is_verified_user, add_new_user, register_or_update_user
from functions.login_functions import get_user_access_level, load_user_access_levels
from functions.login_functions import hash_password, get_stored_password, verify_password
from functions.login_functions import update_user_password

# Logging Format
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file, 
                    filemode='a')

# Define a specific logger for user access
user_logger = logging.getLogger('user_access')
if not user_logger.handlers:
    user_logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    user_logger.addHandler(handler)
    user_logger.propagate = False  # Prevent propagation to the root logger

class User:
    def __init__(self, username, password, access_level):
        self.username = username
        self.password = password
        self.access_level = access_level
        user_logger.info(f"Login - username: {self.username} / access level: {access_level}")
        
class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Login")
        self.overrideredirect(True)
        self.configure(background=APP_BG_COLOR)
        
        self.username = tk.StringVar(value=str(get_user_id()))

        if is_verified_user(get_user_id()):
            self.open_login_window()
            #self.open_registration_window()
        else:
            self.open_registration_window()
            #self.open_login_window()

        # Center the window on the parent application
        self.center_window()

    def center_window(self):
        self.update_idletasks()  # Update window dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"+{position_x}+{position_y}")

    def open_registration_window(self):
        """Picture Frame"""
        self.registration_window_picture_frame = ctk.CTkFrame(self)
        self.registration_window_picture_frame.grid(row=0, column=0, sticky="nsew")

        self.registration_window_image = ctk.CTkImage(light_image=Image.open(REGISTRATION_BANNER_IMAGE),
                                                    dark_image=Image.open(REGISTRATION_BANNER_IMAGE),
                                                    size=(250, 500))
        self.registration_window_image_label = ctk.CTkLabel(
            self.registration_window_picture_frame,
            text="",
            image=self.registration_window_image
        )
        self.registration_window_image_label.grid(row=0, column=0, sticky="nsew")

        """Registration Frame"""
        self.registration_window_signin_frame = ctk.CTkFrame(self, fg_color=APP_BG_COLOR)
        self.registration_window_signin_frame.grid(row=0, column=1, padx=(20, 20), pady=(40, 0), sticky="nsew")

        self.new_user_info_label = ctk.CTkLabel(
            self.registration_window_signin_frame, 
            text="Welcome!\nPlease enter your information below to register.",
            font=("Calibri", 14), text_color="white"
        )
        self.new_user_info_label.grid(row=0, column=0, padx=10, pady=(50, 5), sticky="w")

        self.new_username_label = ctk.CTkLabel(
            self.registration_window_signin_frame, 
            text="Your Username is your System UserID:",
            font=("Calibri", 14), text_color="white"
        )
        self.new_username_label.grid(row=1, column=0, padx=10, pady=(50, 5), sticky="w")

        self.new_username_entry = ctk.CTkEntry(
            self.registration_window_signin_frame, 
            state="disabled", 
            textvariable=self.username, 
            text_color="black", 
            fg_color="#6f73f7"
        )
        self.new_username_entry.grid(row=2, column=0, padx=10, pady=(0, 20), sticky="ew")

        self.new_password_label = ctk.CTkLabel(
            self.registration_window_signin_frame, text="Please select your new Password:",
            font=("Calibri", 14), text_color="white"
        )
        self.new_password_label.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="w")

        self.new_password_entry = ctk.CTkEntry(self.registration_window_signin_frame, show="*")
        self.new_password_entry.grid(row=4, column=0, padx=10, pady=(0, 20), sticky="ew")

        self.confirm_login_information_button = ctk.CTkButton(
            self.registration_window_signin_frame,
            text="Confirm Login Information",
            command=self.store_new_credentials,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_BG_COLOR,
            text_color=TEXT_COLOR
        )
        self.confirm_login_information_button.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Bind the "Enter" key event to the login button
        self.confirm_login_information_button.bind("<Return>", lambda event: self.store_new_credentials())

        # Bind the "Enter" key event to the login window
        self.bind("<Return>", lambda event: self.store_new_credentials())

        self.bypass_login_button = ctk.CTkButton(
            self.registration_window_signin_frame,
            text="Bypass Login (read-only)",
            command=self.read_only_access,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_BG_COLOR,
            text_color=TEXT_COLOR
        )
        self.bypass_login_button.grid(row=6, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.close_registration_button = ctk.CTkButton(
            self.registration_window_signin_frame,
            text="Close App",
            command=self.close_app,
            fg_color="#730110",
            hover_color="#940115",
            text_color=TEXT_COLOR
        )
        self.close_registration_button.grid(row=7, column=0, padx=10, pady=(0, 25), sticky="ew")
        
        self.trademark_info_label = ctk.CTkLabel(
            self.registration_window_signin_frame, 
            text="Created April 2024 @ MDGL",
            font=("Calibri", 8), text_color=TEXT_COLOR
        )
        self.trademark_info_label.grid(row=8, column=0, sticky="e")

    def open_login_window(self):
        """Picture Frame"""
        self.login_window_picture_frame = ctk.CTkFrame(self)
        self.login_window_picture_frame.grid(row=0, column=0, sticky="nsew")

        self.login_window_image = ctk.CTkImage(light_image=Image.open(LOGIN_BANNER_IMAGE),
                                            dark_image=Image.open(LOGIN_BANNER_IMAGE),
                                            size=(250, 500))
        self.login_window_image_label = ctk.CTkLabel(
            self.login_window_picture_frame,
            text="",
            image=self.login_window_image
        )
        self.login_window_image_label.grid(row=0, column=0, sticky="nsew")

        """Login Frame"""
        self.login_window_frame = ctk.CTkFrame(self, fg_color=APP_BG_COLOR)
        self.login_window_frame.grid(row=0, column=1, padx=(20, 20), pady=(40, 0), sticky="nsew")

        self.user_info_label = ctk.CTkLabel(
            self.login_window_frame, 
            text="Welcome!\nPlease enter your password below to login.",
            font=("Calibri", 14), text_color="white"
        )
        self.user_info_label.grid(row=0, column=0, padx=10, pady=(20, 0), sticky="w")
        
        self.username_label = ctk.CTkLabel(
            self.login_window_frame, text="System ID:",
            font=("Calibri", 14), text_color="white"
        )
        self.username_label.grid(row=1, column=0, padx=10, pady=(30, 5), sticky="w")
        self.username_entry = ctk.CTkEntry(
            self.login_window_frame, 
            state="disabled", 
            textvariable=self.username, 
            fg_color="#6f73f7"
            )
        self.username_entry.grid(row=2, column=0, padx=10, pady=(0, 20), sticky="ew")

        self.password_label = ctk.CTkLabel(
            self.login_window_frame, text="Password:",
            font=("Calibri", 14), text_color="white"
        )
        self.password_label.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="w")
        self.password_entry = ctk.CTkEntry(self.login_window_frame, show="*")
        self.password_entry.grid(row=4, column=0, padx=10, pady=(0, 20), sticky="ew")
        
        self.remember_me_var = tk.BooleanVar()
        # Retrieve the remember_me value and set the state of the checkbox
        stored_hash, self.remember_me = get_stored_password(self.username_entry.get())
        self.remember_me_var.set(self.remember_me)
        
        self.remember_me_checkbox = ctk.CTkCheckBox(
            self.login_window_frame,
            text="Remember my password",
            border_width=2,
            hover_color="#6f73f7",
            font=("Calibri", 14),
            text_color="white",
            fg_color=(APP_BG_COLOR,"#6f73f7"),
            variable=self.remember_me_var,
            onvalue=True,
            offvalue=False,
            command=self.toggle_password_entry
        )
        self.remember_me_checkbox.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # If remember_me is true, disable the password entry and populate it with asterisks
        if self.remember_me:
            hidden_password = "**********"
            self.password_entry.configure(
                placeholder_text=hidden_password, 
                textvariable=hidden_password, 
                fg_color="#6f73f7", 
                placeholder_text_color="black"
            )
            # Entry must be disabled after setting placeholder text to color
            self.password_entry.configure(state="disabled")

        self.login_button = ctk.CTkButton(
            self.login_window_frame, text="Login",
            command=self.authenticate,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_BG_COLOR,
            text_color=TEXT_COLOR
        )
        self.login_button.grid(row=6, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Bind the "Enter" key event to the login button
        self.login_button.bind("<Return>", lambda event: self.authenticate())

        # Bind the "Enter" key event to the login window
        self.bind("<Return>", lambda event: self.authenticate())

        self.read_only_button = ctk.CTkButton(
            self.login_window_frame, text="Read-only",
            command=self.read_only_access,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_BG_COLOR,
            text_color=TEXT_COLOR
        )
        self.read_only_button.grid(row=7, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.close_login_button = ctk.CTkButton(
            self.login_window_frame,
            text="Close App",
            command=self.close_app,
            fg_color="#730110",
            hover_color="#940115",
            text_color=TEXT_COLOR
        )
        self.close_login_button.grid(row=8, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        self.reset_password_button = ctk.CTkButton(
            self.login_window_frame,
            text="Forgot Password?",
            command=self.reset_password,
            fg_color=APP_BG_COLOR,
            hover_color=APP_BG_COLOR,
            text_color="#6f73f7",
            border_width=0,
            font=("Calibri", 12, "underline")
        )
        self.reset_password_button.grid(row=9, column=0, padx=0, pady=(0, 10), sticky="w")
        
        self.login_trademark_info_label = ctk.CTkLabel(
            self.login_window_frame, 
            text="Created April 2024 @ MDGL",
            font=("Calibri", 8), text_color=TEXT_COLOR
        )
        self.login_trademark_info_label.grid(row=10, column=0, sticky="e")
    
    def reset_password(self):
        self.destroy()
        ResetPasswordWindow(self.parent)
    
    def toggle_password_entry(self):
        if not self.remember_me_var.get():
            self.password_entry.configure(state="normal", fg_color="white")
            self.password_entry.delete(0, tk.END)
    
    def store_new_credentials(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Registration Failed", "Please enter your password.")
            return
        
        hashed_password = hash_password(self.new_password_entry.get())
        add_new_user(self.new_username_entry.get(), hashed_password)
        
        # Set default access level for the new user
        user_access_levels = load_user_access_levels()
        if username not in user_access_levels:
            register_or_update_user(username, "read-only")
        
        messagebox.showinfo("Successfully Registered", "Your User ID and password have been registered.\nPlease login with your new password in the next window.")
        self.destroy()
        LoginWindow(self.parent)  # Create a new instance of LoginWindow
        
    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        remember_me = self.remember_me_var.get()

        if not self.remember_me:
            # Not necessary in: 
                #Test Case 2
            if not username or not password:
                messagebox.showerror("Login Failed", "Please enter your password.")
                return

        stored_hash_tuple = get_stored_password(username)

        if self.remember_me and remember_me and stored_hash_tuple[1]:
            # If "Remember me" is selected and the stored remember_me value is True
            user_access_levels = load_user_access_levels()
            access_level = get_user_access_level(username, user_access_levels)
            if access_level:
                self.parent.current_user = User(username, "", access_level)
                self.parent.initialize_application()
                self.destroy()
            else:
                messagebox.showerror("Login Failed", "Access level not set for this user.")
        else: 
            if not password:
                messagebox.showerror("Login Failed", "Please enter your password.")
                return
            if stored_hash_tuple and verify_password(stored_hash_tuple, password):
                update_remember_me(username, remember_me)
                
                user_access_levels = load_user_access_levels()
                access_level = get_user_access_level(username, user_access_levels)
                if access_level:
                    self.parent.current_user = User(username, "", access_level)
                    self.parent.initialize_application()
                    self.destroy()
                else:
                    messagebox.showerror("Login Failed", "Access level not set for this user.")
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

    def read_only_access(self):
        self.parent.current_user = User("", "", "read-only")
        self.parent.initialize_application()
        self.destroy()
        
    def close_app(self):
        self.parent.destroy()
        
class ResetPasswordWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Reset Password")
        self.overrideredirect(True)
        self.configure(background=APP_BG_COLOR)

        self.username = tk.StringVar(value=str(get_user_id()))

        self.open_reset_password_window()

        # Center the window on the parent application
        self.center_window()

    def center_window(self):
        self.update_idletasks()  # Update window dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"+{position_x}+{position_y}")

    def open_reset_password_window(self):
        """Picture Frame"""
        self.reset_password_picture_frame = ctk.CTkFrame(self)
        self.reset_password_picture_frame.grid(row=0, column=0, sticky="nsew")

        self.reset_password_image = ctk.CTkImage(light_image=Image.open(RESET_PASS_BANNER_IMAGE),
                                                 dark_image=Image.open(RESET_PASS_BANNER_IMAGE),
                                                 size=(250, 500))
        self.reset_password_image_label = ctk.CTkLabel(
            self.reset_password_picture_frame,
            text="",
            image=self.reset_password_image
        )
        self.reset_password_image_label.grid(row=0, column=0, sticky="nsew")

        """Reset Password Frame"""
        self.reset_password_frame = ctk.CTkFrame(self, fg_color=APP_BG_COLOR)
        self.reset_password_frame.grid(row=0, column=1, padx=(20, 20), pady=(40, 0), sticky="nsew")

        self.reset_password_info_label = ctk.CTkLabel(
            self.reset_password_frame,
            text="Reset Password\nPlease enter your new password below.",
            font=("Calibri", 14), text_color="white"
        )
        self.reset_password_info_label.grid(row=0, column=0, padx=10, pady=(50, 5), sticky="w")

        self.reset_password_username_label = ctk.CTkLabel(
            self.reset_password_frame,
            text="Your Username:",
            font=("Calibri", 14), text_color="white"
        )
        self.reset_password_username_label.grid(row=1, column=0, padx=10, pady=(50, 5), sticky="w")

        self.reset_password_username_entry = ctk.CTkEntry(
            self.reset_password_frame,
            state="disabled",
            textvariable=self.username,
            text_color="black",
            fg_color="#6f73f7"
        )
        self.reset_password_username_entry.grid(row=2, column=0, padx=10, pady=(0, 20), sticky="ew")

        self.reset_password_new_password_label = ctk.CTkLabel(
            self.reset_password_frame, text="New Password:",
            font=("Calibri", 14), text_color="white"
        )
        self.reset_password_new_password_label.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="w")

        self.reset_password_new_password_entry = ctk.CTkEntry(self.reset_password_frame, show="*")
        self.reset_password_new_password_entry.grid(row=4, column=0, padx=10, pady=(0, 20), sticky="ew")

        self.reset_password_confirm_button = ctk.CTkButton(
            self.reset_password_frame,
            text="Confirm Password Reset",
            command=self.update_password,
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_BG_COLOR,
            text_color=TEXT_COLOR
        )
        self.reset_password_confirm_button.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Bind the "Enter" key event to the confirm button
        self.reset_password_confirm_button.bind("<Return>", lambda event: self.update_password())

        # Bind the "Enter" key event to the reset password window
        self.bind("<Return>", lambda event: self.update_password())

        self.reset_password_close_button = ctk.CTkButton(
            self.reset_password_frame,
            text="Close",
            command=self.close_reset_password_window,
            fg_color="#730110",
            hover_color="#940115",
            text_color=TEXT_COLOR
        )
        self.reset_password_close_button.grid(row=6, column=0, padx=10, pady=(0, 25), sticky="ew")

        self.reset_password_trademark_info_label = ctk.CTkLabel(
            self.reset_password_frame,
            text="Created April 2024 @ MDGL",
            font=("Calibri", 8), text_color=TEXT_COLOR
        )
        self.reset_password_trademark_info_label.grid(row=7, column=0, sticky="e")

    def update_password(self):
        username = self.username.get()
        new_password = self.reset_password_new_password_entry.get()

        if not username or not new_password:
            messagebox.showerror("Reset Password Failed", "Please enter your new password.")
            return

        hashed_password = hash_password(new_password)
        update_user_password(username, hashed_password)

        messagebox.showinfo("Password Updated", "Your password has been successfully updated.")
        self.destroy()
        LoginWindow(self.parent)  # Create a new instance of LoginWindow

    def close_reset_password_window(self):
        self.destroy()
        LoginWindow(self.parent)  # Create a new instance of LoginWindow