from abc import ABC, abstractmethod
from frontend import constants

class ScreenInterface(ABC):
    def __init__(self, screen):
        """
        Initialize the ScreenInterface instance.

        Sets up the screen dimensions, calculates the scale factor based on the screen size, 
        and loads any necessary assets.

        Args:
           screen (pygame.Surface): The display surface where screen components will be drawn.
        """
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
        """
        Set the next screen for transition.

        Specifies the screen that should be displayed after the current screen.

        Args:
           next_screen (str): Identifier for the next screen (e.g., `MAIN_MENU`, `SETTINGS`).

        """
        self.next_screen = next_screen

    def x_percent(self, value):
        """
        Convert a horizontal position value to a percentage-based coordinate, adjusted for any offset.

        Args:
           value (float): Horizontal position value in pixels.

        Returns:
           (float): Adjusted x-coordinate as a percentage of the screen width.
        """
        return self.offset_x + value / self.img_width

    def y_percent(self, value):
        """
        Convert a vertical position value to a percentage-based coordinate, adjusted for any offset.

        Args:
           value (float): Vertical position value in pixels.

        Returns:
           (float): Adjusted y-coordinate as a percentage of the screen height.
        """
        return self.offset_y + value / self.img_height

    @abstractmethod
    def draw(self):
        """
        Draw all screen components.
        """
        pass

    @abstractmethod
    def load_assets(self):
        """
        Load necessary assets for the screen.

        Raises:
           FileNotFoundError: If any required assets cannot be loaded.
        """
        pass

    def update(self):
        """
        Update the screen state and handle any events.
        """
        self.screen.fill((0, 0, 0))
        self.draw()
