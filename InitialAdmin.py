# PEP8 Compliant Guidance
# Standard Library Imports
import os
import pickle

# Third-Party Library Imports
from Crypto.Cipher import AES

# Local Application/Library Specific Imports
from constants import ACCESS_LEVEL_ENCRYPTION
from functions.login_functions import user_exists, register_or_update_user, get_user_access_level
from functions.header_functions import get_user_id

# Use the fixed 256-bit AES key
key = b'S)\xba\xe4\xaf\x7f\x08\xf1\xe9\xd5\xb6\xdb\xe9\x89\xcc=\x0b\x92)6F\xc14\x19p\x88\xa3\x07\t\xacq\x01'

# Encryption function
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return nonce, ciphertext, tag

# Decryption function
def decrypt_data(nonce, ciphertext, tag, key):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode('utf-8')

# Data structure to store user access levels
user_access_levels = {} # type: ignore

# Save user access levels to the access_levels.enc file
def save_user_access_levels():
    with open(ACCESS_LEVEL_ENCRYPTION, "wb") as f:
        pickle.dump(user_access_levels, f)

# Load user access levels from the access_levels.enc file
def load_user_access_levels():
    try:
        if os.path.exists(ACCESS_LEVEL_ENCRYPTION):
            with open(ACCESS_LEVEL_ENCRYPTION, "rb") as f:
                user_access_levels = pickle.load(f)
        else:
            # File doesn't exist, initialize an empty dictionary
            user_access_levels = {}
    except Exception as e:
        print(f"Error loading user access levels: {e}")
        user_access_levels = {}

    return user_access_levels

# Grant admin access to the current user
def grant_admin_access():
    current_user_id = get_user_id()
    if user_exists(current_user_id):
        # Update the existing user's access level to admin
        register_or_update_user(current_user_id, "admin")
        print(f"Updated admin access for user: {current_user_id}")
    else:
        # Register the new user with admin access level
        register_or_update_user(current_user_id, "admin")
        print(f"Granted admin access to new user: {current_user_id}")

# Main function
def main():
    current_user_id = get_user_id()
    load_user_access_levels()  # Load user access levels before granting admin access
    grant_admin_access()

    # Check the access level for the current user
    access_level = get_user_access_level(current_user_id, user_access_levels)
    if access_level:
        print(f"User {current_user_id} has access level: {access_level}")
    else:
        print(f"User {current_user_id} not found or access level not set.")

if __name__ == "__main__":
    main()