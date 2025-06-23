import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import sys  # For platform-specific commands


class App:
    def __init__(self, master):
        self.master = master
        master.title("Non-Blocking Process in Tkinter")

        self.status_label = tk.Label(master, text="Ready.")
        self.status_label.pack(pady=10)

        self.start_button = ttk.Button(
            master, text="Start Long Process", command=self.start_long_process
        )
        self.start_button.pack(pady=5)

        self.other_button = ttk.Button(
            master, text="Test Responsiveness", command=self.test_responsiveness
        )
        self.other_button.pack(pady=5)

        self.process_thread = None  # To hold the thread object

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

    def start_long_process(self):
        self.status_label.config(text="Process started (running in background)...")
        self.start_button.config(
            state=tk.DISABLED
        )  # Disable button to prevent multiple clicks

        # Define the command and arguments based on OS
        if sys.platform.startswith("linux") or sys.platform == "darwin":
            program = "sleep"
            args = ["5"]  # Sleeps for 5 seconds
        elif sys.platform == "win32":
            program = "timeout"
            args = ["/t", "5", "/nobreak"]  # Sleeps for 5 seconds (cmd.exe specific)
        else:
            self.status_label.config(text="Unsupported OS for this example.")
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
                self.status_label.config(text=message, fg="green")
            else:
                message = f"Process finished with error (code {return_code})."
                self.status_label.config(text=message, fg="red")

            if stdout:
                print("Process Stdout:\n", stdout)
            if stderr:
                print("Process Stderr:\n", stderr)

        else:
            self.status_label.config(text="Process encountered an error.", fg="red")

        self.start_button.config(state=tk.NORMAL)  # Re-enable the button

    def test_responsiveness(self):
        messagebox.showinfo("Responsiveness Test", "Tkinter GUI is responsive!")


root = tk.Tk()
app = App(root)
root.mainloop()
