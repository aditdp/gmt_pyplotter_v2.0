# import customtkinter as ctk


# class ColorPickerApp(ctk.CTk):
#     def __init__(self):
#         super().__init__()

#         self.title("RGB Color Picker with Preview")
#         self.geometry("400x200")

#         self.colors = {
#             "Red (255, 0, 0)": "#FF0000",
#             "Green (0, 255, 0)": "#00FF00",
#             "Blue (0, 0, 255)": "#0000FF",
#             "Yellow (255, 255, 0)": "#FFFF00",
#             "Cyan (0, 255, 255)": "#00FFFF",
#             "Magenta (255, 0, 255)": "#FF00FF",
#         }

#         self.color_var = ctk.StringVar(value="Select a color")
#         self.color_menu = ctk.CTkOptionMenu(
#             self,
#             variable=self.color_var,
#             values=list(self.colors.keys()),
#             command=self.update_preview,
#         )
#         self.color_menu.pack(pady=10)

#         self.color_menu.set("Red (255, 0, 0)")
#         self.update_preview("Red (255, 0, 0)")

#     def update_preview(self, color_name):
#         if color_name in self.colors:
#             color_code = self.colors[color_name]
#             self.color_menu.configure(fg_color=color_code)


# if __name__ == "__main__":
#     app = ColorPickerApp()
#     app.mainloop()


import customtkinter as ctk
from tkinter import colorchooser


class ColorPickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RGB Color Picker with Preview")
        self.geometry("400x200")

        self.colors = {
            "Red (255, 0, 0)": "#FF0000",
            "Green (0, 255, 0)": "#00FF00",
            "Blue (0, 0, 255)": "#0000FF",
            "Yellow (255, 255, 0)": "#FFFF00",
            "Cyan (0, 255, 255)": "#00FFFF",
            "Magenta (255, 0, 255)": "#FF00FF",
            "Browse Color...": "",
        }

        self.color_var = ctk.StringVar(value="Select a color")
        self.color_menu = ctk.CTkOptionMenu(
            self,
            variable=self.color_var,
            values=list(self.colors.keys()),
            command=self.update_preview,
        )
        self.color_menu.pack(pady=10)

        self.preview_label = ctk.CTkLabel(
            self, text=" ", width=100, height=100, fg_color="white"
        )
        self.preview_label.pack(pady=10)

    def update_preview(self, color_name):
        if color_name == "Browse Color...":
            color_code = colorchooser.askcolor()[1]
            if color_code:
                self.preview_label.configure(fg_color=color_code)
                self.color_var.set(f"Custom Color {color_code}")
                self.color_menu.set(f"Custom Color {color_code}")
        else:
            color_code = self.colors[color_name]
            if color_code:
                self.preview_label.configure(fg_color=color_code)


if __name__ == "__main__":
    app = ColorPickerApp()
    app.mainloop()
