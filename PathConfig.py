import os

def get_shared_path():
    config_file = os.path.normpath(os.path.join(os.getcwd(), "SaveFiles", "UserRegistry", "shared_path.txt"))
    if os.path.exists(os.path.normpath(config_file)):
        with open(config_file, 'r') as file:
            return file.read().strip()
    return None

def save_shared_path(path):
    config_dir = os.path.normpath(os.path.join(os.getcwd(), "SaveFiles", "UserRegistry"))
    config_file = os.path.normpath(os.path.join(config_dir, "shared_path.txt"))
    
    # Create the directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    
    with open(config_file, 'w') as file:
        file.write(path)