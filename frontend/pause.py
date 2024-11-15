import pygame
from frontend.constants import *
from frontend.button import Button
from frontend.textbox import Textbox
from frontend.image import Image
from frontend.screen import ScreenInterface

# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "pause_screen")

class PauseScreen(ScreenInterface):
    def __init__(self, screen):
        """
        Initialize the Main Menu Screen.

        Args:
            screen (pygame.Surface): The display surface where the main menu screen components will be drawn.
        """
        super().__init__(screen)
        self.background = Image(screen, self.background_image, self.x_percent(482 + 475.76/2), self.y_percent(209 + 572.94/2), self.scale_factor)
        self.title = Image(screen, self.title_image, self.x_percent(727), self.y_percent(218), self.scale_factor)
        self.pause_title = Textbox(self.screen,"PAUSED", self.x_percent(727), self.y_percent(218), 188, 72, font_size=40, scale_factor=self.scale_factor), 
        self.background = Image(screen, self.background_image, 0.5, 0.5, self.scale_factor)
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
        self.background.draw()
        self.title.draw()

    def toggle(self):
        self.hide = not self.hide
        print('toggle', self.hide)

    def update(self):
        """Update the screen and handle events."""
        if not self.hide:
            self.draw()
    