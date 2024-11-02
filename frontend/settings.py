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
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        back_arrow_path = os.path.join(ASSETS_DIRECTORY, "back_arrow.png")

        slider_bg_path = os.path.join(ASSETS_DIRECTORY, "sliderback.png")
        slider_fg_path = os.path.join(ASSETS_DIRECTORY, "sliderfore.png")
        slider_knob_path = os.path.join(ASSETS_DIRECTORY, "knob.png")

        background_image = pygame.image.load(background_path).convert_alpha()
        back_arrow_image = pygame.image.load(back_arrow_path).convert_alpha()

        slider_bg_image = pygame.image.load(slider_bg_path).convert_alpha()
        slider_fg_image = pygame.image.load(slider_fg_path).convert_alpha()
        slider_knob_image = pygame.image.load(slider_knob_path).convert_alpha()
        
        screen_width, screen_height = self.screen.get_size()
        img_width, img_height = 1440, 1024
        width_scale = screen_width / img_width
        height_scale = screen_height / img_height
        scale_factor = min(width_scale, height_scale)  

        background_width = background_image.get_width() * scale_factor
        background_height = background_image.get_height() * scale_factor

        offset_x = (screen_width - background_width) / (2 * screen_width)
        offset_y = (screen_height - background_height) / (2 * screen_height)

        # position all scene objects
        self.background = image.Image(screen, background_image, 0.5, 0.5, scale_factor)
        self.back_arrow = button.Button(screen, back_arrow_image, back_arrow_image, back_arrow_image, offset_x + 64/img_width, offset_y + 860/img_height, scale_factor)

        self.sliderSFX = slider.Slider(screen, slider_bg_image, slider_fg_image, slider_knob_image, 442.01 * scale_factor, 44.91 * scale_factor, 
            offset_x + 342.005/img_width, offset_y + 459.455/img_height, scale_factor)
        
        self.sliderVolume = slider.Slider(screen, slider_bg_image, slider_fg_image, slider_knob_image, 442.01 * scale_factor, 44.91 * scale_factor,
            offset_x + 343/img_width, offset_y + 274.195/img_height, scale_factor)
        
    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.back_arrow.draw()
        self.sliderSFX.draw()
        self.sliderVolume.draw()
        pygame.display.flip()

    def update(self):
        """Update the screen and handle keypress events."""
        super().update() 
        self.draw()

        # Handle events
        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(constants.MAIN_MENU)
            self.sliderSFX.handle_event(event)
            self.sliderVolume.handle_event(event)

