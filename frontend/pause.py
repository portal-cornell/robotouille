import pygame
from frontend.constants import MAIN_MENU, GAME
from frontend.button import Button
from frontend.slider import Slider
from frontend.textbox import Textbox
from frontend.image import Image
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "pause_screen"))

class PauseScreen(ScreenInterface):
    def __init__(self, window_size, mouse_offset_x=0, mouse_offset_y=0):
        """
        Initialize the Main Menu Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size)
        self.background = Image(self.screen, self.background_image, self.x_percent(482), self.y_percent(209), self.scale_factor, anchor="topleft")
        self.title = Image(self.screen, self.title_image, self.x_percent(614), self.y_percent(179), self.scale_factor, anchor="topleft")
        self.pause_title = Textbox(self.screen,"PAUSED", self.x_percent(655), self.y_percent(194), 143, 48, font_size=40, scale_factor=self.scale_factor, anchor="topleft")
        
        self.music_title = Textbox(self.screen,"MUSIC", self.x_percent(556), self.y_percent(276.53), 335, 48, font_size=40, scale_factor=self.scale_factor, align_text="left")
        self.sfx_title = Textbox(self.screen,"SFX", self.x_percent(556), self.y_percent(381.81), 335, 48, font_size=40, scale_factor=self.scale_factor, align_text="left")
        self.music_plus_button = Button(self.screen, self.plus_button_image, self.x_percent(840), self.y_percent(326), self.scale_factor)
        self.music_minus_button = Button(self.screen, self.minus_button_image, self.x_percent(549), self.y_percent(326), self.scale_factor)
        self.music_slider = Slider(self.screen, self.bar_bg_image, self.bar_fg_image, 327.71, 37, 304, 25,
                                    self.x_percent(556), self.y_percent(333), scale_factor=self.scale_factor,
                                    foreground_padding=(10, 10, 0, 0), background_padding=(10, 10, 0, 0), anchor="topleft")
        self.sfx_plus_button = Button(self.screen, self.plus_button_image, self.x_percent(840), self.y_percent(430), self.scale_factor)
        self.sfx_minus_button = Button(self.screen, self.minus_button_image, self.x_percent(549), self.y_percent(430), self.scale_factor)
        self.sfx_slider = Slider(self.screen, self.bar_bg_image, self.bar_fg_image, 327.71, 37, 304, 25,
                                    self.x_percent(556), self.y_percent(437.81), scale_factor=self.scale_factor, 
                                    foreground_padding=(10, 10, 0, 0), background_padding=(10, 10, 0, 0),anchor="topleft")
        self.resume_button = Button(self.screen, self.resume_button_image, self.x_percent(556), self.y_percent(501.1), self.scale_factor)
        self.retry_button = Button(self.screen, self.retry_button_image, self.x_percent(556), self.y_percent(619), self.scale_factor)
        self.exit_button = Button(self.screen, self.back_image, self.x_percent(556 + 335/2), self.y_percent(619), self.scale_factor)

        self.hide = True
        self.p_key_was_pressed = False

    def load_assets(self):
        """
        Loads necessary assets.
        """
        # load asset paths then images
        self.background_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["background.png"]
        self.title_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["title.png"]
        self.bar_fg_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["bar_foreground.png"]
        self.bar_bg_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["bar_background.png"]

        self.retry_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["replay-button.png"]
        self.back_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["exit-button.png"]
        self.resume_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["play.png"]
        self.minus_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["minus.png"]
        self.plus_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["plus.png"]
    
    def draw(self):
        """Draws all the screen components."""
        if not self.hide:
            self.background.draw()
            self.title.draw()
            self.pause_title.draw()

            self.music_title.draw()
            self.sfx_title.draw()
            self.music_slider.draw()
            self.music_plus_button.draw()
            self.music_minus_button.draw()
            self.sfx_slider.draw()
            self.sfx_plus_button.draw()
            self.sfx_minus_button.draw()
            self.resume_button.draw()
            self.retry_button.draw()
            self.exit_button.draw()
        else:
            self.screen.fill((0, 0, 0, 0))

    def toggle(self):
        """
        Toggles the visibility of the pause screen.
        """
        self.hide = not self.hide

    def is_active(self):
        """
        Returns whether the pause screen is currently active (visible).
        """
        return not self.hide
    
    def update(self, events):
        """Update the screen and handle events."""
        self.draw()

        if self.hide:
            return
        
        for event in events:
            # Return to main menu when exit button is pressed.
            if self.exit_button.handle_event(event):
                self.set_next_screen(MAIN_MENU)
            
            # Hides the pause menu when resume button is pressed.
            if self.resume_button.handle_event(event):
                self.hide = True
            
            # Restarts the level if retry_button is pressed
            if self.retry_button.handle_event(event):
                self.set_next_screen(GAME)
            
            # Increase/decrease music volume if plus button and music minus button is pressed
            if self.music_minus_button.in_bound() and not self.music_slider.is_moving():
                if self.music_minus_button.handle_event(event):
                    self.music_slider.set_value(self.music_slider.get_value() - 0.1)
            elif self.music_plus_button.in_bound() and not self.music_slider.is_moving():
                if self.music_plus_button.handle_event(event):
                    self.music_slider.set_value(self.music_slider.get_value() + 0.1)
            else:
                # Increase/decrease music volume if slider is moved
                self.music_slider.handle_event(event)
    
            # Increase/decrease sfx volume if plus button and music minus button is pressed
            if self.sfx_minus_button.in_bound() and not self.sfx_slider.is_moving():
                if self.sfx_minus_button.handle_event(event):
                    self.sfx_slider.set_value(self.sfx_slider.get_value() - 0.1)
            elif self.sfx_plus_button.in_bound() and not self.sfx_slider.is_moving():
                if self.sfx_plus_button.handle_event(event):
                    self.sfx_slider.set_value(self.sfx_slider.get_value() + 0.1)
            else:
                # Increase/decrease sfx volume if slider is moved
                self.sfx_slider.handle_event(event)

