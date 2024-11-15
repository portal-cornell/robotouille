import pygame
from frontend.constants import *
from frontend.button import Button
from frontend.textbox import Textbox
from frontend.image import Image
from frontend.screen import ScreenInterface

# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "pause_screen")

class PauseScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the Main Menu Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(pygame.Surface(window_size, pygame.SRCALPHA))
        self.background = Image(self.screen, self.background_image, self.x_percent(482), self.y_percent(209), self.scale_factor, anchor="topleft")
        self.title = Image(self.screen, self.title_image, self.x_percent(614), self.y_percent(179), self.scale_factor, anchor="topleft")
        self.pause_title = Textbox(self.screen,"PAUSED", self.x_percent(655), self.y_percent(194), 143, 48, font_size=40, scale_factor=self.scale_factor, anchor="topleft")
        self.hide = True
        self.p_key_was_pressed = False

        self.hide = True
        self.p_key_was_pressed = False

    def load_assets(self):
        """
        Loads necessary assets.
        """
        # load asset paths then images
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        title_path = os.path.join(ASSETS_DIRECTORY, "title.png")
        bar_foreground_path = os.path.join(ASSETS_DIRECTORY, "bar_foreground.png")
        bar_background_path = os.path.join(ASSETS_DIRECTORY, "bar_background.png")

        self.background_image =  pygame.image.load(background_path).convert_alpha()
        self.title_image = pygame.image.load(title_path).convert_alpha()
        self.bar_fg_image = pygame.image.load(bar_foreground_path).convert_alpha()
        self.bar_bg_image = pygame.image.load(bar_background_path).convert_alpha()
    
    def draw(self):
        """Draws all the screen components."""
        if not self.hide:
            self.background.draw()
            self.title.draw()
            self.pause_title.draw()
        else:
            self.screen.fill((0, 0, 0, 0))

    def toggle(self):
        self.hide = not self.hide


    def update(self):
        """Update the screen and handle events."""
        self.draw()

    