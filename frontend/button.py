import pygame
from frontend import image

class Button(image.Image):
    def __init__(self, screen, image_source, x_percent, y_percent, scale_factor=1.0, hover_color=None):
        super().__init__(screen, image_source, x_percent, y_percent, scale_factor)
        
        self.hover_image = self.image

        # if we want hovering, we either need to separate out text from image, or we need to add a second image

    def is_hovered(self):
        """Check if the mouse is over the button."""
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self):
        """Draw the button with hover effect."""
        if self.is_hovered():
            self.screen.blit(self.hover_image, (self.x, self.y))
        else:
            self.screen.blit(self.image, (self.x, self.y))

    def is_clicked(self, event):
        """Check if the button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered():
            return True
        return False
