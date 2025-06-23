import customtkinter as ctk
import os
from customtkinter import (
    StringVar,
    DoubleVar,
    CTkButton,
    CTkLabel,
    CTkEntry,
    CTkFrame,
    CTkImage,
    CTkOptionMenu,
    filedialog,
)
from tkinter import colorchooser, messagebox

# from CTkListbox import CTkListbox
from PIL import Image
from time import sleep
from ctk_tooltip import CTkToolTip
from ctk_coordinate_gui import CoordWindow
from ctk_scrollable_dropdown import CTkScrollableDropdown


def resize_image(file):
    try:
        image_dir = "image"
        path = os.path.dirname(os.path.abspath(__file__))
        for i in range(1, 6):
            filename = f"{file[:-5]}{i}{file[-4:]}"

            if not os.path.exists(os.path.join(path, "image", filename)):
                image = Image.open(os.path.join(path, image_dir, file))
                w, h = image.size
                new_w, new_h = w // (2**i), h // (2**i)
                resized = image.resize((new_w, new_h), Image.LANCZOS)
                resized.save(os.path.join(path, image_dir, filename), optimize=True)

    except IOError:
        messagebox.showerror("Error", f"Unable to open file '{file}', file not found")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("gmt_pyplotter")
        self.geometry("700x500")
        self.minsize(700, 500)
        resize_image("map_simple_0.png")
        resize_image("map_relief_0.jpg")

        self.frame_map_param = CTkFrame(
            self,
        )
        self.frame_layers = CTkFrame(
            self,
        )
        self.frame_map_param.place(x=0, y=0, relwidth=0.3, relheight=1)
        self.frame_layers.place(relx=0.3, y=0, relwidth=0.7, relheight=1)
        self.get_name = MapFileName(self, self.frame_map_param)
        self.get_coordinate = MapCoordinate(self, self.frame_map_param)
        self.get_projection = MapProjection(self, self.frame_map_param)
        self.get_layers = LayerMenu(self, self.frame_layers)
        self.mainloop()


class MapFileName(CTkFrame):
    def __init__(self, main: MainApp, mainframe):
        super().__init__(mainframe)
        self.main = main
        self.place(relx=0.01, rely=0.01, relheight=0.24, relwidth=0.95)
        for i in range(5):
            if i in [0, 3, 4]:
                w = 0
            else:
                w = 1
            self.columnconfigure(i, weight=w, uniform="a")
            if i < 3:
                self.rowconfigure(i, weight=0, uniform="a")

        self.output_dir = StringVar(self, value=os.path.expanduser("~"))
        self.file_name = StringVar(self, value="untitled_map")
        self.extension = StringVar(self, value=".png")
        label = CTkLabel(
            self,
            text="FILE NAME",
            # fg_color="gray16",
            corner_radius=5,
            font=("Helvetica", 14, "bold"),
        )
        label.grid(column=0, row=0, columnspan=5, sticky="we")
        self.browse_directory(self)
        self.filename_entry(self)
        self.file_extension(self)

    def browse_directory(self, frame):
        folder_exist = ctk.BooleanVar(value=True)

        def select_dir():
            cur_dir = self.output_dir.get()
            directory_path = filedialog.askdirectory(
                title="Browse output directory", initialdir=cur_dir
            )
            if directory_path:
                self.output_dir.set(directory_path)

        def validate_folder(event):
            folder_path = self.output_dir.get()
            if os.path.isdir(folder_path):

                outdir_entry.configure(fg_color="#343638")
                folder_exist.set(True)
            else:
                folder_exist.set(False)
                outdir_entry.configure(fg_color="red")
                messagebox.showerror(
                    title="Invalid directory",
                    message="The directory is not valid",
                )

        dark_directory_logo = Image.open("./image/dark_folder.png")
        light_directory_logo = Image.open("./image/light_folder.png")
        directory_logotk = CTkImage(
            dark_image=dark_directory_logo,
            light_image=light_directory_logo,
            size=(15, 15),
        )
        browse_out_directory = CTkButton(
            frame,
            image=directory_logotk,
            text="",
            command=select_dir,
            width=20,
            hover_color="gray",
            fg_color="dim gray",
            anchor="e",
        )
        browse_out_directory.grid(row=1, column=0, sticky="e", padx=3, pady=3)
        CTkToolTip(
            browse_out_directory,
            "Browse output \ndirectory location",
        )
        outdir_entry = CTkEntry(
            frame,
            textvariable=self.output_dir,
        )
        outdir_entry.bind("<FocusOut>", validate_folder)
        outdir_entry.bind("<Return>", validate_folder)
        outdir_entry.grid(row=1, column=1, columnspan=4, sticky="ew", padx=3, pady=3)

    def filename_entry(self, frame):
        entry = CTkEntry(frame, width=150, textvariable=self.file_name)
        entry.grid(row=2, column=0, columnspan=3, sticky="ew", padx=3, pady=3)

    def file_extension(self, frame):
        ext_option = CTkButton(
            frame, width=50, text="png", fg_color="#565B5E", hover_color="#7A848D"
        )
        ext_option.grid(row=2, column=3, columnspan=2, sticky="ew", padx=5, pady=3)
        CTkScrollableDropdown(
            ext_option,
            values=[".png", ".pdf", ".jpg"],
            width=100,
            resize=False,
            scrollbar=False,
            command=lambda e: ext_option.configure(text=e),
        )


