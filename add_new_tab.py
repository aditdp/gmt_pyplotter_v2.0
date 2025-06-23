# import tkinter as tk
# from tkinter import ttk


# class TabApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Tab View with Add Button")

#         self.tab_control = ttk.Notebook(root)
#         self.tabs = []

#         self.add_tab_button = tk.Button(root, text="Add Tab", command=self.add_tab)
#         self.add_tab_button.pack(side="top")

#         self.tab_control.pack(expand=1, fill="both")

#         self.add_tab()  # Add the first tab

#     def add_tab(self):
#         new_tab = ttk.Frame(self.tab_control)
#         self.tab_control.add(new_tab, text=f"Layer {len(self.tabs) + 1}")
#         self.tabs.append(new_tab)


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TabApp(root)
#     root.mainloop()


# import customtkinter as ctk


# class TabApp(ctk.CTk):
#     def __init__(self):
#         super().__init__()

#         self.title("CustomTkinter TabView with Entry and Button")
#         self.geometry("400x300")

#         self.tab_control = ctk.CTkTabview(self)
#         self.tab_control.pack(expand=1, fill="both")

#         self.add_tab_button = ctk.CTkButton(self, text="Add Tab", command=self.add_tab)
#         self.add_tab_button.pack(side="top", pady=10)

#         self.tabs = []
#         self.add_tab()  # Add the first tab

#     def add_tab(self):
#         new_tab = self.tab_control.add(f"Tab {len(self.tabs) + 1}")
#         self.tabs.append(new_tab)

#         entry = ctk.CTkEntry(new_tab)
#         entry.pack(pady=10)

#         button = ctk.CTkButton(
#             new_tab, text="Print Input", command=lambda: self.print_input(entry)
#         )
#         button.pack(pady=10)

#     def print_input(self, entry):
#         print(entry.get())


# if __name__ == "__main__":
#     app = TabApp()
#     app.mainloop()


import customtkinter as ctk


class TabApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CustomTkinter TabView with Entry and Button")
        self.geometry("400x300")

        self.tab_control = ctk.CTkTabview(self)
        self.tab_control.pack(expand=1, fill="both")

        self.add_tab_button = ctk.CTkButton(self, text="Add Tab", command=self.add_tab)
        self.add_tab_button.pack(side="top", pady=10)

        self.tabs = []

        self.max_tabs = 7
        self.add_tab()  # Add the first tab

    def add_tab(self):
        if len(self.tabs) < self.max_tabs:
            new_tab = self.tab_control.add(f"Tab {len(self.tabs) + 1}")
            self.tabs.append(new_tab)

            entry = ctk.CTkEntry(new_tab)
            entry.pack(pady=10)

            button = ctk.CTkButton(
                new_tab,
                text="Print Input",
                command=lambda entry=entry: self.print_input(entry),
            )
            button.pack(pady=10)
        else:
            print("Maximum number of tabs reached.")

    def print_input(self, entry):
        print(entry.get())


if __name__ == "__main__":
    app = TabApp()
    app.mainloop()
