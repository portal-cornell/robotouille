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

class EndScreen(ScreenInterface):
    def __init__(self, screen):
        super.__init__()
    
    def draw(self):
        """Draws all the screen components."""
        pass
    
    def load_assets(self):
        """Load necessary assets."""
        background_path = os.path.join(SHARED_DIRECTORY, "background.png")
        profile_path = os.path.join(ASSETS_DIRECTORY, "profile.png")
        bell_path = os.path.join(ASSETS_DIRECTORY, "bell.png")
        coin_path = os.path.join(ASSETS_DIRECTORY, "coin.png")
        pending_path = os.path.join(ASSETS_DIRECTORY, "pending.png")
        yes_path = os.path.join(ASSETS_DIRECTORY, "yes.png")
        no_path = os.path.join(ASSETS_DIRECTORY, "no.png")
        star_full_path = os.path.join(ASSETS_DIRECTORY, "star_full.png")
        star_empty_path = os.path.join(ASSETS_DIRECTORY, "star_empty.png")

        self.background_image = pygame.image.load(background_path).convert_alpha()
        self.profile_image =  pygame.image.load(profile_path).convert_alpha()
        self.bell_image =  pygame.image.load(bell_path).convert_alpha()
        self.coin_image =  pygame.image.load(coin_path).convert_alpha()
        self.pending_image =  pygame.image.load(pending_path).convert_alpha()
        self.yes_image =  pygame.image.load(yes_path).convert_alpha()
        self.no_image =  pygame.image.load(no_path).convert_alpha()
        self.star_full_image =  pygame.image.load(star_full_path).convert_alpha()
        self.star_empty_image =  pygame.image.load(star_empty_path).convert_alpha()
