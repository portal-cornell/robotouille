import pygame
from frontend.constants import SHARED_DIRECTORY, MAIN_MENU, FONT_PATH, WHITE, SETTINGS, BLUE
from frontend.button import Button
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.editable_textbox import EditableTextbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "profile"))


class ProfileScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the Profile Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size) 
        self.zero_star_count = 0
        self.one_star_count = 0
        self.two_star_count = 0
        self.three_star_count = 0
       
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.back_arrow = Button(self.screen, self.back_arrow_image, self.x_percent(64), self.y_percent(860), self.scale_factor, anchor="topleft")

        self.avatar = Button(self.screen, self.start_button_image,
                                            self.x_percent(362), self.y_percent(61), self.scale_factor,
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "AVATAR", font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")
        self.stats = Button(self.screen, self.start_button_image,
                                            self.x_percent(750), self.y_percent(61), self.scale_factor, 
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "STATS", font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")
        self.name_bg = Image(self.screen, self.name_bg_image, self.x_percent(500), self.y_percent(195), self.scale_factor, anchor="topleft")
        self.name = EditableTextbox(self.screen, "NAME", self.x_percent(600), self.y_percent(195) , 355, 72, align_text="left", scale_factor= self.scale_factor)
    
        self.zero_star = Image(self.screen, self.zero_star_image, self.x_percent(500), self.y_percent(456), self.scale_factor, anchor="topleft")
        self.one_star = Image(self.screen, self.one_star_image, self.x_percent(500), self.y_percent(565), self.scale_factor, anchor="topleft")
        self.two_star = Image(self.screen, self.two_star_image, self.x_percent(500), self.y_percent(678), self.scale_factor, anchor="topleft")
        self.three_star = Image(self.screen, self.three_star_image, self.x_percent(500), self.y_percent(785), self.scale_factor, anchor="topleft")

        self.zero_star_score = Textbox(self.screen, str(self.zero_star_count), self.x_percent(808), self.y_percent(468) , 188, 72, scale_factor= self.scale_factor, anchor="topleft")
        self.one_star_score = Textbox(self.screen,  str(self.one_star_count), self.x_percent(808), self.y_percent(587) , 188, 72, scale_factor= self.scale_factor, anchor="topleft")
        self.two_star_score = Textbox(self.screen,  str(self.two_star_count), self.x_percent(808), self.y_percent(702), 188, 72, scale_factor= self.scale_factor, anchor="topleft")
        self.three_star_score = Textbox(self.screen,  str(self.three_star_count), self.x_percent(808), self.y_percent(809) , 188, 72, scale_factor= self.scale_factor, anchor="topleft")

        self.showing_avatar = True
        self.showing_stats = False  


    def load_assets(self):
        """
        Loads necessary assets.
        """
        self.background_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["background.png"]
        self.start_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b.png"]
        self.start_hover_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_h.png"]
        self.start_pressed_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_p.png"]
        self.back_arrow_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["back_arrow.png"]

        self.name_bg_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["name_bg.png"]
        
        self.zero_star_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["zero_star.png"]
        self.one_star_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["one_star.png"]
        self.two_star_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["two_star.png"]
        self.three_star_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["three_star.png"]
        
    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.back_arrow.draw()
        self.avatar.draw()
        self.stats.draw()

        if self.showing_avatar:
          self.name_bg.draw()
          self.name.draw()

        if self.showing_stats:
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
        """Update the screen and handle events."""
        super().update() 
       
        # Handle events
        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(MAIN_MENU)
            if self.avatar.handle_event(event):
                self.showing_avatar = True
                self.showing_stats = False 
            if self.stats.handle_event(event):
                self.showing_stats = True  
                self.showing_avatar = False
            self.name.handle_event(event)