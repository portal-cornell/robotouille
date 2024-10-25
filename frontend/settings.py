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
        back_arrow_path = os.path.join(ASSETS_DIRECTORY, "back_arrow.png")

        background_image =  pygame.image.load(background_path).convert_alpha()
        back_arrow_image =  pygame.image.load(back_arrow_path).convert_alpha()
        
        # calculate the scale factor 
        screen_width, screen_height = self.screen.get_size()
        img_width, img_height = 1440, 1024
        width_scale = screen_width / img_width
        height_scale = screen_height / img_height
        scale_factor = min(width_scale, height_scale)  

        self.background = image.Image(screen, background_image, 0, 0, scale_factor, anchor = "topleft")
        self.back_arrow = button.Button(screen, back_arrow_image, 64/img_width, 860/img_height, scale_factor, hover_color=constants.GREY)

    
    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.back_arrow.draw()
        pygame.display.flip()

    def update(self):
        """Update the screen and handle keypress events."""
        self.draw()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif self.back_arrow.is_clicked(event):
                self.set_next_screen(constants.MAIN_MENU)

