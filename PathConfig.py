import os

def get_shared_path():
    config_file = os.path.join(os.getcwd(), "SaveFiles", "UserRegistry", "shared_path.txt")
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            return file.read().strip()
    return None

def save_shared_path(path):
    config_file = os.path.join(os.getcwd(), "SaveFiles", "UserRegistry", "shared_path.txt")
    with open(config_file, 'w') as file:
        file.write(path)