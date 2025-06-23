import customtkinter as ctk
import os, threading, subprocess
from customtkinter import (
    StringVar,
    DoubleVar,
    CTkButton,
    CTkLabel,
    CTkEntry,
    CTkFrame,
    CTkImage,
    CTkCheckBox,
    CTkOptionMenu,
    filedialog,
)
import ctypes
from tkinter import messagebox, Canvas
from _date_delay_entry import DateEntry

# from CTkListbox import CTkListbox
from PIL import Image, ImageTk
from time import sleep
from datetime import datetime
from dateutil.relativedelta import relativedelta

# from tkcalendar import DateEntry
# from utils import *
from ctk_tooltip import CTkToolTip
from ctk_coordinate_gui import CoordWindow
from ctk_scrollable_dropdown import CTkScrollableDropdown
from CTkColorPicker import *
from ctk_rangeslider import CTkRangeSlider

if os.name == "nt":
    scalefactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    print(scalefactor)
    ctk.set_widget_scaling(1 / scalefactor)
    ctk.set_window_scaling(1 / scalefactor)


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
        self.geometry("700x550")
        self.minsize(700, 550)
        resize_image("map_simple_0.png")
        resize_image("map_relief_0.jpg")

        self.frame_map_param = CTkFrame(self, width=210, height=550)
        self.frame_layers = CTkFrame(self, width=490, height=550)
        self.frame_map_param.place(x=0, y=0, relwidth=0.3, relheight=1)
        self.frame_layers.place(relx=0.3, y=0, relwidth=0.7, relheight=1)
        self.get_name = MapFileName(self, self.frame_map_param)
        self.get_coordinate = MapCoordinate(self, self.frame_map_param)
        self.get_projection = MapProjection(self, self.frame_map_param)
        self.get_layers = LayerMenu(self, self.frame_layers)

        button = CTkButton(
            self.frame_map_param, text="scale", command=lambda: self.scalling()
        )
        button.place(relx=0, rely=0.95)
        self.orig = True
        self.mainloop()

    def scalling(self):
        if self.orig == False:
            ctk.set_widget_scaling(1 / scalefactor)
            ctk.set_window_scaling(1 / scalefactor)
            self.orig = True
        else:
            ctk.set_widget_scaling(1)
            ctk.set_window_scaling(1)
            self.orig = False


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

        # self.output_dir = StringVar(self, value=os.path.expanduser("~"))
        self.output_dir = StringVar(self, value="D:/guii")
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
        return f"-R{roi[0].get()}/{roi[1].get()}/{roi[2].get()}/{roi[3].get()}"

    def update_coor_entry(self):
        self.coord_button.configure(state="disabled")
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
        self.coord_button.configure(state="normal")


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
        scale_entry.grid(row=row, column=2, columnspan=1, pady=5)
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

        self.layers = {}
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

    def generate_temporary_map(self):
        pass

    def delete_tab(self):
        active_tab = self.layer_control.get()
        deleting_layer = messagebox.askyesno(
            message=f"Delete layer: '{active_tab}' ?",
            title="Deleting layer..",
        )
        if active_tab in self.layers and deleting_layer == True:
            self.layers.pop(active_tab)
            self.layer_control.delete(active_tab)

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
            case "Cosmetics":
                self.cosmetics = Cosmetics(new_layer)


