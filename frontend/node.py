from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, screen, surface, x_percent, y_percent, anchor="center", offset_x=0, offset_y=0):
        """
        Args:
            screen (pygame.Surface): The screen on which to draw the NinePatch.
            image_source (pygame.Surface): A temp surface, used to determine the boundaries
            x_percent (float): The horizontal position of the button as a percentage of the screen width.
            y_percent (float): The vertical position of the button as a percentage of the screen height.
            anchor (str): Positioning anchor, either "topleft" or "center".
        """
        self.screen = screen
        self.surface = surface
        self.x_percent = x_percent
        self.y_percent = y_percent
        self.anchor = anchor
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.calculate_position()

    def adjusted_mouse_position(self, mouse_pos):
        """
        Adjusts the global mouse position to account for the position of this node,
        allowing for local interaction within the node's surface.

        Args:
            mouse_pos (tuple): The current mouse position in global screen coordinates (x, y).

        Returns:
            tuple: The adjusted mouse position relative to this node's surface.
        """
        # Unpack global mouse position.
        mouse_x, mouse_y = mouse_pos
        
        # Adjust the position relative to the node's position.
        local_x = mouse_x - self.offset_x
        local_y = mouse_y - self.offset_y

        return local_x, local_y
    
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
        self.screen_width, self.screen_height = self.screen.get_size()
        x_coord = int(self.screen_width * self.x_percent)
        y_coord = int(self.screen_height * self.y_percent)
        
        if self.anchor == "center":
            self.rect = self.surface.get_rect(center=(x_coord, y_coord))
        else:  
            self.rect = self.surface.get_rect(topleft=(x_coord, y_coord))
            
        self.x, self.y = self.rect.topleft

    @abstractmethod
    def draw(self):
        """Draws all the screen components."""
        pass

