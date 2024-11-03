import pygame

class Textbox:
    def __init__(self, screen, text, font, x_percent, y_percent, text_color=(0, 0, 0), scale_factor=1.0):
        self.screen = screen
        self.text = text
        self.font = font
        self.text_color = text_color
        self.scale_factor = scale_factor

        self.x = int(screen.get_width() * x_percent)
        self.y = int(screen.get_height() * y_percent)

        self.update_text_rect()

    def update_text_rect(self):
        """Render the text and update the rectangle dimensions and position."""
        if self.text and self.font:
            self.text_surface = self.font.render(self.text, True, self.text_color)
            self.text_surface = pygame.transform.scale(
                self.text_surface,
                (
                    int(self.text_surface.get_width() * self.scale_factor),
                    int(self.text_surface.get_height() * self.scale_factor),
                ),
            )
            self.rect = self.text_surface.get_rect(center=(self.x, self.y))

    def draw(self):
        """Draw the text surface on the screen."""
        if self.text_surface:
            self.screen.blit(self.text_surface, self.rect)

    def set_text(self, new_text):
        """Update the text and refresh the text surface."""
        self.text = new_text
        self.update_text_rect()