class MapPreview:
    def __init__(self, main: MainApp, button_frame: CTkFrame):

        self.main = main
        self.preview_status = "off"
        self.button_ = button_frame
        self.map_preview_buttons()

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
            self.print_script()
            # self.start_long_process()
            self.threading_process(
                self.gmt_execute,
                args=[
                    self.main.get_name.file_name.get(),
                    self.main.get_name.output_dir.get(),
                ],
                name="generate Preview Map",
            )

            self.preview_status = "on"
        else:
            self.map_preview_off()
            self.preview_status = "off"
            self.button_preview_refresh.pack_forget()

    def map_preview_refresh(self):
        self.map_preview_off()
        self.print_script()
        self.threading_process(
            self.gmt_execute,
            args=[
                self.main.get_name.file_name.get(),
                self.main.get_name.output_dir.get(),
            ],
            name="refresh Preview Map",
        )

    def map_preview_on(self):
        cur_x = self.main.winfo_x()
        cur_y = self.main.winfo_y()
        print("sebelum loading gambar")
        image = Image.open(self.main.get_name.dir_prename_map)

        print("setelah loading gambar")
        ratio = image.width / image.height

        new_width = int(700 + (ratio * 550))
        image_resize = image.resize((int((new_width - 710)), int(545)))

        resize = f"{new_width}x550+{cur_x}+{cur_y}"

        self.imagetk = ImageTk.PhotoImage(image_resize)
        self.main.geometry(resize)

        self.main.frame_map_param.pack(side="left")
        self.main.frame_layers.pack(side="left")

        print(f"rel frame layer width= {210/new_width}")
        self.frame_preview = CTkFrame(self.main, height=550, width=new_width - 700)

        self.frame_preview.pack(side="left", fill="both", anchor="nw")
        self.expand_window(self.imagetk)

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
            for layer, script in get_layers.layers.items():
                match layer:
                    case "Coastal line":
                        script = get_layers.coast.script
                    case "Earth relief":
                        script = get_layers.grdimage.script
                    case "Contour line":
                        script = get_layers.contour.script.script
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
                prev_script.write(f"\t{script}\n")
            prev_script.write(f"gmt end\n")

    def run_external_process(self, program, args, callback):
        """
        Function to be run in a separate thread.
        It executes the external program and then calls a callback with the result.
        """
        try:
            print(f"[{threading.current_thread().name}] Starting external process...")
            # Use platform-specific command
            if sys.platform.startswith("linux") or sys.platform == "darwin":
                cmd = [program] + args
            elif sys.platform == "win32":
                cmd = [
                    "cmd",
                    "/c",
                    program,
                ] + args  # Use cmd /c for Windows to run common commands
            else:
                print("Unsupported OS.")
                callback("Error: Unsupported OS", None)
                return

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            # This 'wait' happens in the new thread, NOT the main Tkinter thread
            stdout, stderr = process.communicate()
            return_code = process.returncode
            print(
                f"[{threading.current_thread().name}] Process finished with code: {return_code}"
            )
            callback(stdout, stderr, return_code)  # Call the main thread via callback
        except FileNotFoundError:
            print(
                f"[{threading.current_thread().name}] Error: Program '{program}' not found."
            )
            callback(None, f"Error: Program '{program}' not found.", -1)
        except Exception as e:
            print(f"[{threading.current_thread().name}] An error occurred: {e}")
            callback(None, f"An error occurred: {e}", -1)

    def threading_process(self, worker, args, name):
        self.process_thread = threading.Thread(target=worker, args=args, name=name)
        self.process_thread.daemon = True
        self.process_thread.start()

    def start_long_process(self):
        print("Process started (running in background)...")
        self.button_preview.configure(
            state="disabled"
        )  # Disable button to prevent multiple clicks
        self.button_preview_refresh.configure(
            state="disabled"
        )  # Disable button to prevent multiple clicks

        # Define the command and arguments based on OS
        if sys.platform.startswith("linux") or sys.platform == "darwin":
            program = "sleep"
            args = ["10"]  # Sleeps for 5 seconds
        elif sys.platform == "win32":
            program = "timeout"
            args = ["/t", "10", "/nobreak"]  # Sleeps for 5 seconds (cmd.exe specific)
        else:
            print("Unsupported OS for this example.")
            return

        # Create and start a new thread
        self.process_thread = threading.Thread(
            target=self.run_external_process,
            args=(program, args, self.on_process_complete),
            name="ExternalProcessThread",  # Give it a name for easier debugging
        )
        self.process_thread.daemon = (
            True  # Allow main program to exit even if thread is running
        )
        self.process_thread.start()

    def on_process_complete(self, stdout, stderr, return_code):
        """
        This method is called from the worker thread.
        It updates the GUI (which MUST be done in the main thread).
        """
        if return_code is not None:
            if return_code == 0:
                message = "Process finished successfully!"
                print(message)
            else:
                message = f"Process finished with error (code {return_code})."
                print(message)

            if stdout:
                print("Process Stdout:\n", stdout)
            if stderr:
                print("Process Stderr:\n", stderr)

        else:
            print("Process encountered an error.")

        self.button_preview.configure(state=tk.NORMAL)  # Re-enable the button
        self.button_preview_refresh.configure(state=tk.NORMAL)  # Re-enable the button

    def gmt_execute(self, script_name, output_dir):
        cwd = os.getcwd()
        os.chdir(output_dir)
        match os.name:
            case "nt":
                command = f"{script_name}.bat"
            case _:
                os.system(f"chmod +x {output_dir}/{script_name}.gmt")
                command = f"./{script_name}.gmt"

        try:
            print(
                f"Running '{output_dir}/{script_name}.bat' with subprocess.   Popen()..."
            )
            # exit_code = os.system(f"{name}.bat")
            generate_map = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = generate_map.communicate()
            return_code = generate_map.returncode
            print(
                f"[{threading.current_thread().name}] Process finished with     code: {return_code}"
            )
            if return_code is not None:
                if return_code == 0:
                    print(return_code)
                    self.map_preview_on()
                    print("done map preview")
                    self.button_preview_refresh.pack(side="left", padx=(5, 5))

            if stdout:
                print("Process Stdout:\n", stdout)
            if stderr:
                print("Process Stderr:\n", stderr)

            # penerusnya apa
        except FileNotFoundError:
            print(
                f"[{threading.current_thread().name}] Error: Program '{command} ' not found."
            )

        except Exception as e:
            f"[{threading.current_thread().name}] An error occurred: {e}"
        os.chdir(cwd)

    def expand_window(self, image):

        self.canvas = Canvas(self.frame_preview, width=1100, height=550)
        self.canvas.pack(expand=True, fill="both")
        # self.canvas.image = image
        self.canvas.create_image(5, 0, image=image, anchor="nw")

        self.canvas.create_text(1, 550, text="askldfjsaldkf", anchor="sw")

        print(f"winfo {self.canvas.winfo_width()} {self.canvas.winfo_height()}")


