import pygame
from frontend import constants, screen, image, button
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend")

class LogoScreen(screen.ScreenInterface):
    def __init__(self, screen):
        super().__init__(screen)
        self.screen = screen
        self.fade_alpha = 0  
        self.fade_in_duration = 500 
        self.delay = 1000 
        self.start_time = None  
        self.fade_in_complete = False 
        self.load_assets()
        
    def draw(self):
        """Draws all the screen components with a fade-in effect."""
        if self.start_time is None:
            self.start_time = pygame.time.get_ticks() 

        elapsed_time = pygame.time.get_ticks() - self.start_time

        if elapsed_time > self.delay:
            fade_in_time = elapsed_time - self.delay
            alpha = min(255, int(255 * (fade_in_time / self.fade_in_duration)))  

            if alpha >= 255:
                self.fade_in_complete = True

            self.background.set_alpha(alpha)
            self.background.draw()
 

    def load_assets(self):
        """Load necessary assets."""
        background_path = os.path.join(ASSETS_DIRECTORY, "logo.png")
        self.background_image = pygame.image.load(background_path).convert_alpha()
        self.background = image.Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor)
        self.background.set_alpha(0)  # Start with the image fully transparent

    def update(self):
        """Update the screen and handle events."""
        super().update() 
        self.draw()
        # Handle events
        if self.fade_in_complete:
            self.set_next_screen(constants.MAIN_MENU)
