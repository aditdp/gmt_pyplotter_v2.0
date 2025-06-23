import tkinter as tk


def create_stippled_square():
    root = tk.Tk()
    root.title("Stippled (Simulated Transparent) Square")

    canvas = tk.Canvas(root, width=400, height=300, bg="lightblue")
    canvas.pack(padx=20, pady=20)

    # Draw a background circle to show the effect
    canvas.create_oval(100, 100, 300, 250, fill="yellow", outline="orange", width=3)

    # Create a rectangle with a stipple pattern
    # This will make it appear semi-transparent
    canvas.create_rectangle(
        50, 80, 250, 220, fill="purple", outline="darkblue", width=2, stipple="gray50"
    )  # 50% "transparent" effect
    canvas.create_text(150, 60, text="Stippled 50% Fill", fill="purple")

    canvas.create_rectangle(
        200, 150, 380, 280, fill="red", outline="", width=2, stipple="gray25"
    )  # 75% "transparent" effect (25% opaque)
    canvas.create_text(290, 130, text="Stippled 25% Fill", fill="red")

    root.mainloop()


if __name__ == "__main__":
    create_stippled_square()
