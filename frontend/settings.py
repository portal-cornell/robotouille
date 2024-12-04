import pygame
from frontend.constants import SHARED_DIRECTORY, MAIN_MENU, FONT_PATH, WHITE
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

        self.zero_star_count = 0
        self.one_star_count = 0
        self.two_star_count = 0
        self.three_star_count = 0
        self.background = Image(self.screen, self.background_image, self.x_percent(0), self.y_percent(0), self.scale_factor, anchor="topleft")
        self.back_arrow = Button(self.screen, self.back_arrow_image, self.x_percent(64), self.y_percent(860), self.scale_factor, anchor="topleft")
        self.profile = Image(self.screen, self.profile_image, self.x_percent(746), self.y_percent(109), self.scale_factor, anchor="topleft")

        self.sliderSFX = Slider(self.screen, self.slider_bg_image, self.slider_fg_image, 442.01, 44.91, 390, 31.19,
                                       self.x_percent(122), self.y_percent(437), scale_factor= self.scale_factor, anchor="topleft")
        self.sliderVolume = Slider(self.screen, self.slider_bg_image, self.slider_fg_image, 442.01, 44.91, 390, 31.19,
                                          self.x_percent(122), self.y_percent(252), scale_factor= self.scale_factor, anchor="topleft")
        
        self.VolumeMinus = Button(self.screen, self.minus_image, self.x_percent(122), self.y_percent(252), self.scale_factor, anchor="topleft")
        self.VolumePlus = Button(self.screen, self.plus_image, self.x_percent(519), self.y_percent(252), self.scale_factor, anchor="topleft")
        self.SFXMinus = Button(self.screen, self.minus_image, self.x_percent(122), self.y_percent(437), self.scale_factor, anchor="topleft")
        self.SFXPlus = Button(self.screen, self.plus_image, self.x_percent(519), self.y_percent(437), self.scale_factor, anchor="topleft")

        self.name_bg = Image(self.screen, self.name_bg_image, self.x_percent(917), self.y_percent(132), self.scale_factor, anchor="topleft")
        self.name = EditableTextbox(self.screen, "name", self.x_percent(928), self.y_percent(139) , 355, 72, align_text="left", scale_factor= self.scale_factor)
        self.music = Textbox(self.screen, "MUSIC", self.x_percent(233), self.y_percent(175) , 188, 72, scale_factor= self.scale_factor, anchor="topleft")
        self.sfx = Textbox(self.screen, "SFX", self.x_percent(233), self.y_percent(365), 188, 72, scale_factor= self.scale_factor, anchor="topleft")
        self.zero_star_score = Textbox(self.screen, str(self.zero_star_count), self.x_percent(1115), self.y_percent(413) , 188, 72, scale_factor= self.scale_factor, anchor="topleft")
        self.one_star_score = Textbox(self.screen,  str(self.one_star_count), self.x_percent(1115), self.y_percent(532) , 188, 72, scale_factor= self.scale_factor, anchor="topleft")
        self.two_star_score = Textbox(self.screen,  str(self.two_star_count), self.x_percent(1115), self.y_percent(647), 188, 72, scale_factor= self.scale_factor, anchor="topleft")
        self.three_star_score = Textbox(self.screen,  str(self.three_star_count), self.x_percent(1115), self.y_percent(744) , 188, 72, scale_factor= self.scale_factor, anchor="topleft")

        self.tutorial = Button(self.screen, self.start_button_image,
                                            self.x_percent(186), self.y_percent(551), self.scale_factor,
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "TUTORIAL", font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")
        self.credits = Button(self.screen, self.start_button_image,
                                            self.x_percent(186), self.y_percent(688), self.scale_factor, 
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "CREDITS", font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")

        self.zero_star = Image(self.screen, self.zero_star_image, self.x_percent(807), self.y_percent(401), self.scale_factor, anchor="topleft")
        self.one_star = Image(self.screen, self.one_star_image, self.x_percent(807), self.y_percent(510), self.scale_factor, anchor="topleft")
        self.two_star = Image(self.screen, self.two_star_image, self.x_percent(807), self.y_percent(623), self.scale_factor, anchor="topleft")
        self.three_star = Image(self.screen, self.three_star_image, self.x_percent(807), self.y_percent(720), self.scale_factor, anchor="topleft")


        
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
        self.name_bg_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["name_bg.png"]
        self.start_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b.png"]
        self.start_hover_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_h.png"]
        self.start_pressed_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_p.png"]
        self.zero_star_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["zero_star.png"]
        self.one_star_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["one_star.png"]
        self.two_star_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["two_star.png"]
        self.three_star_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["three_star.png"]
        
    def draw(self):
        """Draws all the self.screen components."""
        self.background.draw()
        self.profile.draw()
        self.back_arrow.draw()

        # volume & sfx 
        self.sliderSFX.draw()
        self.sliderVolume.draw()
        self.VolumePlus.draw()
        self.VolumeMinus.draw()
        self.SFXPlus.draw()
        self.SFXMinus.draw()
        
        self.name_bg.draw()
        self.name.draw()
        self.tutorial.draw()
        self.credits.draw()
        self.music.draw()
        self.sfx.draw()

        self.zero_star.draw()
        self.one_star.draw()
        self.two_star.draw()
        self.three_star.draw()
        
        self.zero_star_score.draw()
        self.one_star_score.draw()
        self.two_star_score.draw()
        self.three_star_score.draw()


    def increment_zero_star(self):
        """
        Increment the zero-star count and update the display.
        """
        self.zero_star_count += 1
        self.zero_star_score.set_text(str(self.zero_star_count))
    
    def increment_one_star(self):
        """
        Increment the one-star count and update the display.
        """
        self.one_star_count += 1
        self.one_star_score.set_text(str(self.one_star_count))
        
    def increment_two_star(self):
        """
        Increment the two-star count and update the display.
        """
        self.two_star_count += 1
        self.two_star_score.set_text(str(self.two_star_count))

    def increment_three_star(self):
        """
        Increment the three-star count and update the display.
        """
        self.three_star_count += 1
        self.three_star_score.set_text(str(self.three_star_count))


    def update(self):
        """
        Update the settings self.screen and handle events.
        """
        super().update() 

        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(MAIN_MENU)
            
            if self.VolumeMinus.in_bound() and not self.sliderVolume.is_moving():
                if self.VolumeMinus.handle_event(event):
                    self.sliderVolume.set_value(self.sliderVolume.get_value() - 0.1)
            elif self.VolumePlus.in_bound() and not self.sliderVolume.is_moving():
                if self.VolumePlus.handle_event(event):
                    self.sliderVolume.set_value(self.sliderVolume.get_value() + 0.1)
            else:
                self.sliderVolume.handle_event(event)
    
            if self.SFXMinus.in_bound() and not self.sliderSFX.is_moving():
                if self.SFXMinus.handle_event(event):
                    self.sliderSFX.set_value(self.sliderSFX.get_value() - 0.1)
            elif self.SFXPlus.in_bound() and not self.sliderSFX.is_moving():
                if self.SFXPlus.handle_event(event):
                    self.sliderSFX.set_value(self.sliderSFX.get_value() + 0.1)
            else:
                self.sliderSFX.handle_event(event)

            self.name.handle_event(event)
