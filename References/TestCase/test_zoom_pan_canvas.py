import tkinter as tk

class ZoomableFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.zoom_scale = 1.0
        self.zoom_factor = 1.1

        self.canvas = tk.Canvas(self, width=800, height=600, relief=tk.SOLID)
        self.canvas.pack(fill="both", expand=True)

        self.content_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.zoom_in_button = tk.Button(self, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.pack(side="left", padx=10, pady=10)

        self.zoom_out_button = tk.Button(self, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.pack(side="left", padx=10, pady=10)

    def zoom_in(self):
        self.zoom_scale *= self.zoom_factor
        self.canvas.scale("all", 0, 0, self.zoom_factor, self.zoom_factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def zoom_out(self):
        self.zoom_scale /= self.zoom_factor
        self.canvas.scale("all", 0, 0, 1/self.zoom_factor, 1/self.zoom_factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width, height=event.height)
        
# Create the main application window
root = tk.Tk()
root.title("Zoomable Frame Example")

# Create a zoomable frame
zoomable_frame = ZoomableFrame(root)
zoomable_frame.pack(fill="both", expand=True)

# Add widgets to the content frame
label = tk.Label(zoomable_frame.content_frame, text="Zoomable Content")
label.pack()

button = tk.Button(zoomable_frame.content_frame, text="Button")
button.pack()

entry = tk.Entry(zoomable_frame.content_frame)
entry.pack()

root.mainloop()