class MapCoordinate(CTkFrame):
    def __init__(self, main: MainApp, mainframe):
        super().__init__(mainframe)
        self.main = main
        self.place(relx=0.01, rely=0.27, relheight=0.40, relwidth=0.95)
        self.coord_picked = False

        def create_entry(text_var):
            return ctk.CTkEntry(
                self,
                width=80,
                font=("Consolas", 14),
                textvariable=text_var,
                state="disabled",
            )

        for i in range(5):
            if i in [0, 3, 4]:
                w = 0
            else:
                w = 1
            self.columnconfigure(i, weight=w, uniform="a")
            if i < 3:
                self.rowconfigure(i, weight=0, uniform="a")

        label = CTkLabel(
            self,
            text="COORDINATES",
            font=("Helvetica", 14, "bold"),
        )
        label.grid(column=0, row=0, columnspan=5)

        global roi
        roi = [StringVar(self) for _ in range(4)]
        roi[0].set("min lon")
        roi[1].set("max lon")
        roi[2].set("min lat")
        roi[3].set("max lat")

        self.x_min_entry = create_entry(roi[0])
        self.x_max_entry = create_entry(roi[1])
        self.y_min_entry = create_entry(roi[2])
        self.y_max_entry = create_entry(roi[3])
        self.coord_button = CTkButton(
            self,
            text="Get Coordinate",
            command=lambda: self.update_coor_entry(),
            hover_color="gray",
            fg_color="dim gray",
        )
        self.y_max_entry.grid(row=1, column=1, columnspan=2, pady=3)
        self.x_min_entry.grid(row=2, column=0, columnspan=2, pady=3, padx=10)
        self.x_max_entry.grid(row=2, column=2, columnspan=2, pady=3, padx=10)
        self.y_min_entry.grid(row=3, column=1, columnspan=2, pady=3)
        self.coord_button.grid(row=4, column=0, columnspan=3, pady=3)

    def coord(self):
        """returning the coordinate boundaries in list:
        [0] min longitude,
        [1] max longitude,
        [2] min latitude,
        [3] max latitude"""
        return [
            float(roi[0].get()),
            float(roi[1].get()),
            float(roi[2].get()),
            float(roi[3].get()),
        ]

    def update_coor_entry(self):
        if self.coord_picked == False:
            coord = None
        else:
            coord = roi[0].get(), roi[1].get(), roi[2].get(), roi[3].get()
        get_coord = CoordWindow(coord)
        acquired_coord = get_coord.return_roi()

        if acquired_coord not in [None, ""]:
            roi[0].set(acquired_coord[0])
            roi[1].set(acquired_coord[1])
            roi[2].set(acquired_coord[2])
            roi[3].set(acquired_coord[3])
            self.coord_picked = True
            self.coord_button.configure(text="Edit Coordinate")


