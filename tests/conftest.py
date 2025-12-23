import sys
import os
import pytest
import pygame

# Add RDproject to sys.path so tests can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../RDproject')))

@pytest.fixture(scope="session", autouse=True)
def mock_pygame_setup():
    """Mock pygame init and display for headless testing if needed, 
       or just ensure it's initialized."""
    # We can perform a headless setup for pygame if we strictly want to avoid window creation
    # or rely on the system. For simple unit tests causing no render, just init is often enough.
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()
