import pygame
from frontend import constants, screen, image, button, slider
import os 
# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "settings")

class SettingScreen(screen.ScreenInterface):
    def __init__(self, screen):
        """Initialize the settings screen."""
        super().__init__() 
        self.screen = screen

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
        
        screen_width, screen_height = self.screen.get_size()
        img_width, img_height = 1440, 1024
        width_scale = screen_width / img_width
        height_scale = screen_height / img_height
        scale_factor = min(width_scale, height_scale)  

        background_width = scale_factor * 1440
        background_height = scale_factor * 1024

        offset_x = (screen_width - background_width) / (2 * screen_width)
        offset_y = (screen_height - background_height) / (2 * screen_height)

        # backgrounds
        # self.background = image.Image(screen, background_image, 0.5, 0.5, scale_factor)
        self.back_arrow = button.Button(screen, back_arrow_image, back_arrow_image, back_arrow_image, offset_x + 64/img_width, offset_y + 860/img_height, scale_factor)
        self.pencil = button.Button(screen, pencil_image, pencil_image, pencil_image, offset_x + 1148.93/img_width, offset_y + 173.525/img_height, scale_factor)
        self.profile = image.Image(screen, profile_image, offset_x + 780.5/img_width, offset_y + 169.5/img_height, scale_factor)

        # sliders
        self.sliderSFX = slider.Slider(screen, slider_bg_image, slider_fg_image, 442.01 * scale_factor, 44.91 * scale_factor, 
            offset_x + 342.005/img_width, offset_y + 459.455/img_height, scale_factor)
        self.sliderVolume = slider.Slider(screen, slider_bg_image, slider_fg_image, 442.01 * scale_factor, 44.91 * scale_factor,
            offset_x + 343/img_width, offset_y + 274.195/img_height, scale_factor)
        
        # volume buttons 
        self.VolumeMinus = button.Button(screen, minus_image, minus_image, minus_image, offset_x + 144.505/img_width, offset_y + 274.455/img_height, scale_factor)
        self.VolumePlus = button.Button(screen, plus_image, plus_image, plus_image, offset_x + 541.505/img_width, offset_y + 274.455/img_height, scale_factor)
        self.SFXMinus = button.Button(screen, minus_image, minus_image, minus_image, offset_x + 143.505/img_width, offset_y + 459.455/img_height, scale_factor)
        self.SFXPlus = button.Button(screen, plus_image, plus_image, plus_image, offset_x + 540.505/img_width, offset_y + 459.455/img_height, scale_factor)

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
        pygame.display.flip()

    def update(self):
        """Update the screen and handle keypress events."""
        super().update() 
        self.draw()

        # Handle events
        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(constants.MAIN_MENU)
            
            if self.VolumeMinus.in_bound():
                if self.VolumeMinus.handle_event(event):
                    self.sliderVolume.setValue(self.sliderVolume.getValue() - 0.1)
            elif self.VolumePlus.in_bound():
                if self.VolumePlus.handle_event(event):
                    self.sliderVolume.setValue(self.sliderVolume.getValue() + 0.1)
            else:
                self.sliderVolume.handle_event(event)

            if self.SFXMinus.in_bound():
                if self.SFXMinus.handle_event(event):
                    self.sliderSFX.setValue(self.sliderSFX.getValue() - 0.1)
            elif self.SFXPlus.in_bound():
                if self.SFXPlus.handle_event(event):
                    self.sliderSFX.setValue(self.sliderSFX.getValue() + 0.1)
            else:
                self.sliderSFX.handle_event(event)


