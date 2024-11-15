import pygame
from frontend.ninepatch import NinePatch
from frontend.image import Image
from frontend.node import Node

class Slider(Node):
    def __init__(self, screen, background_image, foreground_image, background_width, background_height, 
                 foreground_width, foreground_height, x_percent, y_percent, scale_factor=1, filled_percent=0.5, knob_image=None, anchor = "center"):
        """
        Initialize a Slider object.

        Args:
            screen (pygame.Surface): The display surface where the slider will be drawn.
            background_image (pygame.Surface): Background image of the slider.
            foreground_image (pygame.Surface): Foreground image of the slider.
            background_width (float): Width of the background in pixels.
            background_height (float): Height of the background in pixels.
            foreground_width (float): Width of the foreground in pixels.
            foreground_height (float): Height of the foreground in pixels.
            x_percent (float): X position as a percentage of the screen width.
            y_percent (float): Y position as a percentage of the screen height.
            scale_factor (float, optional): Scale factor for resizing the images. Defaults to 1.0.
            filled_percent (float): Initial filled percentage of the slider (0 to 1). Defaults to 0.5.
            knob_image (pygame.Surface, optional): Knob image. Defaults to None.
            anchor (str, optional): Determines how the textbox rectangle is anchored on the screen. Options are "center" or "topleft". Defaults to "center".
        """

        self.background_width = background_width * scale_factor
        self.background_height = background_height * scale_factor
        self.foreground_width = foreground_width * scale_factor
        self.foreground_height = foreground_height * scale_factor
        super().__init__(screen, pygame.Surface((int(self.background_width), int(self.background_height))), x_percent, y_percent, anchor)
        self.scale_factor = scale_factor

        self.background = NinePatch(screen, background_image, self.x, self.y, self.background_width, self.background_height, scale_factor=self.scale_factor)
        
        self.foreground_x = self.x + (self.background_width - self.foreground_width) / 2
        self.foreground_y = self.y + (self.background_height - self.foreground_height) / 2
        self.foreground = NinePatch(screen, foreground_image, self.foreground_x, self.foreground_y, self.foreground_width, self.foreground_height, scale_factor=self.scale_factor)

        self.knob = None
        if knob_image:
            self.knob = Image(screen, knob_image, x_percent, y_percent, self.scale_factor, anchor="center")

        self.setValue(filled_percent)
        self.moving = False

    def setValue(self, value):
        """
        Set the slider's value (filled percentage), ensuring it is between 0 and 1.

        Args:
           value (float): The new filled percentage for the slider, clamped between 0 and 1.
        """
        self.slider_value = max(0.0, min(1.0, value))
        self.update_knob_position()

    def getValue(self):
        """
        Get the slider's current value (filled percentage).

        Returns:
           float: The current filled percentage of the slider.
        """
        return self.slider_value 
        
    def update_knob_position(self):
        """
        Update the knob's position based on the slider value.
        """
        if self.knob:
            filled_width = self.background_width * self.slider_value
            knob_x_percent = self.x_percent + (filled_width - self.background_width / 2) / self.screen.get_width()
            self.knob.set_percentage(new_x_percent=knob_x_percent)

    def draw(self):
        """
        Draw the slider components: background, foreground, and knob.
        """
        self.background.draw()
        
        filled_width = self.foreground_width * self.slider_value
        self.foreground.set_width(filled_width)
        self.foreground.draw()
        
        if self.knob:
            self.knob.draw()

    def handle_event(self, event):
        """
        Handle mouse events to update the slider value.

        Args:
           event (pygame.event.Event): The Pygame event to handle, typically of type MOUSEBUTTONDOWN or MOUSEMOTION.
        """

        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]:
            if pygame.mouse.get_pressed()[0]: 
                mouse_x, mouse_y = event.pos
                if self.is_mouse_over_slider(mouse_x, mouse_y):
                    new_value = (mouse_x - (self.x + (self.background_width - self.foreground_width) / 2)) / self.foreground_width
                    self.setValue(new_value)
                    self.moving = True
            else:
                self.moving = False 
        else:
            self.moving = False 

    def is_moving(self):
        """
        Check if the slider is currently being moved by the user.

        Returns:
           (bool): True if the slider is being dragged; False otherwise.
        """
        return self.moving
    
    def is_mouse_over_slider(self, mouse_x, mouse_y):
        """
        Check if the mouse is over the slider's area.

        Args:
           mouse_x (int): The x-coordinate of the mouse position.
           mouse_y (int): The y-coordinate of the mouse position.

        Returns:
           (bool): True if the mouse is within the bounds of the slider; False otherwise.
        """
        return (self.x <= mouse_x <= self.x + self.background_width and
                self.y <= mouse_y <= self.y + self.background_height)
