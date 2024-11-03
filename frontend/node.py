from abc import ABC, abstractmethod
from frontend import constants

class Node(ABC):
    def __init__(self, screen, image, x_percent, y_percent, anchor="center"):
        self.screen = screen
        self.temp = image
        self.x_percent = x_percent
        self.y_percent = y_percent
        self.anchor = anchor
        self.calculate_position()

    def set_percentage(self, new_x_percent = None, new_y_percent= None):
        """
        Update the x and y position percentages and recalculate the position.
        
        Args:
            new_x_percent: New horizontal position as a percentage of screen width.
            new_y_percent: New vertical position as a percentage of screen height.
        """
        if new_x_percent: self.x_percent = new_x_percent
        if new_y_percent: self.y_percent = new_y_percent
        self.calculate_position()

    def calculate_position(self):
        """
        Given the x and y position percentages and calculate the position.
        """
        screen_width, screen_height = self.screen.get_size()
        x = int(screen_width * self.x_percent)
        y = int(screen_height * self.y_percent)
        
        if self.anchor == "center":
            self.rect = self.temp.get_rect(center=(x, y))
        else:  
            self.rect = self.temp.get_rect(topleft=(x, y))
            
        self.x, self.y = self.rect.topleft

    @abstractmethod
    def draw(self):
        """Draws all the screen components."""
        pass

