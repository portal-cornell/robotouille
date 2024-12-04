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
    def __init__(self, window_size):
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
        self.music_plus = Button(self.screen, self.plus_image, self.x_percent(840), self.y_percent(326), self.scale_factor)
        self.music_minus = Button(self.screen, self.minus_image, self.x_percent(549), self.y_percent(326), self.scale_factor)
        self.music_slider = Slider(self.screen, self.bar_bg_image, self.bar_fg_image, 327.71, 37, 304, 25,
                                       self.x_percent(556), self.y_percent(333), scale_factor= self.scale_factor, anchor="topleft")
        self.sfx_plus = Button(self.screen, self.plus_image, self.x_percent(840), self.y_percent(430), self.scale_factor)
        self.sfx_minus = Button(self.screen, self.minus_image, self.x_percent(549), self.y_percent(430), self.scale_factor)
        self.sfx_slider = Slider(self.screen, self.bar_bg_image, self.bar_fg_image, 327.71, 37, 304, 25,
                                       self.x_percent(556), self.y_percent(437.81), scale_factor= self.scale_factor, anchor="topleft")
        self.resume = Button(self.screen, self.resume_image, self.x_percent(556), self.y_percent(501.1), self.scale_factor)
        self.retry = Button(self.screen, self.retry_image, self.x_percent(556), self.y_percent(619), self.scale_factor)
        self.exit = Button(self.screen, self.back_image, self.x_percent(556 + 335/2), self.y_percent(619), self.scale_factor)

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

        self.retry_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["replay-button.png"]
        self.back_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["exit-button.png"]
        self.resume_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["play.png"]
        self.minus_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["minus.png"]
        self.plus_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["plus.png"]
    
    def draw(self):
        """Draws all the screen components."""
        if not self.hide:
            self.background.draw()
            self.title.draw()
            self.pause_title.draw()
            
            self.music_title.draw()
            self.sfx_title.draw()
            self.music_slider.draw()
            self.music_plus.draw()
            self.music_minus.draw()
            self.sfx_slider.draw()
            self.sfx_plus.draw()
            self.sfx_minus.draw()
            self.resume.draw()
            self.retry.draw()
            self.exit.draw()

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
            if self.exit.handle_event(event):
                self.set_next_screen(MAIN_MENU)
            
            if self.resume.handle_event(event):
                self.hide = True
            
            if self.retry.handle_event(event):
                self.set_next_screen(GAME)
            
            if self.music_plus.in_bound() and not self.music_slider.is_moving():
                if self.music_plus.handle_event(event):
                    self.music_slider.set_value(self.music_slider.get_value() + 0.1)
            elif self.music_plus.in_bound() and not self.music_slider.is_moving():
                if self.music_plus.handle_event(event):
                    self.music_slider.set_value(self.music_slider.get_value() - 0.1)
            else:
                self.music_slider.handle_event(event)
    
            if self.sfx_minus.in_bound() and not self.sfx_slider.is_moving():
                if self.sfx_minus.handle_event(event):
                    self.sfx_slider.set_value(self.sfx_slider.get_value() - 0.1)
            elif self.sfx_plus.in_bound() and not self.sfx_slider.is_moving():
                if self.sfx_plus.handle_event(event):
                    self.sfx_slider.set_value(self.sfx_slider.get_value() + 0.1)
            else:
                self.sfx_slider.handle_event(event)

