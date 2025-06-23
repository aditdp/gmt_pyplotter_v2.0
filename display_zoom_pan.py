import customtkinter as ctk
from tkinter import Canvas, PhotoImage
from PIL import Image, ImageTk


class ImageApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Image Viewer with Zoom and Pan")
        self.geometry("800x600")

        self.canvas = Canvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.image_path = "GMT_RGBchart.png"
        self.load_image()

        self.canvas.bind("<Button-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan_image)
        self.bind("<MouseWheel>", self.zoom_image)

    def load_image(self):
        self.image = Image.open(self.image_path)
        self.zoom = 1.0
        self.show_image()

    def show_image(self):
        width, height = int(self.image.width * self.zoom), int(
            self.image.height * self.zoom
        )
        resized_image = self.image.resize((width, height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def pan_image(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom_image(self, event):
        if event.delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.show_image()


if __name__ == "__main__":
    app = ImageApp()
    app.mainloop()
