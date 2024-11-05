import pygame
from frontend import constants, screen, image, button, slider, textbox
import os 
# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "settings")
GENERAL_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend")

class SettingScreen(screen.ScreenInterface):
    def __init__(self, screen):
        """Initialize the settings screen."""
        super().__init__(screen) 

        font_path = os.path.join(GENERAL_DIRECTORY, "hug.ttf")
        font = pygame.font.Font(font_path, 48)

        # load asset paths then images
        # background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        back_arrow_path = os.path.join(ASSETS_DIRECTORY, "back_arrow.png")

        slider_bg_path = os.path.join(ASSETS_DIRECTORY, "sliderback.png")
        slider_fg_path = os.path.join(ASSETS_DIRECTORY, "sliderfore.png")
        # slider_knob_path = os.path.join(ASSETS_DIRECTORY, "knob.png")
        minus_path = os.path.join(ASSETS_DIRECTORY, "minus.png")
        plus_path = os.path.join(ASSETS_DIRECTORY, "plus.png")
        profile_path = os.path.join(ASSETS_DIRECTORY, "button_profile.png")
        pencil_path = os.path.join(ASSETS_DIRECTORY, "pencil.png")

        # background_image = pygame.image.load(background_path).convert_alpha()
        back_arrow_image = pygame.image.load(back_arrow_path).convert_alpha()

        slider_bg_image = pygame.image.load(slider_bg_path).convert_alpha()
        slider_fg_image = pygame.image.load(slider_fg_path).convert_alpha()
        # slider_knob_image = pygame.image.load(slider_knob_path).convert_alpha()
        plus_image = pygame.image.load(plus_path).convert_alpha()
        minus_image = pygame.image.load(minus_path).convert_alpha()
        profile_image = pygame.image.load(profile_path).convert_alpha()
        pencil_image = pygame.image.load(pencil_path).convert_alpha()
    

        # backgrounds
        # self.background = image.Image(screen, background_image, 0.5, 0.5, self.scale_factor)
        self.back_arrow = button.Button(screen, back_arrow_image, back_arrow_image, back_arrow_image, self.x_percent(64), self.y_percent(860), self.scale_factor)
        self.pencil = button.Button(screen, pencil_image, pencil_image, pencil_image, self.x_percent(1148.93), self.y_percent(173.525), self.scale_factor)
        self.profile = image.Image(screen, profile_image, self.x_percent(780.5), self.y_percent(169.5), self.scale_factor)

        # sliders
        self.sliderSFX = slider.Slider(screen, slider_bg_image, slider_fg_image, 442.01 * self.scale_factor, 44.91 * self.scale_factor, 
                                       self.x_percent(342.005), self.y_percent(459.455), self.scale_factor)
        self.sliderVolume = slider.Slider(screen, slider_bg_image, slider_fg_image, 442.01 * self.scale_factor, 44.91 * self.scale_factor,
                                          self.x_percent(343), self.y_percent(274.195), self.scale_factor)
        
        # volume buttons 
        self.VolumeMinus = button.Button(screen, minus_image, minus_image, minus_image, self.x_percent(144.505), self.y_percent(274.455), self.scale_factor)
        self.VolumePlus = button.Button(screen, plus_image, plus_image, plus_image, self.x_percent(541.505), self.y_percent(274.455), self.scale_factor)
        self.SFXMinus = button.Button(screen, minus_image, minus_image, minus_image, self.x_percent(143.505), self.y_percent(459.455), self.scale_factor)
        self.SFXPlus = button.Button(screen, plus_image, plus_image, plus_image, self.x_percent(540.505), self.y_percent(459.455), self.scale_factor)

        self.name = textbox.Textbox(screen, "name", font, self.x_percent(983), self.y_percent(169) , 188 * self.scale_factor, 72 * self.scale_factor)
        
        
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

    def update(self):
        """Update the screen and handle keypress events."""
        super().update() 
        self.draw()

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



