import pygame
from frontend.node import Node

class Image(Node):
    def __init__(self, screen, image_source, x_percent, y_percent, scale_factor=1.0, anchor="center"):
        """
        Initialize an Image object.

        Args:
            screen (pygame.Surface): Pygame screen to draw the image on.
            image_source (pygame.Surface): Loaded image object.
            x_percent (float): Horizontal position as a percentage of screen width.
            y_percent (float): Vertical position as a percentage of screen height.
            scale_factor (float): Factor by which to scale the image.
            anchor (str): Positioning anchor, either "topleft" or "center".
        """
        super().__init__(screen, image_source, x_percent, y_percent, anchor)

        self.image = image_source
        
        # Scale the image based on the scale factor
        original_width, original_height = self.image.get_size()
        scaled_width = original_width * scale_factor
        scaled_height = original_height * scale_factor
        self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))

    def draw(self):
        """Draws the image to the screen."""
        self.screen.blit(self.image, (self.x, self.y))

    def set_alpha(self, alpha):
        """
        Set the transparency level of the image.

        Args:
            alpha (int): Transparency level (0 to 255), where 0 is fully transparent and 255 is fully opaque.
        """
        self.image.set_alpha(alpha)