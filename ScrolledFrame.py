# PEP8 Compliant Guidance
# Standard Library Imports
import tkinter as tk

# Third-Party Library Imports
import customtkinter as ctk #type: ignore

# Local Application/Library Specific Imports
from constants import APP_BG_COLOR, SCROLLBAR_FG_COLOR, SCROLLBAR_HOVER_COLOR


class ScrolledFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, highlightthickness=0, bg=APP_BG_COLOR)
        self.scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview,
                                          fg_color=APP_BG_COLOR, button_color=SCROLLBAR_FG_COLOR, 
                                          button_hover_color=SCROLLBAR_HOVER_COLOR,
                                          width=16)
        self.scrollable_frame = tk.Frame(self.canvas, bg=APP_BG_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="bottom", fill="x")

        self.adjust_size()
        self.bind("<Configure>", self.on_resize)

    def update_scroll_region(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def adjust_size(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        canvas_width = int(screen_width * 0.77)
        canvas_height = int(screen_height * 0.85)

        self.canvas.configure(width=canvas_width, height=canvas_height)

    def on_resize(self, event):
        self.adjust_size()