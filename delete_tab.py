import customtkinter as ctk
import os, threading, subprocess
from customtkinter import (
    StringVar,
    DoubleVar,
    BooleanVar,
    CTkButton,
    CTkLabel,
    CTkEntry,
    CTkFrame,
    CTkImage,
    CTkCheckBox,
    CTkOptionMenu,
    filedialog,
    DISABLED,
    NORMAL,
)
import ctypes, json, queue, sys
from tkinter import messagebox, Canvas, TclError
from _date_delay_entry import DateEntry
from functools import wraps

# from CTkListbox import CTkListbox
from pathlib import Path
from PIL import Image, ImageTk
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ctk_tooltip import CTkToolTip
from ctk_coordinate_gui import CoordWindow
from ctk_scrollable_dropdown import CTkScrollableDropdown
from CTkColorPicker import *
from ctk_rangeslider import CTkRangeSlider
from utils import *

if os.name == "nt":
    scalefactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    print(scalefactor)
    ctk.set_widget_scaling(1 / scalefactor)
    ctk.set_window_scaling(1 / scalefactor)

else:
    scalefactor = 1


# def run_in_thread(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         thread = threading.Thread(target=func, args=args, kwargs=kwargs)
#         thread.daemon = True
#         thread.start()
#         return thread

#     return wrapper


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("gmt_pyplotter")
        self.geometry("700x550+100+100")
        self.minsize(700, 550)
        self.resize_image("map_simple_0.png")
        self.resize_image("map_relief_0.jpg")
        output_dir = self.load_state()

        self.frame_map_param = CTkFrame(self, width=210, height=550)
        self.frame_layers = CTkFrame(self, width=490, height=550)
        self.frame_map_param.place(x=0, y=0, relwidth=0.3, relheight=1)
        self.frame_layers.place(relx=0.3, y=0, relwidth=0.7, relheight=1)
        self.get_name = MapFileName(self, self.frame_map_param, output_dir)
        self.get_coordinate = MapCoordinate(self, self.frame_map_param)
        self.get_projection = MapProjection(self, self.frame_map_param)
        self.get_layers = LayerMenu(self, self.frame_layers)

        button = CTkButton(
            self.frame_map_param, text="scale", command=lambda: self.scalling()
        )
        button.place(relx=0, rely=0.95)
        self.orig = True
        self.protocol("WM_DELETE_WINDOW", self.closing)
        self.mainloop()

    def resize_image(self, file):
        try:
            image_dir = "image"
            path = Path(__file__).resolve().parent
            for i in range(1, 6):
                filename = f"{file[:-5]}{i}{file[-4:]}"

                if not os.path.exists(os.path.join(path, "image", filename)):
                    image = Image.open(os.path.join(path, image_dir, file))
                    w, h = image.size
                    new_w, new_h = w // (2**i), h // (2**i)
                    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    resized.save(os.path.join(path, image_dir, filename), optimize=True)

        except IOError:
            messagebox.showerror(
                "Error", f"Unable to open file '{file}', file not found"
            )

    def scalling(self):
        if self.orig == False:
            ctk.set_widget_scaling(1 / scalefactor)
            ctk.set_window_scaling(1 / scalefactor)
            self.orig = True
        else:
            ctk.set_widget_scaling(1)
            ctk.set_window_scaling(1)
            self.orig = False

    def save_state(self):
        state = {
            "output_dir": self.get_name.output_dir.get(),
            "roi": [x.get() for x in roi],
        }

        with open("saved_param.json", "w") as f:
            json.dump(state, f)

    def closing(self):
        self.save_state()
        self.withdraw()
        self.quit()
        self.destroy()

    def load_state(self):
        try:
            with open("saved_param.json", "r") as f:
                state = json.load(f)
                output_dir = state["output_dir"]
            return output_dir
        except FileNotFoundError:
            return os.path.expanduser("~")


class MapFileName(CTkFrame):
    def __init__(self, main: MainApp, mainframe, output_dir):
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

        # self.output_dir = StringVar(self, value=os.path.expanduser("~"))
        self.output_dir = StringVar(self, value=output_dir)
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
            size=(20, 20),
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

    @property
    def name_script(self):
        if os.name == "posix":
            script = ".sh"
        elif os.name == "nt":
            script = ".bat"
        return f"{self.file_name.get()}{script}"

    @property
    def name_map(self):
        return f"{self.file_name.get()}{self.extension.get()}"

    @property
    def dir_name(self):
        return os.path.join(self.output_dir.get(), self.file_name.get())

    @property
    def dir_name_script(self):
        return os.path.join(self.output_dir.get(), self.name_script)

    @property
    def dir_name_map(self):
        return os.path.join(self.output_dir.get(), self.name_map)

    @property
    def dir_prename_map(self):
        return os.path.join(self.output_dir.get(), f"preview_{self.name_map}")


class MapCoordinate(CTkFrame):
    def __init__(self, main: MainApp, mainframe):
        super().__init__(mainframe)
        self.main = main
        self.place(relx=0.01, rely=0.27, relheight=0.40, relwidth=0.95)

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

        self.generate_roi_variable()

        self.x_min_entry = self.create_entry(roi[0])
        self.x_max_entry = self.create_entry(roi[1])
        self.y_min_entry = self.create_entry(roi[2])
        self.y_max_entry = self.create_entry(roi[3])
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

    def generate_roi_variable(self):
        global roi
        roi = [StringVar(self) for _ in range(4)]

        try:
            with open("saved_param.json", "r") as f:
                state = json.load(f)
                saved_roi = state["roi"]
                roi[0].set(saved_roi[0])
                roi[1].set(saved_roi[1])
                roi[2].set(saved_roi[2])
                roi[3].set(saved_roi[3])
                self.coord_picked = True
        except KeyError:
            roi[0].set("min lon")
            roi[1].set("max lon")
            roi[2].set("min lat")
            roi[3].set("max lat")
            self.coord_picked = False

    def create_entry(self, text_var):
        return CTkEntry(
            self, width=80, font=("Consolas", 14), textvariable=text_var, state=DISABLED
        )

    @property
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

    @property
    def coord_r(self):
        """returning the coordinate boundaries in gmt format:
        -Rmin longitude/max longitude/min latitude/max latitude
        """
        coord_r = f"-R{roi[0].get()}/{roi[1].get()}/{roi[2].get()}/{roi[3].get()}"
        return coord_r

    def update_coor_entry(self):
        self.coord_button.configure(state=DISABLED)
        if self.coord_picked == False:
            coord = None
        else:
            coord = roi[0].get(), roi[1].get(), roi[2].get(), roi[3].get()
        get_coord = CoordWindow(coord)
        acquired_coord = get_coord.return_roi()

        try:
            float(acquired_coord[0])
            roi[0].set(acquired_coord[0])
            roi[1].set(acquired_coord[1])
            roi[2].set(acquired_coord[2])
            roi[3].set(acquired_coord[3])
            self.coord_picked = True
            self.coord_button.configure(text="Edit Coordinate")
        except ValueError:
            pass
        self.coord_button.configure(state=NORMAL)


