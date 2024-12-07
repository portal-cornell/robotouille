import pygame

class NinePatch:
    def __init__(self, screen, image_source, x, y, width, height, padding=(10, 10, 10, 10), scale_factor = 1):
        """
        Initialize a NinePatch object. ONLY SUPPORTS "topleft' ANCHOR.

        Args:
            screen (pygame.Surface): The screen on which to draw the NinePatch.
            image_source (pygame.Surface): The source image to slice and scale.
            x (float): The x-coordinate of the top-left corner of the NinePatch on the screen.
            y (float): The y-coordinate of the top-left corner of the NinePatch on the screen.
            width (int): The total width of the NinePatch to be drawn.
            height (int): The total height of the NinePatch to be drawn.
            padding (tuple): Padding values (left, right, top, bottom) that define the borders for slicing the UNSCALED image.
            scale_factor (float, optional): Scale factor for resizing the images. Defaults to 1.0.
        """
        self.screen = screen
        self.image_source = image_source
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = padding
        self.image_source = pygame.transform.smoothscale(
            image_source,
            (int(image_source.get_width() * scale_factor), int(image_source.get_height() * scale_factor))
        )
        self.img_width, self.img_height = self.image_source.get_size()
        self.padding = tuple(int(p * scale_factor) for p in padding)
        self.scale_factor = scale_factor
        self.slices = self.slice_image()
    
    def set_position(self, x, y):
        self.x = x
        self.y = y

    def slice_image(self):
        """
        Divides the source image into 9 parts based on padding values.

        Returns:
            slices (dict): A dictionary containing the source image divided into nine parts.
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

        Args:
            new_width (int): The new width of the NinePatch.
        """
        self.width = new_width

    def set_height(self, new_height):
        """
        Set a new height for the NinePatch image, keeping the top-left position fixed.

        Args:
            new_height (int): The new height of the NinePatch.
        """
        self.height = new_height

    def draw(self):
        """
        Draws the NinePatch image on the screen by scaling and positioning each slice based on the specified width, height, and padding.
        """
        left, right, top, bottom = self.padding
        x, y = int(self.x), int(self.y)

        center_w = max(0, int(self.width) - left - right)
        center_h = max(0, int(self.height) - top - bottom)

        x_positions = {'left': x, 'center': x + left, 'right': x + int(self.width) - right}
        y_positions = {'top': y, 'center': y + top, 'bottom': y + int(self.height) - bottom}

        if self.width >= left + right:
            if self.height >= top + bottom:
                self.screen.blit(self.slices['top_left'], (x_positions['left'], y_positions['top']))
                self.screen.blit(self.slices['top_right'], (x_positions['right'], y_positions['top']))
                self.screen.blit(self.slices['bottom_left'], (x_positions['left'], y_positions['bottom']))
                self.screen.blit(self.slices['bottom_right'], (x_positions['right'], y_positions['bottom']))

        if center_w > 0 and self.height >= top + bottom:
            top_edge = pygame.transform.smoothscale(self.slices['top'], (center_w, top))
            bottom_edge = pygame.transform.smoothscale(self.slices['bottom'], (center_w, bottom))
            self.screen.blit(top_edge, (x_positions['center'], y_positions['top']))
            self.screen.blit(bottom_edge, (x_positions['center'], y_positions['bottom']))

        if center_h > 0 and self.width >= left + right:
            left_edge = pygame.transform.smoothscale(self.slices['left'], (left, center_h))
            right_edge = pygame.transform.smoothscale(self.slices['right'], (right, center_h))
            self.screen.blit(left_edge, (x_positions['left'], y_positions['center']))
            self.screen.blit(right_edge, (x_positions['right'], y_positions['center']))

        if center_w > 0 and center_h > 0:
            center_area = pygame.transform.smoothscale(self.slices['center'], (center_w, center_h))
            self.screen.blit(center_area, (x_positions['center'], y_positions['center']))
