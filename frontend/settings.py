import pygame
from frontend.constants import SHARED_DIRECTORY, MAIN_MENU, FONT_PATH, WHITE, GREY, BLUE
from frontend.button import Button
from frontend.image import Image
from frontend.slider import Slider
from frontend.textbox import Textbox
from frontend.editable_textbox import EditableTextbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "settings"))

class SettingScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the settings screen.

        Args:
           window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size) 

       
        self.background = Image(self.screen, self.background_image, self.x_percent(0), self.y_percent(0), self.scale_factor, anchor="topleft")
        self.back_arrow = Button(self.screen, self.back_arrow_image, self.x_percent(64), self.y_percent(860), self.scale_factor, anchor="topleft")
        self.profile = Image(self.screen, self.profile_image, self.x_percent(746), self.y_percent(109), self.scale_factor, anchor="topleft")

        self.music_slider = Slider(self.screen, self.slider_bg_image, self.slider_fg_image, 442.01, 44.91, 390, 31.19,
                                self.x_percent(520), self.y_percent(324), scale_factor= self.scale_factor,
                                foreground_padding=(10, 10, 0, 0), background_padding=(10, 10, 0, 0), anchor="topleft")
        self.sfx_slider = Slider(self.screen, self.slider_bg_image, self.slider_fg_image, 442.01, 44.91, 390, 31.19,
                                self.x_percent(520), self.y_percent(509), scale_factor= self.scale_factor,
                                foreground_padding=(10, 10, 0, 0), background_padding=(10, 10, 0, 0), anchor="topleft")
       
        self.music_minus_button = Button(self.screen, self.minus_image, self.x_percent(499), self.y_percent(318), self.scale_factor, anchor="topleft")
        self.music_plus_button = Button(self.screen, self.plus_image, self.x_percent(905), self.y_percent(318), self.scale_factor, anchor="topleft")
        self.sfx_minus_button = Button(self.screen, self.minus_image, self.x_percent(499), self.y_percent(500), self.scale_factor, anchor="topleft")
        self.sfx_plus_button = Button(self.screen, self.plus_image, self.x_percent(905), self.y_percent(500), self.scale_factor, anchor="topleft")

        self.settings = Textbox(self.screen, "SETTINGS", self.x_percent(538), self.y_percent(75) , 364, 95, text_color=BLUE, font_size = 80, scale_factor= self.scale_factor, anchor="topleft")
        self.music = Textbox(self.screen, "MUSIC", self.x_percent(630), self.y_percent(247) , 188, 72, text_color=GREY, scale_factor= self.scale_factor, anchor="topleft")
        self.sfx = Textbox(self.screen, "SFX", self.x_percent(630), self.y_percent(437), 188, 72, text_color=GREY, scale_factor= self.scale_factor, anchor="topleft")
       
        self.tutorial = Button(self.screen, self.start_button_image,
                                            self.x_percent(563), self.y_percent(623), self.scale_factor,
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "TUTORIAL", font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")
        self.credits = Button(self.screen, self.start_button_image,
                                            self.x_percent(563), self.y_percent(760), self.scale_factor, 
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "CREDITS", font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")


        
    def load_assets(self):
        """Load necessary assets."""
        # Images
        self.background_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["background.png"]
        self.back_arrow_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["back_arrow.png"]
        self.slider_bg_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["sliderback.png"]
        self.slider_fg_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["sliderfore.png"]
        self.minus_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["minus.png"]
        self.plus_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["plus.png"]
        self.profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["button_profile.png"]
        self.start_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b.png"]
        self.start_hover_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_h.png"]
        self.start_pressed_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_p.png"]

    def draw(self):
        """Draws all the self.screen components."""
        self.background.draw()
        # self.profile.draw()
        self.back_arrow.draw()
        self.settings.draw()

        # volume & sfx 
        self.sfx_slider.draw()
        self.music_slider.draw()
        self.music_plus_button.draw()
        self.music_minus_button.draw()
        self.sfx_plus_button.draw()
        self.sfx_minus_button.draw()
        
      
        self.tutorial.draw()
        self.credits.draw()
        self.music.draw()
        self.sfx.draw()

  

    def update(self):
        """
        Update the settings self.screen and handle events.
        """
        super().update() 

        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(MAIN_MENU)
            
            # Increase/decrease volume if music plus button and music minus button is pressed
            if self.music_minus_button.in_bound() and not self.music_slider.is_moving():
                if self.music_minus_button.handle_event(event):
                    self.music_slider.set_value(self.music_slider.get_value() - 0.1)
            elif self.music_plus_button.in_bound() and not self.music_slider.is_moving():
                if self.music_plus_button.handle_event(event):
                    self.music_slider.set_value(self.music_slider.get_value() + 0.1)
            else:
                # Increase/decrease muisc volume if slider is moved
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