class MapProjection(CTkFrame):
    def __init__(self, main: MainApp, mainframe):
        CTkFrame.__init__(self, master=mainframe)
        self.main = main
        main.get_name
        self.place(relx=0.01, rely=0.69, relheight=0.29, relwidth=0.95)
        self.projection_name = StringVar(self, value="Mercator")
        self.projection_option = StringVar(self, value="width")
        self.proj_width = StringVar(self, value="20")
        self.proj_scale = StringVar(self, value="10000")
        self.create_projection_menu()

    def create_projection_menu(self):
        label_main = CTkLabel(
            self,
            text="PROJECTION",
            font=("Helvetica", 14, "bold"),
        )

        label_projection = CTkLabel(self, text="Projection :", anchor="e")
        select_projection = CTkButton(
            self,
            width=70,
            text="Select projection",
            textvariable=self.projection_name,
            hover_color="gray",
            fg_color="dim gray",
        )

        CTkScrollableDropdown(
            select_projection,
            width=200,
            values=["Mercator", "Orthographic"],
        )
        label_main.grid(column=0, row=0, columnspan=5)
        label_projection.grid(row=1, column=0, columnspan=1, pady=5)
        select_projection.grid(row=1, column=2, columnspan=1, pady=5, padx=10)

        row = 3

        self.scale_radio = ctk.CTkRadioButton(
            self,
            width=7,
            variable=self.projection_option,
            value="scale",
            radiobutton_height=12,
            radiobutton_width=12,
            text_color_disabled="gray",
            text="Scale = 1 :",
            command=self.select_projection_option,
        )
        self.scale_entry = ctk.CTkEntry(
            self,
            width=70,
            textvariable=DoubleVar(value=10000),
            text_color="white",
        )
        self.scale_unit = ctk.CTkLabel(self, text="cm", anchor="w")
        self.scale_radio.grid(row=row, column=0, columnspan=1, pady=5, sticky="w")
        self.scale_entry.grid(row=row, column=2, columnspan=1, pady=5)
        self.scale_unit.grid(row=row, column=5, pady=5)

        row = 2
        self.width_radio = ctk.CTkRadioButton(
            self,
            width=7,
            variable=self.projection_option,
            value="width",
            radiobutton_height=12,
            radiobutton_width=12,
            text_color_disabled="gray",
            text="Width =",
            command=self.select_projection_option,
            # command=select_projection_option,
        )
        self.width_entry = ctk.CTkEntry(
            self,
            width=70,
            textvariable=DoubleVar(value=20),
            text_color="white",
        )
        self.width_unit = ctk.CTkLabel(self, text="cm", anchor="w")
        self.width_radio.grid(row=row, column=0, columnspan=1, pady=5, sticky="w")
        self.width_entry.grid(row=row, column=2, columnspan=1, pady=5)  # , padx=10)
        self.width_unit.grid(row=row, column=5, pady=5)
        self.select_projection_option()

    def select_projection_option(self):
        if self.projection_option.get() == "scale":
            self.scale_entry.configure(state=NORMAL, text_color="white")
            self.scale_unit.configure(text_color="white")
            self.width_entry.configure(state=DISABLED, text_color="gray")
            self.width_unit.configure(text_color="gray")
            self.scale_radio.configure(text_color="white")
            self.width_radio.configure(text_color="gray")
        elif self.projection_option.get() == "width":
            self.scale_entry.configure(state=DISABLED, text_color="gray")
            self.scale_unit.configure(text_color="gray")
            self.width_entry.configure(state=NORMAL, text_color="white")
            self.width_unit.configure(text_color="white")
            self.scale_radio.configure(text_color="gray")
            self.width_radio.configure(text_color="white")
        else:
            self.scale_entry.configure(state=DISABLED, text_color="gray")
            self.scale_unit.configure(text_color="gray")
            self.width_entry.configure(state=DISABLED, text_color="gray")
            self.width_unit.configure(text_color="gray")
            self.scale_radio.configure(text_color="gray")
            self.width_radio.configure(text_color="gray")

    @property
    def map_scale_factor(self):
        width = float(roi[1].get()) - float(roi[0].get())
        return width * 111.11 / (int(self.proj_width.get()) * 0.0001)


class LayerMenu(ctk.CTkFrame):
    def __init__(self, main: MainApp, mainframe):
        super().__init__(mainframe)
        self.main = main
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.button_frame = CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10, fill="x")

        self.layer_control = ctk.CTkTabview(
            self,
            segmented_button_selected_color="SpringGreen4",
            segmented_button_selected_hover_color="OliveDrab4",
            text_color_disabled="coral",
            segmented_button_unselected_color="dim grey",
            segmented_button_unselected_hover_color="honeydew4",
            anchor="w",
        )
        self.layer_control.pack(expand=1, fill="both")

        self.layers = []
        self.add_remove_layer()
        MapPreview(self.main, self.button_frame)

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
            "Cosmetics",
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

    def delete_tab(self):
        active_tab = self.layer_control.get()
        delete_layer = messagebox.askyesno(
            message=f"Delete layer: '{active_tab}' ?",
            title="Deleting layer..",
        )
        print("cek dulu isi active tab dan self.layers")
        print(active_tab)
        print(self.layers)
        if delete_layer == False:
            print("gajadi delete")
            return

        self.layers.remove(active_tab)
        match active_tab:
            case "Coastal line":
                if hasattr(self, "coast") and self.coast is not None:
                    del self.coast
            case "Earth relief":
                if hasattr(self, "grdimage") and self.grdimage is not None:
                    del self.grdimage
            case "Contour line":
                print("deleting contour instance")
                # if hasattr(self, "contour") and self.contour is not None:
                if self.contour.after_id:
                    self.main.after_cancel(self.contour.after_id)
                self.contour.remove_traces()
                del self.contour
                print("contour deleted")
            case "Earthquake plot":
                if hasattr(self, "earthquake") and self.earthquake is not None:
                    del self.earthquake
            case "Focal mechanism":
                if hasattr(self, "focmec") and self.focmec is not None:
                    del self.focmec
            case "Regional tectonics":
                if hasattr(self, "tectonics") and self.tectonics is not None:
                    del self.tectonics
            case "Map inset":
                if hasattr(self, "inset") and self.inset is not None:
                    del self.inset
            case "Legend":
                if hasattr(self, "legend") and self.legend is not None:
                    del self.legend
            case "Cosmetics":
                if hasattr(self, "cosmetics") and self.cosmetics is not None:
                    del self.cosmetics
        self.layer_control.delete(active_tab)

    def add_tab(self, choice):
        # tab_name = f"{len(self.tabs)+1}. {choice}"
        layer = choice
        new_layer = self.layer_control.add(layer)
        self.layers.append(layer)

        self.layer_control.set(layer)
        # label = ctk.CTkLabel(new_tab, text=choice, bg_color="red")
        # label.pack(side="right")
        match choice:
            case "Coastal line":
                self.coast = Coast(new_layer, self)
            case "Earth relief":
                self.grdimage = GrdImage(new_layer, self)
            case "Contour line":
                self.contour = Contour(self.main, new_layer)
            case "Earthquake plot":
                self.earthquake = Earthquake(new_layer, self.main)
            case "Focal mechanism":
                self.focmec = Focmec(new_layer)
            case "Regional tectonics":
                self.tectonics = Tectonic(new_layer)
            case "Map inset":
                self.inset = Inset(new_layer)
            case "Legend":
                self.legend = Legend(new_layer)
            case "Cosmetics":
                self.cosmetics = Cosmetics(new_layer)

    def tab_menu_layout_divider(self, tab: CTkFrame):
        """Configures the grid layout for a tab widget.

        This function sets the column and row weights for a tab's grid layout,
        ensuring consistent sizing and responsiveness.

        Args:
            tab: The tab widget to configure.
        """
        text = CTkFrame(tab)
        text.place(x=0, y=0, relwidth=0.35, relheight=1)
        opti = CTkFrame(tab)
        opti.place(relx=0.35, y=0, relwidth=0.65, relheight=1)
        text.columnconfigure(0, weight=1)
        for i in range(10):
            text.rowconfigure(i, weight=1)
            opti.rowconfigure(i, weight=1)
        for i in range(7):
            opti.columnconfigure(i, weight=1, uniform="a")

        return text, opti

    def parameter_labels(self, label_frame: ctk.CTkFrame, labels_tips: dict[str, str]):
        labels = list(labels_tips.keys())
        tips = list(labels_tips.values())
        widget_labels: dict[str, CTkLabel] = dict()

        for i in range(len(labels_tips)):

            widget_labels[str(i)] = CTkLabel(
                label_frame, text=f"{labels[i]}  :", anchor="e"
            )
            # print(widget_labels[str(i)])
            CTkToolTip(widget_labels[str(i)], message=tips[i])
            widget_labels[str(i)].grid(row=i + 1, column=0, sticky="nsew", padx=10)


