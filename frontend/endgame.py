import pygame
from frontend import constants, screen, image, button
import os
# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "main_menu")
SHARED_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "shared")

class EndScreen(screen.ScreenInterface):
    def __init__(self, screen):
        pass
    
    def draw(self):
        """Draws all the screen components."""
        pass
    
    def load_assets(self):
        """Load necessary assets."""
        pass