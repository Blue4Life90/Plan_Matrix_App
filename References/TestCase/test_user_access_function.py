from functions import register_or_update_user, load_user_access_levels
from functions import decrypt_data
from functions import key

import logging
import pickle
import os
from unittest.mock import patch

from constants import ACCESS_LEVEL_ENCRYPTION
import win32security # type: ignore

file_path = ACCESS_LEVEL_ENCRYPTION

def print_access_levels():
    global user_access_levels
    try:
        if os.path.exists(ACCESS_LEVEL_ENCRYPTION):
            with open(ACCESS_LEVEL_ENCRYPTION, "rb") as f:
                user_access_levels = pickle.load(f)
            
            print("Current user access levels:")
            for user_id, access_data in user_access_levels.items():
                nonce, ciphertext, tag = access_data
                access_level = decrypt_data(nonce, ciphertext, tag, key)
                print(f"User ID: {user_id}, Access Level: {access_level}")
        else:
            print("Access levels file not found.")
    except Exception as e:
        logging.error(f"Error loading user access levels: {e}")
        
# Print the current access level list
print_access_levels()

def find_file_ownership(file_path):

    # Get the file's owner SID (Security Identifier)
    sd = win32security.GetFileSecurity(file_path, win32security.OWNER_SECURITY_INFORMATION)
    owner_sid = sd.GetSecurityDescriptorOwner()

    # Translate the SID to a readable name
    name, domain, type = win32security.LookupAccountSid(None, owner_sid)

    print_filepath = f"File: {file_path}"
    owner_name = f"Owner: {domain}\\{name}\nFilepath: {print_filepath}"

    return owner_name

# Determine File Ownership
# print(find_file_ownership(file_path))

def test_register_or_update_user():
    global user_access_levels
    user_access_levels = {}  # Clear the user access levels before each test

    # Test case 1: User has no access and will be assigned read-only access
    user_id = "user1"
    access_level = "read-only"
    register_or_update_user(user_id, access_level)
    user_access_levels = load_user_access_levels()  # Load the updated access levels from the file
    assert user_id in user_access_levels
    assert decrypt_data(*user_access_levels[user_id], key) == access_level

    # Test case 2: User has no access and will be assigned privileged access
    user_id = "user2"
    access_level = "privileged"
    register_or_update_user(user_id, access_level)
    user_access_levels = load_user_access_levels()  # Load the updated access levels from the file
    assert user_id in user_access_levels
    assert decrypt_data(*user_access_levels[user_id], key) == access_level

    # Test case 3: User has no access and will be assigned admin access
    user_id = "user3"
    access_level = "admin"
    register_or_update_user(user_id, access_level)
    user_access_levels = load_user_access_levels()  # Load the updated access levels from the file
    assert user_id in user_access_levels
    assert decrypt_data(*user_access_levels[user_id], key) == access_level

    # Test case 4: User already has the assigned access of which they are being assigned
    user_id = "user4"
    access_level = "read-only"
    register_or_update_user(user_id, access_level)
    user_access_levels = load_user_access_levels()  # Load the updated access levels from the file

    # Mock the messagebox.showinfo function
    with patch('tkinter.messagebox.showinfo') as mock_showinfo:
        register_or_update_user(user_id, access_level)
        mock_showinfo.assert_called_once_with("Info", f"User {user_id} already has {access_level} access.")

    # Test case 5: User access level is switched from read-only access to privileged access
    user_id = "user5"
    access_level = "read-only"
    register_or_update_user(user_id, access_level)
    user_access_levels = load_user_access_levels()  # Load the updated access levels from the file
    access_level = "privileged"
    register_or_update_user(user_id, access_level)
    user_access_levels = load_user_access_levels()  # Load the updated access levels from the file
    assert decrypt_data(*user_access_levels[user_id], key) == access_level

    # Test case 6: User access level is switched from privileged access to admin access
    user_id = "user6"
    access_level = "privileged"
    register_or_update_user(user_id, access_level)
    user_access_levels = load_user_access_levels()  # Load the updated access levels from the file
    access_level = "admin"
    register_or_update_user(user_id, access_level)
    user_access_levels = load_user_access_levels()  # Load the updated access levels from the file
    assert decrypt_data(*user_access_levels[user_id], key) == access_level

    print("All test cases passed!")

# Run test cases
# test_register_or_update_user()