class MapPreview:
    def __init__(self, main: MainApp, button_frame: CTkFrame):

        self.main = main
        self.preview_status = "off"
        self.button_ = button_frame
        self.preview_queue = queue.Queue()
        self.map_preview_buttons()
        # self.get_window_offset()
        self.main.after(100, self._check_queue)

    def map_preview_buttons(self):
        self.button_preview = CTkButton(
            self.button_,
            text="Map Preview",
            width=100,
            command=lambda: self.map_preview_toggle(),
        )
        dark_refresh_logo = Image.open("./image/dark_refresh.png")
        light_refresh_logo = Image.open("./image/light_refresh.png")
        refresh_logotk = CTkImage(
            dark_image=dark_refresh_logo, light_image=light_refresh_logo, size=(18, 18)
        )
        self.button_preview.pack(side="left", padx=(10, 0))
        self.button_preview_refresh = CTkButton(
            self.button_,
            image=refresh_logotk,
            text="",
            width=17,
            hover_color="gray",
            fg_color="dim gray",
            anchor="e",
            command=lambda: self.map_preview_refresh(),
        )

    def map_preview_toggle(self):
        if self.preview_status == "off":
            self.prev_coord = set([r.get() for r in roi])
            self.button_preview.configure(state=DISABLED)
            self.print_script()

            self.threading_process(
                self.gmt_execute,
                args=[
                    self.main.get_name.name_script,
                    self.main.get_name.output_dir.get(),
                ],
                name="generate Preview Map",
            )

        else:
            self.map_preview_off()
            self.preview_status = "off"
            self.button_preview_refresh.pack_forget()

    def map_preview_on(self, success_status, message=""):
        if not success_status:
            print(f"Map generation failed: {message}")
            messagebox.showerror("Map Error", message)  # Show error to user
            # Handle UI for failure (e.g., revert status, don't show map)
            self.preview_status = "off"
            self.button_preview.configure(state=NORMAL)
            self.button_preview_refresh.pack_forget()
            return
        print(message)
        self.preview_status = "on"
        cur_x = self.main.winfo_x()
        cur_y = self.main.winfo_y()

        new_width = self.loading_image()

        resize = f"{new_width}x550+{cur_x}+{cur_y}"

        self.main.geometry(resize)

        self.main.frame_map_param.pack(side="left")
        self.main.frame_layers.pack(side="left")

        print(f"rel frame layer width= {210/new_width}")
        self.frame_preview = CTkFrame(self.main, height=550, width=new_width - 700)

        self.frame_preview.pack(side="left", fill="both", anchor="nw")
        self.canvas = Canvas(self.frame_preview, width=new_width - 700, height=550)
        self.canvas.pack(expand=True, fill="both")
        self.button_preview_refresh.pack(side="left")
        self.canvas.create_image(5, 0, image=self.imagetk, anchor="nw", tags="map")
        self.button_preview.configure(state=NORMAL)
        self.button_preview_refresh.configure(state=NORMAL)

    def map_preview_off(self):
        print(f"window size={self.main.winfo_width()}x{self.main.winfo_height()}")
        self.frame_preview.destroy()
        cur_x = self.main.winfo_x()
        cur_y = self.main.winfo_y()
        print(cur_x)
        print(cur_y)
        resize = f"700x550+{cur_x}+{cur_y}"
        self.main.geometry(resize)
        self.main.frame_map_param.place(x=0, y=0, relwidth=0.3, relheight=1)
        self.main.frame_layers.place(relx=0.3, y=0, relwidth=0.7, relheight=1)

    def map_preview_refresh(self):

        self.button_preview.configure(state=DISABLED)
        self.button_preview_refresh.configure(state=DISABLED)
        self.block_canvas_loading()
        self.print_script()
        self.threading_process(
            self.gmt_execute,
            args=[
                self.main.get_name.name_script,
                self.main.get_name.output_dir.get(),
            ],
            name="refresh Preview Map",
            refresh=True,
        )

    def block_canvas_loading(self):
        width = self.canvas.winfo_width()

        height = self.canvas.winfo_height()
        self.canvas.create_rectangle(
            0,
            0,
            width,
            height,
            fill="purple",
            outline="darkblue",
            width=2,
            stipple="gray50",
            tags="loading",
        )  # 50% "transparent" effect
        self.canvas.create_text(
            int(width / 2),
            int(height / 2),
            anchor="center",
            text="Loading Map",
            font=("Consolas", 20),
            fill="black",
            tags="loading",
        )

    def refreshed(self):
        for r in roi:
            self.prev_coord.add(r.get())

        if len(self.prev_coord) != 4:
            self.map_preview_off()
            print(self.prev_coord)
            print("coordinate berubah")
            self.map_preview_on(True)
        else:
            print(self.prev_coord)
            print("coordinate tetap")
            self.loading_image()
            self.canvas.delete("map")
            self.canvas.create_image(5, 0, image=self.imagetk, anchor="nw", tags="map")

        self.canvas.delete("loading")
        self.button_preview.configure(state=NORMAL)
        self.button_preview_refresh.configure(state=NORMAL)

    def print_script(self):

        bounds = self.main.get_coordinate.coord_r

        fname = self.main.get_name.file_name.get()
        exten = self.main.get_name.extension.get()[1:]
        temp_script = self.main.get_name.dir_name_script
        if os.path.exists(temp_script):
            os.remove(temp_script)
        with open((temp_script), "a", encoding="utf-8") as prev_script:

            get_layers = self.main.get_layers
            prev_script.write(f"gmt begin preview_{fname} {exten}\n")
            prev_script.write(f"\tgmt basemap {bounds} -JM20c  -Ba\n")
            for layer in get_layers.layers:
                match layer:
                    case "Coastal line":
                        script = get_layers.coast.script
                    case "Earth relief":
                        script = get_layers.grdimage.script
                    case "Contour line":
                        script = get_layers.contour.script
                    case "Earthquake plot":
                        script = get_layers.earthquake.script
                    case "Focal mechanism":
                        script = get_layers.focmec.script
                    case "Regional tectonics":
                        script = get_layers.tectonics.script
                    case "Map inset":
                        script = get_layers.inset.script
                    case "Legend":
                        script = get_layers.legend.script
                    case "Cosmetics":
                        script = get_layers.cosmetics.script
                    case _:
                        script = ""
                prev_script.write(f"\t{script}\n")
            prev_script.write(f"gmt end\n")

    def threading_process(self, worker, args, name, refresh=False):
        def thread_wrapper():
            try:
                worker(*args, self.preview_queue, refresh)
            except Exception as e:
                # Catch any unexpected errors in the worker itself and report via queue
                self.preview_queue.put(("COMPLETE", False, f"Worker thread error: {e}"))

        self.process_thread = threading.Thread(target=thread_wrapper, name=name)
        self.process_thread.daemon = False
        self.process_thread.start()

    def gmt_execute(self, script_name, output_dir, main_queue: queue.Queue, refresh):
        cwd = os.getcwd()
        os.chdir(output_dir)
        if os.name == "posix":
            os.system(f"chmod +x {script_name}")
        match os.name:
            case "nt":
                command = script_name
            case _:
                command = f"./{script_name}"

        try:
            print(f"Running '{output_dir}/{script_name}' with subprocess.Popen()...")
            # exit_code = os.system(f"{name}.bat")
            generate_map = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = generate_map.communicate()
            return_code = generate_map.returncode
            print(
                f"[{threading.current_thread().name}] Process finished with     code: {return_code}"
            )
            if return_code == 0:
                if refresh == False:
                    main_queue.put(
                        ("COMPLETE", True, "GMT script executed successfully.")
                    )
                else:
                    main_queue.put(
                        ("REFRESHED", True, "GMT script executed successfully.")
                    )

            else:
                main_queue.put(
                    (
                        "COMPLETE",
                        False,
                        f"GMT script failed. Code: {return_code}\nStderr: {stderr}",
                    )
                )
            if stdout:
                print("Process Stdout:\n", stdout)
            if stderr:
                print("Process Stderr:\n", stderr)

            # penerusnya apa
        except FileNotFoundError as e:
            main_queue.put(
                ("COMPLETE", False, f"Error: Program '{command}' not found. ({e})")
            )

        except Exception as e:
            main_queue.put(("COMPLETE", False, f"An unexpected error occurred: {e}"))
        finally:
            os.chdir(cwd)

    def _check_queue(self):
        try:
            message_type, *data = self.preview_queue.get_nowait()
            if message_type == "COMPLETE":
                success_status, message = data
                self.map_preview_on(success_status, message)  # Call GUI update
            elif message_type == "REFRESHED":
                self.refreshed()
            # elif message_type == "STATUS":  # For optional progress updates
            #     self.main.status_label.configure(
            #         text=f"Status: {data[0]}"
            # )  # Assuming you have a status_label
        except queue.Empty:
            pass  # No messages in queue

        self.main.after(100, self._check_queue)  # Reschedule itself

    def loading_image(self):
        image = Image.open(self.main.get_name.dir_prename_map)
        ratio = image.width / image.height
        new_width = int(700 + (ratio * 550))
        image_resize = image.resize((int((new_width - 710)), int(545)))
        self.imagetk = ImageTk.PhotoImage(image_resize)
        return new_width


