import pygame
from frontend.constants import WHITE, SHARED_DIRECTORY, MATCHMAKING, SETTINGS
from frontend.button import Button
from frontend.image import Image
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "main_menu"))

class MenuScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the Main Menu Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size) 
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.start_button = Button(self.screen, self.start_button_image, 
                                            self.x_percent(720), self.y_percent(392), self.scale_factor, 
                                            hover_image_source= self.start_hover_button_image,
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "START", text_color=WHITE, anchor="center")
        self.setting_button = Button(self.screen, self.start_button_image, 
                                            self.x_percent(720), self.y_percent(524), self.scale_factor,
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "SETTINGS", text_color=WHITE, anchor="center")
    def load_assets(self):
        """
        Loads necessary assets.
        """
        # load asset paths then images
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        start_button_path = os.path.join(SHARED_DIRECTORY, "button_b.png")
        start_hover_button_path = os.path.join(SHARED_DIRECTORY, "button_b_h.png")
        start_pressed_button_path = os.path.join(SHARED_DIRECTORY, "button_b_p.png")

        self.background_image = LoadingScreen.ASSET[background_path]
        self.start_button_image = LoadingScreen.ASSET[start_button_path]
        self.start_hover_button_image = LoadingScreen.ASSET[start_hover_button_path]
        self.start_pressed_button_image = LoadingScreen.ASSET[start_pressed_button_path]
    
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
                self.set_next_screen(MATCHMAKING)
            if self.setting_button.handle_event(event):
                self.set_next_screen(SETTINGS)
