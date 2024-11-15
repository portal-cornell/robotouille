from abc import ABC, abstractmethod

class ScreenInterface(ABC):
    def __init__(self, screen, width = 1440, height = 1024):
        """
        Initialize the ScreenInterface instance.

        Sets up the screen dimensions, calculates the scale factor based on the screen size, 
        and loads any necessary assets.

        Args:
           screen (pygame.Surface): The display surface where screen components will be drawn.
           width (float): The width of the Figma screen
           height (float): The height of the Figma screen
        """
        # Screen identifiers, should be MAIN_MENU, SETTINGS, etc
        self.next_screen = None

        self.screen = screen
        self.screen_width, self.screen_height = self.screen.get_size()
        self.img_width, self.img_height = width, height
        width_scale = self.screen_width / self.img_width
        height_scale = self.screen_height / self.img_height

        self.scale_factor = min(width_scale, height_scale)  

        background_width = self.scale_factor * width
        background_height = self.scale_factor * height

        self.offset_x = (self.screen_width - background_width) / (2 * self.screen_width)
        self.offset_y = (self.screen_height - background_height) / (2 * self.screen_height)

        self.load_assets()

    def set_next_screen(self, next_screen):
        """
        Set the next screen for transition.

        Specifies the screen that should be displayed after the current screen.

        Args:
           next_screen (str): Identifier for the next screen (e.g., `MAIN_MENU`, `SETTINGS`).

        """
        self.next_screen = next_screen

    def x_percent(self, value, anchor="center"):
        """
        Convert a horizontal position value to a scaled screen coordinate, adjusted for the offset.

        Args:
           value (float): Horizontal position value in pixels.
           anchor (str): Anchor point for positioning ("center" or "topleft").

        Returns:
           (float): Adjusted x-coordinate as a percentage of the screen width.
        """
        scaled_x = self.scale_factor * value
        if anchor == "center":
            return self.offset_x + (scaled_x/ self.screen_width)
        if anchor == "topleft":
            return (scaled_x/ self.screen_width)
        raise ValueError("Invalid anchor. Use 'center' or 'topleft'.")

    def y_percent(self, value, anchor="center"):
        """
        Convert a vertical position value to a scaled screen coordinate, adjusted for the offset.

        Args:
           value (float): Vertical position value in pixels.
           anchor (str): Anchor point for positioning ("center" or "topleft").

        Returns:
           (float): Adjusted y-coordinate as a percentage of the screen height.
        """
        scaled_y = self.scale_factor * value
        if anchor == "center":
            return self.offset_y + (scaled_y/ self.screen_height)
        if anchor == "topleft":
            return (scaled_y/ self.screen_height)
        raise ValueError("Invalid anchor. Use 'center' or 'topleft'.")

    
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

    def get_screen(self):
        return self.screen