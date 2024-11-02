import pygame

class NinePatch:
    def __init__(self, screen, image_source, x, y, width, height, padding=(10, 10, 10, 10)):
        """
        Initialize a NinePatch object.
        """
        self.screen = screen
        self.image_source = image_source
        self.x = x  # Keep this fixed as the anchor point
        self.y = y  # Keep this fixed as the anchor point
        self.width = width
        self.height = height
        self.padding = padding
        self.img_width, self.img_height = self.image_source.get_size()
        self.slices = self.slice_image()

    def slice_image(self):
        left, right, top, bottom = self.padding
        img_w, img_h = self.img_width, self.img_height

        x1 = left
        x2 = img_w - right
        y1 = top
        y2 = img_h - bottom

        slices = {}
        image = self.image_source

        # Slicing the image into nine parts
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

    def draw(self):
        left, right, top, bottom = self.padding
        dest_x = self.x
        dest_y = self.y
        dest_w = self.width
        dest_h = self.height

        left_w = left
        right_w = right
        top_h = top
        bottom_h = bottom

        center_w = dest_w - left_w - right_w
        center_h = dest_h - top_h - bottom_h

        # Drawing each slice appropriately
        self.screen.blit(self.slices['top_left'], (dest_x, dest_y))
        top_edge = pygame.transform.scale(self.slices['top'], (int(center_w), top_h))
        self.screen.blit(top_edge, (dest_x + left_w, dest_y))
        self.screen.blit(self.slices['top_right'], (dest_x + left_w + center_w, dest_y))

        left_edge = pygame.transform.scale(self.slices['left'], (left_w, int(center_h)))
        self.screen.blit(left_edge, (dest_x, dest_y + top_h))
        center = pygame.transform.scale(self.slices['center'], (int(center_w), int(center_h)))
        self.screen.blit(center, (dest_x + left_w, dest_y + top_h))
        right_edge = pygame.transform.scale(self.slices['right'], (right_w, int(center_h)))
        self.screen.blit(right_edge, (dest_x + left_w + center_w, dest_y + top_h))

        self.screen.blit(self.slices['bottom_left'], (dest_x, dest_y + top_h + center_h))
        bottom_edge = pygame.transform.scale(self.slices['bottom'], (int(center_w), bottom_h))
        self.screen.blit(bottom_edge, (dest_x + left_w, dest_y + top_h + center_h))
        self.screen.blit(self.slices['bottom_right'], (dest_x + left_w + center_w, dest_y + top_h + center_h))