import sys
import os
import time
from functools import wraps


def disable_input(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.name == "posix":
            import termios
            import tty

            fd = sys.stdin.fileno()
            original_attributes = termios.tcgetattr(fd)
            tty.setcbreak(fd)
        elif os.name == "nt":
            import msvcrt

        result = None
        try:
            result = func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nProcess interrupted by user!")
        finally:
            if os.name == "posix":
                termios.tcsetattr(fd, termios.TCSANOW, original_attributes)
            elif os.name == "nt":
                while msvcrt.kbhit():
                    msvcrt.getch()  # Clear the buffer
        return result

    return wrapper


@disable_input
def long_running_process():
    print("Process started... No input will be accepted.")
    time.sleep(5)  # Simulating a long-running task
    print("Process completed. Input is now accepted.")


if __name__ == "__main__":
    try:
        long_running_process()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user!")
