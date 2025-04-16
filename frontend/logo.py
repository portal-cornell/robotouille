import pygame
from frontend.constants import LOADING
from frontend.image import Image
from frontend.screen import ScreenInterface
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend"))

class LogoScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the Logo Screen.

        Args:
           window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size)
        self.fade_alpha = 0
        self.fade_in_duration = 500
        self.fade_out_duration = 500
        self.delay = 1000
        self.wait = 1000
        self.start_time = None
        self.fade_in_complete = False
        self.fade_out_started = False
        self.fade_out_complete = False
        self.load_assets()
        self.background = Image(self.screen, self.background_image, self.x_percent(0), self.y_percent(0), self.scale_factor)
        self.background.set_alpha(0)

    def draw(self):
        """Draws all the screen components with fade-in and fade-out effects."""
        if self.start_time is None:
            self.start_time = pygame.time.get_ticks()

        elapsed_time = pygame.time.get_ticks() - self.start_time

        if not self.fade_in_complete:  # Fade in
            if elapsed_time > self.delay:
                fade_in_time = elapsed_time - self.delay
                alpha = min(255, int(255 * (fade_in_time / self.fade_in_duration)))
                if alpha >= 255:
                    self.fade_in_complete = True
                    self.start_time = pygame.time.get_ticks()  
                self.background.set_alpha(alpha)

        elif not self.fade_out_started:  # wait
            if elapsed_time > self.wait:
                self.fade_out_started = True
                self.start_time = pygame.time.get_ticks() 
                
        else:  # Fade out
            fade_out_time = pygame.time.get_ticks() - self.start_time
            alpha = max(0, 255 - int(255 * (fade_out_time / self.fade_out_duration)))
            if alpha <= 0:
                self.fade_out_complete = True
            self.background.set_alpha(alpha)

        self.background.draw()

    def load_assets(self):
        """Load necessary assets."""
        background_path = os.path.join(ASSETS_DIRECTORY, "logo.png")
        self.background_image = pygame.image.load(background_path).convert_alpha()

    def update(self):
        """Update the screen and handle events."""
        self.screen.fill((0, 0, 0))
        super().update()
        if self.fade_out_complete:
            self.set_next_screen(LOADING)
