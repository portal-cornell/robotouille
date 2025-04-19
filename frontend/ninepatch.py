import pygame
from frontend.constants import DEBUG

class NinePatch:
    def __init__(self, screen, image_source, x, y, width, height, padding=(10, 10, 10, 10), scale_factor = 1, offset_x=0, offset_y=0):
        """
        Initializes the NinePatch object.

        CURRENT BUGGY WHEN YOU SCALE DOWN (less than 10pixels)

        Args:
            screen (pygame.Surface): The screen on which to draw the NinePatch.
            image_source (pygame.Surface): The source image to slice.
            x (float): The x-coordinate of the top-left corner of the NinePatch on the screen.
            y (float): The y-coordinate of the top-left corner of the NinePatch on the screen.
            width (int): The total width of the NinePatch to be drawn.
            height (int): The total height of the NinePatch to be drawn.
            padding (tuple): Padding values (left, right, top, bottom) that define the borders for slicing the UNSCALED image.
            scale_factor (float, optional): Scale factor for resizing the images. Defaults to 1.0.
            offset_x (int): Represents the number of pixels vertically this nodes is offseted from the parent screen
            offset_y (int): Represents the number of pixels horizonally this nodes is offseted from the parent screen
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
        padding = (int(p * self.scale_factor) for p in self.padding)
        left, right, top, bottom = padding

        center_w = max(0, self.width - left - right)
        center_h = max(0, self.height - top - bottom)

        def scale(img, w, h):
            """
            Scales the image if it exist otherwise returns None
            """
            w, h = int(w), int(h)
            if img and w>0 and h>0: 
                return pygame.transform.smoothscale(img, (w, h)) 
            else:
                return None

        shrunk_top =  (top/ (top + bottom)) * self.height if top + bottom > 0 else 0
        shrunk_bottom =  (bottom/ (top + bottom)) * self.height if top + bottom > 0 else 0
        shrunk_left = (left/ (left + right)) * self.width if left + right > 0 else 0
        shrunk_right = (left/ (left + right)) * self.width if left + right > 0 else 0

        if all(val < 5 for val in (shrunk_top, shrunk_bottom, shrunk_left, shrunk_right)):
            shrunk_top = shrunk_bottom = shrunk_left = shrunk_right = 0
            
        self.slices = {
            'top_left':     scale(self.raw_slices['top_left'], min(shrunk_left, left), min(shrunk_top, top)),
            'top':          scale(self.raw_slices['top'], center_w,  min(shrunk_top, top)),
            'top_right':    scale(self.raw_slices['top_right'], min(shrunk_right, right),  min(shrunk_top, top)),
            'left':         scale(self.raw_slices['left'], min(shrunk_left, left), center_h),
            'center':       scale(self.raw_slices['center'], center_w, center_h),
            'right':        scale(self.raw_slices['right'], min(shrunk_right, right), center_h),
            'bottom_left':  scale(self.raw_slices['bottom_left'], min(shrunk_left, left),  min(shrunk_bottom, bottom)),
            'bottom':       scale(self.raw_slices['bottom'], center_w, min(shrunk_bottom, bottom)),
            'bottom_right': scale(self.raw_slices['bottom_right'], min(shrunk_right, right), min(shrunk_bottom, bottom))
        }

        x, y = int(self.x), int(self.y)

        # Compute positions for each column and row
        x_pos = {'left': x, 'center': x + left, 'right': max(x, x + int(self.width) - right - 1)}
        y_pos = {'top': y, 'center': y + top, 'bottom': max(y, y + int(self.height) - bottom - 1)}

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
        Draws the NinePatch using available slices.
        """
        for key in self.slices:
            img = self.slices[key]
            if img:
                self.screen.blit(img, self.draw_map[key])
        if DEBUG: pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, self.width, self.height), 1)
