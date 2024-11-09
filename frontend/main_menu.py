import pygame
from frontend.constants import *
from frontend.button import Button
from frontend.image import Image
from frontend.screen import ScreenInterface

# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "main_menu")

class MenuScreen(ScreenInterface):
    def __init__(self, screen):
        """
        Initialize the Main Menu Screen.

        Args:
            screen (pygame.Surface): The display surface where the main menu screen components will be drawn.
        """
        super().__init__(screen)
        self.background = Image(screen, self.background_image, 0.5, 0.5, self.scale_factor)
        self.start_button = Button(screen, self.start_button_image, 
                                            self.x_percent(720), self.y_percent(392), self.scale_factor, 
                                            hover_image_source= self.start_hover_button_image,
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "START", text_color=WHITE)
        self.setting_button = Button(screen, self.start_button_image, 
                                            self.x_percent(720), self.y_percent(524), self.scale_factor,
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "SETTINGS", text_color=WHITE)
    def load_assets(self):
        """
        Loads necessary assets.
        """
        # load asset paths then images
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        start_button_path = os.path.join(SHARED_DIRECTORY, "button_b.png")
        start_hover_button_path = os.path.join(SHARED_DIRECTORY, "button_b_h.png")
        start_pressed_button_path = os.path.join(SHARED_DIRECTORY, "button_b_p.png")

        self.background_image =  pygame.image.load(background_path).convert_alpha()
        self.start_button_image = pygame.image.load(start_button_path).convert_alpha()
        self.start_hover_button_image = pygame.image.load(start_hover_button_path).convert_alpha()
        self.start_pressed_button_image = pygame.image.load(start_pressed_button_path).convert_alpha()
    
    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.start_button.draw()
        self.setting_button.draw()

    def update(self):
        """Update the screen and handle events."""
        super().update() 

        # Handle events
        for event in pygame.event.get():
            if self.start_button.handle_event(event):
                self.set_next_screen(GAME)
            if self.setting_button.handle_event(event):
                self.set_next_screen(SETTINGS)
