import pygame
import os

def fix_transparency():
    pygame.init()
    # Setup a dummy display surface for image conversion
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    assets_dir = os.path.join(os.getcwd(), "assets")
    if not os.path.exists(assets_dir):
        print("Assets directory not found.")
        return

    files = [f for f in os.listdir(assets_dir) if f.startswith("dice_") and f.endswith(".png")]
    
    print(f"Found {len(files)} dice images to process.")

    for filename in files:
        path = os.path.join(assets_dir, filename)
        try:
            surface = pygame.image.load(path).convert() # Load without alpha to see RGB values clearly
            
            # Sample top-left pixel as background color
            bg_color = surface.get_at((0, 0))
            
            # Convert to alpha capable surface
            surface = surface.convert_alpha()
            
            width, height = surface.get_size()
            
            # Lock the surface for pixel access
            for y in range(height):
                for x in range(width):
                    color = surface.get_at((x, y))
                    # Check distance to bg_color
                    dist = sum([abs(color[i] - bg_color[i]) for i in range(3)])
                    
                    # Tolerance for compression artifacts, keeping it low for clean art
                    if dist < 30: 
                        # Make transparent
                        surface.set_at((x, y), (0, 0, 0, 0))
                    else:
                        # Assuming the icon is white/light, we want to keep it.
                        # But if the background was light, this might invert.
                        # Given user prompt "white icon", "grey background", 
                        # we assume background is darker than the icon or distinct.
                        pass
            
            # Save back
            pygame.image.save(surface, path)
            print(f"Processed {filename}: Removed background color {bg_color}")
            
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    print("Done.")
    pygame.quit()

if __name__ == "__main__":
    fix_transparency()
