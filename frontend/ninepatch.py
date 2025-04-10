import pygame

class NinePatch:
    def __init__(self, screen, image_source, x, y, width, height, padding=(10, 10, 10, 10), offset_x=0, offset_y=0, scale_factor = 1):
        """
        Initializes the NinePatch object.

        Args:
            screen (pygame.Surface): Where the NinePatch will be drawn.
            image_source (pygame.Surface): Source image to slice.
            x (float): Top-left X coordinate in pixel of the patch on screen.
            y (float): Top-left Y coordinate in pixel of the patch on screen.
            width (int): Desired width on screen.
            height (int): Desired height on screen.
            padding (tuple): (left, right, top, bottom) padding for slicing.
            offset_x (int): Additional X offset for positioning.
            offset_y (int): Additional Y offset for positioning.
        """
        self.screen = screen
        self.image_source = image_source
        self.x = x
        self.y = y
        self.width = width * scale_factor
        self.height = height * scale_factor
        self.padding = padding  # (left, right, top, bottom)
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.scale_factor = scale_factor

        self.raw_slices = self.slice_image() # slices original image into 9 pieces
        self.slices = {}
        self.update_scaled_slices()

    def set_position(self, x, y):
        """Set the position of the NinePatch on screen."""
        self.x = x
        self.y = y

    def slice_image(self):
        """
        Splits the original image into 9 unscaled parts.

        Returns:
            dict: Dictionary of raw subsurfaces (unscaled).
        """
        left, right, top, bottom = self.padding
        img_w, img_h = self.image_source.get_size()

        x1, x2 = left, img_w - right
        y1, y2 = top, img_h - bottom

        def subsurface_safe(rx, ry, rw, rh):
            """
            Check that the region is valid
            """
            if rx + rw <= img_w and ry + rh <= img_h and rw > 0 and rh > 0:
                return self.image_source.subsurface((rx, ry, rw, rh))
            return None

        return {
            'top_left':     subsurface_safe(0, 0, left, top),
            'top':          subsurface_safe(x1, 0, x2 - x1, top),
            'top_right':    subsurface_safe(x2, 0, right, top),
            'left':         subsurface_safe(0, y1, left, y2 - y1),
            'center':       subsurface_safe(x1, y1, x2 - x1, y2 - y1),
            'right':        subsurface_safe(x2, y1, right, y2 - y1),
            'bottom_left':  subsurface_safe(0, y2, left, bottom),
            'bottom':       subsurface_safe(x1, y2, x2 - x1, bottom),
            'bottom_right': subsurface_safe(x2, y2, right, bottom),
        }

    def update_scaled_slices(self):
        """
        Updates self.slices by scaling the raw pieces based on current width and height.
        """
        left, right, top, bottom = self.padding

        center_w = max(0, self.width - left - right)
        center_h = max(0, self.height - top - bottom)

        def scale(img, w, h):
            """
            Scales the image if it exist otherwise returns None
            """
            return pygame.transform.smoothscale(img, (w, h)) if img else None

        self.slices = {
            'top_left':     scale(self.raw_slices['top_left'], left, top),
            'top':          scale(self.raw_slices['top'], center_w, top),
            'top_right':    scale(self.raw_slices['top_right'], right, top),
            'left':         scale(self.raw_slices['left'], left, center_h),
            'center':       scale(self.raw_slices['center'], center_w, center_h),
            'right':        scale(self.raw_slices['right'], right, center_h),
            'bottom_left':  scale(self.raw_slices['bottom_left'], left, bottom),
            'bottom':       scale(self.raw_slices['bottom'], center_w, bottom),
            'bottom_right': scale(self.raw_slices['bottom_right'], right, bottom),
        }
        
        left, right, top, bottom = self.padding
        x, y = int(self.x), int(self.y)

        # Compute positions for each column and row
        x_pos = {'left': x, 'center': x + left, 'right': x + self.width - right}
        y_pos = {'top': y, 'center': y + top, 'bottom': y + self.height - bottom}

        self.draw_map = {
            'top_left':     (x_pos['left'],   y_pos['top']),
            'top':          (x_pos['center'], y_pos['top']),
            'top_right':    (x_pos['right'],  y_pos['top']),
            'left':         (x_pos['left'],   y_pos['center']),
            'center':       (x_pos['center'], y_pos['center']),
            'right':        (x_pos['right'],  y_pos['center']),
            'bottom_left':  (x_pos['left'],   y_pos['bottom']),
            'bottom':       (x_pos['center'], y_pos['bottom']),
            'bottom_right': (x_pos['right'],  y_pos['bottom']),
        }

    def set_width(self, new_width):
        """
        Sets a new width and updates scaled slices.
        """
        self.width = new_width * self.scale_factor
        self.update_scaled_slices()

    def set_height(self, new_height):
        """
        Sets a new height and updates scaled slices.
        """
        self.height = new_height * self.scale_factor
        self.update_scaled_slices()

    def scale_to_size(self, width, height):
        """
        Scales the object to a new width and height.
        """
        self.width = width * self.scale_factor
        self.height = height * self.scale_factor
        self.update_scaled_slices()

    def adjusted_mouse_position(self, mouse_pos):
        """
        Converts global mouse position to local NinePatch space.

        Returns:
            tuple: Local (x, y) coordinates.
        """
        mouse_x, mouse_y = mouse_pos
        return (mouse_x - self.offset_x, mouse_y - self.offset_y)

    def _in_bound(self, location):
        """
        Checks if a global screen coordinate is inside this NinePatch.

        Returns:
            bool: True if inside bounds.
        """
        rect = pygame.Rect(self.x + self.offset_x, self.y + self.offset_y, self.width, self.height)
        return rect.collidepoint(location)

    def draw(self):
        """
        Draws the NinePatch using pre-scaled slices. Only draws slices that are available.
        """

        for key, img in self.slices.items():
            if img:
                self.screen.blit(img, self.draw_map[key])
