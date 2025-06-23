from customtkinter import StringVar, CTkLabel, CTkEntry, CTkComboBox
from delete_tab import LayerMenu


class Coast(LayerMenu):
    def __init__(self, tab):
        # super().__init__(tab)
        self.tab_grid_layout(tab)
        self.color_land(tab)
        self.color_sea = StringVar(tab, value="azure")
        self.line_size = StringVar(tab, value="0.25p")
        self.line_color = StringVar(tab, value="black")
        self.script = "gmt coast"

    def color_land(self, tab):
        color_land = StringVar(tab, "lightgreen")
        label = CTkLabel(tab, text="Land color", anchor="e")
        entry = CTkEntry(tab, width=300, textvariable=color_land)
        self.color_picker_button(tab, row=1, col=2, var=color_land, name="land")
        self.color_preview(tab, row=1, col=3, var=color_land)
        label.grid(row=1, column=0, sticky="nsew", padx=10)
        entry.grid(row=1, column=1)
        return color_land.get()

    def create_coast_widget(self, tab):

        label_color_sea = CTkLabel(tab, text="Sea color", anchor="e")
        label_line_size = CTkLabel(tab, text="Outline size", anchor="e")
        label_line_color = CTkLabel(tab, text="Outline color", anchor="e")

        entry_color_sea = CTkEntry(tab, width=300, textvariable=self.color_sea)
        entry_line_size = CTkComboBox(tab, width=300, variable=self.line_size)
        entry_line_color = CTkEntry(tab, width=300, textvariable=self.line_color)

        label_color_sea.grid(row=2, column=0, sticky="nsew", padx=10)
        entry_color_sea.grid(row=2, column=1)
        self.color_picker_button(tab, row=2, col=2, var=self.color_sea, name="sea")
        self.color_preview(tab, row=2, col=3, var=color_sea)

        label_line_size.grid(row=3, column=0, sticky="nsew", padx=10)
        entry_line_size.grid(row=3, column=1)

        label_line_color.grid(row=4, column=0, sticky="nsew", padx=10)
        entry_line_color.grid(row=4, column=1)
        self.color_picker_button(tab, row=4, col=2, var=line_color, name="sea")

    def label(self, tab):
        pass

    def user_input(self, tab):
        pass


class GridImage:
    pass


class Earthquake:
    pass


class Focmec:
    pass


class Tectonic:
    pass


class Inset:
    pass


class Legend:
    pass