class LayerParameters:
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

    __grd_data = [
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
        __grd_data[0]: [__grd_codes[0]] + __res,
        __grd_data[1]: [__grd_codes[1]] + __res,
        __grd_data[2]: [__grd_codes[2]] + __res,
        __grd_data[3]: [__grd_codes[3]] + __res[4:],
        __grd_data[4]: [__grd_codes[4]] + __res[3:],
        __grd_data[5]: [__grd_codes[5]] + __res[3:],
        __grd_data[6]: [__grd_codes[6]] + __res[5:],
        __grd_data[7]: [__grd_codes[7]] + __res[5:],
        __grd_data[8]: [__grd_codes[8]] + __res[6:],
        __grd_data[9]: [__grd_codes[9]] + __res[4:],
        __grd_data[10]: [__grd_codes[10]] + __res[4:],
        __grd_data[11]: [__grd_codes[11]] + __res[4:],
    }

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
        r, g, b = self.any_to_r_g_b(var.get())

        color_code = AskColor(initial_color=self.rgb_to_hex(r, g, b))
        # print(type(color_code))
        # print(color_code)

        # print("")
        # print(f"hex code : {color_code.get()}")
        # print(type(color_code.get()))
        # print("")
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

    def gmt_color_table(self, master, row, col, var):
        self.button_color_table = CTkButton(
            master,
            text="Color Table",
            command=lambda: self.color_table(var),
            width=20,
            hover_color="gray",
        )
        self.button_color_table.grid(row=row, column=col)

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

    # def hex_to_rgb(self, hex_color):
    #     r = int(hex_color[1:3], 16)
    #     g = int(hex_color[3:5], 16)
    #     b = int(hex_color[5:7], 16)

    #     return f"{r}/{g}/{b}"
    def hex_to_rgb(self, hex_color):

        # Remove the '#' prefix if it exists
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]

        # Check if the hex code has the correct length (6 characters for RRGGBB)
        if len(hex_color) != 6:
            print(
                f"Error: Invalid hex color code length. Expected 6 characters,  got {len(hex_color)}."
            )
            return None

        try:
            # Convert each 2-character hex pair to an integer
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            return f"{r}/{g}/{b}"
        except ValueError:
            # This error occurs if the hex_color string contains non-hex    characters
            print(f"Error: Invalid hexadecimal characters in '{hex_color}'.")
            return None

    def parameter_color(self, frame: CTkFrame, row: int, var: StringVar):

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

    def parameter_2dgridimage(self, frame, row):

        self.grdimg_resource = StringVar(frame, value=next(iter(self.gmt_grd_dict)))

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
            values=self.gmt_grd_dict.keys(),
            command=lambda e: self.setvariable(frame, e),
            width=400,
            height=300,
            justify="left",
            resize=False,
        )

        entry.grid(row=row, column=0, columnspan=6, sticky="ew")

    def setvariable(self, opti, a):
        self.grdimg_resource.set(a)
        self.parameter_grd_res(opti, 2)

    def parameter_grd_res(self, opti, row):

        print(self.grdimg_resource.get())
        self.grdimg_resolution = StringVar(
            opti, value=self.gmt_grd_dict[self.grdimg_resource.get()][3]
        )

        entry = ctk.CTkOptionMenu(
            opti,
            variable=self.grdimg_resolution,
            fg_color="#565B5E",
            button_color="#565B5E",
            button_hover_color="#7A848D",
            dynamic_resizing=False,
        )
        CTkScrollableDropdown(
            entry,
            values=self.gmt_grd_dict[self.grdimg_resource.get()][1:],
            command=lambda e: self.grdimg_resolution.set(e),
            width=100,
            height=300,
            justify="left",
            resize=False,
            autocomplete=True,
        )

        entry.grid(row=row, column=0, columnspan=3, sticky="ew")

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
            entry.configure(state="normal", text_color="white")
            label2.configure(state="normal")
            label3.configure(state="normal")
        else:
            entry.configure(state="disabled", text_color="#565B5E")
            label2.configure(state="disabled")
            label3.configure(state="disabled")

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


