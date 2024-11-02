import pygame

class Image:
    def __init__(self, screen, image_source, x_percent, y_percent, scale_factor=1.0, anchor="center"):
        """
        Initialize an Image object.

        Parameters:
        - screen: Pygame screen to draw the image on.
        - image_source: Loaded image object.
        - x_percent: Horizontal position as a percentage of screen width.
        - y_percent: Vertical position as a percentage of screen height.
        - scale_factor: Factor by which to scale the image.
        - anchor: Positioning anchor, either "topleft" or "center".
        """
        self.screen = screen
        self.image = image_source
        
        # Scale the image based on the scale factor
        original_width, original_height = self.image.get_size()
        scaled_width = int(original_width * scale_factor)
        scaled_height = int(original_height * scale_factor)
        self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))

        self.x_percent = x_percent
        self.y_percent = y_percent
        self.anchor = anchor
        self.update_position()

    def set_percentage(self, new_x_percent = None, new_y_percent= None):
        """
        Update the x and y position percentages and recalculate the position.
        
        Parameters:
        - new_x_percent: New horizontal position as a percentage of screen width.
        - new_y_percent: New vertical position as a percentage of screen height.
        """
        if new_x_percent: self.x_percent = new_x_percent
        if new_y_percent: self.y_percent = new_y_percent
        self.update_position()

    def update_position(self):
        screen_width, screen_height = self.screen.get_size()
        x = int(screen_width * self.x_percent)
        y = int(screen_height * self.y_percent)
        
        if self.anchor == "center":
            self.rect = self.image.get_rect(center=(x, y))
        else:  
            self.rect = self.image.get_rect(topleft=(x, y))
            
        self.x, self.y = self.rect.topleft

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))
