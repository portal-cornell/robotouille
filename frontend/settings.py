import pygame
from frontend.constants import *
from frontend.button import Button
from frontend.image import Image
from frontend.slider import Slider
from frontend.textbox import Textbox
from frontend.editable_textbox import EditableTextbox
from frontend.screen import ScreenInterface

# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "settings")

class SettingScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the settings screen.

        Args:
           screen (pygame.Surface): The display surface where the settings self.screen components will be drawn.
        """
        super().__init__(pygame.Surface(window_size, pygame.SRCALPHA)) 

        self.zero_star_count = 0
        self.one_star_count = 0
        self.two_star_count = 0
        self.three_star_count = 0
        
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor)
        self.back_arrow = Button(self.screen, self.back_arrow_image, self.x_percent(64), self.y_percent(860), self.scale_factor)
        self.pencil = Button(self.screen, self.pencil_image, self.x_percent(1148.93), self.y_percent(173.525), self.scale_factor)
        self.profile = Image(self.screen, self.profile_image, self.x_percent(780.5), self.y_percent(169.5), self.scale_factor)

        self.sliderSFX = Slider(self.screen, self.slider_bg_image, self.slider_fg_image, 442.01, 44.91, 390, 31.19,
                                       self.x_percent(342.005), self.y_percent(459.455), scale_factor= self.scale_factor)
        self.sliderVolume = Slider(self.screen, self.slider_bg_image, self.slider_fg_image, 442.01, 44.91, 390, 31.19,
                                          self.x_percent(343), self.y_percent(274.195), scale_factor= self.scale_factor)
        
        self.VolumeMinus = Button(self.screen, self.minus_image, self.x_percent(144.505), self.y_percent(274.455), self.scale_factor)
        self.VolumePlus = Button(self.screen, self.plus_image, self.x_percent(541.505), self.y_percent(274.455), self.scale_factor)
        self.SFXMinus = Button(self.screen, self.minus_image, self.x_percent(143.505), self.y_percent(459.455), self.scale_factor)
        self.SFXPlus = Button(self.screen, self.plus_image, self.x_percent(540.505), self.y_percent(459.455), self.scale_factor)

        self.name = EditableTextbox(self.screen, "name", self.x_percent(983), self.y_percent(169) , 188, 72, align_text="left", scale_factor= self.scale_factor)
        self.music = Textbox(self.screen, "MUSIC", self.x_percent(327), self.y_percent(211) , 188, 72, scale_factor= self.scale_factor)
        self.sfx = Textbox(self.screen, "SFX", self.x_percent(327), self.y_percent(401), 188, 72, scale_factor= self.scale_factor)
        self.zero_star_score = Textbox(self.screen, str(self.zero_star_count), self.x_percent(1148), self.y_percent(449) , 188, 72, scale_factor= self.scale_factor)
        self.one_star_score = Textbox(self.screen,  str(self.one_star_count), self.x_percent(1148), self.y_percent(568) , 188, 72, scale_factor= self.scale_factor)
        self.two_star_score = Textbox(self.screen,  str(self.two_star_count), self.x_percent(1148), self.y_percent(683), 188, 72, scale_factor= self.scale_factor)
        self.three_star_score = Textbox(self.screen,  str(self.three_star_count), self.x_percent(1148), self.y_percent(780) , 188, 72, scale_factor= self.scale_factor)

        self.tutorial = Button(self.screen, self.start_button_image,
                                            self.x_percent(350), self.y_percent(601), self.scale_factor,
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "TUTORIAL", font_path=FONT_PATH, font_size=60, text_color=WHITE)
        self.credits = Button(self.screen, self.start_button_image,
                                            self.x_percent(350), self.y_percent(738), self.scale_factor, 
                                            hover_image_source= self.start_hover_button_image, 
                                            pressed_image_source= self.start_pressed_button_image, 
                                            text = "CREDITS", font_path=FONT_PATH, font_size=60, text_color=WHITE)

        self.zero_star = Image(self.screen, self.zero_star_image, self.x_percent(888.5), self.y_percent(449), self.scale_factor)
        self.one_star = Image(self.screen, self.one_star_image, self.x_percent(888.5), self.y_percent(568), self.scale_factor)
        self.two_star = Image(self.screen, self.two_star_image, self.x_percent(888.5), self.y_percent(683), self.scale_factor)
        self.three_star = Image(self.screen, self.three_star_image, self.x_percent(888.5), self.y_percent(780), self.scale_factor)


        
    def load_assets(self):
        """Load necessary assets."""

        # Construct Paths
        background_path = os.path.join(SHARED_DIRECTORY, "background.png")
        back_arrow_path = os.path.join(SHARED_DIRECTORY, "back_arrow.png")
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
        self.background_image = pygame.image.load(background_path).convert_alpha()
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
        """Draws all the self.screen components."""
        self.background.draw()
        # self.screen.fill(CYAN)
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
        Update the settings self.screen and handle events.
        """
        super().update() 

        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(MAIN_MENU)
            
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

            self.name.handle_event(event)
