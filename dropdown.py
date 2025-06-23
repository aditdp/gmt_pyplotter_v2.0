import customtkinter as ctk


class DropdownApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CustomTkinter Dropdown List")
        self.geometry("400x300")

        self.main_menu = ctk.CTkOptionMenu(
            self,
            values=["coast", "earthquake", "grdimage"],
            command=self.update_submenu,
        )
        self.main_menu.pack(pady=20)

        self.submenu = ctk.CTkOptionMenu(self, values=["Select an option"])
        self.submenu.pack(pady=20)

    def update_submenu(self, selected_option):
        if selected_option == "coast":
            self.submenu.configure(values=["blue", "green", "red"])
        elif selected_option == "earthquake":
            self.submenu.configure(
                values=["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0", "9.0"]
            )
        elif selected_option == "grdimage":
            self.submenu.configure(values=["low", "medium", "high"])
        else:
            self.submenu.configure(values=["Select an option"])
        self.submenu.set("Select an option")


if __name__ == "__main__":
    app = DropdownApp()
    app.mainloop()
