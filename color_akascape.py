import CTkColorPicker

import customtkinter as ctk
from CTkColorPicker import *


def ask_color():
    pick_color = AskColor()  # open the color picker
    color = pick_color.get()  # get the color string
    button.configure(fg_color=color)


root = ctk.CTk()

button = ctk.CTkButton(
    master=root, text="CHOOSE COLOR", text_color="black", command=ask_color
)
button.pack(padx=30, pady=20)
root.mainloop()


def hex_to_rgb(hex_color):
    """
    Converts a hexadecimal color code (e.g., "#RRGGBB" or "RRGGBB")
    into an RGB tuple (R, G, B).

    Args:
        hex_color (str): The hexadecimal color code string.

    Returns:
        tuple: A tuple (R, G, B) where R, G, B are integers from 0 to 255.
               Returns None if the input hex_color is invalid.
    """
    # Remove the '#' prefix if it exists
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]

    # Check if the hex code has the correct length (6 characters for RRGGBB)
    if len(hex_color) != 6:
        print(
            f"Error: Invalid hex color code length. Expected 6 characters, got {len(hex_color)}."
        )
        return None

    try:
        # Convert each 2-character hex pair to an integer
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        return f"{r}/{g}/{b}"
    except ValueError:
        # This error occurs if the hex_color string contains non-hex characters
        print(f"Error: Invalid hexadecimal characters in '{hex_color}'.")
        return None


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Hex to RGB Converter ---")

    # Valid hex codes
    hex1 = "#FF0000"
    hex2 = "00FF00"
    hex3 = "#0000FF"
    hex4 = "#1A2B3C"
    hex5 = "#FFFFFF"
    hex6 = "#000000"

    print(f"Converting '{hex1}': {hex_to_rgb(hex1)}")
    print(f"Converting '{hex2}': {hex_to_rgb(hex2)}")
    print(f"Converting '{hex3}': {hex_to_rgb(hex3)}")
    print(f"Converting '{hex4}': {hex_to_rgb(hex4)}")
    print(f"Converting '{hex5}': {hex_to_rgb(hex5)}")
    print(f"Converting '{hex6}': {hex_to_rgb(hex6)}")

    print("\n--- Testing Invalid Inputs ---")
    # Invalid hex codes
    invalid_hex1 = "#FFF"  # Too short
    invalid_hex2 = "ABCDEFG"  # Too long
    invalid_hex3 = "#GGGGGG"  # Invalid characters
    invalid_hex4 = "12345Z"  # Invalid character

    print(f"Converting '{invalid_hex1}': {hex_to_rgb(invalid_hex1)}")
    print(f"Converting '{invalid_hex2}': {hex_to_rgb(invalid_hex2)}")
    print(f"Converting '{invalid_hex3}': {hex_to_rgb(invalid_hex3)}")
    print(f"Converting '{invalid_hex4}': {hex_to_rgb(invalid_hex4)}")

    # You can also use it to get user input
    # user_input = input("\nEnter a hex color code (e.g., #RRGGBB): ")
    # rgb_output = hex_to_rgb(user_input)
    # if rgb_output:
    #     print(f"RGB value: {rgb_output}")
