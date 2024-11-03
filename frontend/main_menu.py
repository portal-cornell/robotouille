import pygame
from frontend import constants, screen, image, button
import os
# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "main_menu")
GENERAL_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend")

class MenuScreen(screen.ScreenInterface):
    def __init__(self, screen):
        """Initialize the main menu screen."""
        super().__init__()
        self.screen = screen
        
        # load asset paths then images
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        start_button_path = os.path.join(ASSETS_DIRECTORY, "start_button.png")
        start_hover_button_path = os.path.join(ASSETS_DIRECTORY, "hover.png")
        start_pressed_button_path = os.path.join(ASSETS_DIRECTORY, "pressed.png")
        font_path = os.path.join(GENERAL_DIRECTORY, "hug.ttf")

        background_image =  pygame.image.load(background_path).convert_alpha()
        start_button_image = pygame.image.load(start_button_path).convert_alpha()
        start_hover_button_image = pygame.image.load(start_hover_button_path).convert_alpha()
        start_pressed_button_image = pygame.image.load(start_pressed_button_path).convert_alpha()

        font = pygame.font.Font(font_path, 48)
        
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
        self.start_button = button.Button(screen, start_button_image, start_hover_button_image, start_pressed_button_image, offset_x + 720/img_width, offset_y + 392/img_height, scale_factor, text = "START", font = font, text_color=constants.WHITE)
        self.setting_button = button.Button(screen, start_button_image, start_hover_button_image, start_pressed_button_image, offset_x + 720/img_width, offset_y + 524/img_height, scale_factor, text = "SETTINGS", font = font, text_color=constants.WHITE)

    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.start_button.draw()
        self.setting_button.draw()
        pygame.display.flip()

    def update(self):
        """Update the screen and handle events."""
        super().update() 
        self.draw()
        # Handle events
        for event in pygame.event.get():
            if self.start_button.handle_event(event):
                self.set_next_screen(constants.GAME)
            if self.setting_button.handle_event(event):
                self.set_next_screen(constants.SETTINGS)

        # # Handle keypresses 
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_s]:
        #     self.set_next_screen(constants.SETTINGS)