class Coast(LayerParameters):
    def __init__(self, tab):

        text, opti = self.tab_menu_layout_divider(tab)
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
        self.parameter_labels(text, labels)

        self.parameter_color(opti, 1, self.color_land)
        self.parameter_color(opti, 2, self.color_sea)
        self.parameter_color(opti, 3, self.line_color)
        self.parameter_line_thickness(opti, 4, self.line_size)

        # print(self.script.get())

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


class GridImage(LayerParameters):
    def __init__(self, tab):

        labels = {
            "Grid data": "",
            "Grid resolution": "",
            "Color Palette Table": "",
            "Grid Shading": "",
            "Sea Masking": "",
        }
        text, opti = self.tab_menu_layout_divider(tab)
        self.parameter_labels(text, labels)
        self.parameter_2dgridimage(opti, 1)
        self.parameter_grd_res(opti, 2)
        self.parameter_cpt(opti, 3)
        self.parameter_shading(opti, 4)
        self.parameter_masking(opti, 5)

    @property
    def script(self):
        remote_data = f"{self.gmt_grd_dict[self.grdimg_resource.get()][0]}{self.grdimg_resolution.get()}"
        shade = ""
        mask = ""
        if self.grdimg_shading.get() == "on":
            shade = f"-I+a{self.grdimg_shading_az.get()}+nt1+m0"
        if self.grdimg_masking.get() == "on":
            mask = "\ngmt coast -Slightblue"

        return f"gmt grdimage {remote_data} {shade} -C{self.grdimg_cpt_color.get()} {mask} "


