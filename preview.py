import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk


class MapPreview:
    def __init__(self, master):
        self.master = master

        self.master.title("Map Preview")
        self.master.geometry("800x600")

        self.frame = ctk.CTkFrame(master)
        self.frame.pack()
        self.canvas = tk.Canvas(self.frame, background="red", width=800, height=600)
        self.tk_image = []
        image = Image.open("./image/map_relief_5.jpg")
        imagetk = ImageTk.PhotoImage(image)
        self.tk_image.append(imagetk)
        print(imagetk.width())
        print(f"winfo {self.canvas.winfo_width()} {self.canvas.winfo_height()}")
        self.canvas.create_image(
            0,
            0,
            image=self.tk_image,
            anchor="nw",
        )
        self.canvas.pack()


root = ctk.CTk()

app = MapPreview(root)
root.mainloop()
