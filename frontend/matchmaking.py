import pygame
from frontend.constants import *
from frontend.button import Button
from frontend.image import Image
from frontend.slider import Slider
from frontend.textbox import Textbox
from frontend.editable_textbox import EditableTextbox
from frontend.screen import ScreenInterface

# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "main_menu")

class MatchMakingScreen(ScreenInterface):
    def __init__(self, screen):
        pass
    
    def draw(self):
        """Draws all the screen components."""
        pass
    
    def load_assets(self):
        """Load necessary assets."""
        pass