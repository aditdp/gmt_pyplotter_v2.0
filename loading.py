import tkinter as tk
from tkinter import Canvas, Label, PhotoImage
import threading
import time


def load_image(canvas, file_path):
    # Simulate a delay in loading the image
    time.sleep(3)

    # Load the image
    image = PhotoImage(file=file_path)

    # Clear the canvas and add the image
    canvas.delete("all")
    canvas.create_image(0, 0, anchor=tk.NW, image=image)
    canvas.image = image  # Keep a reference to the image

    # Hide the loading label
    loading_label.pack_forget()


def start_loading(canvas, file_path):
    # Display the loading label
    loading_label.pack(pady=20)

    # Start a new thread to load the image
    threading.Thread(target=load_image, args=(canvas, file_path)).start()


# Create the main window
root = tk.Tk()
root.title("Image Loader")
root.geometry("500x500")

# Create a canvas widget
canvas = Canvas(root, width=500, height=400, bg="white")
canvas.pack()

# Create a loading label
loading_label = Label(root, text="Loading...", font=("Helvetica", 16))

# Button to start loading the image
btn_load_image = tk.Button(
    root,
    text="Load Image",
    command=lambda: start_loading(canvas, "./image/map_simple_5.png"),
)
btn_load_image.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
