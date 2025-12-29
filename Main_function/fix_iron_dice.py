from PIL import Image, ImageDraw
import os

# Load the iron dice image
img_path = r"c:\Users\5594i\group_1\RDproject\assets\dice_iron.png"
img = Image.open(img_path).convert("RGBA")

# Get image dimensions
width, height = img.size

# Define the area to remove the white dot (top-right corner)
# Assuming the dot is roughly in the top-right 20% of the image
dot_region_x = int(width * 0.75)  # Start from 75% width
dot_region_y = 0  # Start from top
dot_region_w = width - dot_region_x
dot_region_h = int(height * 0.25)  # Cover top 25%

# Get pixel data
pixels = img.load()

# Remove white/light colored pixels in the top-right region
for x in range(dot_region_x, width):
    for y in range(dot_region_y, dot_region_y + dot_region_h):
        r, g, b, a = pixels[x, y]
        # If pixel is very light (close to white), make it transparent
        if r > 200 and g > 200 and b > 200 and a > 100:
            pixels[x, y] = (r, g, b, 0)  # Make transparent

# Save the modified image
img.save(img_path)
print(f"Successfully removed white dot from {img_path}")
