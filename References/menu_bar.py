import tkinter as tk

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Create a menu bar
        self.menu_bar = tk.Menu(self)

        # Create a File menu and add it to the menu bar
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Create a Help menu and add it to the menu bar
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

        # Display the menu bar
        self.config(menu=self.menu_bar)

    def new_file(self):
        pass  # Implement this method

    def open_file(self):
        pass  # Implement this method

    def save_file(self):
        pass  # Implement this method

    def show_about(self):
        pass  # Implement this method

app = App()

app.mainloop()
    
app = App()

app.mainloop()