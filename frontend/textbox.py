import pygame
from frontend.node import Node
from frontend.constants import FONT_PATH, BLUE

class Textbox(Node):
    def __init__(self, screen, text, x_percent, y_percent, width, height, 
                 text_color=BLUE, font_path=FONT_PATH, font_size=60, scale_factor=1.0, align_text="center", anchor="topleft", offset_x=0, offset_y=0):
        
        """
        Initialize a Textbox object.

        Args:
            screen (pygame.Surface): The main display surface where the textbox will be rendered.
            text (str): The text to be displayed within the textbox.
            x_percent (float): X-axis position as a percentage of the screen width. Controls the horizontal placement of the rectangle.
            y_percent (float): Y-axis position as a percentage of the screen height. Controls the vertical placement of the rectangle.
            width (int): The width of the textbox rectangle.
            height (int): The height of the textbox rectangle.
            text_color (tuple): The RGB color of the text. Defaults to blue.
            font_path (str): The path to the font used to render the text.
            font_size (int): The size of the font.
            scale_factor (float): Scale factor for resizing the text. Defaults to 1.0.
            align_text (str): The alignment of the text within the textbox. Options are "left", "center", or "right". Defaults to "center".
            anchor (str): Determines how the textbox rectangle is anchored on the screen. Options are "center" or "topleft". Defaults to "topleft".
        """

        super().__init__(screen, pygame.Surface((width * scale_factor, height* scale_factor), pygame.SRCALPHA), x_percent, y_percent, offset_x, offset_y)
        
        
        self.text = text
        self.font = pygame.font.Font(font_path, int(font_size * scale_factor))
        self.text_color = text_color
        self.scale_factor = scale_factor
        self.align_text = align_text
        self.anchor = anchor
        self.background_color = (255, 255, 255, 0) 
        self.text_surface = None
        
        self.update_text_rect()

    def update_text_rect(self):
        """Render the text and update rectangle dimensions and position based on anchor."""
        if self.font:
            self.text_surface = self.font.render(self.text, True, self.text_color)
            scaled_size = (int(self.text_surface.get_width() * self.scale_factor),
                           int(self.text_surface.get_height() * self.scale_factor))
            self.text_surface = pygame.transform.smoothscale(self.text_surface, scaled_size)

            self.rect = self.surface.get_rect()
            if self.anchor == "topleft":
                self.rect.topleft = (self.screen.get_width() * self.x_percent, 
                                     self.screen.get_height() * self.y_percent)
            elif self.anchor == "center":
                self.rect.center = (self.screen.get_width() * self.x_percent, 
                                    self.screen.get_height() * self.y_percent)

            self.text_rect = self.text_surface.get_rect()
            if self.align_text == "left":
                self.text_rect.midleft = (0, self.surface.get_height() // 2)
            elif self.align_text == "center":
                self.text_rect.center = self.surface.get_rect().center
            elif self.align_text == "right":
                self.text_rect.midright = (self.surface.get_width(), self.surface.get_height() // 2)

    def draw(self):
        """Draw the background and aligned text surface within the anchored rectangle on the screen."""
        self.surface.fill(self.background_color)
        if self.text_rect:
            self.surface.blit(self.text_surface, self.text_rect)
        self.screen.blit(self.surface, self.rect)

    def set_text(self, new_text):
        """Update the text and refresh the text surface."""
        self.text = new_text
        self.update_text_rect()

    def get_text(self):
        """Get text string"""
        return self.text