class MapProjection(CTkFrame):
    def __init__(self, main: MainApp, mainframe):
        CTkFrame.__init__(self, master=mainframe)
        self.main = main
        main.get_name
        self.place(relx=0.01, rely=0.69, relheight=0.29, relwidth=0.95)
        self.projection_type = StringVar(self, value="Mercator")
        label = CTkLabel(
            self,
            text="PROJECTION",
            font=("Helvetica", 14, "bold"),
        )
        label.grid(column=0, row=0, columnspan=5)
        label_projection = CTkLabel(self, text="Projection :", anchor="e")
        label_projection.grid(row=1, column=0, columnspan=1, pady=5)
        select_projection = CTkButton(
            self,
            width=70,
            text="Select projection",
            textvariable=self.projection_type,
            hover_color="gray",
            fg_color="dim gray",
        )
        select_projection.grid(row=1, column=2, columnspan=1, pady=5, padx=10)
        CTkScrollableDropdown(
            select_projection,
            width=200,
            values=["Mercator", "Orthographic"],
        )
        self.projection_option = StringVar(self, value="width")

        def select_projection_option():
            if self.projection_option.get() == "scale":
                scale_entry.configure(state="normal", text_color="white")
                scale_unit.configure(text_color="white")
                width_entry.configure(state="disabled", text_color="gray")
                width_unit.configure(text_color="gray")
                scale_radio.configure(text_color="white")
                width_radio.configure(text_color="gray")

            elif self.projection_option.get() == "width":
                scale_entry.configure(state="disabled", text_color="gray")
                scale_unit.configure(text_color="gray")
                width_entry.configure(state="normal", text_color="white")
                width_unit.configure(text_color="white")
                scale_radio.configure(text_color="gray")
                width_radio.configure(text_color="white")
            else:
                scale_entry.configure(state="disabled", text_color="gray")
                scale_unit.configure(text_color="gray")
                width_entry.configure(state="disabled", text_color="gray")
                width_unit.configure(text_color="gray")
                scale_radio.configure(text_color="gray")
                width_radio.configure(text_color="gray")

        row = 3

        scale_radio = ctk.CTkRadioButton(
            self,
            width=7,
            variable=self.projection_option,
            value="scale",
            radiobutton_height=12,
            radiobutton_width=12,
            text_color_disabled="gray",
            text="Scale = 1 :",
            command=select_projection_option,
        )
        scale_entry = ctk.CTkEntry(
            self,
            width=70,
            textvariable=DoubleVar(value=10000),
            text_color="white",
        )
        scale_unit = ctk.CTkLabel(self, text="cm", anchor="w")
        scale_radio.grid(row=row, column=0, columnspan=1, pady=5, sticky="w")
        scale_entry.grid(row=row, column=2, columnspan=1, pady=5)  # , padx=10)
        scale_unit.grid(row=row, column=5, pady=5)

        row = 2
        width_radio = ctk.CTkRadioButton(
            self,
            width=7,
            variable=self.projection_option,
            value="width",
            radiobutton_height=12,
            radiobutton_width=12,
            text_color_disabled="gray",
            text="Width =",
            command=select_projection_option,
            # command=select_projection_option,
        )
        width_entry = ctk.CTkEntry(
            self,
            width=70,
            textvariable=DoubleVar(value=20),
            text_color="white",
        )
        width_unit = ctk.CTkLabel(self, text="cm", anchor="w")
        width_radio.grid(row=row, column=0, columnspan=1, pady=5, sticky="w")
        width_entry.grid(row=row, column=2, columnspan=1, pady=5)  # , padx=10)
        width_unit.grid(row=row, column=5, pady=5)

        select_projection_option()


