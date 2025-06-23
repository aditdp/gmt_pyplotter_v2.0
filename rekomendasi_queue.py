import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import subprocess
import queue
import os
import platform
from PIL import Image, ImageTk  # Assuming you have Pillow installed
from customtkinter import CTkFrame  # Assuming you are using customtkinter

# Determine command based on OS
if platform.system() == "Windows":
    # Using a simple bat file for demonstration
    # Create a dummy_script.bat for testing:
    # @echo off
    # echo Running dummy script...
    # timeout /t 3 /nobreak > nul
    # echo Dummy script finished.
    # exit /b 0
    COMMAND_SCRIPT_EXT = ".bat"
    COMMAND_PREFIX = ""  # No prefix for .bat files
else:
    # Using a simple shell script for demonstration
    # Create a dummy_script.gmt (or .sh) for testing:
    # #!/bin/bash
    # echo "Running dummy script..."
    # sleep 3
    # echo "Dummy script finished."
    # exit 0
    COMMAND_SCRIPT_EXT = ".gmt"  # Or .sh, based on your actual script
    COMMAND_PREFIX = "./"


class YourAppClass:  # Assuming this is part of a larger Tkinter app class
    def __init__(self, master):
        self.master = master
        master.title("GMT Map Generator")

        # --- Communication Queue ---
        self.gui_queue = queue.Queue()

        # --- GUI Elements (Simplified for example) ---
        self.start_button = tk.Button(
            master, text="Generate Map", command=self.map_preview_toggle
        )
        self.start_button.pack(pady=10)

        self.output_text = scrolledtext.ScrolledText(master, width=80, height=10)
        self.output_text.pack(padx=10, pady=10)

        self.status_label = tk.Label(
            master, text="Status: Idle", bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

        self.button_preview_refresh = tk.Button(
            master, text="Refresh Preview", command=self.refresh_preview_from_button
        )
        # Initially packed_forget, will pack when map is generated

        self.preview_status = "off"
        self.process_thread = None  # To hold the thread object

        # Dummy attributes for demonstration
        class GetName:
            def __init__(self):
                self.file_name = tk.StringVar(value="dummy_script")
                self.output_dir = tk.StringVar(
                    value="."
                )  # Current directory for simplicity
                self.dir_prename_map = "dummy_map.png"  # Path to your generated image

        self.main = master  # self.main reference from your original code
        self.main.get_name = GetName()  # Initialize dummy get_name
        self.main.frame_map_param = CTkFrame(
            self.main, width=100, height=550
        )  # Dummy frame
        self.main.frame_layers = CTkFrame(
            self.main, width=100, height=550
        )  # Dummy frame

        # Start checking the queue periodically
        self.master.after(100, self.check_gui_queue)

        # Create a dummy map file for testing
        self._create_dummy_map_file()

    def _create_dummy_map_file(self):
        # Create a dummy image file for map_preview_on to load
        try:
            dummy_image = Image.new("RGB", (800, 600), color="red")
            dummy_image.save(self.main.get_name.dir_prename_map)
            print(f"Created dummy map file: {self.main.get_name.dir_prename_map}")
        except Exception as e:
            print(f"Error creating dummy map file: {e}")

        # Create a dummy script for testing (for gmt_execute)
        script_content_win = """
@echo off
echo Running GMT script (Windows)...
timeout /t 3 /nobreak > nul
echo GMT script finished (Windows).
exit /b 0
"""
        script_content_linux = """#!/bin/bash
echo "Running GMT script (Linux)..."
sleep 3
echo "GMT script finished (Linux)."
exit 0
"""
        script_path = os.path.join(
            self.main.get_name.output_dir.get(),
            f"{self.main.get_name.file_name.get()}{COMMAND_SCRIPT_EXT}",
        )
        with open(script_path, "w") as f:
            if platform.system() == "Windows":
                f.write(script_content_win)
            else:
                f.write(script_content_linux)
        if platform.system() != "Windows":
            os.chmod(script_path, 0o755)  # Make executable on Linux/macOS
        print(f"Created dummy script: {script_path}")

    def threading_process(self, worker, args, name):
        self.process_thread = threading.Thread(target=worker, args=args, name=name)
        self.process_thread.daemon = True
        self.process_thread.start()

    def gmt_execute(self, script_name, output_dir):
        cwd = os.getcwd()
        os.chdir(output_dir)

        # Use sys.platform for better OS differentiation
        if sys.platform == "win32":
            command = [f"{script_name}{COMMAND_SCRIPT_EXT}"]
            # For .bat files, you might need to explicitly call cmd.exe
            # command = ["cmd.exe", "/c", f"{script_name}.bat"]
        else:  # Covers 'linux', 'darwin', etc.
            # Ensure script is executable
            script_path = f"{output_dir}/{script_name}{COMMAND_SCRIPT_EXT}"
            if not os.path.exists(script_path):
                self.gui_queue.put(("error", f"Script not found: {script_path}"))
                return
            os.system(f"chmod +x {script_path}")  # Ensure executable
            command = [f"{COMMAND_PREFIX}{script_name}{COMMAND_SCRIPT_EXT}"]

        try:
            self.gui_queue.put(
                (
                    "output",
                    f"Running '{os.path.join(output_dir, command[0])}' with subprocess.Popen()...\n",
                )
            )

            generate_map = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            # Stream output line by line for responsiveness
            for line in generate_map.stdout:
                self.gui_queue.put(("output", line))

            # After stdout is exhausted, read stderr (if any)
            stderr_output = generate_map.stderr.read()
            if stderr_output:
                self.gui_queue.put(("output", f"\n--- STDERR ---\n{stderr_output}\n"))

            return_code = generate_map.wait()  # Wait for process to finish
            self.gui_queue.put(
                (
                    "output",
                    f"[{threading.current_thread().name}] Process finished with code: {return_code}\n",
                )
            )

            if return_code == 0:
                self.gui_queue.put(("status", "success"))  # Signal success to GUI
            else:
                self.gui_queue.put(("status", f"failed_code:{return_code}"))

        except FileNotFoundError:
            self.gui_queue.put(
                (
                    "error",
                    f"Program '{command[0]}' not found. Ensure it's in PATH or specified with full path.",
                )
            )
        except Exception as e:
            self.gui_queue.put(
                ("error", f"An error occurred during subprocess execution: {e}")
            )
        finally:
            os.chdir(cwd)  # Always change back to original directory

    def map_preview_toggle(self):
        if self.preview_status == "off":
            self.output_text.delete(1.0, tk.END)  # Clear previous output
            self.output_text.insert(tk.END, "Starting map generation...\n")
            self.status_label.config(text="Status: Generating Map...")
            self.start_button.config(state=tk.DISABLED)
            self.button_preview_refresh.pack_forget()  # Hide refresh during generation

            self.threading_process(
                self.gmt_execute,
                args=[
                    self.main.get_name.file_name.get(),
                    self.main.get_name.output_dir.get(),
                ],
                name="generate Preview Map",
            )
            self.preview_status = (
                "on"  # Optimistically set, actual status handled by queue
            )
        else:
            self.map_preview_off()
            self.preview_status = "off"
            self.button_preview_refresh.pack_forget()

    def refresh_preview_from_button(self):
        # This function would be called by the refresh button
        # It needs to trigger map_preview_on again without re-running gmt_execute
        self.map_preview_on_gui_thread(
            success=True
        )  # Call directly as it's already on main thread

    def map_preview_on_gui_thread(self, success):
        # This method is designed to be called ONLY from the main GUI thread
        # It directly manipulates Tkinter widgets
        if not success:
            self.output_text.insert(
                tk.END, "Map generation failed, cannot show preview.\n"
            )
            self.status_label.config(text="Status: Map generation failed.")
            self.start_button.config(state=tk.NORMAL)
            return

        cur_x = self.main.winfo_x()
        cur_y = self.main.winfo_y()
        self.output_text.insert(tk.END, "Loading image...\n")  # Update GUI directly
        print("sebelum loading gambar")  # This print is fine in main thread

        try:
            image = Image.open(self.main.get_name.dir_prename_map)
        except FileNotFoundError:
            self.output_text.insert(
                tk.END,
                f"Error: Map image not found at {self.main.get_name.dir_prename_map}\n",
            )
            self.status_label.config(text="Status: Image not found.")
            self.start_button.config(state=tk.NORMAL)
            return
        except Exception as e:
            self.output_text.insert(tk.END, f"Error loading image: {e}\n")
            self.status_label.config(text="Status: Image load error.")
            self.start_button.config(state=tk.NORMAL)
            return

        print("setelah loading gambar")  # This print is fine
        self.output_text.insert(tk.END, "Image loaded successfully.\n")

        ratio = image.width / image.height
        new_width = int(700 + (ratio * 550))  # Recalculate width based on image ratio
        image_resize = image.resize(
            (int((new_width - 710)), int(545)), Image.LANCZOS
        )  # Use a good resampling filter

        resize = f"{new_width}x550+{cur_x}+{cur_y}"
        self.main.geometry(resize)

        self.imagetk = ImageTk.PhotoImage(image_resize)  # IMPORTANT: Keep a reference!
        self.main.frame_map_param.pack(side="left")
        self.main.frame_layers.pack(side="left")

        print(f"rel frame layer width= {210/new_width}")  # Fine
        # Remove existing frame_preview if it exists and pack a new one
        if hasattr(self, "frame_preview") and self.frame_preview.winfo_exists():
            self.frame_preview.destroy()

        self.frame_preview = CTkFrame(self.main, height=550, width=new_width - 700)
        self.frame_preview.pack(side="left", fill="both", anchor="nw")

        self.expand_window(self.imagetk)  # This should update GUI with the image

        self.output_text.insert(tk.END, "Map preview displayed.\n")
        self.status_label.config(text="Status: Map ready.")
        self.button_preview_refresh.pack(side="left", padx=(5, 5))
        self.start_button.config(
            state=tk.NORMAL
        )  # Re-enable button after preview is up

    def expand_window(self, imagetk_obj):
        # This method needs to draw the image onto the frame_preview
        # You'll likely need a CTkCanvas or a Label inside CTkFrame
        # For simplicity, let's just put it in a CTkLabel here.
        if hasattr(self, "image_label") and self.image_label.winfo_exists():
            self.image_label.destroy()

        self.image_label = tk.Label(self.frame_preview, image=imagetk_obj)
        self.image_label.pack(expand=True, fill="both")
        self.image_label.image = imagetk_obj  # Keep reference!

    def map_preview_off(self):
        # Logic to turn off the preview
        self.main.geometry("700x550")  # Reset window size
        if hasattr(self, "frame_preview") and self.frame_preview.winfo_exists():
            self.frame_preview.destroy()
        self.main.frame_map_param.pack_forget()
        self.main.frame_layers.pack_forget()
        self.status_label.config(text="Status: Preview Off")
        self.output_text.insert(tk.END, "Map preview turned off.\n")

    def check_gui_queue(self):
        """Periodically checks the queue for messages from the worker thread."""
        try:
            while True:
                msg_type, data = self.gui_queue.get_nowait()
                if msg_type == "output":
                    self.output_text.insert(tk.END, data)
                    self.output_text.see(tk.END)
                elif msg_type == "status":
                    if data == "success":
                        self.map_preview_on_gui_thread(
                            success=True
                        )  # Call GUI update method
                        print("done map preview")
                    elif data.startswith("failed_code:"):
                        return_code = data.split(":")[1]
                        self.output_text.insert(
                            tk.END,
                            f"GMT script failed with code: {return_code}. Cannot show preview.\n",
                        )
                        self.status_label.config(
                            text=f"Status: Failed (Code: {return_code})"
                        )
                        self.start_button.config(state=tk.NORMAL)
                        self.button_preview_refresh.pack_forget()
                        self.preview_status = "off"  # Reset status
                elif msg_type == "error":
                    self.output_text.insert(tk.END, f"\n--- ERROR ---\n{data}\n")
                    self.output_text.see(tk.END)
                    self.status_label.config(text="Status: Error during execution")
                    self.start_button.config(state=tk.NORMAL)
                    self.button_preview_refresh.pack_forget()
                    self.preview_status = "off"  # Reset status

                self.gui_queue.task_done()
        except queue.Empty:
            pass  # No messages in the queue
        finally:
            self.master.after(100, self.check_gui_queue)  # Schedule next check


# --- Main Tkinter setup ---
if __name__ == "__main__":
    # Create dummy files for testing
    # This will create 'dummy_script.bat' (Windows) or 'dummy_script.gmt' (Linux/macOS)
    # and 'dummy_map.png' in the current directory.
    # The 'gmt_execute' function will run 'dummy_script.bat'/.gmt
    # and then 'map_preview_on_gui_thread' will try to load 'dummy_map.png'.

    root = tk.Tk()
    app = YourAppClass(root)
    root.mainloop()
