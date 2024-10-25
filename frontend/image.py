import pygame

class Image:
    def __init__(self, screen, image_source, x_percent, y_percent, scale_factor=1.0):
        self.screen = screen
        self.image = image_source
        
        # Scale the image based on the scale factor
        original_width, original_height = self.image.get_size()
        scaled_width = int(original_width * scale_factor)
        scaled_height = int(original_height * scale_factor)
        self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))

        self.x_percent = x_percent
        self.y_percent = y_percent
        self.update_position()

    def update_position(self):
        screen_width, screen_height = self.screen.get_size()
        self.x = int(screen_width * self.x_percent)
        self.y = int(screen_height * self.y_percent)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))