class LayerMenu(ctk.CTkFrame):
    def __init__(self, main: MainApp, mainframe):
        super().__init__(mainframe)
        self.main = main
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10, fill="x")

        self.layer_control = ctk.CTkTabview(
            self,
            segmented_button_selected_color="SpringGreen4",
            segmented_button_selected_hover_color="OliveDrab4",
            text_color_disabled="coral",
        )
        self.layer_control.pack(expand=1, fill="both")

        self.layers = {}
        self.add_remove_layer()

    def print_script(self):
        bounds = f"{roi[0].get()}/{roi[1].get()}/{roi[2].get()}/{roi[3].get()}"
        print("gmt begin peta png")
        print(f"\tgmt basemap -R{bounds} -JM20c")
        for layer, script in self.layers.items():
            if layer == "Coastal line":

                script = self.coast.call_script()

            elif layer == "Earth relief":
                script = self.grdimage.call_script()
            print(f"\t{script}")
        print("gmt end")

    def add_remove_layer(self):
        del_tab_button = CTkButton(
            self.button_frame,
            text="Delete layer",
            command=self.delete_tab,
            width=30,
            hover_color="red",
        )
        del_tab_button.pack(side="left", padx=10)

        options = [
            "Coastal line",
            "Earth relief",
            "Contour line",
            "Earthquake plot",
            "Focal mechanism",
            "Regional tectonics",
            "Map inset",
            "Legend",
        ]

        button_add_layer = CTkButton(self.button_frame, text="Add layer", width=20)
        button_add_layer.pack(side="left", padx=10)

        CTkScrollableDropdown(
            button_add_layer,
            values=options,
            justify="left",
            height=265,
            width=200,
            resize=False,
            button_height=23,
            scrollbar=False,
            command=self.add_tab,
        )
        button_print = CTkButton(
            self.button_frame, text="Layer List", command=lambda: self.print_script()
        )
        button_print.pack(side="left", padx=10)

    def color_picker_button(self, master, row, col, var, name, widget):
        dark_picker_logo = Image.open("./image/dark_eyedropper.png")
        light_picker_logo = Image.open("./image/light_eyedropper.png")
        color_picker_logotk = CTkImage(
            dark_image=dark_picker_logo, light_image=light_picker_logo, size=(20, 20)
        )

        select_color = ctk.CTkButton(
            master,
            image=color_picker_logotk,
            text="",
            command=lambda: self.color_chooser(var, name, widget),
            width=30,
            hover_color="gray",
            fg_color="dim gray",
        )
        select_color.grid(row=row, column=col)
        CTkToolTip(select_color, "Color picker")

    def color_chooser(self, var, name, widget):
        color_code = colorchooser.askcolor(title=f"choose the {name} color")
        print(type(color_code))
        print(color_code)
        print(f"hex code : {color_code[1]}")
        rgb_code = f"{color_code[0][0]}/{color_code[0][1]}/{color_code[0][2]}"
        print(var)
        var.set(rgb_code)
        self.update_preview(var, widget=widget)
        return rgb_code

    def gmt_color_table(self, master, row, col, var):
        self.button_color_table = CTkButton(
            master,
            text="Color Table",
            command=lambda: self.color_table(var),
            width=20,
            hover_color="gray",
        )
        self.button_color_table.grid(row=row, column=col)

    def color_preview(self, master, row, col, var):
        self.label_preview = CTkLabel(
            master, width=70, height=20, fg_color=var.get(), text=""
        )
        self.label_preview.grid(column=col, row=row)
        self.update_preview(var, self.label_preview)
        return self.label_preview

    def update_preview(self, var_color, widget):
        from color_list import rgb_dict

        color_name = var_color.get()
        print("update")
        print(color_name)
        if "/" in color_name:
            print("split")
            red, green, blue = color_name.split("/")
            # label_preview
        elif color_name.lower() in rgb_dict:
            print("konversi dictionary")
            rgb_code = rgb_dict[color_name.lower()]
            red, green, blue = rgb_code.split("/")

        else:
            print("color name/code not match")
            red, green, blue = "255", "255", "255"
        widget.configure(fg_color=self._hex(red, green, blue))

    def _hex(self, r, g, b):
        """translates an rgb tuple of int to a tkinter friendly color code"""
        r = int(r)
        g = int(g)
        b = int(b)
        return f"#{r:02x}{g:02x}{b:02x}"

    def add_tab(self, choice):
        # tab_name = f"{len(self.tabs)+1}. {choice}"
        layer = choice
        new_layer = self.layer_control.add(layer)
        self.script = StringVar()
        self.layers[layer] = self.script

        self.layer_control.set(layer)
        # label = ctk.CTkLabel(new_tab, text=choice, bg_color="red")
        # label.pack(side="right")
        match choice:
            case "Coastal line":
                self.coast = Coast(new_layer)
            case "Earth relief":
                self.grdimage = GridImage(new_layer)
                self.layers["Earth relief"] = self.grdimage.script
            case "Contour line":
                self.contour = Contour(new_layer)
            case "Earthquake plot":
                self.earthquake = Earthquake(new_layer)
            case "Focal mechanism":
                self.focmec = Focmec(new_layer)
            case "Regional tectonics":
                self.tectonics = Tectonic(new_layer)
            case "Map inset":
                self.inset = Inset(new_layer)
            case "Legend":
                self.legend = Legend(new_layer)

    def tab_grid_layout(self, tab: CTkFrame, ncol=15):
        """Configures the grid layout for a tab widget.

        This function sets the column and row weights for a tab's grid layout,
        ensuring consistent sizing and responsiveness.

        Args:
            tab: The tab widget to configure.
        """

        num_cols = 4  # Number of columns
        col_weights = [5] + [1] * ncol  # Weights for each column

        num_rows = 10  # Number of rows
        row_weight = 1  # Weight for all rows (uniform)

        for i in range(ncol):
            tab.columnconfigure(i, weight=1, uniform="a")

        for i in range(num_rows):
            tab.rowconfigure(i, weight=row_weight, uniform="b")

    def optionmenu_callback(self, choice):
        print("optionmenu dropdown clicked:", choice)

    def delete_tab(self):
        active_tab = self.layer_control.get()
        deleting_layer = messagebox.askyesno(
            message=f"Delete layer: '{active_tab}' ?",
            title="Deleting layer..",
        )
        if active_tab in self.layers and deleting_layer == True:
            self.layers.pop(active_tab)
            # print(self.layer_control.index(active_tab))
            # index_of_deleted = self.layer_control.index(active_tab)
            # self.tabs.pop(index_of_deleted)
            # print(self.layer_control.index(active_tab))
            self.layer_control.delete(active_tab)

            # print(self.tab_names)
            # print(self.tabs)

    def widget_color(self, tab, row: int, text: list, var: StringVar):
        label = CTkLabel(tab, text=text[0], anchor="e")
        CTkToolTip(label, text[1])
        entry = CTkEntry(tab, width=200, textvariable=var)
        entry.bind(
            "<FocusOut>",
            lambda event: self.update_preview(var_color=var, widget=preview),
        )
        entry.bind(
            "<Return>",
            lambda event: self.update_preview(var_color=var, widget=preview),
        )
        preview = self.color_preview(tab, row=row, col=13, var=var)
        self.color_picker_button(
            tab, row=row, col=10, var=var, name=text[0], widget=preview
        )
        label.grid(row=row, column=0, columnspan=5, sticky="nsew", padx=10)
        entry.grid(row=row, column=5, columnspan=5)


