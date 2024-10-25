import pygame
from frontend import constants, screen, image, button
import os 
# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "settings")

class SettingScreen(screen.ScreenInterface):
    def __init__(self, screen):
        """Initialize the settings screen."""
        super().__init__() 
        self.screen = screen

         # load asset paths then images
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")

        background_image =  pygame.image.load(background_path).convert_alpha()
        
        # calculate the scale factor 
        screen_width, screen_height = self.screen.get_size()
        img_width, img_height = background_image.get_size()
        width_scale = screen_width / img_width
        height_scale = screen_height / img_height
        scale_factor = min(width_scale, height_scale)  

        self.background = image.Image(screen, background_image, 0, 0, scale_factor)

    
    def draw(self):
        self.background.draw()
        pygame.display.flip()
        
    def update(self):
        """Update the screen and handle keypress events."""
        self.draw()

        # Handle keypresses specific to the settings menu
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            self.set_next_screen(constants.MAIN_MENU)
