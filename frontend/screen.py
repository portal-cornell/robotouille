from abc import ABC, abstractmethod
from frontend import constants

class ScreenInterface(ABC):
    def __init__(self, screen):
        # Screen identifiers, should be MAIN_MENU, SETTINGS, etc
        self.next_screen = None

        self.screen = screen
        screen_width, screen_height = self.screen.get_size()
        self.img_width, self.img_height = 1440, 1024
        width_scale = screen_width / self.img_width
        height_scale = screen_height / self.img_height
        self.scale_factor = min(width_scale, height_scale)  

        background_width = self.scale_factor * 1440
        background_height = self.scale_factor * 1024

        self.offset_x = (screen_width - background_width) / (2 * screen_width)
        self.offset_y = (screen_height - background_height) / (2 * screen_height)
        self.load_assets()

    def set_next_screen(self, next_screen):
        """Set the next screen to transition to."""
        self.next_screen = next_screen

    def x_percent(self, value):
        return self.offset_x + value/self.img_width

    def y_percent(self, value):
        return self.offset_y + value/self.img_height
    
    @abstractmethod
    def draw(self):
        """Draws all the screen components."""
        pass
    
    @abstractmethod
    def load_assets(self):
        """Load necessary assets."""
        pass

    def update(self):
        """Update the screen and handle keypress events."""
        self.screen.fill((0, 0, 0))  # Clear screen after changing the state
    