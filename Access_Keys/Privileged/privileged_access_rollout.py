# PEP8 Compliant Guidance
# Standard Library Imports
import os
import logging
import pickle
import tkinter as tk
from tkinter import messagebox

# Third-Party Library Imports
from Crypto.Cipher import AES

"""
PyInstaller Export

pip install pyinstaller

Syntax:
pyinstaller --name="Privileged_Key" --noconsole --onefile --icon=icon.ico privileged_access_rollout.py
"""

"""
Nuitka Export

pip install nuitka

Syntax:
python -m nuitka --onefile --windows-disable-console --windows-icon-from-ico=icon.ico --output-filename="Privileged_Key.exe" privileged_access_rollout.py
"""

log_directory = os.path.join(os.getcwd(), "SaveFiles", "TrackingLogs")
log_file = os.path.join(log_directory, "app.log")

registry_directory = os.path.join(os.getcwd(), "SaveFiles", "UserRegistry")
ACCESS_LEVEL_ENCRYPTION = os.path.join(registry_directory, "access_levels.enc")

# Fixed Level List
ACCESS_LEVELS = ["admin", "privileged", "read-only"]

# Create log directory if it doesn't exist
try:
    os.makedirs(log_directory, exist_ok=True)
except OSError as e:
    messagebox.showerror("Error", f"Failed to create log directory: {str(e)}")
    logging.error(f"Failed to create log directory: {str(e)}")

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file,
                    filemode='a')

# Create registry directory if it doesn't exist
try:
    os.makedirs(registry_directory, exist_ok=True)
except OSError as e:
    messagebox.showerror("Error", f"Failed to create registry directory: {str(e)}")
    logging.error(f"Failed to create registry directory: {str(e)}")

# Use the fixed 256-bit AES key
key = b'S)\xba\xe4\xaf\x7f\x08\xf1\xe9\xd5\xb6\xdb\xe9\x89\xcc=\x0b\x92)6F\xc14\x19p\x88\xa3\x07\t\xacq\x01'

user_access_levels = {} # type: ignore

# Load user access levels from the access_levels.enc file
def load_user_access_levels():
    """
    Load user access levels from the access_levels.enc file.

    Returns:
        dict: A dictionary containing user access levels.
    """
    try:
        if os.path.exists(ACCESS_LEVEL_ENCRYPTION):
            with open(ACCESS_LEVEL_ENCRYPTION, "rb") as f:
                user_access_levels = pickle.load(f)
        else:
            user_access_levels = {}
    except Exception as e:
        logging.error(f"Error loading user access levels: {e}")
        user_access_levels = {}

    return user_access_levels

def get_user_access_level(username, user_access_levels):
    """
    Retrieve a user's access level during the login process.

    Args:
        username (str): The username.
        user_access_levels (dict[str, tuple[bytes, bytes, bytes]]): A dictionary containing user access levels.

    Returns:
        str | None: The user's access level if found, None otherwise.
    """
    if username in user_access_levels:
        nonce, ciphertext, tag = user_access_levels[username]
        try:
            access_level = decrypt_data(nonce, ciphertext, tag, key)
            return access_level
        except ValueError as e:
            logging.error(f"Error decrypting access level for user {username}: {str(e)}")
            return None
    return None

def encrypt_data(data, key):
    """
    Encrypt the given data using the provided key with AES encryption.

    Args:
        data (str): The data to be encrypted.
        key (bytes): The encryption key.

    Returns:
        tuple[bytes, bytes, bytes]: A tuple containing the nonce, ciphertext, and authentication tag.
    """    
    try:
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        return nonce, ciphertext, tag
    except Exception as e:
        logging.error(f"An error occurred during encryption: {str(e)}")
        return None

