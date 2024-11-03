import pygame
from frontend import image

class textbox():
    def __init__(self, screen, text, font,  x_percent, y_percent, text_color=(0, 0, 0), scale_factor=1.0):
        self.screen = screen
        self.x_percent = x_percent
        self.y_percent = y_percent

        self.text = text
        self.font = font
        self.text_color = text_color

    def draw(self):
        """Draw the button and the text (if any) separately."""
        if self.text and self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            self.screen.blit(text_surface, text_rect)