class Contour(LayerParameters):
    def __init__(self, tab):
        # interval
        # resolution
        # warna index biasa
        # ketebalan kontur index biasa
        self.color_minor = StringVar(tab, "lightgreen")
        self.color_major = StringVar(tab, value="lightblue")
        self.line_major = StringVar(tab, value="0.25p")
        self.line_minor = StringVar(tab, value="0.25p")

        labels = {
            "Grid data": "",
            "Grid resolution": "",
            "Contour Interval": "",
            "Annotation interval": "",
            "Contour Color": "",
            "Contour Thickness": "",
            # "Different Annotated Contour Line": "",
        }
        text, opti = self.tab_menu_layout_divider(tab)
        self.parameter_labels(text, labels)
        self.parameter_2dgridimage(opti, 1)
        self.parameter_grd_res(opti, 2)
        self.parameter_color(opti, 3, self.color_major)
        self.parameter_line_thickness(opti, 4, self.line_major)
        self.parameter_color(opti, 5, self.color_minor)
        self.parameter_line_thickness(opti, 6, self.line_minor)

        self.script = StringVar()
        self.script.set(self.call_script())
        # print(self.script.get())

    def call_script(self):
        script = f"gmt contour -G{self.color_land.get()} -S{self.color_sea.get()} -W{self.line_size.get()},{self.line_color.get()}"
        self.script.set(script)

        return script


class Earthquake(LayerParameters):
    # tanggal awal
    # tanggal akhir
    # sumber katalog usgs, isc, user supplied
    # minmax magnitude rangeslider
    # minmax depth rangeslider
    def __init__(self, tab):
        self.date_start = StringVar(tab, "lightgreen")
        self.date_end = StringVar(tab, value="lightblue")
        self.eq_catalog = StringVar(tab, value="USGS")
        self.mag_min = StringVar(tab, value="0")
        self.mag_max = StringVar(tab, value="10")
        self.dep_min = StringVar(tab, value="0")
        self.dep_max = StringVar(tab, value="1000")

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
        self.button_download(tab)
        self.button_show_catalog(tab)

    def button_download(self, tab):
        button = CTkButton(
            tab,
            text="Download",
            width=60,
            hover_color="gray",
            fg_color="dim gray",
        )
        button.place(relx=0.4, rely=0.87)

    def button_show_catalog(self, tab):
        button = CTkButton(
            tab,
            text="Catalog Preview",
            width=50,
            hover_color="gray",
            fg_color="dim gray",
        )

        button.place(relx=0.57, rely=0.87)


class Focmec(LayerParameters):
    # tanggal awal
    # tanggal akhir
    # sumber katalog gcmt, user supplied
    # minmax magnitude
    # minmax depth
    pass


class Tectonic(LayerParameters):
    # source
    # ketebalan garis
    # warna garis
    pass


class Inset(LayerParameters):
    # lokasi

    pass


class Legend(LayerParameters):
    def __init__(self):
        self.legend_eq = ctk.BooleanVar()
        self.legend_fm = ctk.BooleanVar()
        self.legend_date = ctk.BooleanVar()
        self.legend_colorbar_elev = ctk.BooleanVar()
        self.legend_colorbar_eq = ctk.BooleanVar()
        self.legend_eq_loc = StringVar()

    # lokasi
    # radio button info apa aja yg masuk
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


if __name__ == "__main__":
    app = MainApp()
"""
buat programnya menghasilkan peta
penambahan layer dan fitur nanti dulu
"""
