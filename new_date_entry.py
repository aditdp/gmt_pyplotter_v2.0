import customtkinter as ctk
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from PIL import Image
import time, threading
import calendar
import os  # Added for image path check
from tkinter import TclError  # Import TclError from tkinter
from typing import Optional  # Import Optional for type hinting

# Dummy image files for demonstration if not present
# In a real app, ensure these paths are correct or provide default images
if not os.path.exists("./image/dark_calendar.png"):
    # Create a dummy image if it doesn't exist
    try:
        os.makedirs("./image", exist_ok=True)
        dummy_image = Image.new("RGB", (20, 20), color=(70, 70, 70))  # Dark gray
        dummy_image.save("./image/dark_calendar.png")
        dummy_image = Image.new("RGB", (20, 20), color=(180, 180, 180))  # Light gray
        dummy_image.save("./image/light_calendar.png")
    except Exception as e:
        print(
            f"Could not create dummy images: {e}. Please ensure ./image directory exists and is writable."
        )


class DateEntry(ctk.CTkFrame):
    def __init__(
        self, master, textvar=None, initial_date: Optional[datetime] = None, **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        # Use the provided StringVar as the primary source of truth for the entry's text.
        # If no StringVar is provided, create one internally.
        if textvar is not None:
            self.text_variable = textvar
        else:
            # If no textvar, use initial_date for default value, or current datetime.
            if initial_date is None:
                initial_date = datetime.now()
            self.text_variable = ctk.StringVar(
                self, value=initial_date.strftime("%Y-%m-%d")
            )

        # self.selected_date will hold the datetime object, derived from the StringVar
        # or initialized from initial_date. It's used for calendar popup and get() method.
        try:
            self.selected_date: datetime = datetime.strptime(
                self.text_variable.get(), "%Y-%m-%d"
            )
        except ValueError:
            # Fallback if the StringVar's initial content is not a valid date string
            # Ensure initial_date is a datetime object here, as it could be None
            self.selected_date: datetime = (
                initial_date if initial_date is not None else datetime.now()
            )
            self.text_variable.set(
                self.selected_date.strftime("%Y-%m-%d")
            )  # Ensure StringVar is valid

        # Entry to display the date - linked directly to self.text_variable
        self.date_entry = ctk.CTkEntry(self, width=90, textvariable=self.text_variable)
        self.date_entry.grid(row=0, column=0, padx=(0, 5))

        self.validation_timer_id: Optional[str] = None  # Use this for self.after_cancel
        self.validation_delay_ms = 1500

        # Bind events for manual input validation
        self.date_entry.bind("<Return>", self._validate_and_set_date)  # On Enter key
        self.date_entry.bind(
            "<FocusOut>", self._validate_and_set_date
        )  # When focus leaves
        self.date_entry.bind(
            "<KeyRelease>", self._on_date_entry_keyrelease
        )  # For debounced validation

        # Button to open the calendar
        dark_calendar_logo = Image.open("./image/dark_calendar.png")
        light_calendar_logo = Image.open("./image/light_calendar.png")
        calendar_logotk = ctk.CTkImage(
            dark_image=dark_calendar_logo,
            light_image=light_calendar_logo,
            size=(20, 20),
        )
        self.open_calendar_button = ctk.CTkButton(
            self,
            image=calendar_logotk,
            text="",
            width=30,
            command=self._open_calendar,
            hover_color="gray",
            fg_color="dim gray",
        )
        self.open_calendar_button.grid(row=0, column=1)

        self.calendar_popup: Optional["CalendarPopup"] = (
            None  # Type hint for calendar_popup
        )

    def _open_calendar(self):
        if self.calendar_popup is not None and self.calendar_popup.winfo_exists():
            self.calendar_popup.lift()
            return

        if not self.master.winfo_exists():
            return

        # Ensure the popup starts with the currently displayed date in the entry
        try:
            # Parse the current entry text (from StringVar) to initialize the calendar with it
            current_date_in_entry = datetime.strptime(
                self.text_variable.get(), "%Y-%m-%d"
            )
        except ValueError:
            # If entry has invalid date, default to current selected_date or now
            current_date_in_entry = (
                self.selected_date if self.selected_date else datetime.now()
            )

        self.calendar_popup = CalendarPopup(
            self.master, current_date_in_entry, self._set_date_from_calendar
        )

        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.calendar_popup.geometry(f"+{x}+{y}")

        # Fix for Pylance warning: Make the popup transient to the main top-level window
        self.calendar_popup.transient(self.winfo_toplevel())
        self.calendar_popup.grab_set()

    def _set_date_from_calendar(self, date_obj: datetime):
        self.selected_date = date_obj
        self._update_entry_display(self.selected_date)

        if self.calendar_popup is not None and self.calendar_popup.winfo_exists():
            self.calendar_popup._on_closing()
            self.calendar_popup = None

    def _update_entry_display(self, date_obj: datetime):
        """Updates the date entry field's linked StringVar with the given datetime object."""
        self.text_variable.set(date_obj.strftime("%Y-%m-%d"))
        self.date_entry.configure(
            fg_color=self.date_entry.cget("bg_color")
        )  # Reset background color if was red

    def _on_date_entry_keyrelease(self, event=None):
        """
        This method is called on every key release.
        It manages the debouncing timer for date validation using self.after.
        """
        if self.validation_timer_id:
            self.after_cancel(self.validation_timer_id)

        # Schedule validation after a delay. If another key is pressed, the previous
        # scheduled validation will be cancelled.
        self.validation_timer_id = self.after(
            self.validation_delay_ms, self._validate_and_set_date
        )

    def _validate_and_set_date(
        self, event=None
    ):  # event is optional, as it might be called by after()
        entered_date_str = (
            self.text_variable.get().strip()
        )  # Get from StringVar and strip whitespace

        try:
            parsed_date: datetime = datetime.strptime(entered_date_str, "%Y-%m-%d")
            self.selected_date = parsed_date  # Update the internal datetime object
            self.date_entry.configure(
                fg_color=self.date_entry.cget("bg_color")
            )  # Reset background color

            # If the calendar popup is open, update it to reflect the manually entered date
            if self.calendar_popup is not None and self.calendar_popup.winfo_exists():
                self.calendar_popup.current_display_date = self.selected_date
                self.calendar_popup._populate_calendar()

        except ValueError:
            # Invalid date format or non-existent date
            self.date_entry.configure(fg_color="red")  # Highlight error
            print(f"Invalid date format: '{entered_date_str}'. Please use YYYY-MM-DD.")

    def get(self) -> datetime:
        """Returns the currently selected date as a datetime object."""
        try:
            # Always try to parse the current content of the StringVar for the most up-to-date value
            return datetime.strptime(self.text_variable.get().strip(), "%Y-%m-%d")
        except ValueError:
            # If StringVar content is invalid, return the last valid selected_date
            print(
                f"Warning: DateEntry content '{self.text_variable.get()}' is invalid. Returning last valid date."
            )
            return self.selected_date

    def set(self, date_obj: datetime):
        """Sets the date entry's value from a datetime object."""
        if isinstance(date_obj, datetime):
            self.selected_date = date_obj  # Update internal datetime object
            self.text_variable.set(
                date_obj.strftime("%Y-%m-%d")
            )  # Update StringVar directly
        else:
            raise ValueError("Input to DateEntry.set() must be a datetime object")


class CalendarPopup(ctk.CTkToplevel):
    DEBOUNCE_DELAY_MS = 300

    def __init__(self, master, initial_date: datetime, callback):
        super().__init__(master)
        self.title("Select Date")
        self.resizable(False, False)

        self.current_display_date: datetime = initial_date
        self.callback = callback

        self.cal_instance = calendar.Calendar(firstweekday=calendar.SUNDAY)

        self.click_counts = {
            "prev_year": 0,
            "next_year": 0,
            "prev_month": 0,
            "next_month": 0,
        }
        # Initialize debounce_jobs with None, but self.after returns an int ID
        # Pylance is being strict here.
        self.debounce_jobs: dict[str, Optional[str]] = (
            {  # Explicitly type values as Optional[str]
                "prev_year": None,
                "next_year": None,
                "prev_month": None,
                "next_month": None,
            }
        )

        self._create_widgets()
        self._populate_calendar()

        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Escape>", lambda e: self._on_closing())
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.after(10, self.focus_set)

    def _create_widgets(self):
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(pady=5, padx=5)

        self.prev_year_button = ctk.CTkButton(
            nav_frame,
            text="<<",
            width=30,
            command=lambda: self._handle_nav_click("prev_year"),
        )
        self.prev_year_button.grid(row=0, column=0, padx=2)

        self.prev_month_button = ctk.CTkButton(
            nav_frame,
            text="<",
            width=30,
            command=lambda: self._handle_nav_click("prev_month"),
        )
        self.prev_month_button.grid(row=0, column=1, padx=2)

        self.month_year_label = ctk.CTkLabel(nav_frame, text="", width=150)
        self.month_year_label.grid(row=0, column=2, padx=5)

        self.next_month_button = ctk.CTkButton(
            nav_frame,
            text=">",
            width=30,
            command=lambda: self._handle_nav_click("next_month"),
        )
        self.next_month_button.grid(row=0, column=3, padx=2)

        self.next_year_button = ctk.CTkButton(
            nav_frame,
            text=">>",
            width=30,
            command=lambda: self._handle_nav_click("next_year"),
        )
        self.next_year_button.grid(row=0, column=4, padx=2)

        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(padx=0)
        for i, day in enumerate(day_names):
            ctk.CTkLabel(
                header_frame,
                text=day,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=30,
            ).grid(row=0, column=i, padx=2, pady=1)

        self.calendar_grid_frame = ctk.CTkFrame(self)
        self.calendar_grid_frame.pack(padx=5, pady=5)

    def _populate_calendar(self):
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        month_name = self.current_display_date.strftime("%B")
        year = self.current_display_date.year
        self.month_year_label.configure(text=f"{month_name} {year}")

        month_days = self.cal_instance.monthdayscalendar(
            year, self.current_display_date.month
        )

        for week_num, week in enumerate(month_days):
            for day_num, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(
                        self.calendar_grid_frame, text="", width=30, height=25
                    ).grid(row=week_num, column=day_num, padx=2, pady=2)
                else:
                    date_obj = datetime(year, self.current_display_date.month, day)
                    button_text = str(day)

                    button = ctk.CTkButton(
                        self.calendar_grid_frame,
                        text=button_text,
                        width=30,
                        height=25,
                        command=lambda d=date_obj: self._select_date(d),
                        hover_color="gray",
                        fg_color="dim gray",
                    )
                    button.grid(row=week_num, column=day_num, padx=2, pady=2)

                    if date_obj.date() == datetime.now().date():
                        button.configure(fg_color=("lightblue", "cornflowerblue"))

                    if date_obj.date() == self.current_display_date.date():
                        button.configure(fg_color=("green", "darkgreen"))

    def _handle_nav_click(self, button_type: str):
        self.click_counts[button_type] += 1

        # Retrieve the job ID from the dictionary
        job_id_to_cancel = self.debounce_jobs[button_type]

        # Only call after_cancel if there's an active job ID
        if job_id_to_cancel is not None:
            self.after_cancel(job_id_to_cancel)
            self.debounce_jobs[button_type] = None  # Clear the ID after cancelling

        # Schedule a new job and store its ID
        self.debounce_jobs[button_type] = self.after(
            self.DEBOUNCE_DELAY_MS, lambda: self._process_nav_clicks(button_type)
        )

    def _process_nav_clicks(self, button_type: str):
        clicks = self.click_counts[button_type]

        if button_type == "prev_year":
            self.current_display_date = self.current_display_date.replace(
                year=self.current_display_date.year - clicks
            )
        elif button_type == "next_year":
            self.current_display_date = self.current_display_date.replace(
                year=self.current_display_date.year + clicks
            )
        elif button_type == "prev_month":
            for _ in range(clicks):
                temp_date = self.current_display_date.replace(day=1) - timedelta(days=1)
                self.current_display_date = temp_date.replace(day=1)
        elif button_type == "next_month":
            for _ in range(clicks):
                next_month = self.current_display_date.month % 12 + 1
                next_year = self.current_display_date.year + (
                    1 if next_month == 1 else 0
                )
                self.current_display_date = datetime(next_year, next_month, 1)

        self.click_counts[button_type] = 0
        self.debounce_jobs[button_type] = None

        if self.winfo_exists():
            self._populate_calendar()

    def _select_date(self, date_obj: datetime):
        self.callback(date_obj)
        self._on_closing()

    def _on_focus_out(self, event=None):  # event can be None if called directly
        if not self.winfo_exists():
            return

        # Check if the event widget is outside the popup or its descendants
        # This is a more robust check for focus leaving the popup
        if event and event.widget:  # Ensure event and widget exist
            if not self.winfo_containing(event.x_root, event.y_root) == self:
                # If the new focus is not within this popup, close it
                self._on_closing()
        # If event is None (called directly), or event.widget is None, do nothing
        # or implement alternative closing logic if desired.

    def _on_closing(self):
        if self.winfo_exists():
            for job_id in self.debounce_jobs.values():
                if job_id is not None:
                    try:
                        self.after_cancel(job_id)
                    except ValueError:
                        pass
            try:
                self.grab_release()
            except TclError:
                pass
            self.destroy()

    def is_ancestor(self, widget: ctk.CTkBaseClass) -> bool:  # Add type hint for widget
        current = widget
        while current is not None:
            if current == self:
                return True
            try:
                current = current.master
            except AttributeError:
                break
        return False


# Example usage (for testing DateEntry independently)
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("CustomTkinter Date Entry with Manual Input")
    app.geometry("400x300")

    # Create a StringVar to link to the DateEntry
    my_date_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

    def print_selected_date():
        # Get the datetime object from the DateEntry
        selected_dt = my_date_entry.get()
        print(f"Selected Date: {selected_dt.strftime('%Y-%m-%d')}")
        print(f"StringVar value: {my_date_var.get()}")

    my_date_entry = DateEntry(app, textvar=my_date_var)
    my_date_entry.pack(pady=20)

    get_date_button = ctk.CTkButton(
        app, text="Get Selected Date", command=print_selected_date
    )
    get_date_button.pack(pady=10)

    # Example of setting the date programmatically
    set_date_button = ctk.CTkButton(
        app,
        text="Set Date to 2024-01-15",
        command=lambda: my_date_entry.set(datetime(2024, 1, 15)),
    )
    set_date_button.pack(pady=10)

    app.mainloop()
