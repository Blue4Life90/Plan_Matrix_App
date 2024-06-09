import tkinter as tk
from tkinter import ttk
import time
import threading

"""Loading Screen for IdleTasks

In this modified example, the loading_process method is introduced to perform the actual loading tasks. 
Instead of simulating the progress, it can include your application's initialization logic, such as 
loading data or performing computations.

The loading process is executed in a separate thread using threading.Thread to prevent the splash screen 
from freezing while the tasks are being performed. The loading_process method updates the progress bar 
value based on the progress of the loading tasks.

Once the loading process is completed, the splash screen is closed using self.destroy(), and the main 
application window is shown using self.master.deiconify().

By executing the loading tasks in a separate thread, the splash screen remains responsive, and the 
loading progress is updated in real-time. You can customize the loading_process method to include your 
specific loading tasks and update the progress bar accordingly.

Remember to handle any exceptions or errors that may occur during the loading process to ensure a 
smooth user experience.

"""



class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Splash Screen")
        self.geometry("400x200")
        self.overrideredirect(True)  # Remove window decorations

        # Create a label for the splash screen
        label = tk.Label(self, text="Loading...")
        label.pack(pady=20)

        # Create a progress bar
        self.progress_bar = ttk.Progressbar(self, length=200, mode='determinate')
        self.progress_bar.pack()

        # Center the splash screen on the screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Start the loading process in a separate thread
        self.loading_thread = threading.Thread(target=self.loading_process)
        self.loading_thread.start()

    def loading_process(self):
        # Perform actual loading tasks here
        for i in range(1, 11):
            time.sleep(0.5)  # Simulate loading time
            progress = i * 10
            self.progress_bar['value'] = progress
            self.update_idletasks()

        # Close the splash screen and show the main application window
        self.destroy()
        self.master.deiconify()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Application")
        self.geometry("800x600")

        # Create widgets for the main application
        label = tk.Label(self, text="Welcome to the Main Application")
        label.pack(pady=20)

        # Hide the main application window
        self.withdraw()

        # Create and display the splash screen
        splash_screen = SplashScreen(self)

if __name__ == "__main__":
    app = App()
    app.mainloop()