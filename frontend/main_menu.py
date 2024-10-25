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


        self.background = image.Image(screen, background_image, 0, 0, scale_factor, anchor = "topleft")
        self.start_button = button.Button(screen, start_button_image, 0.5, 0.5, scale_factor, hover_color=constants.GREY)

    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.start_button.draw()
        pygame.display.flip()

    def update(self):
        """Update the screen and handle events."""
        self.draw()
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif self.start_button.is_clicked(event):
                self.set_next_screen(constants.GAME)

        # Handle keypresses 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.set_next_screen(constants.SETTINGS)