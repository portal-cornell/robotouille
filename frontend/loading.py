import pygame
from frontend.constants import *
from frontend.image import Image
from frontend.slider import Slider
from frontend.screen import ScreenInterface

# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "loading")

class LoadingScreen(ScreenInterface):
    def __init__(self, screen):
        """
        Initialize the Loading Screen.

        Args:
           screen (pygame.Surface): The display surface where the loading screen components will be drawn.
        """
        super().__init__(screen)
        self.percent = 0
        self.background = Image(screen, self.background_image, 0.5, 0.5, self.scale_factor)
        self.loading_bar = Slider(screen, self.progress_border_image, self.progress_bar_image,
                                         573 * self.scale_factor, 93 * self.scale_factor, 539 * self.scale_factor, 61 * self.scale_factor,
                                         0.5, 0.75, filled_percent= self.percent)
    
    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.loading_bar.draw()
    
    def load_assets(self):
        """Load necessary assets."""
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        progress_bar_path = os.path.join(ASSETS_DIRECTORY, "progress_bar.png")
        progress_border_path = os.path.join(ASSETS_DIRECTORY, "progress_border.png")

        self.background_image =  pygame.image.load(background_path).convert_alpha()
        self.progress_bar_image =  pygame.image.load(progress_bar_path).convert_alpha()
        self.progress_border_image =  pygame.image.load(progress_border_path).convert_alpha()

    def set_loading_percent(self, value):
        """
        Set the loading percentage for the loading bar.

        Args:
           value (float): The new percentage value to set on the loading bar (between 0 and 1).

        Side Effects:
        - Sets the new value on the loading bar slider.
        """

        self.percent = value
        self.loading_bar.setValue(self.percent)

    def update(self):
        """Update the screen and handle events."""
        super().update() 

        if self.percent >= 1:
            self.set_next_screen(MAIN_MENU)
        
        self.percent += 0.01
        self.loading_bar.setValue(self.percent)

        
