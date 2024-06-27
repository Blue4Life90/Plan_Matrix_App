# PEP8 Compliant Guidance
# Standard Library Imports
import os
import csv
import pickle
import logging

# Third-Party Library Imports
import bcrypt
from Crypto.Cipher import AES

# Local Application/Library Specific Imports
from constants import log_file
from constants import USER_ID_FILE, ACCESS_LEVEL_ENCRYPTION

# Logging Format
logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file, 
                    filemode='a'
)

# Blank list for function assignment
user_access_levels = {} # type: ignore

# Fixed Level List
ACCESS_LEVELS = ["admin", "privileged", "read-only"]

def get_user_ids():
    """
    Retrieves a list of user IDs from the USER_ID_FILE.

    Returns:
        list[str]: A list of user IDs.
    """
    users_file_path = USER_ID_FILE
    user_ids = []
    try:
        with open(users_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_ids.append(row['username'])
    except FileNotFoundError:
        logging.error(f"File '{users_file_path}' not found.")
        return []
    except Exception as e:
        logging.error(f"An error occurred while reading user IDs: {str(e)}")
        return []
    return user_ids

# Fixed 256-bit AES key
key = b'S)\xba\xe4\xaf\x7f\x08\xf1\xe9\xd5\xb6\xdb\xe9\x89\xcc=\x0b\x92)6F\xc14\x19p\x88\xa3\x07\t\xacq\x01'

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

def save_user_access_levels():
    """
    Save the user access levels to the access_levels.enc file.
    """
    global user_access_levels
    try:
        with open(ACCESS_LEVEL_ENCRYPTION, "wb") as f:
            pickle.dump(user_access_levels, f)
        os.chmod(ACCESS_LEVEL_ENCRYPTION, 0o600)  # Set file permissions to read-write for owner only
    except PermissionError as e:
        logging.error(f"Permission error while saving user access levels: {str(e)}")
    except Exception as e:
        logging.error(f"Error saving user access levels: {str(e)}")

def update_user_password(username, hashed_password):
    users_file_path = USER_ID_FILE
    rows = []
    with open(users_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['username'] == username:
                row['password_hash'] = hashed_password
            rows.append(row)
    with open(users_file_path, 'w', newline='') as file:
        fieldnames = ['username', 'password_hash', 'remember_me']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def load_user_access_levels():
    """
    Load user access levels from the access_levels.enc file.

    Returns:
        dict[str, tuple[bytes, bytes, bytes]]: A dictionary containing user IDs as keys and tuples of (nonce, ciphertext, tag) as values.
    """
    global user_access_levels
    try:
        if os.path.exists(ACCESS_LEVEL_ENCRYPTION):
            with open(ACCESS_LEVEL_ENCRYPTION, "rb") as f:
                try:
                    user_access_levels = pickle.load(f)
                except EOFError:
                    # File is empty, initialize an empty dictionary
                    user_access_levels = {}
        else:
            # File doesn't exist, initialize an empty dictionary
            user_access_levels = {}
    except Exception as e:
        logging.error(f"Error loading user access levels: {e}")
        user_access_levels = {}
    return user_access_levels

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
                logging.info(f"User {user_id} already has {access_level} access.")
                return
        nonce, ciphertext, tag = encrypt_data(access_level, key)
        user_access_levels[user_id] = (nonce, ciphertext, tag)
        save_user_access_levels()
    else:
        logging.error(f"Invalid access level: {access_level}")

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

def is_verified_user(user_id):
    """
    Check if a user ID exists in the USER_ID_FILE by calling
    user_exists(user_id)

    Args:
        user_id (str): The user ID to check.

    Returns:
        bool: True if the user ID exists, False otherwise.
    """
    return user_exists(user_id)

def user_exists(user_id):
    """
    Check if a user ID exists in the USER_ID_FILE.
    Returns to is_verified_user(user_id).

    Args:
        user_id (str): The user ID to check.

    Returns:
        bool: True if the user ID exists, False otherwise.
    """
    users_file_path = USER_ID_FILE
    with open(users_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            if row[0] == user_id:
                return True
    return False

def add_new_user(user_id, password):
    """
    Add a new user to the USER_ID_FILE.

    Args:
        user_id (str): The user ID.
        password (str): The user's password (hashed).
    """
    hashed_password = password
    users_file_path = USER_ID_FILE
    file_exists = os.path.isfile(users_file_path)
    with open(users_file_path, 'a', newline='') as file:
        fieldnames = ['username', 'password_hash', 'remember_me']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'username': user_id, 'password_hash': hashed_password, 'remember_me': 'False'})
        
def hash_password(password):
    """
    Hash a password for storing using bcrypt.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def get_stored_password(username):
    """
    Retrieve the stored password hash for the given username from the USER_ID_FILE.

    Args:
        username (str): The username.

    Returns:
        str | None: The stored password hash if found, None otherwise.
    """
    users_file_path = USER_ID_FILE  # Assuming USER_ID_FILE is the path to your CSV file
    with open(users_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['username'] == username:
                return row['password_hash'], row.get('remember_me', 'False') == 'True'
    return None, False

def verify_password(stored_password_tuple, provided_password):
    """
    Verify a provided password against a stored password hash using bcrypt.

    Args:
        stored_password (str): The stored password hash.
        provided_password (str): The password provided by the user.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    stored_password, _ = stored_password_tuple
    # Ensure the stored password hash is in bytes
    stored_password_bytes = stored_password.encode('utf-8')
    # The provided password needs to be converted to bytes for comparison
    provided_password_bytes = provided_password.encode('utf-8')
    # Use bcrypt's checkpw function to compare the provided password against the stored hash
    return bcrypt.checkpw(provided_password_bytes, stored_password_bytes)

def update_remember_me(username, remember_me):
    users_file_path = USER_ID_FILE
    rows = []
    with open(users_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['username'] == username:
                row['remember_me'] = str(remember_me)
            rows.append(row)
    with open(users_file_path, 'w', newline='') as file:
        fieldnames = ['username', 'password_hash', 'remember_me']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)