class Coast(LayerMenu):
    def __init__(self, tab):

        self.tab_grid_layout(tab)
        self.color_land = StringVar(tab, "lightgreen")
        self.color_sea = StringVar(tab, value="lightblue")
        self.line_color = StringVar(tab, "black")
        self.widget_color(
            tab,
            1,
            ["Land Color :", "The color of dry area or island"],
            self.color_land,
        )
        self.widget_color(
            tab,
            2,
            ["Sea Color :", "The color of wet area like sea or lake"],
            self.color_sea,
        )
        self.widget_color(
            tab,
            3,
            ["Line color :", "Line color of the coastal boundary"],
            self.line_color,
        )

        self.wdg_line_thickness(tab, 4)

        self.script = StringVar()
        self.script.set(self.call_script())

        # print(self.script.get())

    def call_script(self):
        script = f"gmt coast -G{self.color_land.get()} -S{self.color_sea.get()} -W{self.line_size.get()},{self.line_color.get()}"
        self.script.set(script)

        return script

    def wdg_line_thickness(self, tab, row):
        pen = ["0p", "0.25p", "0.50p", "0.75p", "1p", "1.5p", "2p", "3p"]
        self.line_size = StringVar(tab, value="0.25p")
        label = CTkLabel(tab, text="Outline size: ", anchor="e")
        entry = ctk.CTkComboBox(
            tab,
            width=300,
            variable=self.line_size,
            values=pen,
        )
        label.grid(row=row, column=0, columnspan=5, sticky="nsew", padx=10)
        entry.grid(row=row, column=5, columnspan=6)


