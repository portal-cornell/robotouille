import pygame
from frontend import node

class Image(node.Node):
    def __init__(self, screen, image_source, x_percent, y_percent, scale_factor=1.0, anchor="center"):
        """
        Initialize an Image object.

        Args:
            screen: Pygame screen to draw the image on.
            image_source: Loaded image object.
            x_percent: Horizontal position as a percentage of screen width.
            y_percent: Vertical position as a percentage of screen height.
            scale_factor: Factor by which to scale the image.
            anchor: Positioning anchor, either "topleft" or "center".
        """
        super().__init__(screen, image_source, x_percent, y_percent, anchor)

        self.image = image_source
        
        # Scale the image based on the scale factor
        original_width, original_height = self.image.get_size()
        scaled_width = original_width * scale_factor
        scaled_height = original_height * scale_factor
        self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))
