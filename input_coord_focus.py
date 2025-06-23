import customtkinter as ctk


class CoordinateApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Coordinate Input Validator")
        self.geometry("400x200")

        self.create_widgets()

    def create_widgets(self):
        self.lon_label = ctk.CTkLabel(self, text="Longitude:")
        self.lon_label.pack(pady=5)
        self.lon_entry = ctk.CTkEntry(self)
        self.lon_entry.pack(pady=5)
        self.lon_entry.bind("<FocusOut>", self.validate_lon)

        self.lat_label = ctk.CTkLabel(self, text="Latitude:")
        self.lat_label.pack(pady=5)
        self.lat_entry = ctk.CTkEntry(self)
        self.lat_entry.pack(pady=5)
        self.lat_entry.bind("<FocusOut>", self.validate_lat)

        self.result_label = ctk.CTkLabel(self, text="")
        self.result_label.pack(pady=5)

    def validate_lon(self, event):
        lon = self.lon_entry.get()
        if self.is_valid_number(lon, -180, 180):
            self.result_label.configure(
                text=f"Longitude: {lon} is valid", text_color="green"
            )
        else:
            self.result_label.configure(text="Invalid Longitude", text_color="red")

    def validate_lat(self, event):
        lat = self.lat_entry.get()
        if self.is_valid_number(lat, -90, 90):
            self.result_label.configure(
                text=f"Latitude: {lat} is valid", text_color="green"
            )
        else:
            self.result_label.configure(text="Invalid Latitude", text_color="red")

    def is_valid_number(self, value, min_val, max_val):
        try:
            num = float(value)
            return min_val <= num <= max_val
        except ValueError:
            return False


if __name__ == "__main__":
    app = CoordinateApp()
    app.mainloop()
