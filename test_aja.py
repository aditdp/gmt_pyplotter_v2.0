from customtkinter import StringVar
import customtkinter as ctk

main = ctk.CTk()
date = [StringVar(value="date start"), StringVar(value="date_end")]


if type(date) == list:
    for data in date:

        if type(data) == StringVar:
            print(data.get())
