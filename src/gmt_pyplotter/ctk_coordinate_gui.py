import os
import math
import psutil, json
import warnings
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
from tkinter import TclError
from pathlib import Path


# if using conda on ubuntu, there is bug in tkinter for rendering the corner and font
# fix with installing tkinter build with truetype support, by running this in terminal:
# conda install "tk[build=xft_*]"

ctk.set_appearance_mode("dark")
Image.MAX_IMAGE_PIXELS = 1000000000
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

b1_motion = "<B1-Motion>"
b1_release = "<ButtonRelease-1>"
focusout = "<FocusOut>"
return_ = "<Return>"
grid_anot = "grid anot"
msg_invalid_coord = "invalid coordinate value"
not_coord = "coordinate not inputed yet"
script_dir = Path(__file__).resolve().parent
autosave = os.path.join(script_dir, "saved_param.json")


class AutoScrollbar(ctk.CTkScrollbar):
    """A scrollbar that hides itself if it's not needed. Works only for grid geometry manager"""

    def set_(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ctk.CTkScrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError("Cannot use pack with the widget " + self.__class__.__name__)

    def place(self, **kw):
        raise tk.TclError("Cannot use place with the widget " + self.__class__.__name__)


class GlobeMap:
    """Display and zoom image"""

    def __init__(self, placeholder, given_coords: list[float]):
        """Initialize the ImageFrame"""
        global earth_relief
        # Scale for the canvas image zoom, public for outer classes
        self.imscale = 1.0
        self.__delta = 1.3  # Zoom magnitude
        self.__previous_state = 0  # Previous state of the keyboard
        self.grid_color = "grey10"
        earth_relief = tk.StringVar(value="on")
        # Create ImageFrame in placeholder widget
        self._imframe = ctk.CTkFrame(placeholder)

        self.__initialize_scrollbars()
        self.__initialize_canvas()
        self.__bind_canvas_events()
        self.__create_image_pyramid()
        self.__initialize_image_container()
        last_view_position = self.load_state()
        self.__show_image("init")
        self.__create_coord_info()

        self.canvas.xview_moveto(last_view_position[0])
        self.canvas.yview_moveto(last_view_position[1])

        self.get_coordinate = CoordinateWidget(self, given_coords)
        self.canvas.focus_set()

    def save_state(self):
        try:
            with open(autosave, "r") as f:
                state = json.load(f)

            state["earth_relief"] = earth_relief.get()
            state["grid_color"] = self.grid_color
            state["imscale"] = self.imscale
            state["xview"] = self.canvas.xview()
            state["yview"] = self.canvas.yview()
            state["__curr_img"] = self.__curr_img
            state["__scale"] = self.__scale
            state["container_coords"] = self.container
            state["hbar"] = self.hbar.get()
            state["vbar"] = self.vbar.get()

            with open(autosave, "w") as f:
                json.dump(state, f, indent=4)
        except FileNotFoundError:
            print(f"Error: The file {autosave} was not found.")
        except json.JSONDecodeError:
            print(f"Error: The file {autosave} is not a valid JSON file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def load_state(self):
        try:
            with open(autosave, "r") as f:
                state = json.load(f)
                earth_relief.set(state["earth_relief"])
                self.grid_color = state["grid_color"]
                self.imscale = state["imscale"]
                self.__curr_img = state["__curr_img"]
                self.__scale = state["__scale"]
                self.canvas.scale("all", 0, 0, self.imscale, self.imscale)
                self.container = state["container_coords"]
                self.canvas.xview_moveto(state["xview"][0])
                self.canvas.yview_moveto(state["yview"][0])
                return state["xview"][0], state["yview"][0]
        except FileNotFoundError:
            print("No previous state found")
            return 0.5, 0.5

    def __initialize_canvas(self):
        """Initialize and configure the canvas"""
        self.canvas = tk.Canvas(
            self._imframe,
            background="gray20",
            highlightthickness=0,
            xscrollcommand=self.hbar.set,
            yscrollcommand=self.vbar.set,
        )
        self.canvas.grid(row=0, column=0, sticky="nswe")
        self.canvas.update()

    def __initialize_scrollbars(self):
        """Initialize and configure scrollbars"""
        self.hbar = AutoScrollbar(self._imframe, orientation="horizontal")
        self.vbar = AutoScrollbar(self._imframe, orientation="vertical")
        self.hbar.grid(row=1, column=0, sticky="we")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.hbar.configure(command=self.__scroll_x)
        self.vbar.configure(command=self.__scroll_y)

    def __bind_canvas_events(self):
        """Bind events to the canvas"""
        self.canvas.bind("<Configure>", lambda event: self.__show_image("configure"))
        self.canvas.bind("<Motion>", self.update_mouse_coord)
        self.canvas.bind(b1_motion, self.update_mouse_coord, add="+")

        self.canvas.bind("<ButtonPress-2>", self.__move_from)
        self.canvas.bind("<B2-Motion>", self.__move_to)
        self.canvas.bind("<ButtonPress-3>", self.__move_from)
        self.canvas.bind("<B3-Motion>", self.__move_to)
        self.canvas.bind("<MouseWheel>", self.__wheel)
        self.canvas.bind("<Button-5>", self.__wheel)
        self.canvas.bind("<Button-4>", self.__wheel)
        self.canvas.bind(
            "<Key>", lambda event: self.canvas.after_idle(self.__keystroke, event)
        )

    def __create_image_pyramid(self):
        """Create image pyramid"""
        # Suppress DecompressionBombError for large images
        image_folder = "image"
        # Check Performance for the largest image
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        avail_memory = memory_info.available / 1073741824
        p = 0 if cpu_usage < 50 and avail_memory > 4 else 1
        path = os.path.dirname(os.path.abspath(__file__))
        path_simple = os.path.join(path, image_folder, f"map_simple_{p}.png")
        path_relief = os.path.join(path, image_folder, f"map_relief_{p}.jpg")
        self._pyramid_simple = [Image.open(path_simple)]
        self._pyramid_relief = [Image.open(path_relief)]
        self.imwidth, self.imheight = self._pyramid_simple[0].size
        self.__min_side = min(self.imwidth, self.imheight)
        self.__ratio = 1.0
        self.__curr_img = 0
        self.__scale = self.imscale * self.__ratio

        for i in range(1 + p, 5 + p):
            self._pyramid_simple.append(
                Image.open(
                    os.path.join(
                        path,
                        image_folder,
                        f"map_simple_{i}.png",
                    )
                )
            )
            self._pyramid_relief.append(
                Image.open(
                    os.path.join(
                        path,
                        image_folder,
                        f"map_relief_{i}.jpg",
                    )
                )
            )

    def __initialize_image_container(self):
        """Initialize the image container"""
        self.canvas.create_rectangle((0, 0, self.imwidth, self.imheight), width=0)
        self.container = self.canvas.create_rectangle(
            (0, 0, self.imwidth, self.imheight), width=0
        )

    def grid(self, **kw):
        """Put CanvasImage widget on the parent widget"""
        self._imframe.grid(**kw)  # place CanvasImage widget on the grid
        self._imframe.grid(sticky="nswe")  # make frame container sticky
        self._imframe.rowconfigure(0, weight=1)  # make canvas expandable
        self._imframe.columnconfigure(0, weight=1)

    def pack(self, **kw):
        """Exception: cannot use pack with this widget"""
        raise TclError("Cannot use pack with the widget " + self.__class__.__name__)

    def place(self, **kw):
        """Exception: cannot use place with this widget"""
        raise TclError("Cannot use place with the widget " + self.__class__.__name__)

    # noinspection PyUnusedLocal
    def __scroll_x(self, *args, **kwargs):
        """Scroll canvas horizontally and redraw the image"""
        self.canvas.xview(*args)  # scroll horizontally
        self.__show_image("scroll x")  # redraw the image

    # noinspection PyUnusedLocal
    def __scroll_y(self, *args, **kwargs):
        """Scroll canvas vertically and redraw the image"""
        self.canvas.yview(*args)  # scroll vertically
        self.__show_image("scroll y")  # redraw the image

    def __show_image(self, job=None):
        """Show image on the Canvas. Implements correct image zoom almost like in Google Maps"""
        if earth_relief.get() == "on":
            self._pyramid = self._pyramid_relief
        elif earth_relief.get() == "off":
            self._pyramid = self._pyramid_simple

        box_image = self.canvas.coords(self.container)  # get image area
        box_canvas = (
            self.canvas.canvasx(0),  # get visible area of the canvas
            self.canvas.canvasy(0),
            self.canvas.canvasx(self.canvas.winfo_width()),
            self.canvas.canvasy(self.canvas.winfo_height()),
        )
        box_img_int = tuple(
            map(int, box_image)
        )  # convert to integer or it will not work properly
        # Get scroll region box
        box_scroll = [
            min(box_img_int[0], box_canvas[0]),
            min(box_img_int[1], box_canvas[1]),
            max(box_img_int[2], box_canvas[2]),
            max(box_img_int[3], box_canvas[3]),
        ]
        # Horizontal part of the image is in the visible area
        if box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0] = box_img_int[0]
            box_scroll[2] = box_img_int[2]
        # Vertical part of the image is in the visible area
        if box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1] = box_img_int[1]
            box_scroll[3] = box_img_int[3]
        # Convert scroll region to tuple and to integer
        self.canvas.configure(
            scrollregion=tuple(map(int, box_scroll))
        )  # set scroll region
        x1 = max(
            box_canvas[0] - box_image[0], 0
        )  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]
        if (
            int(x2 - x1) > 0 and int(y2 - y1) > 0
        ):  # show image if it in the visible area

            image = self._pyramid[
                max(0, self.__curr_img)
            ].crop(  # crop current img from pyramid
                (
                    int(x1 / self.__scale),
                    int(y1 / self.__scale),
                    int(x2 / self.__scale),
                    int(y2 / self.__scale),
                )
            )

            #
            imagetk = ImageTk.PhotoImage(
                image.resize((int(x2 - x1), int(y2 - y1)), Image.Resampling.LANCZOS)
            )
            imageid = self.canvas.create_image(
                max(box_canvas[0], box_img_int[0]),
                max(box_canvas[1], box_img_int[1]),
                anchor="nw",
                image=imagetk,
            )
            self.canvas.lower(imageid)  # set image into background
            self.canvas_imagetk = (
                imagetk  # keep an extra reference to prevent garbage-collection
            )
            GridLines(
                mainmap=self,
                pingx1=max(box_canvas[0], box_img_int[0]) + 5,
                pingy1=max(box_canvas[1], box_img_int[1]) + 5,
            )
            # if hasattr(self, "get_coordinate.rect.lon_min"):
            # self.get_coordinate.rect.call_back_coord()
            try:
                self.get_coordinate.rect.draw_rect_manually(job)
            except AttributeError:
                pass

    def __move_from(self, event):
        """Remember previous coordinates for scrolling with the mouse"""
        self.canvas.scan_mark(event.x, event.y)

    def __move_to(self, event):
        """Drag (move) canvas to the new position"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.__show_image("move")  # zoom tile and show it on the canvas

    def outside(self, x, y):
        """Checks if the point (x,y) is outside the image area"""
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] < x < (bbox[2] + 2) and bbox[1] < y < (bbox[3] + 2):
            return False  # point (x,y) is inside the image area
        else:
            return True  # point (x,y) is outside the image area

    def __wheel(self, event):
        """Zoom with mouse wheel"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.outside(x, y):
            return
        scale = 1.0

        if event.num == 5 or event.delta < 0:  # scroll down, smaller
            if round(self.__min_side * self.imscale) < 30:
                return  # image is less than 30 pixels
            self.imscale /= self.__delta
            scale /= self.__delta
        if event.num == 4 or event.delta > 0:  # scroll up, bigger
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height()) >> 1
            if i < self.imscale:
                return  # 1 pixel is bigger than the visible area
            self.imscale *= self.__delta
            scale *= self.__delta
        # Take appropriate image from the pyramid
        k = self.imscale * self.__ratio  # temporary coefficient
        self.__curr_img = min((-1) * int(math.log(k, 2)), len(self._pyramid) - 1)
        self.__scale = k * math.pow(2, max(0, self.__curr_img))
        #
        self.canvas.scale("all", x, y, scale, scale)  # rescale all objects
        # Redraw some figures before showing image on the screen

        self.__show_image(job="zooming")

    def __keystroke(self, event):
        """Scrolling with the keyboard.
        Independent from the language of the keyboard, CapsLock, <Ctrl>+<key>, etc."""
        if (
            event.state - self.__previous_state == 4
        ):  # means that the Control key is pressed
            pass  # do nothing if Control key is pressed
        else:
            self.__previous_state = event.state  # remember the last keystroke state
            # Up, Down, Left, Right keystrokes
            if event.keycode in [
                68,
                39,
                102,
            ]:  # scroll right: keys 'D', 'Right' or 'Numpad-6'
                self.__scroll_x("scroll", 1, "unit", event=event)

            elif event.keycode in [
                65,
                37,
                100,
            ]:  # scroll left: keys 'A', 'Left' or 'Numpad-4'
                self.__scroll_x("scroll", -1, "unit", event=event)

            elif event.keycode in [
                87,
                38,
                104,
            ]:  # scroll up: keys 'W', 'Up' or 'Numpad-8'
                self.__scroll_y("scroll", -1, "unit", event=event)

            elif event.keycode in [
                83,
                40,
                98,
            ]:  # scroll down: keys 'S', 'Down' or 'Numpad-2'
                self.__scroll_y("scroll", 1, "unit", event=event)

    def crop(self, bbox):
        """Crop rectangle from the image and return it"""

        return self._pyramid[0].crop(bbox)

    def map_background(self):

        if earth_relief.get() == "off":
            self.grid_color = "deepskyblue"
            self.__show_image("change bg")

        elif earth_relief.get() == "on":
            self.grid_color = "grey10"
            self.__show_image("change bg")

    def __create_coord_info(self):
        self.mouse_position_frame = ctk.CTkFrame(self.canvas, width=100, height=100)
        self.mouse_position_frame.place(relx=1, rely=1, x=-5, y=-5, anchor="se")

        self.mouse_position_label = ctk.CTkLabel(
            self.mouse_position_frame,
            text="Lon=        \n Lat=         ",
            font=("Consolas", 14),
            width=90,
            height=40,
        )
        self.map_background_sw = ctk.CTkSwitch(
            self.mouse_position_frame,
            text="Earth Relief",
            font=("Consolas", 12),
            switch_height=14,
            switch_width=28,
            button_length=1,
            command=self.map_background,
            variable=earth_relief,
            onvalue="on",
            offvalue="off",
        )
        self.map_background_sw.pack(fill="both", expand=True, padx=5)
        self.mouse_position_label.pack(fill="both", expand=True)

    def update_mouse_coord(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.outside(x, y):
            return

        pointer_lon, pointer_lat = self.pixel_to_degree(x, y)

        self.mouse_position_label.configure(
            text=f"Lon={pointer_lon:.4f}\nLat={pointer_lat:.4f}",
            justify="left",
        )
        self.canvas.focus_set()

    def pixel_to_degree(self, x=0, y=0):
        image_box = self.canvas.coords(self.container)
        k_w = self.imwidth * self.imscale
        k_h = self.imheight * self.imscale
        lon: float = -180 + ((x - image_box[0]) / k_w) * 360
        lat: float = 90 - ((y - image_box[1]) / k_h) * 180
        return lon, lat

    def degree_to_pixel(self, lon=0.0, lat=0.0):
        image_box = self.canvas.coords(self.container)
        k_w = self.imwidth * self.imscale
        k_h = self.imheight * self.imscale
        x = (lon + 180) * k_w / 360 + image_box[0]
        y = (90 - lat) * k_h / 180 + image_box[1]
        return x, y


class GridLines:
    def __init__(self, mainmap: GlobeMap, pingx1, pingy1):
        self.globemap = mainmap
        self.canvas = mainmap.canvas
        self.imscale = mainmap.imscale
        self.imwidth = mainmap.imwidth
        self.container = mainmap.container
        self.grid_color = mainmap.grid_color
        self.draw_grid_lines_and_anots(pingx1=pingx1, pingy1=pingy1)

    def degree_to_pixel(self, lon=0, lat=0):
        return self.globemap.degree_to_pixel(lon, lat)

    def draw_grid_lines_and_anots(self, pingx1, pingy1):
        self.clear_grid_lines()
        color = self.grid_color
        scaled_width = self.imscale * self.imwidth / 1000
        interval = self.determine_grid_interval(scaled_width)
        grid_limit = self.get_grid_limits()
        lon_range = [-180 + i * interval for i in range(int((360) / interval) + 1)]
        lat_range = [-90 + i * interval for i in range(int((180) / interval) + 1)]
        self.draw_lines(lon_range, lat_range, grid_limit, color)
        self.draw_anots(lon_range, lat_range, grid_limit, pingy1, pingx1)

    def draw_lines(self, lon_range, lat_range, grid_limit, color):

        for lon in lon_range:  # Draw longitude lines
            if lon not in [-180, 180]:
                x, y = self.degree_to_pixel(lon=lon)
                if grid_limit[0] <= x <= (grid_limit[2] + 2):
                    self.canvas.create_line(
                        x, grid_limit[1], x, grid_limit[3], fill=color, tags="grid"
                    )

        for lat in lat_range:  # Draw latitude lines
            if lat not in [-90, 90]:
                x, y = self.degree_to_pixel(lat=lat)
                if grid_limit[1] <= y <= (grid_limit[3] + 2):
                    self.canvas.create_line(
                        grid_limit[0], y, grid_limit[2], y, fill=color, tags="grid"
                    )

    def draw_anots(self, lon_range, lat_range, grid_limit, pingy1, pingx1):

        for lon in lon_range:  # Draw longitude annotations
            x, y = self.degree_to_pixel(lon=lon)
            if grid_limit[0] <= x <= (grid_limit[2] + 2):
                self.create_longitude_text(x, pingy1, lon)

        for lat in lat_range:  # Draw latitude annotations
            x, y = self.degree_to_pixel(lat=lat)
            if grid_limit[1] <= y <= (grid_limit[3] + 2):
                self.create_latitude_text(pingx1, y, lat)

    def create_longitude_text(self, x, y, lon):
        anot_lon = f"{lon}ºE" if lon >= 0 else f"{abs(lon)}ºW"
        if lon == 180:
            x -= 20
        for i in range(-1, 2):
            for j in range(-1, 2):
                self.canvas.create_text(
                    x + i,
                    y + j,
                    text=str(anot_lon),
                    fill=self.grid_color,
                    font=("Consolas", 12),
                    tags=grid_anot,
                    angle=270,
                    anchor="sw",
                )
        self.canvas.create_text(
            x,
            y,
            text=str(anot_lon),
            fill="white",
            tags=grid_anot,
            angle=270,
            font=("Consolas", 12),
            anchor="sw",
        )

    def create_latitude_text(self, x, y, lat):
        x_180, _ = self.degree_to_pixel(lon=-180)
        if lat == 90 and x < (x_180 + 5):
            x += 17
        if lat == -90:
            y -= 20
        anot_lat = f"{lat}ºN" if lat >= 0 else f"{abs(lat)}ºS"
        for i in range(-1, 2):
            for j in range(-1, 2):
                self.canvas.create_text(
                    x + i,
                    y + j,
                    text=str(anot_lat),
                    fill=self.grid_color,
                    font=("Consolas", 12),
                    tags=grid_anot,
                    anchor="nw",
                )
        self.canvas.create_text(
            x,
            y,
            text=str(anot_lat),
            fill="white",
            tags=grid_anot,
            font=("Consolas", 12),
            anchor="nw",
        )

    def clear_grid_lines(self):
        self.canvas.delete("grid")
        self.canvas.delete(grid_anot)

    def determine_grid_interval(self, scaled_width):
        intervals = [
            (600, 0.125),
            (400, 0.25),
            (300, 0.5),
            (90, 1),
            (47, 2),
            (18, 5),
            (6, 10),
            (4.7, 15),
            (2.4, 30),
        ]
        interval = 45  # Default interval
        for threshold, drawed_interval in intervals:
            if scaled_width > threshold:
                return drawed_interval
        return interval

    def get_grid_limits(self):
        box_canvas = (
            self.canvas.canvasx(0),
            self.canvas.canvasy(0),
            self.canvas.canvasx(self.canvas.winfo_width()),
            self.canvas.canvasy(self.canvas.winfo_height()),
        )
        image_box = self.canvas.coords(self.container)
        return [
            max(box_canvas[0], image_box[0]),
            max(box_canvas[1], image_box[1]),
            min(box_canvas[2], image_box[2]),
            min(box_canvas[3], image_box[3]),
        ]


class CoordinateWidget:
    def __init__(self, mainmap: GlobeMap, given_coords: list[float]):
        self.globemap = mainmap
        self.canvas = mainmap.canvas
        self.status = [not_coord]
        self.make_roi(given_coords)
        self.roi_panel()
        self.rect = ResizeableRectangle(mainmap, self)
        if given_coords is not None:
            self.rect.draw_rect_manually("given coord")

    def update_mouse_coord(self, event):
        return self.globemap.update_mouse_coord(event)

    def make_roi(self, given_coords: list[float]):
        self.roi = [ctk.StringVar() for _ in range(4)]
        if given_coords is not None:
            self.roi[0].set(str(given_coords[0]))
            self.roi[1].set(str(given_coords[1]))
            self.roi[2].set(str(given_coords[2]))
            self.roi[3].set(str(given_coords[3]))

            self.status.clear()

        else:
            self.roi[0].set("min lon")
            self.roi[1].set("max lon")
            self.roi[2].set("min lat")
            self.roi[3].set("max lat")

    def pixel_to_degree(self, x=0, y=0):
        return self.globemap.pixel_to_degree(x, y)

    def degree_to_pixel(self, lon=0.0, lat=0.0):
        return self.globemap.degree_to_pixel(lon, lat)

    def outside(self, x, y):
        return self.globemap.outside(x, y)

    def roi_panel(self):
        self.roi_info_frame = ctk.CTkFrame(self.canvas, width=100, height=100)
        self.roi_info_frame.place(relx=0, rely=1, anchor="sw")
        self.x_min_entry = self.create_entry(self.roi[0])
        self.x_max_entry = self.create_entry(self.roi[1])
        self.y_min_entry = self.create_entry(self.roi[2])
        self.y_max_entry = self.create_entry(self.roi[3])

        self.roi_info_frame.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.roi_info_frame.rowconfigure((0, 1, 2), weight=1)

        self.y_max_entry.grid(row=0, column=1, columnspan=2, pady=3)
        self.x_min_entry.grid(row=1, column=0, columnspan=2, pady=3, padx=10)
        self.x_max_entry.grid(row=1, column=2, columnspan=2, pady=3, padx=10)
        self.y_min_entry.grid(row=2, column=1, columnspan=2, pady=3)

    def create_entry(self, text_var):
        return ctk.CTkEntry(
            self.roi_info_frame,
            width=80,
            font=("Consolas", 14),
            textvariable=text_var,
            state=tk.DISABLED,
            text_color="gray",
        )

    def validate(self):
        self.status.clear()

        self.x_min_entry.configure(text_color="white", state=tk.NORMAL)
        self.x_max_entry.configure(text_color="white", state=tk.NORMAL)
        self.y_min_entry.configure(text_color="white", state=tk.NORMAL)
        self.y_max_entry.configure(text_color="white", state=tk.NORMAL)
        if not self.is_valid_number((self.roi[0].get()), -180, 180):
            self.x_min_entry.configure(text_color="red")
            self.status += [msg_invalid_coord]
        if not self.is_valid_number((self.roi[1].get()), -180, 180):
            self.x_max_entry.configure(text_color="red")
            self.status += [msg_invalid_coord]
        if not self.is_valid_number((self.roi[2].get()), -90, 90):
            self.y_min_entry.configure(text_color="red")
            self.status += [msg_invalid_coord]
        if not self.is_valid_number((self.roi[3].get()), -90, 90):
            self.y_max_entry.configure(text_color="red")
            self.status += [msg_invalid_coord]
        # self.replot_button()

    def is_valid_number(self, value, min_val, max_val):
        try:
            num = float(value)
            return min_val <= num <= max_val
        except ValueError:
            return False

    def replot_button(self):
        state = tk.NORMAL if msg_invalid_coord not in self.status else tk.DISABLED
        replot_button = ctk.CTkButton(
            self.roi_info_frame,
            text="Replot",
            font=("Consolas", 14),
            width=8,
            state=state,
        )
        replot_button.bind("<Button-1>", lambda event: self.rect.draw_rect_manually())
        replot_button.grid(row=1, column=4, padx=5)


class ResizeableRectangle:
    def __init__(self, mainmap: GlobeMap, coord_widget: CoordinateWidget):

        self.canvas = mainmap.canvas
        self.coord_widget = coord_widget
        self.roi = coord_widget.roi
        self.imwidth = mainmap.imwidth
        self.imheight = mainmap.imheight
        self.canvas.bind("<ButtonPress-1>", self.create_or_resize_rect)
        self.canvas.bind("<Motion>", self.selecting_line_to_resize, add="+")

        self.side_width = 5

        self.roi[0].trace_add(
            "write", lambda name, index, mode: self.coord_widget.validate
        )
        self.roi[1].trace_add(
            "write", lambda name, index, mode: self.coord_widget.validate
        )
        self.roi[2].trace_add(
            "write", lambda name, index, mode: self.coord_widget.validate
        )
        self.roi[3].trace_add(
            "write", lambda name, index, mode: self.coord_widget.validate
        )
        self.update_roi_from_entry()
        self.resize_side = None
        self.highlighted_side = None

    def pixel_to_degree(self, x=0, y=0):
        return self.coord_widget.pixel_to_degree(x, y)

    def create_or_resize_rect(self, event):
        if self.highlighted_side is None:
            self.rect_create_click(event)

        else:
            self.rect_resize_click(event)

    def selecting_line_to_resize(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if (
            hasattr(self, "x_max")
            and abs(x - self.x_max) <= self.side_width
            and self.y_min > y > self.y_max
        ):
            self.canvas.config(cursor="right_side")
            self.highlighted_side = "right"
        elif (
            hasattr(self, "x_min")
            and abs(x - self.x_min) <= self.side_width
            and self.y_min > y > self.y_max
        ):
            self.canvas.config(cursor="left_side")
            self.highlighted_side = "left"
        elif (
            hasattr(self, "y_max")
            and abs(y - self.y_max) <= self.side_width
            and self.x_min < x < self.x_max
        ):
            self.canvas.config(cursor="top_side")
            self.highlighted_side = "top"
        elif (
            hasattr(self, "y_min")
            and abs(y - self.y_min) <= self.side_width
            and self.x_min < x < self.x_max
        ):
            self.canvas.config(cursor="bottom_side")
            self.highlighted_side = "bottom"
        else:
            self.canvas.config(cursor="")
            self.highlighted_side = None
        self.canvas.delete("highlight")
        self.draw_highlighted_side()

    def draw_highlighted_side(self):
        highlight_color = "yellow"
        highlight_thickness = 3
        if self.highlighted_side:
            if self.highlighted_side == "right":
                self.canvas.create_line(
                    self.x_max,
                    self.y_max,
                    self.x_max,
                    self.y_min,
                    fill=highlight_color,
                    width=highlight_thickness,
                    tags="highlight",
                )
            elif self.highlighted_side == "left":
                self.canvas.create_line(
                    self.x_min,
                    self.y_max,
                    self.x_min,
                    self.y_min,
                    fill=highlight_color,
                    width=highlight_thickness,
                    tags="highlight",
                )
            elif self.highlighted_side == "top":
                self.canvas.create_line(
                    self.x_min,
                    self.y_max,
                    self.x_max,
                    self.y_max,
                    fill=highlight_color,
                    width=highlight_thickness,
                    tags="highlight",
                )
            elif self.highlighted_side == "bottom":
                self.canvas.create_line(
                    self.x_min,
                    self.y_min,
                    self.x_max,
                    self.y_min,
                    fill=highlight_color,
                    width=highlight_thickness,
                    tags="highlight",
                )
            self.canvas.tag_raise("highlight")

    def rect_resize_click(self, event):
        global rectangle
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if abs(x - self.x_max) <= self.side_width:
            self.resize_side = "right"
        elif abs(x - self.x_min) <= self.side_width:
            self.resize_side = "left"
        elif abs(y - self.y_max) <= self.side_width:
            self.resize_side = "top"
        elif abs(y - self.y_min) <= self.side_width:
            self.resize_side = "bottom"
        self.canvas.delete(rectangle)
        rectangle = self.canvas.create_rectangle(
            self.x_min,
            self.y_max,
            self.x_max,
            self.y_min,
            outline="dodgerblue3",
            width=2,
        )
        self.canvas.bind(b1_motion, self.rect_resize_drag, add="+")
        self.canvas.bind(b1_motion, self.coord_widget.update_mouse_coord, add="+")
        self.canvas.bind(b1_release, self.rect_release)

    def rect_resize_drag(self, event):
        new_x = self.canvas.canvasx(event.x)
        new_y = self.canvas.canvasy(event.y)

        if self.resize_side == "right":
            self.x_max = new_x

        elif self.resize_side == "left":
            self.x_min = new_x

        elif self.resize_side == "top":
            self.y_max = new_y

        elif self.resize_side == "bottom":
            self.y_min = new_y

        self.canvas.delete("highlight")
        self.draw_highlighted_side()
        self.canvas.coords(
            rectangle,
            self.x_min,
            self.y_max,
            self.x_max,
            self.y_min,
        )

        self.refresh_roi()

    def rect_release(self, event):
        global rectangle
        if "rectangle" in globals():
            self.canvas.delete(rectangle)
        if "temp_rectangle" in globals():
            self.canvas.delete(temp_rectangle)
        self.x_min, self.x_max = sorted([self.x_min, self.x_max])
        self.y_max, self.y_min = sorted([self.y_min, self.y_max])

        rectangle = self.canvas.create_rectangle(
            self.x_min,
            self.y_min,
            self.x_max,
            self.y_max,
            outline="orangered3",
            width=2,
        )

        self.resize_side = None
        self.refresh_roi()
        self.canvas.unbind(b1_release)
        self.canvas.unbind(b1_motion)

    def rect_create_click(self, event):
        global temp_rectangle
        self.x_1 = self.canvas.canvasx(event.x)
        self.y_1 = self.canvas.canvasy(event.y)
        if self.coord_widget.outside(self.x_1, self.y_1):
            return

        temp_rectangle = self.canvas.create_rectangle(
            self.x_1, self.y_1, self.x_1, self.y_1, outline="yellow", width=2
        )

        self.canvas.bind(b1_release, self.rect_release)
        self.canvas.bind(b1_motion, self.coord_widget.update_mouse_coord, add="+")
        self.canvas.bind(b1_motion, self.rect_create_drag, add="+")

    def rect_create_drag(self, event):
        global temp_rectangle

        self.x_2 = self.canvas.canvasx(event.x)
        self.y_2 = self.canvas.canvasy(event.y)
        self.x_min, self.x_max = sorted([self.x_1, self.x_2])
        self.y_max, self.y_min = sorted([self.y_1, self.y_2])

        self.canvas.coords(
            temp_rectangle, self.x_min, self.y_min, self.x_max, self.y_max
        )
        self.refresh_roi()

    def draw_rect_manually(self, job=None):

        if (
            msg_invalid_coord not in self.coord_widget.status
            and not_coord not in self.coord_widget.status
        ):

            global rectangle
            self.coord_widget.validate()
            lon1 = float(self.roi[0].get())
            lon2 = float(self.roi[1].get())
            lat1 = float(self.roi[2].get())
            lat2 = float(self.roi[3].get())
            if "rectangle" in globals():
                self.canvas.delete(rectangle)

            min_x, min_y = self.coord_widget.degree_to_pixel(lon1, lat1)
            max_x, max_y = self.coord_widget.degree_to_pixel(lon2, lat2)
            self.x_min = min_x
            self.y_min = min_y
            self.x_max = max_x
            self.y_max = max_y
            rectangle = self.canvas.create_rectangle(
                min_x, min_y, max_x, max_y, outline="orangered3", width=2
            )
            if job not in ["given coord", "edit"]:
                return
            self.coord_widget.validate()
            self.refresh_roi()
            return (
                (min_x + (max_x - min_x) / 2) / self.imwidth,
                (min_y + (max_y - min_y) / 2) / self.imheight,
            )

    def refresh_roi(self):

        lon_min, lat_min = self.pixel_to_degree(x=int(self.x_min), y=int(self.y_min))
        lon_max, lat_max = self.pixel_to_degree(x=int(self.x_max), y=int(self.y_max))

        self.roi[0].set(str(round(lon_min, 4)))
        self.roi[1].set(str(round(lon_max, 4)))
        self.roi[2].set(str(round(lat_min, 4)))
        self.roi[3].set(str(round(lat_max, 4)))

    def update_roi_from_entry(self):
        self.coord_widget.x_min_entry.bind(
            focusout, lambda event: self.draw_rect_manually("edit")
        )
        self.coord_widget.x_max_entry.bind(
            focusout, lambda event: self.draw_rect_manually("edit")
        )
        self.coord_widget.y_max_entry.bind(
            focusout, lambda event: self.draw_rect_manually("edit")
        )
        self.coord_widget.y_min_entry.bind(
            focusout, lambda event: self.draw_rect_manually("edit")
        )
        self.coord_widget.x_min_entry.bind(
            return_, lambda event: self.draw_rect_manually("edit")
        )
        self.coord_widget.x_max_entry.bind(
            return_, lambda event: self.draw_rect_manually("edit")
        )
        self.coord_widget.y_max_entry.bind(
            return_, lambda event: self.draw_rect_manually("edit")
        )
        self.coord_widget.y_min_entry.bind(
            return_, lambda event: self.draw_rect_manually("edit")
        )


class CoordWindow(ctk.CTkToplevel):
    """Main window class"""

    def __init__(self, repick_coords):
        """Initialize the main Frame"""
        super().__init__()
        self.title("Select area of interest")
        self.geometry("800x600")  # size of the main window
        loading = ctk.CTkLabel(self, text="Loading...", font=("Consolas", 14))
        loading.pack(expand=True)
        self.attributes("-topmost", True)
        self.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
        self.columnconfigure(0, weight=1)
        self.globemap = GlobeMap(self, repick_coords)
        loading.pack_forget()
        self.globemap.grid(row=0, column=0)  # show widget
        self.protocol("WM_DELETE_WINDOW", self.check_before_close)
        self.mainloop()

    def return_roi(self):
        x1, x2, y1, y2 = (
            self.globemap.get_coordinate.roi[0].get(),
            self.globemap.get_coordinate.roi[1].get(),
            self.globemap.get_coordinate.roi[2].get(),
            self.globemap.get_coordinate.roi[3].get(),
        )
        return [x1, x2, y1, y2]

    def check_before_close(self):
        # if hasattr(self.canvasmain.get_coordinate, "roi"):
        def anot(lon, lat):
            anot_lon = f"{lon:.4f}ºE" if lon >= 0 else f"{abs(lon):.4f}ºW"
            anot_lat = f"{lat:.4f}ºN" if lat >= 0 else f"{abs(lat):.4f}ºS"
            return anot_lon, anot_lat

        if not_coord in self.globemap.get_coordinate.status:
            mesage = "Coordinate not inputed yet,\nDo you want to exit?"
            icon = "warning"
            self.closing(mesage, icon)
        elif msg_invalid_coord not in self.globemap.get_coordinate.status:
            x1, y1 = anot(
                float(self.globemap.get_coordinate.roi[0].get()),
                float(self.globemap.get_coordinate.roi[2].get()),
            )
            x2, y2 = anot(
                float(self.globemap.get_coordinate.roi[1].get()),
                float(self.globemap.get_coordinate.roi[3].get()),
            )
            mesage = f"Longitude = {x1:>11} — {x2:>10}\nLattitude = {y1:>11} — {y2:>10}\n\nUse selected coordinate?"
            icon = "check"
            self.closing(mesage, icon, roi=[str(x1), str(x2), str(y1), str(y2)])
        elif msg_invalid_coord in self.globemap.get_coordinate.status:
            mesage = "Coordinate not valid,\nDo you want to exit?"
            icon = "cancel"
            self.closing(mesage, icon, error=True)

    def closing(self, mesage, icon, roi=None, error=False):
        self.using_coordinate=False
        quiting = CTkMessagebox(
            self,
            title="Exiting coordinate selection",
            message=mesage,
            option_1="No",
            option_2="Yes",
            option_3="Cancel",
            icon=icon,
            wraplength=300,
            fade_in_duration=100,
            option_focus=2,
            font=("Consolas", 14),
            button_width=50,
        )

        if quiting.get() == "Yes":
            if not error:
                self.globemap.save_state()
                self.using_coordinate=True
        elif quiting.get()=="No":
            return
        self.globemap._pyramid_relief.clear()
        self.globemap._pyramid_simple.clear()
        del self.globemap._pyramid[:]
        del self.globemap._pyramid
        self.globemap._imframe.destroy()

        self.withdraw()
        self.quit()
        self.destroy()
            
            


if __name__ == "__main__":

    abc = CoordWindow(None)
    print(abc.return_roi())
