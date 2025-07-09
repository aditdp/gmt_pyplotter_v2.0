from PIL import Image

# Load the image and ensure it has an alpha channel for transparency
input = "light_eyedropper.png"

img = Image.open(input).convert("RGBA")

# Iterate through each pixel to modify black pixels to white
datas = img.getdata()
new_data = []
for item in datas:
    # If the pixel is black (or near black), change it to white with the same alpha value
    if (
        item[0] < 50 and item[1] < 50 and item[2] < 50 and item[3] != 0
    ):  # Check for black with any alpha except fully transparent
        new_data.append(
            (100, 100, 100, item[3])
        )  # Replace with white while preserving transparency
    else:
        new_data.append(item)

# Update image data
img.putdata(new_data)

# Save the new image
img.save(f"off_{input}", "PNG")
