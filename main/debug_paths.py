
import os
import sys

print(f"CWD: {os.getcwd()}")
print(f"__file__: {__file__}")

try:
    from settings import BASE_DIR, ASSETS_DIR, ASSET_FILES
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"ASSETS_DIR from settings: {ASSETS_DIR}")
except ImportError as e:
    print(f"ImportError settings: {e}")

try:
    from dice import ASSET_DIR as DICE_ASSET_DIR
    print(f"ASSET_DIR from dice: {DICE_ASSET_DIR}")
except ImportError as e:
    print(f"ImportError dice: {e}")

try:
    # Mimic main.py ASSET_DIR logic
    MAIN_ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    print(f"Calculated MAIN_ASSET_DIR: {MAIN_ASSET_DIR}")
    
    # Check for freeze dice
    freeze_path = os.path.join(MAIN_ASSET_DIR, "dice_freeze.png")
    print(f"Checking {freeze_path}...")
    if os.path.exists(freeze_path):
        print("EXISTS!")
    else:
        print("DOES NOT EXIST!")
        
except Exception as e:
    print(f"Exception: {e}")
