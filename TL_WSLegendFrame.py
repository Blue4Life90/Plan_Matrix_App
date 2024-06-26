# PEP8 Compliant Guidance
# Standard Library Imports

# Third-Party Library Imports
import customtkinter as ctk # type: ignore

# Local Application/Library Specific Imports
from constants import APP_BG_COLOR, PANE_BG_COLOR, TEXT_COLOR
from constants import COLOR_SPECS, ASSIGNMENT_CODES
from constants import BG_COLOR
import functions.app_functions as app_functions

class WSLegendWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent, fg_color=APP_BG_COLOR)
        self.parent = parent
        self.legend_title_label = ctk.CTkLabel(
            self,
            text="Legend", 
            font=("Calibri", 14, "bold"), 
            text_color=TEXT_COLOR, 
            fg_color=BG_COLOR
        )
        self.legend_title_label.grid(row=0, column=0, columnspan=2, padx=20, sticky="nsew")
        
        self.job_code_frame = ctk.CTkFrame(self, fg_color=PANE_BG_COLOR)
        self.job_code_frame.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="n", ipadx=10, ipady=10)
        
        self.create_job_code_frame_widgets()
        
        self.assignment_code_frame = ctk.CTkFrame(self, fg_color=PANE_BG_COLOR)
        self.assignment_code_frame.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="new", ipadx=10, ipady=58)
        
        self.assignment_code_list_1_frame = ctk.CTkFrame(self.assignment_code_frame, fg_color=PANE_BG_COLOR)
        self.assignment_code_list_1_frame.grid(row=3, column=0, padx=10, sticky="new")
        
        self.assignment_code_list_2_frame = ctk.CTkFrame(self.assignment_code_frame, fg_color=PANE_BG_COLOR)
        self.assignment_code_list_2_frame.grid(row=3, column=1, padx=10, sticky="new")
        
        self.assignment_code_list_3_frame = ctk.CTkFrame(self.assignment_code_frame, fg_color=PANE_BG_COLOR)
        self.assignment_code_list_3_frame.grid(row=3, column=2, padx=10, sticky="new")
        
        self.assignment_code_list_4_frame = ctk.CTkFrame(self.assignment_code_frame, fg_color=PANE_BG_COLOR)
        self.assignment_code_list_4_frame.grid(row=3, column=3, padx=10, sticky="new")
        
        self.assignment_code_list_5_frame = ctk.CTkFrame(self.assignment_code_frame, fg_color=PANE_BG_COLOR)
        self.assignment_code_list_5_frame.grid(row=3, column=4, padx=10, sticky="new")
        
        self.create_assignment_code_frame_widgets()
        
    def create_job_code_frame_widgets(self):
        # Header Label
        
        self.job_code_title_label = ctk.CTkLabel(
            self.job_code_frame, 
            text="Job Code",
            font=("Calibri", 14, "bold"), 
            text_color="white",
            fg_color=PANE_BG_COLOR
        )
        self.job_code_title_label.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10)
        
        # Define a dictionary with label texts
        job_codes = {
            "FCC HO": "1",
            "Alky HO": "2",
            "FCC Console": "3",
            "Alky Console": "4",
            "Alky Operator": "5",
            "67/40 Operator": "6",
            "Cracker Operator": "7",
            "Recovery Operator": "8"
        }
        
        # Create labels dynamically using a loop
        for index, (title, code) in enumerate(job_codes.items(), start=1):
            title_label = ctk.CTkLabel(
                self.job_code_frame, 
                text=title,
                text_color=TEXT_COLOR,
                font=("Calibri", 14)
            )
            title_label.grid(row=index, column=0, sticky="nsew", padx=(20, 0))
            
            code_label = ctk.CTkLabel(
                self.job_code_frame, 
                text=code,
                text_color=TEXT_COLOR,
                font=("Calibri", 14)
            )
            code_label.grid(row=index, column=1, sticky="nsew", padx=20)
    
    def create_assignment_code_frame_widgets(self):
        
        self.assignment_code_title_label = ctk.CTkLabel(
            self.assignment_code_frame, 
            text="Assignment/HR Codes", 
            font=("Calibri", 14, "bold"), 
            text_color="white",
            fg_color=PANE_BG_COLOR
        )
        self.assignment_code_title_label.grid(row=2, column=0, columnspan=5, sticky="nsew")
        
        color_specs = COLOR_SPECS

        assignment_codes = ASSIGNMENT_CODES

        frame_refs = {
            0: self.assignment_code_list_1_frame,
            1: self.assignment_code_list_2_frame,
            2: self.assignment_code_list_3_frame,
            3: self.assignment_code_list_4_frame,
            4: self.assignment_code_list_5_frame
        }
        
        for index, (assignment, code) in enumerate(assignment_codes.items()):
            frame_index = index // 4
            frame_ref = frame_refs[frame_index]

            title_label = ctk.CTkLabel(
                frame_ref,
                text=assignment,
                font=("Calibri", 14), 
                text_color=TEXT_COLOR,
            )
            title_label.grid(row=index % 4 + 1, column=0, sticky="nsew", padx=(20, 0))

            code_frame = ctk.CTkFrame(frame_ref)
            code_frame.grid(row=index % 4 + 1, column=1, sticky="nsew", padx=5, pady=2)

            code_label = ctk.CTkLabel(
                code_frame,
                text=code,
                font=("Calibri", 14)
            )
            code_label.pack(padx=5, expand=True, fill="both", anchor="center")
            
            frame_ref.grid_configure(sticky="new")

            app_functions.assignment_code_formatting(code_frame, code_label, code, color_specs)
    
class TestLegendApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.open_tl_button = ctk.CTkButton(self, text="Open Top Level", command=self.open_legend)
        self.open_tl_button.pack()
        
        self.legend = None
        
    def open_legend(self):
        if self.legend is None or not self.legend.winfo_exists():
            self.legend = WSLegendWindow(self)
            self.legend.title("Legend")
            center_window(self.legend)

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)

if __name__ == "__main__":
    app = TestLegendApp()
    app.mainloop()