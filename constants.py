# PEP8 Compliant Guidance
# Standard Library Imports
import os
from PIL import ImageTk

# Third-Party Library Imports

# Local Application/Library Specific Imports

log_file = os.path.join(os.getcwd(), "SaveFiles/TrackingLogs", "app.log")
TRACKING_LOGS_DIR = os.path.join(os.getcwd(), "SaveFiles", "TrackingLogs")

"""images"""
REGISTRATION_BANNER_IMAGE = os.path.join(os.getcwd(), "Images", "background_images", "Registration_Form_Banner.jpg")
RESET_PASS_BANNER_IMAGE = os.path.join(os.getcwd(), "Images", "background_images", "Reset_Password_Banner.jpg")
LOGIN_BANNER_IMAGE = os.path.join(os.getcwd(), "Images", "background_images", "Login_Form_Banner.jpg")
def load_icons():
    ICON_PATH_0 = ImageTk.PhotoImage(file=os.path.join("images/background_images/svg/ICO/","16px.ico"))
    ICON_PATH_1 = ImageTk.PhotoImage(file=os.path.join("images/background_images/svg/ICO/","32px.ico"))
    ICON_PATH_2 = ImageTk.PhotoImage(file=os.path.join("images/background_images/svg/ICO/","48px.ico"))
    return ICON_PATH_0, ICON_PATH_1, ICON_PATH_2

"""login_functions.py"""
USER_ID_FILE = os.path.join(os.getcwd(), "SaveFiles", "UserRegistry", "user_id.csv")
ACCESS_LEVEL_ENCRYPTION = os.path.join(os.getcwd(), "SaveFiles", "UserRegistry", "access_levels.enc")

"""HrsMatrixFrame.py"""
MEMBER_SAVE_DATA = os.path.join(os.getcwd(), "SaveFiles", "Crew_Member_Save_Data.csv")

"""Work Schedule Formatting Presets"""
ASSIGNMENT_CODES = {
    "Family Care": "FC",
    "HOTT Team": "HT",
    "FCC Task Force": "FTF",
    "Steam Team": "ST",
    "Baby Bonding": "BB",
    "Graduation": "G",
    "Relief": "R",
    "School": "SC",
    "Special Assignment": "SA",
    "Training": "T",
    "Banked Holiday": "BH",
    "Vacation": "V",
    "Personal Choice": "PC",
    "ERT Training": "ERT",
    "Board Training": "BT",
    "Meeting": "M",
    "Jury Duty": "JD",
    "Sick": "SK",
    "Shift Swap": "SW",
    "On Call": "OC"
}

COLOR_SPECS = {
    "FC":{"frame":"#e26b0a", "label_bg":"#e26b0a", "label_text":"yellow"}, 
    "HT":{"frame":"#c0504d", "label_bg":"#c0504d", "label_text":"white"}, 
    "FTF":{"frame":"#ddd9c4", "label_bg":"#ddd9c4", "label_text":"black"}, 
    "ST":{"frame":"#d9d9d9", "label_bg":"#d9d9d9", "label_text":"black"}, 
    "BB":{"frame":"#0071c4", "label_bg":"#0071c4", "label_text":"white"}, 
    "G":{"frame":"#c4d79b", "label_bg":"#c4d79b", "label_text":"black"}, 
    "R":{"frame":"#ffff00", "label_bg":"#ffff00", "label_text":"black"}, 
    "SC":{"frame":"#b1a0c7", "label_bg":"#b1a0c7", "label_text":"black"}, 
    "SA":{"frame":"#c5d9eb", "label_bg":"#c5d9eb", "label_text":"black"}, 
    "T":{"frame":"#00b050", "label_bg":"#00b050", "label_text":"white"}, 
    "BH":{"frame":"#0097b9", "label_bg":"#0097b9", "label_text":"black"}, 
    "V":{"frame":"#00b0f0", "label_bg":"#00b0f0", "label_text":"white"}, 
    "PC":{"frame":"#00b0ef", "label_bg":"#00b0ef", "label_text":"black"}, 
    "ERT":{"frame":"#ff0000", "label_bg":"#ff0000", "label_text":"yellow"}, 
    "BT":{"frame":"#00ffff", "label_bg":"#00ffff", "label_text":"black"}, 
    "M":{"frame":"#ffffff", "label_bg":"#ffffff", "label_text":"black"}, 
    "JD":{"frame":"#d8e4bc", "label_bg":"#d8e4bc", "label_text":"black"}, 
    "SK":{"frame":"#da9694", "label_bg":"#da9694", "label_text":"black"}, 
    "SW":{"frame":"#4e3b63", "label_bg":"#4e3b63", "label_text":"white"}, 
    "OC":{"frame":"#ffc000", "label_bg":"#ffc000", "label_text":"black"},
}

# TODO: Build User Presets
"""
DARKMODE
https://blog.karenying.com/posts/50-shades-of-dark-mode-gray#hex-codes
"""

"""Primary App Theme"""
LIGHT_THEME = {
    "APP_BG_COLOR": "#FFFFFF",
    "FRAME_BG_COLOR": "#F0F0F0",
    "BUTTON_FG_COLOR": "#000000",
    "BUTTON_HOVER_BG_COLOR": "#E0E0E0",
    "TEXT_COLOR": "#000000"
}
DARK_THEME = {
    "APP_BG_COLOR": "#121212",
    "FRAME_BG_COLOR": "#282828",
    "BUTTON_FG_COLOR": "#FFFFFF",
    "BUTTON_HOVER_BG_COLOR": "#404040",
    "TEXT_COLOR": "#FFFFFF"
}

FILE_MENU_BG_COLOR = "#181818"
APP_BG_COLOR = "#121212"
FRAME_BG_COLOR = "#282828"
HOVER_BG_COLOR = "#404040"
FG_PRIME_COLOR = "#FFFFFF"
FG_SECONDARY_COLOR = "#B3B3B3"
SCROLLBAR_FG_COLOR = "#282828"
SCROLLBAR_HOVER_COLOR = "#B3B3B3"

"""Buttons"""
PANE_BG_COLOR = "#181818"
BUTTON_FG_COLOR = "#282828"
BUTTON_HOVER_BG_COLOR = "#404040"
TEXT_COLOR = "#B3B3B3"

"""Treeview Widget"""
TREEVIEW_ODD = "#6f73f7"
TREEVIEW_EVEN = "#8c8ffa"
TREEVIEW_HDR = "#000000"
TREEVIEW_TEXT = "#000129"
TREEVIEW_SELECTED = "#01056e"


"""HeaderFrame"""
mode = "dm"
if mode == "dm":
    BG_COLOR = "#282828"
    FG_COLOR = "#FFFFFF"
else:
    BG_COLOR = "#002060"
    FG_COLOR = "white"

"""HrsMatrixFrame"""
ASKING_HRS_BG_COLOR = "#FFC7CE"
ASKING_HRS_FG_COLOR = "#9C0006"
WORKING_HRS_BG_COLOR = "#C6EFCE"
WORKING_HRS_FG_COLOR = "#006100"