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

        self.lat_label = ctk.CTkLabel(self, text="Latitude:")
        self.lat_label.pack(pady=5)
        self.lat_entry = ctk.CTkEntry(self)
        self.lat_entry.pack(pady=5)

        self.submit_button = ctk.CTkButton(
            self, text="Submit", command=self.validate_inputs
        )
        self.submit_button.pack(pady=20)

        self.result_label = ctk.CTkLabel(self, text="")
        self.result_label.pack(pady=5)

    def validate_inputs(self):
        lon = self.lon_entry.get()
        lat = self.lat_entry.get()

        if self.is_valid_number(lon, -180, 180) and self.is_valid_number(lat, -90, 90):
            self.result_label.configure(
                text=f"Valid Coordinates: Longitude: {lon}, Latitude: {lat}",
                text_color="green",
            )
        else:
            self.result_label.configure(text="Invalid Coordinates", text_color="red")

    def is_valid_number(self, value, min_val, max_val):
        try:
            num = float(value)
            return min_val <= num <= max_val
        except ValueError:
            return False


if __name__ == "__main__":
    app = CoordinateApp()
    app.mainloop()
