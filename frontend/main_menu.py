import pygame
from frontend import constants, screen, image, button
import os
# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "main_menu")

class MenuScreen(screen.ScreenInterface):
    def __init__(self, screen):
        """Initialize the main menu screen."""
        super().__init__()
        self.screen = screen
        
        # load asset paths then images
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        start_button_path = os.path.join(ASSETS_DIRECTORY, "start_button.png")

        background_image =  pygame.image.load(background_path).convert_alpha()
        start_button_image = pygame.image.load(start_button_path).convert_alpha()
        
        # calculate the scale factor 
        screen_width, screen_height = self.screen.get_size()
        img_width, img_height = 1440, 1024
        width_scale = screen_width / img_width
        height_scale = screen_height / img_height
        scale_factor = min(width_scale, height_scale)  

        background_width = background_image.get_width() * scale_factor
        background_height = background_image.get_height() * scale_factor

        offset_x = (screen_width - background_width) / (2 * screen_width)
        offset_y = (screen_height - background_height) / (2 * screen_height)

        self.background = image.Image(screen, background_image, 0.5, 0.5, scale_factor)
        self.start_button = button.Button(screen, start_button_image, start_button_image, start_button_image, 0.5, 0.5, scale_factor)

    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.start_button.draw()
        pygame.display.flip()

    def update(self):
        """Update the screen and handle events."""
        super().update() 
        self.draw()
        # Handle events
        for event in pygame.event.get():
            if self.start_button.handle_event(event):
                self.set_next_screen(constants.GAME)

        # Handle keypresses 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.set_next_screen(constants.SETTINGS)