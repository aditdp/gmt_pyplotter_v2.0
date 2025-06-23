import customtkinter as ctk


class MapPreview(ctk.CTkToplevel):
    """Main window class"""

    def __init__(self):
        """Initialize the main Frame"""
        super().__init__()
        self.title("Map Preview")
        self.geometry("800x600")  # size of the main window
        loading = ctk.CTkLabel(self, text="Loading...", font=("Consolas", 14))
        loading.pack(expand=True)
        self.attributes("-topmost", True)
        self.mainloop()


if __name__ == "__main__":

    abc = MapPreview()
