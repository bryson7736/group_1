from PIL import Image, ImageDraw
import os

# Load the iron dice image
img_path = r"c:\Users\5594i\group_1\RDproject\assets\dice_iron.png"
img = Image.open(img_path).convert("RGBA")

# Get image dimensions
width, height = img.size
print(f"Image size: {width}x{height}")

# Get pixel data
pixels = img.load()

# More aggressive removal - scan entire image for white dots
# Focus on the top-right quadrant but be more thorough
removed_count = 0

for x in range(width):
    for y in range(height):
        r, g, b, a = pixels[x, y]
        
        # Remove very bright pixels (likely the white dot)
        # More aggressive threshold
        if a > 50:  # Only process non-transparent pixels
            brightness = (r + g + b) / 3
            if brightness > 220:  # Very bright pixels
                # Check if it's isolated (likely a dot, not part of main design)
                # Make it fully transparent
                pixels[x, y] = (r, g, b, 0)
                removed_count += 1

print(f"Removed {removed_count} bright pixels")

# Save the modified image
img.save(img_path)
print(f"Successfully cleaned {img_path}")