class GridImage(LayerMenu):
    def __init__(self, tab):
        self.wdth = 200
        self.gmt_grd_res = [
            "01s",
            "03s",
            "15s",
            "30s",
            "01m",
            "02m",
            "03m",
            "04m",
            "05m",
            "06m",
            "10m",
            "15m",
            "20m",
            "30m",
            "01d",
        ]

        self.gmt_grd_src = [
            "Earth Relief v2.6 [SRTM15]",
            "Earth Relief v2.0 [SYNBATH]",
            "Earth Relief 2024 [GEBCO]",
            "Earth Seafloor Age [EarthByte]",
            "Earth Day View [Blue Marble]",
            "Earth Night View [Black Marble]",
            "Earth Magnetic Anomalies at sea-level [EMAG2v3]",
            "Earth Magnetic Anomalies at 4km altitude [EMAG2v3]",
            "Earth Magnetic Anomalies v2.1 [WDMAM]",
            "Earth Vertical Gravity Gradient Anomalies v32 [IGPP]",
            "Earth Free Air Gravity Anomalies v32 [IGPP]",
            "Earth Free Air Gravity Anomalies Errors v32 [IGPP]",
        ]

        self.gmt_grd_dict = {
            self.gmt_grd_src[0]: ["@earth_relief_"] + self.gmt_grd_res,
            self.gmt_grd_src[1]: ["@earth_synbath_"] + self.gmt_grd_res,
            self.gmt_grd_src[2]: ["@earth_gebco_"] + self.gmt_grd_res,
            self.gmt_grd_src[3]: ["@earth_age_"] + self.gmt_grd_res[4:],
            self.gmt_grd_src[4]: ["@earth_day_"] + self.gmt_grd_res[3:],
            self.gmt_grd_src[5]: ["@earth_night"] + self.gmt_grd_res[3:],
            self.gmt_grd_src[6]: ["@earth_mag_"] + self.gmt_grd_res[5:],
            self.gmt_grd_src[7]: ["@earth_mag4km_"] + self.gmt_grd_res[5:],
            self.gmt_grd_src[8]: ["@earth_wdmam_"] + self.gmt_grd_res[6:],
            self.gmt_grd_src[9]: ["@earth_vgg_"] + self.gmt_grd_res[4:],
            self.gmt_grd_src[10]: ["@earth_faa_"] + self.gmt_grd_res[4:],
            self.gmt_grd_src[11]: ["@earth_faaerror_"] + self.gmt_grd_res[4:],
        }
        self.tab_grid_layout(tab)
        self.wdg_grd_resource(tab, 1)
        self.wdg_grd_resolution(tab, 2)
        self.wdg_grd_cpt_color(tab, 3)
        self.wdg_grd_shading(tab, 4)
        self.wdg_grd_masking(tab, 5)
        # self.color_land = self.wdg_color_land(tab)
        # self.color_sea = self.wdg_color_sea(tab)
        # self.line_color = self.wdg_line_color(tab)
        self.script = StringVar()
        self.script.set(self.call_script())
        # print(self.script.get())

    def call_script(self):
        remote_data = f"{self.gmt_grd_dict[self.grdimg_resource.get()][0]}{self.grdimg_resolution.get()}"
        if self.grdimg_masking.get() == "Yes":
            shade = "-I+d"
        else:
            shade = ""
        return f"gmt grdimage {remote_data} {shade}"

    def placing(self, row, var1, var2):
        var1.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=10)
        var2.grid(row=row, column=2, columnspan=5, sticky="ew")

    def wdg_grd_resource(self, tab, row):

        self.grdimg_resource = StringVar(tab, value=self.gmt_grd_src[0])
        label = CTkLabel(tab, text="Grid data: ", anchor="e", bg_color="blue")
        entry = ctk.CTkOptionMenu(
            tab,
            width=self.wdth,
            fg_color="#565B5E",
            button_color="#565B5E",
            button_hover_color="#7A848D",
            variable=self.grdimg_resource,
            dynamic_resizing=False,
        )
        CTkScrollableDropdown(
            entry,
            values=self.gmt_grd_src,
            command=lambda e: self.setvariable(tab, e),
            width=400,
            height=300,
            justify="left",
            resize=False,
            autocomplete=True,
        )
        self.placing(row, label, entry)

    def setvariable(self, tab, a):
        self.grdimg_resource.set(a)
        self.wdg_grd_resolution(tab, 2)

    def wdg_grd_resolution(self, tab, row):

        print(self.grdimg_resource.get())
        self.grdimg_resolution = StringVar(
            tab, value=self.gmt_grd_dict[self.grdimg_resource.get()][3]
        )
        label = CTkLabel(tab, text="Grid resolution: ", anchor="e")
        entry = ctk.CTkOptionMenu(
            tab,
            width=self.wdth,
            variable=self.grdimg_resolution,
            fg_color="#565B5E",
            button_color="#565B5E",
            button_hover_color="#7A848D",
            dynamic_resizing=False,
        )
        CTkScrollableDropdown(
            entry,
            values=self.gmt_grd_res,
            command=lambda e: self.grdimg_resolution.set(e),
            width=100,
            height=300,
            justify="left",
            resize=False,
            autocomplete=True,
        )
        label.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=10)
        entry.grid(row=row, column=2, columnspan=2, sticky="ew")

    def wdg_grd_cpt_color(self, tab, row):
        from color_list import palette_name

        self.grdimg_cpt_color = StringVar(tab, value="earth")
        label = CTkLabel(tab, text="Color palette table(CPT): ", anchor="e")
        entry = ctk.CTkOptionMenu(
            tab,
            width=50,
            variable=self.grdimg_cpt_color,
            values=palette_name,
            fg_color="#565B5E",
            button_color="#565B5E",
            button_hover_color="#7A848D",
        )
        CTkScrollableDropdown(
            entry,
            values=palette_name,
            command=lambda e: self.grdimg_cpt_color.set(e),
            width=200,
            height=300,
            justify="left",
            resize=False,
            autocomplete=True,
        )
        label.grid(row=row, column=0, columnspan=5, sticky="nsew", padx=10)
        entry.grid(row=row, column=5, columnspan=2, sticky="ew")

    def wdg_grd_shading(self, tab, row):
        self.grdimg_masking = StringVar(tab, value="Yes")
        label = CTkLabel(tab, text="Grid shading: ", anchor="e")
        entry = ctk.CTkOptionMenu(
            tab,
            width=50,
            variable=self.grdimg_masking,
            values=["Yes", "No"],
            fg_color="#565B5E",
            button_color="#565B5E",
            button_hover_color="#7A848D",
        )
        CTkScrollableDropdown(
            entry,
            values=["Yes", "No"],
            command=lambda e: self.grdimg_cpt_color.set(e),
            width=100,
            height=100,
            justify="left",
            resize=False,
            autocomplete=True,
        )
        label2 = CTkLabel(tab, text="manual shading", anchor="e")
        # self.placing(4, label, entry)
        label.grid(row=row, column=0, columnspan=4, sticky="nsew", padx=10)
        label2.grid(row=row, column=5, columnspan=4, sticky="nsew", padx=10)
        entry.grid(row=row, column=4, columnspan=1, sticky="ew")

    def wdg_grd_masking(self, tab, row):
        self.grdimg_masking = StringVar(tab, value="Yes")
        label = CTkLabel(tab, text="Sea masking: ", anchor="e")
        entry = ctk.CTkComboBox(
            tab, width=self.wdth, variable=self.grdimg_masking, values=["Yes", "No"]
        )
        self.placing(5, label, entry)


