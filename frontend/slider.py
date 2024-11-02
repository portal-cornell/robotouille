import pygame
from frontend import ninepatch, image

class Slider:
    def __init__(self, screen, background_image, foreground_image, knob_image, width, height, x_percent, y_percent, scale_factor=1.0, filled_percent=0.5):
        """
        Initialize a Slider object.
        """
        self.screen = screen
        self.width = width
        self.height = height
        self.x_percent = x_percent
        self.y_percent = y_percent
        self.scale_factor = scale_factor

        screen_width, screen_height = self.screen.get_size()
        self.x = screen_width * x_percent - width / 2
        self.y = screen_height * y_percent - height / 2

        self.background = ninepatch.NinePatch(screen, background_image, self.x, self.y, width, height)
        self.foreground = ninepatch.NinePatch(screen, foreground_image, self.x, self.y, width, height)
        self.knob = image.Image(screen, knob_image, x_percent, y_percent, scale_factor, anchor="center")
        self.setValue(filled_percent)

    def setValue(self, value):
        """
        Set the slider's value (filled percentage), ensuring it is between 0 and 1.
        """
        self.slider_value = max(0.0, min(1.0, value))
        self.update_knob_position()

    def update_knob_position(self):
        """
        Update the knob's position based on the slider value.
        """
        filled_width = self.width * self.slider_value
        knob_x_percent = self.x_percent + (filled_width - self.width / 2) / self.screen.get_width()
        self.knob.set_percentage(new_x_percent=knob_x_percent)

    def draw(self):
        self.background.draw()
        filled_width = self.width * self.slider_value
        self.foreground.set_width(filled_width)
        self.foreground.draw()
        self.knob.draw()

    def handle_event(self, event):
        """
        Handle mouse events to update the slider value.
        """
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]:
            if pygame.mouse.get_pressed()[0]: 
                mouse_x, mouse_y = event.pos
                if self.is_mouse_over_slider(mouse_x, mouse_y):
                    new_value = (mouse_x - self.x) / self.width
                    self.setValue(new_value)

    def is_mouse_over_slider(self, mouse_x, mouse_y):
        """
        Check if the mouse is over the slider's area.
        """
        return (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height)