class LayerParameters:

    def parameter_cpt(self, opti, row):
        from color_list import palette_name

        self.grdimg_cpt_color = StringVar(opti, value="geo")

        entry = ctk.CTkOptionMenu(
            opti,
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

        entry.grid(row=row, column=0, columnspan=3, sticky="ew")

    def parameter_shading(self, opti, row):
        """Variable created :
        self.grdimg_shading
        self.grdimg_shading_az"""
        self.grdimg_shading = ctk.StringVar(opti, "on")
        self.grdimg_shading_az = StringVar(opti, value="-45")
        entry = CTkEntry(
            opti,
            textvariable=self.grdimg_shading_az,
            justify="right",
        )
        check = CTkCheckBox(
            opti,
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            text="",
            variable=self.grdimg_shading,
            command=lambda: self.shading_azimuth_set(entry, label2, label3),
            onvalue="on",
            offvalue="off",
        )

        check.grid(row=row, column=0)

        label2 = CTkLabel(opti, text="Azimuth :", anchor="e")
        label3 = CTkLabel(opti, text=" º", anchor="w")
        entry.grid(row=row, column=3, sticky="ew")
        label2.grid(row=row, column=1, columnspan=2, sticky="nsew", padx=10)
        label3.grid(row=row, column=4, columnspan=1, sticky="nsew")

    def shading_azimuth_set(self, entry, label2, label3):
        if self.grdimg_shading.get() == "on":
            entry.configure(state=NORMAL, text_color="white")
            label2.configure(state=NORMAL)
            label3.configure(state=NORMAL)
        else:
            entry.configure(state=DISABLED, text_color="#565B5E")
            label2.configure(state=DISABLED)
            label3.configure(state=DISABLED)

    def parameter_masking(self, opti, row):
        self.grdimg_masking = ctk.StringVar(opti, value="off")

        check = CTkCheckBox(
            opti,
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            text="",
            variable=self.grdimg_masking,
            onvalue="on",
            offvalue="off",
        )
        check.grid(row=row, column=0, columnspan=1, sticky="ew")

    def parameter_date(self, frame, row, var, start=False):
        date = datetime.now()
        if start == True:
            date = datetime.now() - relativedelta(years=1)
        var = DateEntry(frame, date)
        var.grid(row=row, column=0, columnspan=5, sticky="ew")

    def parameter_magnitude_range(self, opti, row):
        self.magnitudes = DoubleVar(value=0), DoubleVar(value=10)
        range = CTkRangeSlider(
            opti,
            variables=self.magnitudes,
            from_=0,
            to=10,
            number_of_steps=100,
            button_length=5,
            height=10,
            button_color="dim gray",
        )
        range.grid(column=1, row=row, columnspan=3, padx=5)
        entry_mag_min = CTkEntry(opti, textvariable=self.magnitudes[0])
        entry_mag_max = CTkEntry(opti, width=50, textvariable=self.magnitudes[1])

        entry_mag_min.grid(column=0, row=row, sticky="ew", padx=5)
        entry_mag_max.grid(column=4, row=row, sticky="ew")
        label = CTkLabel(opti, text="M", anchor="w")
        label.grid(column=5, row=row, sticky="w", padx=3)

    def parameter_depth_range(self, opti, row):  # custom depth range coloring feature
        self.depths = ctk.IntVar(value=0), ctk.IntVar(value=1000)
        range = CTkRangeSlider(
            opti,
            variables=self.depths,
            from_=0,
            to=1000,
            number_of_steps=1000,
            button_length=5,
            height=10,
            button_color="dim gray",
        )
        range.grid(column=1, row=row, columnspan=3, padx=5)
        entry_dep_min = CTkEntry(opti, textvariable=self.depths[0])
        entry_dep_max = CTkEntry(opti, width=50, textvariable=self.depths[1])
        label = CTkLabel(opti, text="Km", anchor="w")
        label.grid(column=5, row=row, sticky="w", padx=3)

        entry_dep_min.grid(column=0, row=row, sticky="ew", padx=5)
        entry_dep_max.grid(column=4, row=row)

    def parameter_eq_size(self, opti, row):  # slider auto update the preview if open
        self.circle_size = ctk.DoubleVar(opti, 1)
        slider_size = ctk.CTkSlider(
            opti,
            variable=self.circle_size,
            from_=0,
            to=2,
            button_length=5,
            height=10,
            button_color="dim gray",
        )
        entry = CTkEntry(opti, textvariable=self.circle_size)
        entry.grid(column=4, row=row, columnspan=1)
        slider_size.grid(column=1, row=row, columnspan=3)

    def parameter_fm_size(self):
        pass

    def parameter_catalog_source(self, opti, row, focmec=None):
        catalog = ["USGS", "ISC", "GlobalCMT", "User supplied"]
        if focmec is True:
            cat = catalog[2:]
        else:
            cat = catalog[0:2] + catalog[3:]
        self.catalog = StringVar(value=cat[0])
        entry = ctk.CTkOptionMenu(
            opti,
            variable=self.catalog,
            values=cat,
            fg_color="#565B5E",
            button_color="#565B5E",
            button_hover_color="#7A848D",
        )
        CTkScrollableDropdown(
            entry,
            values=cat,
            command=lambda e: self.catalog.set(e),
            width=200,
            height=100,
            justify="left",
            resize=False,
            autocomplete=True,
        )
        entry.grid(column=0, row=row, columnspan=3, sticky="ew")

    # ctk.CTkSlider()
    def padding(self, text, opti, number):
        text_padding = CTkLabel(text, text="", fg_color="red")
        text_padding.grid(column=0, row=11 - number, rowspan=number, sticky="nswe")
        opti_padding = CTkLabel(opti, text="", fg_color="red")
        opti_padding.grid(column=0, row=11 - number, rowspan=number, sticky="nswe")


class GrdOptions:
    __res = [
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

    __grd_fullname = [
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

    __unit = {
        "@earth_relief_": "m",
        "@earth_synbath_": "m",
        "@earth_gebco_": "m",
        "@earth_age_": "Myr",
        "@earth_day_": "",
        "@earth_night": "",
        "@earth_mag_": "nTesla",
        "@earth_mag4km_": "nTesla",
        "@earth_wdmam_": "nTesla",
        "@earth_vgg_": "Eotvos",
        "@earth_faa_": "mGal",
        "@earth_faaerror_": "mGal",
    }

    __grd_codes = [
        "@earth_relief_",
        "@earth_synbath_",
        "@earth_gebco_",
        "@earth_age_",
        "@earth_day_",
        "@earth_night",
        "@earth_mag_",
        "@earth_mag4km_",
        "@earth_wdmam_",
        "@earth_vgg_",
        "@earth_faa_",
        "@earth_faaerror_",
    ]

    gmt_grd_dict = {
        __grd_fullname[0]: [__grd_codes[0]] + __res,
        __grd_fullname[1]: [__grd_codes[1]] + __res,
        __grd_fullname[2]: [__grd_codes[2]] + __res,
        __grd_fullname[3]: [__grd_codes[3]] + __res[4:],
        __grd_fullname[4]: [__grd_codes[4]] + __res[3:],
        __grd_fullname[5]: [__grd_codes[5]] + __res[3:],
        __grd_fullname[6]: [__grd_codes[6]] + __res[5:],
        __grd_fullname[7]: [__grd_codes[7]] + __res[5:],
        __grd_fullname[8]: [__grd_codes[8]] + __res[6:],
        __grd_fullname[9]: [__grd_codes[9]] + __res[4:],
        __grd_fullname[10]: [__grd_codes[10]] + __res[4:],
        __grd_fullname[11]: [__grd_codes[11]] + __res[4:],
    }
    gmt_ctr_dict = {
        __grd_fullname[0]: [__grd_codes[0]] + __res,
        __grd_fullname[1]: [__grd_codes[1]] + __res,
        __grd_fullname[2]: [__grd_codes[2]] + __res,
        __grd_fullname[3]: [__grd_codes[3]] + __res[4:],
        __grd_fullname[6]: [__grd_codes[6]] + __res[5:],
        __grd_fullname[7]: [__grd_codes[7]] + __res[5:],
        __grd_fullname[8]: [__grd_codes[8]] + __res[6:],
        __grd_fullname[9]: [__grd_codes[9]] + __res[4:],
        __grd_fullname[10]: [__grd_codes[10]] + __res[4:],
        __grd_fullname[11]: [__grd_codes[11]] + __res[4:],
    }

    def __init__(
        self,
        frame: CTkFrame,
        var_grd: StringVar,
        var_res: StringVar,
        row: int = 1,
        ctr=False,
    ):

        self.grd = var_grd
        self.grd.set("@earth_relief_")
        self.res = var_res
        self.dict = self.gmt_grd_dict
        if ctr == True:
            self.dict = self.gmt_ctr_dict
        self.parameter_grd_name(frame, row)
        self.parameter_grd_res(frame, row + 1)

    def parameter_grd_name(self, frame, row):

        self.grdimg_resource = StringVar(frame, value=next(iter(self.dict)))

        entry = ctk.CTkOptionMenu(
            frame,
            fg_color="#565B5E",
            button_color="#565B5E",
            button_hover_color="#7A848D",
            variable=self.grdimg_resource,
            dynamic_resizing=False,
        )
        CTkScrollableDropdown(
            entry,
            values=self.dict.keys(),
            command=lambda e: self.setvariable(frame, row, e),
            width=400,
            height=300,
            justify="left",
            resize=False,
        )

        entry.grid(row=row, column=0, columnspan=6, sticky="ew")

    def setvariable(self, opti, row, e):
        self.grdimg_resource.set(e)
        self.grd.set(self.dict[self.grdimg_resource.get()][0])
        self.parameter_grd_res(opti, row + 1)

    def parameter_grd_res(self, opti, row: int = 2):

        print(self.grdimg_resource.get())
        if self.res.get() not in self.dict[self.grdimg_resource.get()]:
            self.res.set(self.dict[self.grdimg_resource.get()][1])
        print(f"self.res = {self.res.get()}")

        entry = ctk.CTkOptionMenu(
            opti,
            variable=self.res,
            fg_color="#565B5E",
            button_color="#565B5E",
            button_hover_color="#7A848D",
            dynamic_resizing=False,
        )
        CTkScrollableDropdown(
            entry,
            values=self.dict[self.grdimg_resource.get()][1:],
            command=lambda e: self.res.set(e),
            width=100,
            height=300,
            justify="left",
            resize=False,
            autocomplete=True,
        )

        entry.grid(row=row, column=0, columnspan=3, sticky="ew")

    @property
    def unit(self):
        return self.__unit[self.grd.get()]


class ColorOptions:

    def button_color_chooser(self, master, row, col, var, widget):
        dark_picker_logo = Image.open("./image/dark_eyedropper.png")
        light_picker_logo = Image.open("./image/light_eyedropper.png")
        color_picker_logotk = CTkImage(
            dark_image=dark_picker_logo, light_image=light_picker_logo, size=(20, 20)
        )

        select_color = ctk.CTkButton(
            master,
            image=color_picker_logotk,
            text="",
            command=lambda: self.color_chooser(var, widget),
            width=30,
            hover_color="gray",
            fg_color="dim gray",
        )
        select_color.grid(row=row, column=col)
        CTkToolTip(select_color, "Color picker")

    def color_chooser(self, var: StringVar, widget):
        rgb_code = ""
        r, g, b = self.any_to_r_g_b(var.get())

        color_code = AskColor(initial_color=self.rgb_to_hex(r, g, b))

        hex_code = f"{color_code.get()}"
        print(hex_code)
        if hex_code == "None":
            return
        else:
            rgb_code = self.hex_to_rgb(hex_code)
            print(rgb_code)
            print(var)
            print("belom ketangkep")
            var.set(rgb_code)
            self.color_preview_updater(var, widget=widget)
            return rgb_code

    def gmt_color_table(self, frame, row, col):
        self.button_color_table = CTkButton(
            frame,
            text="Color Table",
            command=lambda: self.color_table(),
            width=20,
            hover_color="gray",
        )
        self.button_color_table.grid(row=row, column=col)

    def color_table(self):
        dir = Path(__file__).resolve().parent
        rgb_chart = os.path.join(dir, "image", "GMT_RGBchart.png")
        try:
            if sys.platform == "win32":
                # os.startfile is non-blocking on Windows
                os.startfile(rgb_chart)
            elif sys.platform == "darwin":  # macOS
                # subprocess.Popen is non-blocking
                subprocess.Popen(["open", rgb_chart])
            else:  # Linux and other Unix-like systems
                # subprocess.Popen is non-blocking
                subprocess.Popen(["xdg-open", rgb_chart])
        except (OSError, FileNotFoundError) as e:
            messagebox.showerror(
                "Error", f"Could not open file: {e}\nIs '{rgb_chart}' a valid path?"
            )
        except Exception as e:
            # Catch any other unexpected errors
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def label_color_preview(self, master, row, col, var):
        self.label_preview = CTkLabel(master, height=20, fg_color=var.get(), text="")
        self.label_preview.grid(column=col, row=row, sticky="ew", columnspan=1, padx=5)
        self.color_preview_updater(var, self.label_preview)
        return self.label_preview

    def color_preview_updater(self, var_color, widget):

        color_name = var_color.get()
        print("update")
        print(color_name)
        r, g, b = self.any_to_r_g_b(color_name)
        widget.configure(fg_color=self.rgb_to_hex(r, g, b))

    def any_to_r_g_b(self, color_name: str):
        from color_list import rgb_dict

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
        return red, green, blue

    def rgb_to_hex(self, r, g, b):
        """translates an rgb tuple of int to a tkinter friendly color code"""
        r = int(r)
        g = int(g)
        b = int(b)
        return f"#{r:02x}{g:02x}{b:02x}"

    def hex_to_rgb(self, hex_color):

        # Remove the '#' prefix if it exists
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]

        # Check if the hex code has the correct length (6 characters for RRGGBB)
        if len(hex_color) != 6:
            print(
                f"Error: Invalid hex color code length. Expected 6 characters,  got {len(hex_color)}."
            )
            return ""

        try:
            # Convert each 2-character hex pair to an integer
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            return f"{r}/{g}/{b}"
        except ValueError:
            # This error occurs if the hex_color string contains non-hex    characters
            print(f"Error: Invalid hexadecimal characters in '{hex_color}'.")
            return ""

    def parameter_color(
        self, frame: CTkFrame, row: int, var: StringVar, col_offset: int = 0
    ):

        entry = CTkEntry(frame, textvariable=var)
        entry.bind(
            "<FocusOut>",
            lambda event: self.color_preview_updater(var_color=var, widget=preview),
        )
        entry.bind(
            "<KeyRelease>",
            lambda event: self.color_preview_updater(var_color=var, widget=preview),
        )
        entry.bind(
            "<Return>",
            lambda event: self.color_preview_updater(var_color=var, widget=preview),
        )
        preview = self.label_color_preview(frame, row=row, col=3, var=var)
        self.button_color_chooser(frame, row=row, col=4, var=var, widget=preview)

        entry.grid(row=row, column=0, sticky="ew", columnspan=3, padx=5)

    def parameter_line_thickness(self, frame, row, var):
        # CTkSlider
        pens = ["0p", "0.25p", "0.50p", "0.75p", "1p", "1.5p", "2p", "3p"]

        entry = ctk.CTkComboBox(
            frame,
            variable=var,
            values=pens,
        )

        entry.grid(row=row, column=0, columnspan=3, padx=5, sticky="ew")


class Coast(ColorOptions):
    def __init__(self, tab, menu: LayerMenu):
        self.menu = menu
        text, opti = self.menu.tab_menu_layout_divider(tab)
        self.color_land = StringVar(tab, "lightgreen")
        self.color_sea = StringVar(tab, value="lightblue")
        self.line_color = StringVar(tab, "black")
        self.line_size = StringVar(tab, value="0.25p")
        labels = {
            "Land Color": "The color of dry area or island",
            "Sea Color": "The color of wet area like sea or lake",
            "Line color": "Line color of the coastal boundary",
            "Outline size": "Line thickness of the coastal boundary",
        }
        self.menu.parameter_labels(text, labels)

        self.parameter_color(opti, 1, self.color_land)
        self.parameter_color(opti, 2, self.color_sea)
        self.parameter_color(opti, 3, self.line_color)
        self.parameter_line_thickness(opti, 4, self.line_size)
        self.gmt_color_table(text, row=7, col=0)

    @property
    def script(self):
        sea = ""
        land = ""
        line = "-W0"

        if self.color_land.get() != "off":
            land = f"-G{self.color_land.get()}"

        if self.color_sea.get() != "off":
            sea = f"-S{self.color_sea.get()}"

        if self.line_color.get() != "off":
            line = f"-W{self.line_size.get()},{self.line_color.get()}"
        script = f"gmt coast {land} {sea} {line}"

        return script


class GrdImage(LayerParameters):
    def __init__(self, tab, menu):
        self.menu = menu
        labels = {
            "Grid data": "",
            "Grid resolution": "",
            "Color Palette Table": "",
            "Grid Shading": "",
            "Sea Masking": "",
        }
        text, opti = self.menu.tab_menu_layout_divider(tab)
        self.menu.parameter_labels(text, labels)
        self.grd = StringVar()
        self.res = StringVar()
        self.gmt_grd = GrdOptions(opti, self.grd, self.res)
        self.parameter_cpt(opti, 3)
        self.parameter_shading(opti, 4)
        self.parameter_masking(opti, 5)

    @staticmethod
    def abc(row: int, col: int):
        GrdImage.cde(row, col)

    @staticmethod
    def cde(row, col):
        print(row + col)

    @property
    def script(self):
        remote_data = f"{self.grd.get()}{self.res.get()}"
        shade = ""
        mask = ""
        if self.grdimg_shading.get() == "on":
            shade = f"-I+a{self.grdimg_shading_az.get()}+nt1+m0"
        if self.grdimg_masking.get() == "on":
            mask = "\ngmt coast -Slightblue"

        return f"gmt grdimage {remote_data} {shade} -C{self.grdimg_cpt_color.get()} {mask} "


class Contour(ColorOptions, LayerParameters):
    # Unable to obtain remote file no internet
    def __init__(self, main: MainApp, tab):
        self.main = main
        map_scale_factor = self.main.get_projection.map_scale_factor
        print(map_scale_factor)
        recomend = 100
        resolution = "15s"
        intervals = [
            (2778, 6.25, "01s"),
            (27775, 12.5, "03s"),
            (60000, 25, "15s"),
            (110000, 50, "30s"),
            (277750, 100, "30s"),
            (555500, 125, "30s"),
            (2777750, 250, "01m"),
            (float("inf"), 500, "02m"),
        ]
        self.prev_coord = set([r.get() for r in roi])
        for threshold, recomend, resolution in intervals:
            if map_scale_factor < threshold:
                break
        self.color = StringVar(tab, "gray20")
        self.thickness = StringVar(tab, "0.25p")

        self.interval = [
            StringVar(tab, value=str(recomend)),
            StringVar(tab, value=str(recomend * 4)),
        ]
        self.index = [
            BooleanVar(tab, value=True),  # toggle the index widget
            BooleanVar(tab, value=True),  # toggle thicker index
            BooleanVar(tab, value=True),  # toggle darker index
            BooleanVar(tab, value=False),  # toggle unit
        ]

        labels = {
            "Grid data": "",
            "Grid resolution": "",
            "Contour interval": "",
            "Color": "",
            "Thickness": "",
            "Index contour": "",
            # "Different Annotated Contour Line": "",
        }

        text, self.opti = self.main.get_layers.tab_menu_layout_divider(tab)
        self.main.get_layers.parameter_labels(text, labels)
        label = CTkLabel(text, text=" ")
        label.grid(row=7, column=0)
        self.grd = StringVar()
        self.res = StringVar(value=resolution)
        self.gmt_grd = GrdOptions(self.opti, self.grd, self.res, ctr=True)
        self.parameter_contour_interval()
        self.trace_handlers = []
        trace_id = self.grd.trace_add("write", self.recomend_interval)
        self.trace_handlers.append((self.grd, trace_id))

        # for var in roi:
        #     trace_id = var.trace_add("write", self.recomend_interval)
        #     self.trace_handlers.append((var, trace_id))

        self.after_id = None
        self.parameter_color(self.opti, 4, self.color)
        self.parameter_line_thickness(self.opti, 5, self.thickness)
        self.parameter_contour_index()
        self.contour_queue = queue.Queue()
        self.main.after(100, self._check_queue)

    def roi_changes_check(self):
        for r in roi:
            self.prev_coord.add(r.get())

        if len(self.prev_coord) != 4:
            self.prev_coord = set([r.get() for r in roi])
            self.recomend_interval()
            print("-" * 20)
            print("coordinate berubah")

    def _check_queue(self):
        try:
            status, recomendation = self.contour_queue.get_nowait()
            if status == "COMPLETE":
                print("calculating sucess")
                self.update_unit_and_interval(recomendation)
            elif status == "FAIL":
                print("calculating failed")
                self.update_unit_and_interval("", recomendation)

        except queue.Empty:
            pass

        self.main.after(100, self._check_queue)
        self.main.after(100, self.roi_changes_check)

    def remove_traces(self):
        print("Contour instance being destroyed, removing traces...")
        for var, trace_id in self.trace_handlers:
            try:
                var.trace_remove("write", trace_id)
                print("trace {trace_id} from {var} removed")
            except TclError as e:
                print(f"error removing trace {trace_id} from {var}: {e}")

    def estimate_interval(self, grd, res, coord):
        """check also, is there any data
        min max ada? atau nan nan

        buat script untuk check errornya dimana"""
        print("estimating contour interval")
        command = f"gmt grdinfo {grd}{res} {coord} -G -C -M"

        try:
            est_interval = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
            )
            stdout, stderr = est_interval.communicate()
            return_code = est_interval.returncode

            # debug
            print(" " * 20 + "stdout")
            print(stdout)
            print(" " * 20 + "stderr")
            print(stderr)
            grdinfo = stdout.split("\t")
            print(" " * 20 + "return code")
            print(return_code)

            if "Unable to obtain remote file" in stderr:
                message = f"Couldn't connect to GMT remote server for downloading {grd}{res} data.\nConnect to internet or change network connection."
                raise ConnectionError(message)
            min = grdinfo[5]
            max = grdinfo[6]
            if min.lower() == "nan" or max.lower() == "nan":

                raise ValueError(
                    f"No data {grd}{res} in this area..\nChoose another grid data or delete the Contour layer."
                )

            min = float(grdinfo[5])
            max = float(grdinfo[6])
            print(" " * 20 + "min")
            print(min)
            print(" " * 20 + "max")
            print(max)
            raw_interval = (max - min) / 40
            recomendation = self.round_value(raw_interval)
            if return_code == 0:
                self.contour_queue.put(("COMPLETE", recomendation))
            else:
                self.contour_queue.put(("FAIL", ""))

        except ValueError as e:
            self.contour_queue.put(("FAIL", e))
        except ConnectionError as e:
            self.contour_queue.put(("FAIL", e))
        except Exception as e:
            print("=" * 25)
            print("estimating contour interval error")
            print(e)
            self.contour_queue.put(("FAIL", ""))

    def recomend_interval(self, *_):
        self.interval[0].set("estimating..")
        self.entry_interval.configure(state=DISABLED, text_color="gray")
        if self.res.get() not in self.gmt_grd.dict[self.gmt_grd.grdimg_resource.get()]:
            self.res.set(self.gmt_grd.dict[self.gmt_grd.grdimg_resource.get()][1])
        self.prev_coord = set([r.get() for r in roi])
        calc_thread = threading.Thread(
            target=self.estimate_interval,
            args=[self.grd.get(), self.res.get(), self.main.get_coordinate.coord_r],
            name="est contour interval",
        )
        calc_thread.daemon = True
        calc_thread.start()

    def round_value(self, value):
        if not isinstance(value, (int, float)):
            print(f"Warning: Input '{value}' is not a number. Returning None.")
            return ""
        if 0 < value < 1:
            return f"{value:.2f}"
        elif 1 < value < 10:
            return str(round(value))
        elif 10 <= value <= 50:
            return str(round(value, 1))
        elif 50 < value <= 100:
            return str(round(value, -1))
        elif 100 < value <= 1000:
            return str(round(value, -2))
        elif value > 1000:
            return str(round(value, -3))
        else:
            return str(value)

    def update_unit_and_interval(self, rec: str, status: str = ""):
        self.label_unit.configure(text=self.gmt_grd.unit)
        self.unit_annot.configure(text=self.gmt_grd.unit)
        self.entry_interval.configure(state=NORMAL, text_color="green")
        if rec == "":
            messagebox.showerror("Error", status)
            self.entry_interval.configure(text_color="yellow")
            self.interval[0].set("0")
            self.interval[1].set("0")
            return
        self.interval[0].set(rec)
        self.interval[1].set(str(float(rec) * 4))
        self.index_options()

    def interval_manual_input(self):
        try:
            num = float(self.interval[0].get())
            self.interval[1].set(str(num * 4))
            self.index_options()
            self.entry_interval.configure(text_color="white")
        except ValueError:
            self.entry_interval.configure(text_color="red")
            self.index_options()

    def parameter_contour_interval(self):

        self.entry_interval = CTkEntry(
            self.opti,
            textvariable=self.interval[0],
        )

        self.entry_interval.bind(
            "<FocusOut>", lambda event: self.interval_manual_input()
        )
        self.entry_interval.bind(
            "<KeyRelease>", lambda event: self.interval_manual_input()
        )
        self.entry_interval.bind("<Return>", lambda event: self.interval_manual_input())

        self.label_unit = CTkLabel(self.opti, text=self.gmt_grd.unit)
        self.label_unit.grid(row=3, column=2, sticky="w", padx=[0, 5])
        self.entry_interval.grid(row=3, column=0, sticky="ew", columnspan=2, padx=5)
        self.index_options()

    def index_options(self):
        try:
            interval = float(self.interval[0].get())
            _ = 1 / interval
            contour_index_opt = [
                interval * 4,
                interval * 5,
                interval * 6,
            ]
        except (ValueError, ZeroDivisionError):
            contour_index_opt = []

        index_interval = ctk.CTkOptionMenu(
            self.opti,
            variable=self.interval[1],
            fg_color="#565B5E",
            button_color="#565B5E",
            button_hover_color="#7A848D",
            dynamic_resizing=False,
        )
        CTkScrollableDropdown(
            index_interval,
            values=contour_index_opt,
            command=lambda e: self.interval[1].set(e),
            width=130,
            height=120,
            justify="left",
            resize=False,
            autocomplete=True,
            scrollbar=False,
        )
        index_interval.grid(row=6, column=1, columnspan=2)

    def parameter_contour_index(self):

        index = CTkCheckBox(
            self.opti,
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            text="",
            variable=self.index[0],
            # command=lambda: self.shading_azimuth_set(entry, label2, label3),
            onvalue=True,
            offvalue=False,
        )
        self.unit_annot = CTkCheckBox(
            self.opti,
            text=self.gmt_grd.unit,
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            variable=self.index[3],
            # command=lambda: self.shading_azimuth_set(entry, label2, label3),
            onvalue=True,
            offvalue=False,
        )
        thicker = CTkCheckBox(
            self.opti,
            text=f"Thicker Index",
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            variable=self.index[1],
            # command=lambda: self.shading_azimuth_set(entry, label2, label3),
            onvalue=True,
            offvalue=False,
        )

        darker = CTkCheckBox(
            self.opti,
            text="Darker Index",
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            variable=self.index[2],
            # command=lambda: self.shading_azimuth_set(entry, label2, label3),
            onvalue=True,
            offvalue=False,
        )

        index.grid(row=6, column=0)
        self.unit_annot.grid(row=6, column=3, columnspan=3)
        thicker.grid(row=7, column=0, columnspan=3)

        darker.grid(row=7, column=3, columnspan=3)

    @property
    def script(self):
        remote_data = f"{self.grd.get()}{self.res.get()}"
        if self.index[1].get():
            thickness_index = f"{float(self.thickness.get()[:-1])*2}p"
        else:
            thickness_index = self.thickness.get()

        if self.index[2].get():
            r, g, b = self.any_to_r_g_b(self.color.get())

            color_index = f"{int(int(r)*0.8)}/{int(int(g)*0.8)}/{int(int(b)*0.8)}"
        else:
            color_index = self.color.get()

        if self.index[0].get():
            unit = ""
            if self.index[3].get():
                unit = f'+u" {self.gmt_grd.unit}"'
            interval = f"-A{self.interval[1].get()}+ap{unit} -C{self.interval[0].get()}"
            color = f"-Wa{thickness_index},{color_index} -Wc{self.thickness.get()},{self.color.get()}"
        else:
            interval = f"-C{self.interval[0].get()}"
            color = f"-Wc{self.thickness.get(),{self.color.get()}}"

        return f"gmt grdcontour {remote_data} {interval} {color} -LP "


class Earthquake(LayerMenu, LayerParameters):
    # tanggal awal
    # tanggal akhir
    # sumber katalog usgs, isc, user supplied
    # minmax magnitude rangeslider
    # minmax depth rangeslider
    def __init__(self, tab, main):
        self.main = main
        self.date_start = StringVar(tab, "lightgreen")
        self.date_end = StringVar(tab, value="lightblue")
        self.eq_catalog = StringVar(tab, value="USGS")
        self.mag_min = StringVar(tab, value="0")
        self.mag_max = StringVar(tab, value="10")
        self.dep_min = StringVar(tab, value="0")
        self.dep_max = StringVar(tab, value="1000")
        self.download_queue = queue.Queue()
        labels = {
            "Catalog": "",
            "Start date": "",
            "End date": "",
            "Magnitude": "",
            "Depth": "",
            "Size": "",
            # "Different Annotated Contour Line": "",
        }
        text, opti = self.tab_menu_layout_divider(tab)
        self.parameter_labels(text, labels)
        self.parameter_catalog_source(opti, 1)
        self.parameter_date(opti, 2, self.date_start, True)
        self.parameter_date(opti, 3, self.date_end)
        self.parameter_magnitude_range(opti, 4)
        self.parameter_depth_range(opti, 5)
        self.parameter_eq_size(opti, 6)
        self.button_downloader(tab)
        self.button_show_catalog(tab)
        self.main.after(100, self._check_queue)

    def _check_queue(self):
        try:
            message_type, *data = self.download_queue.get_nowait()
            if message_type == "COMPLETE":
                success_status, message = data
                self.download_button.configure(state=NORMAL)

        except queue.Empty:
            pass

        self.main.after(100, self._check_queue)

    def button_downloader(self, tab):
        self.download_button = CTkButton(
            tab,
            text="Download",
            width=60,
            hover_color="gray",
            fg_color="dim gray",
            command=lambda: self.download_catalog(),
        )
        self.download_button.place(relx=0.4, rely=0.87)

    def button_show_catalog(self, tab):
        button = CTkButton(
            tab,
            text="Catalog Preview",
            width=50,
            hover_color="gray",
            fg_color="dim gray",
        )

        button.place(relx=0.57, rely=0.87)

    def download_catalog(self):
        print("download start")
        self.download_button.configure(state=DISABLED)
        server = {
            "GlobalCMT": gcmt_downloader,
            "ISC": isc_downloader,
            "USGS": usgs_downloader,
        }
        args = (
            self.main.get_name.file_name.get(),
            self.main.get_name.output_dir.get(),
            self.main.get_coordinate.coord,
            [self.date_start, self.date_end],
            [self.mag_min, self.mag_max],
            [self.dep_min, self.dep_max],
        )
        self.threading_download(
            server[self.catalog.get()], args, f"DL catalog {self.catalog.get()}"
        )

    def threading_download(self, worker, args, name):
        def thread_wrapper():
            try:
                worker(*args, self.download_queue)
            except Exception as e:
                self.download_queue.put(
                    ("COMPLETE", False, f"Worker thread error: {e}")
                )

        self.download_thread = threading.Thread(target=thread_wrapper, name=name)
        self.download_thread.daemon = False
        self.download_thread.start()

    @property
    def script(self):
        pass


class Focmec(LayerParameters):
    # tanggal awal
    # tanggal akhir
    # sumber katalog gcmt, user supplied
    # minmax magnitude
    # minmax depth
    def __init__(self, tab):
        self.a = tab

    @property
    def script(self):
        pass


class Tectonic(LayerParameters):
    # source
    # ketebalan garis
    # warna garis
    def __init__(self, tab):
        self.a = tab

    @property
    def script(self):
        pass


class Inset(LayerParameters):
    # lokasi
    def __init__(self, tab):
        self.a = tab

    @property
    def script(self):
        pass


class Legend(LayerParameters):
    def __init__(self, tab):

        self.legend_eq = ctk.BooleanVar()
        self.legend_fm = ctk.BooleanVar()
        self.legend_date = ctk.BooleanVar()
        self.legend_colorbar_elev = ctk.BooleanVar()
        self.legend_colorbar_eq = ctk.BooleanVar()
        self.legend_eq_loc = StringVar()

    # lokasi
    # radio button info apa aja yg masuk
    @property
    def script(self):
        pass


class Cosmetics(LayerParameters):
    """
    Title
    Subtitle
    north arrow
    scalebar
    custom text
    inset map
    auto legend"""

    def __init__(self, tab):
        self.north_arrow = StringVar(tab)
        self.scalebar = StringVar(tab)

    @property
    def script(self):
        pass


if __name__ == "__main__":
    app = MainApp()
