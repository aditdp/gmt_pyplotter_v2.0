import customtkinter as ctk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import date
from dateutil.relativedelta import relativedelta

# butuh package tkcalendar


class DateSelectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CustomTkinter Date Selector")
        self.geometry("400x300")
        self.style = ttk.Style()
        self.style.configure("TEntry", foreground="white", fieldbackground="green")
        self.start_label = ctk.CTkLabel(self, text="Start Date:")
        self.start_label.pack(pady=5)
        self.start_date = DateEntry(
            self,
            width=20,
            justify="center",
            date_pattern="yyyy-mm-dd",
            background="#565B5E",
            foreground="white",
            borderwidth=2,
            showweeknumbers=False,
            showothermonthdays=False,
            normalbackground="#565B5E",
            normalforeground="white",
            weekendbackground="#565B5E",
            weekendforeground="white",
        )

        self.start_date.pack(pady=5)
        self.start_date.set_date(date.today() - relativedelta(years=3))

        self.end_label = ctk.CTkLabel(self, text="End Date:")
        self.end_label.pack(pady=5)
        self.end_date = DateEntry(
            self, width=12, background="darkblue", foreground="white", borderwidth=2
        )
        self.end_date.pack(pady=5)

        self.submit_button = ctk.CTkButton(
            self, text="Submit", command=self.print_dates
        )
        self.submit_button.pack(pady=20)

    def print_dates(self):
        start = self.start_date.get_date()
        end = self.end_date.get_date()
        print(f"Start Date: {start}\nEnd Date: {end}")


if __name__ == "__main__":
    app = DateSelectorApp()
    app.mainloop()
