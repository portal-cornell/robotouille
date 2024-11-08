import pygame
from frontend import constants, screen, image, button, slider, textbox
import os 
# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "settings")
SHARED_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "shared")

class SettingScreen(screen.ScreenInterface):
    def __init__(self, screen):
        """
        Initialize the settings screen.

        Args:
           screen (pygame.Surface): The display surface where the settings screen components will be drawn.
        """
        super().__init__(screen) 

        self.zero_star_count = 0
        self.one_star_count = 0
        self.two_star_count = 0
        self.three_star_count = 0
    
        self.back_arrow = button.Button(screen, self.back_arrow_image, self.x_percent(64), self.y_percent(860), self.scale_factor)
        self.pencil = button.Button(screen, self.pencil_image, self.x_percent(1148.93), self.y_percent(173.525), self.scale_factor)
        self.profile = image.Image(screen, self.profile_image, self.x_percent(780.5), self.y_percent(169.5), self.scale_factor)

        self.sliderSFX = slider.Slider(screen, self.slider_bg_image, self.slider_fg_image, 442.01 * self.scale_factor, 44.91 * self.scale_factor, 390 * self.scale_factor, 31.19 * self.scale_factor,
                                       self.x_percent(342.005), self.y_percent(459.455))
        self.sliderVolume = slider.Slider(screen, self.slider_bg_image, self.slider_fg_image, 442.01 * self.scale_factor, 44.91 * self.scale_factor, 390 * self.scale_factor, 31.19 * self.scale_factor,
                                          self.x_percent(343), self.y_percent(274.195))
        
        self.VolumeMinus = button.Button(screen, self.minus_image, self.x_percent(144.505), self.y_percent(274.455), self.scale_factor)
        self.VolumePlus = button.Button(screen, self.plus_image, self.x_percent(541.505), self.y_percent(274.455), self.scale_factor)
        self.SFXMinus = button.Button(screen, self.minus_image, self.x_percent(143.505), self.y_percent(459.455), self.scale_factor)
        self.SFXPlus = button.Button(screen, self.plus_image, self.x_percent(540.505), self.y_percent(459.455), self.scale_factor)

        self.name = textbox.Textbox(screen, "name", self.font, self.x_percent(983), self.y_percent(169) , 188 * self.scale_factor, 72 * self.scale_factor)
        self.music = textbox.Textbox(screen, "MUSIC", self.font, self.x_percent(327), self.y_percent(211) , 188 * self.scale_factor, 72 * self.scale_factor)
        self.sfx = textbox.Textbox(screen, "SFX", self.font, self.x_percent(327), self.y_percent(401) , 188 * self.scale_factor, 72 * self.scale_factor)
        self.zero_star_score = textbox.Textbox(screen, str(self.zero_star_count), self.font, self.x_percent(1148), self.y_percent(449) , 188 * self.scale_factor, 72 * self.scale_factor)
        self.one_star_score = textbox.Textbox(screen,  str(self.one_star_count), self.font, self.x_percent(1148), self.y_percent(568) , 188 * self.scale_factor, 72 * self.scale_factor)
        self.two_star_score = textbox.Textbox(screen,  str(self.two_star_count), self.font, self.x_percent(1148), self.y_percent(683) , 188 * self.scale_factor, 72 * self.scale_factor)
        self.three_star_score = textbox.Textbox(screen,  str(self.three_star_count), self.font, self.x_percent(1148), self.y_percent(780) , 188 * self.scale_factor, 72 * self.scale_factor)

        self.tutorial = button.Button(screen, self.start_button_image,
                                            self.x_percent(350), self.y_percent(601), self.scale_factor,
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "TUTORIAL", font = self.font, text_color=constants.WHITE)
        self.credits = button.Button(screen, self.start_button_image,
                                            self.x_percent(350), self.y_percent(738), self.scale_factor, 
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "CREDITS", font = self.font, text_color=constants.WHITE)

        self.zero_star = image.Image(screen, self.zero_star_image, self.x_percent(888.5), self.y_percent(449), self.scale_factor)
        self.one_star = image.Image(screen, self.one_star_image, self.x_percent(888.5), self.y_percent(568), self.scale_factor)
        self.two_star = image.Image(screen, self.two_star_image, self.x_percent(888.5), self.y_percent(683), self.scale_factor)
        self.three_star = image.Image(screen, self.three_star_image, self.x_percent(888.5), self.y_percent(780), self.scale_factor)


        
    def load_assets(self):
        """Load necessary assets."""
        font_path = os.path.join(SHARED_DIRECTORY, "hug.ttf")
        self.font = pygame.font.Font(font_path, int(60 * self.scale_factor))

        # Construct Paths
        back_arrow_path = os.path.join(ASSETS_DIRECTORY, "back_arrow.png")
        slider_bg_path = os.path.join(ASSETS_DIRECTORY, "sliderback.png")
        slider_fg_path = os.path.join(ASSETS_DIRECTORY, "sliderfore.png")
        minus_path = os.path.join(ASSETS_DIRECTORY, "minus.png")
        plus_path = os.path.join(ASSETS_DIRECTORY, "plus.png")
        profile_path = os.path.join(ASSETS_DIRECTORY, "button_profile.png")
        pencil_path = os.path.join(ASSETS_DIRECTORY, "pencil.png")
        start_button_path = os.path.join(SHARED_DIRECTORY, "button_b.png")
        start_hover_button_path = os.path.join(SHARED_DIRECTORY, "button_b_h.png")
        start_pressed_button_path = os.path.join(SHARED_DIRECTORY, "button_b_p.png")
        zero_star_path = os.path.join(ASSETS_DIRECTORY, "zero_star.png")
        one_star_path = os.path.join(ASSETS_DIRECTORY, "one_star.png")
        two_star_path = os.path.join(ASSETS_DIRECTORY, "two_star.png")
        three_star_path = os.path.join(ASSETS_DIRECTORY, "three_star.png")
        

        # images
        self.start_button_image = pygame.image.load(start_button_path).convert_alpha()
        self.start_hover_button_image = pygame.image.load(start_hover_button_path).convert_alpha()
        self.start_pressed_button_image = pygame.image.load(start_pressed_button_path).convert_alpha()
        self.back_arrow_image = pygame.image.load(back_arrow_path).convert_alpha()
        self.slider_bg_image = pygame.image.load(slider_bg_path).convert_alpha()
        self.slider_fg_image = pygame.image.load(slider_fg_path).convert_alpha()
        self.plus_image = pygame.image.load(plus_path).convert_alpha()
        self.minus_image = pygame.image.load(minus_path).convert_alpha()
        self.profile_image = pygame.image.load(profile_path).convert_alpha()
        self.pencil_image = pygame.image.load(pencil_path).convert_alpha()
        self.zero_star_image = pygame.image.load(zero_star_path).convert_alpha()
        self.one_star_image = pygame.image.load(one_star_path).convert_alpha()
        self.two_star_image = pygame.image.load(two_star_path).convert_alpha()
        self.three_star_image = pygame.image.load(three_star_path).convert_alpha()
        

    def draw(self):
        """Draws all the screen components."""
        # self.background.draw()
        self.screen.fill(constants.CYAN)
        self.profile.draw()
        self.pencil.draw()
        self.back_arrow.draw()

        # volume & sfx 
        self.sliderSFX.draw()
        self.sliderVolume.draw()
        self.VolumePlus.draw()
        self.VolumeMinus.draw()
        self.SFXPlus.draw()
        self.SFXMinus.draw()
        
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
        Update the settings screen and handle events.
        """
        super().update() 

        # Handle events
        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(constants.MAIN_MENU)
            
            if self.VolumeMinus.in_bound() and not self.sliderVolume.is_moving():
                if self.VolumeMinus.handle_event(event):
                    self.sliderVolume.setValue(self.sliderVolume.getValue() - 0.1)
            elif self.VolumePlus.in_bound() and not self.sliderVolume.is_moving():
                if self.VolumePlus.handle_event(event):
                    self.sliderVolume.setValue(self.sliderVolume.getValue() + 0.1)
            else:
                self.sliderVolume.handle_event(event)
    
            if self.SFXMinus.in_bound() and not self.sliderSFX.is_moving():
                if self.SFXMinus.handle_event(event):
                    self.sliderSFX.setValue(self.sliderSFX.getValue() - 0.1)
            elif self.SFXPlus.in_bound() and not self.sliderSFX.is_moving():
                if self.SFXPlus.handle_event(event):
                    self.sliderSFX.setValue(self.sliderSFX.getValue() + 0.1)
            else:
                self.sliderSFX.handle_event(event)

            # handle textbox
            if self.pencil.handle_event(event):
                self.name.toggle_editing() 
            self.name.handle_event(event)
