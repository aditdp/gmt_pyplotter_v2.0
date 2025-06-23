import tkinter as tk
import customtkinter as ctk
from ctk_date_picker import CTkDatePicker


def main():
    root = ctk.CTk()
    root.geometry("400x300")

    date_picker = CTkDatePicker(root)
    date_picker.set_allow_change_month(True)
    date_picker.set_allow_manual_input(True)
    date_picker.set_change_months("sub", 5)
    date_picker.pack(pady=20)

    def print_date():
        print(f"Selected Date: {date_picker.get_date()}")

    btn = ctk.CTkButton(root, text="Print Date", command=print_date)
    btn.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
