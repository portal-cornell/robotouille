import pygame

class NinePatch:
    def __init__(self, screen, image_source, x, y, width, height, padding=(0, 0, 0, 0)):
        """
        Initialize a NinePatch object.

        Parameters:
        - screen (pygame.Surface): The screen on which to draw the NinePatch.
        - image_source (pygame.Surface): The source image to slice and scale.
        - x (float): The x-coordinate of the top-left corner of the NinePatch on the screen.
        - y (float): The y-coordinate of the top-left corner of the NinePatch on the screen.
        - width (int): The total width of the NinePatch to be drawn.
        - height (int): The total height of the NinePatch to be drawn.
        - padding (tuple): Padding values (left, right, top, bottom) that define the borders for slicing the image.
        """
        self.screen = screen
        self.image_source = image_source
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = padding
        self.img_width, self.img_height = self.image_source.get_size()
        self.slices = self.slice_image()

    def slice_image(self):
        """
        Divides the source image into 9 parts based on padding values.

        Returns:
        dict: A dictionary containing the nine slices:
            - 'top_left': Top-left corner slice
            - 'top': Top edge slice
            - 'top_right': Top-right corner slice
            - 'left': Left edge slice
            - 'center': Center slice
            - 'right': Right edge slice
            - 'bottom_left': Bottom-left corner slice
            - 'bottom': Bottom edge slice
            - 'bottom_right': Bottom-right corner slice
        """
        left, right, top, bottom = self.padding
        img_w, img_h = self.img_width, self.img_height

        x1 = left
        x2 = img_w - right
        y1 = top
        y2 = img_h - bottom

        slices = {}
        image = self.image_source

        slices['top_left'] = image.subsurface((0, 0, left, top))
        slices['top'] = image.subsurface((x1, 0, x2 - x1, top))
        slices['top_right'] = image.subsurface((x2, 0, right, top))
        slices['left'] = image.subsurface((0, y1, left, y2 - y1))
        slices['center'] = image.subsurface((x1, y1, x2 - x1, y2 - y1))
        slices['right'] = image.subsurface((x2, y1, right, y2 - y1))
        slices['bottom_left'] = image.subsurface((0, y2, left, bottom))
        slices['bottom'] = image.subsurface((x1, y2, x2 - x1, bottom))
        slices['bottom_right'] = image.subsurface((x2, y2, right, bottom))

        return slices

    def set_width(self, new_width):
        """
        Set a new width for the NinePatch image, keeping the top-left position fixed.

        Parameters:
        - new_width (int): The new width of the NinePatch.
        """
        self.width = new_width

    def set_height(self, new_height):
        """
        Set a new height for the NinePatch image, keeping the top-left position fixed.

        Parameters:
        - new_height (int): The new height of the NinePatch.
        """
        self.height = new_height

    def draw(self):
        """
        Draws the NinePatch image on the screen by scaling and positioning each slice based on the specified width, height, and padding.
        
        Ensures that:
        - Corners remain unscaled.
        - Edges are scaled only along one dimension (width or height).
        - The center is scaled both horizontally and vertically to fill the remaining area.
        """
        left, right, top, bottom = self.padding
        x, y = self.x, self.y

        center_w = max(0, self.width - left - right)
        center_h = max(0, self.height - top - bottom)

        x_positions = {'left': x, 'center': x + left, 'right': x + self.width - right}
        y_positions = {'top': y, 'center': y + top, 'bottom': y + self.height - bottom}

        # Draw corners
        self.screen.blit(self.slices['top_left'], (x_positions['left'], y_positions['top']))
        self.screen.blit(self.slices['top_right'], (x_positions['right'], y_positions['top']))
        self.screen.blit(self.slices['bottom_left'], (x_positions['left'], y_positions['bottom']))
        self.screen.blit(self.slices['bottom_right'], (x_positions['right'], y_positions['bottom']))

      
        if center_w > 0:
            top_edge = pygame.transform.scale(self.slices['top'], (center_w, top))
            bottom_edge = pygame.transform.scale(self.slices['bottom'], (center_w, bottom))
            self.screen.blit(top_edge, (x_positions['center'], y_positions['top']))
            self.screen.blit(bottom_edge, (x_positions['center'], y_positions['bottom']))

        if center_h > 0:
            left_edge = pygame.transform.scale(self.slices['left'], (left, center_h))
            right_edge = pygame.transform.scale(self.slices['right'], (right, center_h))
            self.screen.blit(left_edge, (x_positions['left'], y_positions['center']))
            self.screen.blit(right_edge, (x_positions['right'], y_positions['center']))

        if center_w > 0 and center_h > 0:
            center_area = pygame.transform.scale(self.slices['center'], (center_w, center_h))
            self.screen.blit(center_area, (x_positions['center'], y_positions['center']))
