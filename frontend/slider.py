import pygame
from frontend import ninepatch, image

class Slider:
    def __init__(self, screen, foreground_image, background_image, knob_image, length, width, x_percent, y_percent, scale_factor=1.0, filled_percent=0.5):
        """
        Initialize a Slider object.
        """
        self.screen = screen
        self.length = length
        self.width = width
        self.x_percent = x_percent
        self.y_percent = y_percent
        self.scale_factor = scale_factor

        screen_width, screen_height = self.screen.get_size()
        self.x = screen_width * x_percent - length / 2
        self.y = screen_height * y_percent - width / 2

        self.background = ninepatch.NinePatch(screen, background_image, self.x, self.y, length, width)
        self.foreground = ninepatch.NinePatch(screen, foreground_image, self.x, self.y, length, width)

        # Scaling the knob image
        self.knob_image = pygame.transform.scale(knob_image, (int(knob_image.get_width() * scale_factor), int(knob_image.get_height() * scale_factor)))
        self.knob_width = self.knob_image.get_width()
        self.knob_height = self.knob_image.get_height()

        self.slider_value = self.set_value(filled_percent)

    def set_value(self, value):
        self.slider_value = min(1, max(0, value))
        
    def draw(self):
        # Draw background
        self.background.draw()

        # Calculate filled area
        filled_width = self.length * self.slider_value
        filled_rect = pygame.Rect(self.x, self.y, filled_width, self.width)

        # Draw foreground with clipping
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(filled_rect)
        self.foreground.draw()
        self.screen.set_clip(prev_clip)

        # Position and draw the knob
        knob_x = self.x + filled_width - self.knob_width / 2
        knob_y = self.y + self.width / 2 - self.knob_height / 2
        self.screen.blit(self.knob_image, (knob_x, knob_y))

    def handle_event(self, event):
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]:
            if pygame.mouse.get_pressed()[0]:
                mouse_x, mouse_y = event.pos
                if self.is_mouse_over_slider(mouse_x, mouse_y):
                    new_value = (mouse_x - self.x) / self.length
                    self.slider_value = max(0.0, min(1.0, new_value))

    def is_mouse_over_slider(self, mouse_x, mouse_y):
        return (self.x <= mouse_x <= self.x + self.length and
                self.y <= mouse_y <= self.y + self.width)