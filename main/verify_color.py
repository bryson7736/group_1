import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from story_mode import StoryManager

def verify():
    sm = StoryManager("test_progress.json")
    stage = sm.get_stage("1-2")
    if stage:
        print(f"Stage 1-2 Path Color: {stage.path_color}")
        if stage.path_color == (255, 0, 0):
            print("SUCCESS: Color is RED")
        else:
            print("FAILURE: Color is NOT RED")
    else:
        print("Stage 1-2 not found")

if __name__ == "__main__":
    verify()
