from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, screen, surface, x_percent, y_percent, offset_x, offset_y, anchor="center"):
        """
        Args:
            screen (pygame.Surface): The screen.
            surface (pygame.Surface): A temp surface, used to determine the boundaries
            x_percent (float): The horizontal position of the button as a percentage of the screen width.
            y_percent (float): The vertical position of the button as a percentage of the screen height.
            offset_x (int): Represents the number of pixels vertically this nodes is offseted from the parent screen
            offset_y (int): Represents the number of pixels horizonally this nodes is offseted from the parent screen
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
    
    def set_offset(self, new_offset_x, new_offset_y):
        """
        Updates the offset_x and offset_y positions

        Args:
            offset_x (int): Represents the number of pixels vertically this nodes is offseted from the top level parent screen
            offset_y (int): Represents the number of pixels horizonally this nodes is offseted from the top level parent screen
        """
        self.offset_x = new_offset_x
        self.offset_y = new_offset_y

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
        Given the x and y position percentages, calculates the pixel location. 
        And then anchors the screen based on the pixel location.
        """
        self.screen_width, self.screen_height = self.screen.get_size()
        x_coord = int(self.screen_width * self.x_percent)
        y_coord = int(self.screen_height * self.y_percent)
        
        if self.anchor == "center":
            self.rect = self.surface.get_rect(center=(x_coord, y_coord))
        else:  
            self.rect = self.surface.get_rect(topleft=(x_coord, y_coord))
            
        self.x, self.y = self.rect.topleft
    
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
        return (local_x, local_y)

    def _in_bound(self, location):
        """
        Check if the location is over the object.

        Returns:
           (bool) True if the  position is within the objects's bounds; False otherwise.
        """
        return self.rect.collidepoint(self.adjusted_mouse_position(location))
    
    @abstractmethod
    def draw(self):
        """Draws all the screen components."""
        pass

