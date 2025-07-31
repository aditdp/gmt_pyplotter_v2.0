import customtkinter as ctk


class AggressiveNarrowColumnZeroApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x200")
        self.title("Aggressive Narrow Column 0")

        # --- Aggressive Column 0 Configuration ---
        # Set weight to 0.
        # Set a very small minsize. Let's try 1 to see if it makes a difference.
        # Some widgets might have an internal minsize that overrides even grid's minsize,
        # but this is the strongest grid-level control.
        self.grid_columnconfigure(
            0, weight=0, minsize=1
        )  # Try minsize=1 or even minsize=0

        # Configure other columns to expand. Give them a higher weight
        # relative to each other, but the key is that they are > 0.
        for i in range(1, 7):
            self.grid_columnconfigure(
                i, weight=10
            )  # Give other columns a significant weight

        self.grid_rowconfigure(0, weight=1)  # Make row expandable

        # --- Widgets ---

        # Column 0: CTkCheckBox with NO text and minimal padding.
        # Also, explicitly set width and height for the checkbox itself.
        self.checkbox0 = ctk.CTkCheckBox(
            self,
            text="",
            checkbox_width=18,  # The actual visual box width
            checkbox_height=18,  # The actual visual box height
            border_width=2,
            width=20,  # Set widget's total requested width very small
            height=20,  # Set widget's total requested height very small
        )
        # Use minimal padx/pady. Sticky to ensure it hugs the cell edges if cell is larger.
        self.checkbox0.grid(
            row=0, column=0, padx=0, pady=0, sticky="nsew"
        )  # Very minimal padding

        # Columns 1 to 6: Labels for comparison
        for i in range(1, 5):
            label = ctk.CTkLabel(
                self,
                text=f"Column {i} Content",
                fg_color="blue" if i % 2 == 0 else "green",
            )
            label.grid(row=0, column=i, padx=0, pady=5, sticky="nsew")


if __name__ == "__main__":
    app = AggressiveNarrowColumnZeroApp()
    app.mainloop()
