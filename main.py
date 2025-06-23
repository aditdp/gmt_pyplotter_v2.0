import customtkinter as ctk


window = ctk.CTk()
window.title("gmt pyplotter")
window.geometry("600x400")

window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=2)
window.columnconfigure(2, weight=1)
window.columnconfigure(3, weight=5)

window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=2)
window.rowconfigure(3, weight=2)
window.rowconfigure(4, weight=2)
window.rowconfigure(5, weight=2)
window.rowconfigure(6, weight=2)
window.rowconfigure(7, weight=2)
window.rowconfigure(8, weight=2)


def autocheck(event):
    try:
        lon = float(longitude_entry.get())
        if -180 < lon < 180:
            status = "good"
            color = "green"

        else:
            status = "longitude in range -180 - 180 degree"
            color = "red"

    except ValueError:
        if longitude_entry.get() == "":
            status = "fill in first"
        else:
            status = "input number only"
        color = "red"

    longitude_status.configure(text=status, text_color=color)


longitude_label = ctk.CTkLabel(window, text="Longitude", anchor="w")
longitude_label.grid(column=1, row=0, sticky="ew", padx=10, pady=5)

longitude_entry = ctk.CTkEntry(window, placeholder_text="-180 - 180 degree")

longitude_entry.bind("<FocusOut>", autocheck)
longitude_entry.grid(column=2, row=0, sticky="ew")

longitude_status = ctk.CTkLabel(window, text="", anchor="w")
longitude_status.grid(column=3, row=0, padx=10, sticky="ew")

latitude_label = ctk.CTkLabel(window, text="Lattitude", anchor="w")
latitude_label.grid(column=1, row=1, sticky="ew", padx=10, pady=5)

latitude_entry = ctk.CTkEntry(window, placeholder_text="-90 - 90 degree")
latitude_entry.grid(column=2, row=1, sticky="ew")

window.mainloop()
