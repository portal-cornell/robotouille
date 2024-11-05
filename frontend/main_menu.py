import pygame
from frontend import constants, screen, image, button
import os
# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "main_menu")
SHARED_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "shared")

class MenuScreen(screen.ScreenInterface):
    def __init__(self, screen):
        """Initialize the main menu screen."""
        super().__init__(screen)
        self.background = image.Image(screen, self.background_image, 0.5, 0.5, self.scale_factor)
        self.start_button = button.Button(screen, self.start_button_image, 
                                            self.start_hover_button_image, self.start_pressed_button_image, 
                                            self.x_percent(720), self.y_percent(392),
                                            self.scale_factor, text = "START", font = self.font, text_color=constants.WHITE)
        self.setting_button = button.Button(screen, self.start_button_image, self.start_hover_button_image, 
                                            self.start_pressed_button_image, 
                                            self.x_percent(720), self.y_percent(524), self.scale_factor, text = "SETTINGS", 
                                            font = self.font, text_color=constants.WHITE)
    def load_assets(self):
        # load asset paths then images
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        start_button_path = os.path.join(SHARED_DIRECTORY, "button_b.png")
        start_hover_button_path = os.path.join(SHARED_DIRECTORY, "button_b_h.png")
        start_pressed_button_path = os.path.join(SHARED_DIRECTORY, "button_b_p.png")
        font_path = os.path.join(SHARED_DIRECTORY, "hug.ttf")

        self.background_image =  pygame.image.load(background_path).convert_alpha()
        self.start_button_image = pygame.image.load(start_button_path).convert_alpha()
        self.start_hover_button_image = pygame.image.load(start_hover_button_path).convert_alpha()
        self.start_pressed_button_image = pygame.image.load(start_pressed_button_path).convert_alpha()

        self.font = pygame.font.Font(font_path, int(60 * self.scale_factor))
    
    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.start_button.draw()
        self.setting_button.draw()

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