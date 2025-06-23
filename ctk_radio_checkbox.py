import customtkinter as ctk

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Radio Buttons and Checkboxes Example")
        self.geometry("400x300")

        # Radio Buttons
        self.radio_label = ctk.CTkLabel(self, text="Select a Color:")
        self.radio_label.pack(pady=10)

        self.radio_var = ctk.IntVar(value=0)  # Initial selection

        self.radio_red = ctk.CTkRadioButton(
            self, text="Red", variable=self.radio_var, value=0
        )
        self.radio_red.pack(pady=5)

        self.radio_blue = ctk.CTkRadioButton(
            self, text="Blue", variable=self.radio_var, value=1
        )
        self.radio_blue.pack(pady=5)

        self.radio_green = ctk.CTkRadioButton(
            self, text="Green", variable=self.radio_var, value=2
        )
        self.radio_green.pack(pady=5)

        # Checkboxes
        self.checkbox_label = ctk.CTkLabel(self, text="Select Fruits:")
        self.checkbox_label.pack(pady=10)

        self.checkbox_vars = {
            "apple": ctk.BooleanVar(),
            "banana": ctk.BooleanVar(),
            "orange": ctk.BooleanVar(),
        }

        self.checkbox_apple = ctk.CTkCheckBox(
            self, text="Apple", variable=self.checkbox_vars["apple"]
        )
        self.checkbox_apple.pack(pady=5)

        self.checkbox_banana = ctk.CTkCheckBox(
            self, text="Banana", variable=self.checkbox_vars["banana"]
        )
        self.checkbox_banana.pack(pady=5)

        self.checkbox_orange = ctk.CTkCheckBox(
            self, text="Orange", variable=self.checkbox_vars["orange"]
        )
        self.checkbox_orange.pack(pady=5)

        # Button to get values
        self.button = ctk.CTkButton(self, text="Get Values", command=self.get_values)
        self.button.pack(pady=20)

    def get_values(self):
        color = self.radio_var.get()
        if color == 0:
            print("Selected color: Red")
        elif color == 1:
            print("Selected color: Blue")
        else:
            print("Selected color: Green")

        selected_fruits = [
            fruit for fruit, var in self.checkbox_vars.items() if var.get()
        ]
        print("Selected fruits:", selected_fruits)


if __name__ == "__main__":
    app = App()
    app.mainloop()