class Contour(LayerMenu):
    def __init__(self, tab):
        # interval
        # resolution
        # warna index biasa
        # ketebalan kontur index biasa
        self.tab_grid_layout(tab)
        self.wdg_color_land(tab)
        self.wdg_color_sea(tab)
        self.wdg_line_size(tab)
        self.wdg_line_color(tab)
        self.script = StringVar()
        self.script.set(self.call_script())
        # print(self.script.get())

    def call_script(self):
        script = f"gmt contour -G{self.color_land.get()} -S{self.color_sea.get()} -W{self.line_size.get()},{self.line_color.get()}"
        self.script.set(script)

        return script

    def wdg_color_land(self, tab):
        self.color_land = StringVar(tab, "lightgreen")
        label = CTkLabel(tab, text="Land color: ", anchor="e")
        entry = CTkEntry(tab, width=300, textvariable=self.color_land)
        entry.bind(
            "<FocusOut>",
            lambda event: self.update_preview(
                var_color=self.color_land, widget=land_preview
            ),
        )

        land_preview = self.color_preview(tab, row=1, col=3, var=self.color_land)
        self.color_picker_button(
            tab, row=1, col=2, var=self.color_land, name="land", widget=land_preview
        )
        label.grid(row=1, column=0, sticky="nsew", padx=10)
        entry.grid(row=1, column=1)

    def wdg_color_sea(self, tab):
        self.color_sea = StringVar(tab, value="lightblue")
        label = CTkLabel(tab, text="Sea color: ", anchor="e")
        entry = CTkEntry(tab, width=300, textvariable=self.color_sea)
        entry.bind(
            "<FocusOut>",
            lambda event: self.update_preview(
                var_color=self.color_sea, widget=sea_preview
            ),
        )
        sea_preview = self.color_preview(tab, row=2, col=3, var=self.color_sea)
        self.color_picker_button(
            tab, row=2, col=2, var=self.color_sea, name="sea", widget=sea_preview
        )
        label.grid(row=2, column=0, sticky="nsew", padx=10)
        entry.grid(row=2, column=1)

    def wdg_line_size(self, tab):
        pen = ["0p", "0.25p", "0.50p", "0.75p", "1p", "1.5p", "2p", "3p"]
        self.line_size = StringVar(tab, value="0.25p")
        label = CTkLabel(tab, text="Outline size: ", anchor="e")
        entry = ctk.CTkComboBox(tab, width=300, variable=self.line_size, values=pen)
        label.grid(row=3, column=0, sticky="nsew", padx=10)
        entry.grid(row=3, column=1)

    def wdg_line_color(self, tab):
        self.line_color = StringVar(tab, "black")
        label_line_color = CTkLabel(tab, text="Outline color: ", anchor="e")

        entry_line_color = ctk.CTkEntry(tab, width=300, textvariable=self.line_color)

        label_line_color.grid(row=4, column=0, sticky="nsew", padx=10)
        entry_line_color.grid(row=4, column=1)
        # self.color_picker_button(tab, row=4, col=2, var=line_color, name="sea", widget=)


class Earthquake(LayerMenu):
    # tanggal awal
    # tanggal akhir
    # sumber katalog usgs, isc, user supplied
    # minmax magnitude
    # minmax depth
    pass


class Focmec(LayerMenu):
    # tanggal awal
    # tanggal akhir
    # sumber katalog gcmt, user supplied
    # minmax magnitude
    # minmax depth
    pass


class Tectonic(LayerMenu):
    # source
    # ketebalan garis
    # warna garis
    pass


class Inset(LayerMenu):
    # lokasi

    pass


class Legend(LayerMenu):
    # lokasi
    # radio button info apa aja yg masuk
    pass


if __name__ == "__main__":
    app = MainApp()