def decrypt_data(nonce, ciphertext, tag, key):  
    """
    Decrypt the given ciphertext using the provided key, nonce, and tag with AES encryption.

    Args:
        nonce (bytes): The nonce used for encryption.
        ciphertext (bytes): The encrypted data.
        tag (bytes): The authentication tag.
        key (bytes): The encryption key.

    Returns:
        str | None: The decrypted data if successful, None otherwise.
    """    
    try:
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        decrypted_data = plaintext.decode('utf-8')
        return decrypted_data
    except ValueError as e:
        logging.error(f"Decryption failed: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"An error occurred during decryption: {str(e)}")
        return None

# Save user access levels to the access_levels.enc file
def save_user_access_levels(user_access_levels):
    """
    Save user access levels to the access_levels.enc file.

    Args:
        user_access_levels (dict): A dictionary containing user access levels.

    Raises:
        Exception: If an error occurs while saving user access levels.
    """
    try:
        with open(ACCESS_LEVEL_ENCRYPTION, "wb") as f:
            pickle.dump(user_access_levels, f)
    except Exception as e:
        logging.error(f"Error saving user access levels: {e}")
        messagebox.showerror("Error", "Failed to save user access levels.")

def register_or_update_user(user_id, access_level):
    """
    Register a new user or update an existing user's access level.

    Args:
        user_id (str): The user ID.
        access_level (str): The access level to be assigned.
    """
    global user_access_levels
    if access_level in ACCESS_LEVELS:
        # Load the existing user access levels from the file
        user_access_levels = load_user_access_levels()

        if user_id in user_access_levels:
            _, existing_ciphertext, _ = user_access_levels[user_id]
            existing_access_level = decrypt_data(*user_access_levels[user_id], key)
            if existing_access_level == access_level:
                messagebox.showinfo("Info", f"User {user_id} already has {access_level} access.")
                logging.info(f"{user_id} attempted to assign duplicate access level: {access_level}")
                return
        nonce, ciphertext, tag = encrypt_data(access_level, key)
        user_access_levels[user_id] = (nonce, ciphertext, tag)
        save_user_access_levels(user_access_levels)  # Pass user_access_levels as an argument
    else:
        logging.error(f"Invalid access level: {access_level}")
        messagebox.showerror("Error", f"Invalid access level: {access_level}")

# Grant privileged access to the current user
def grant_privileged_access():
    """
    Grant privileged access to the current user.

    This function retrieves the current user ID, checks if the user already has privileged access,
    and grants privileged access if not. It updates the user access levels and saves them to the file.
    """
    current_user_id = get_user_id()
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

def get_user_id():
    """
    Retrieve the user ID of the current user.

    Returns:
        str: The user ID, or "Unknown User" if an error occurred.
    """
    try:
        user_id = os.getlogin()
        return user_id
    except Exception as e:
        logging.error(f"Failed to retrieve user ID: {str(e)}")
        return "Unknown User"

# GUI class to provide the access grant interface
class AccessGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grant Privileged Access")
        self.configure(background="white")

        self.user_id = get_user_id()

        self.label_user = tk.Label(self, text=f"User: {self.user_id}", bg="white", fg="black", font=("Calibri", 12, "bold"))
        self.label_user.pack(padx=10, pady=10)

        self.label_instruction = tk.Label(self, text="Click the button below to gain Privileged access to the schedule.", bg="white", fg="black", font=("Calibri", 12))
        self.label_instruction.pack(padx=10, pady=10)
        
        self.label_instruction = tk.Label(
            self, 
            text="Note: This program must be located in the same directory as\nit's affiliated program for it to work as expected.", 
            bg="white", fg="black", font=("Calibri", 12, "italic"), justify="left")
        self.label_instruction.pack(pady=10)

        self.button_grant_access = tk.Button(self, text="Grant Privileged Access", command=self.grant_access, bg="blue", fg="white", font=("Calibri", 12))
        self.button_grant_access.pack(pady=20)

    def grant_access(self):
        grant_privileged_access()

# Main function to run the GUI
def main():
    """
    Run the Access GUI application.
    """
    app = AccessGUI()
    app.mainloop()

if __name__ == "__main__":
    main()