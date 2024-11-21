import pygame
from frontend.image import Image
from frontend.node import Node
from frontend.constants import *
from frontend.textbox import Textbox
from frontend.constants import FONT_PATH

class Button(Node):
    def __init__(self, screen, normal_image_source, x_percent, y_percent, scale_factor=1.0, hover_image_source = None, pressed_image_source = None, text=None, font_path=FONT_PATH, font_size= 60, text_color=(0, 0, 0), anchor="topleft"):
        """
        Initialize a Button instance.

        Creates a button with normal, hover, and pressed images, positioned on the screen at specified percentages. 
        If the button has text on top, must provide text and font.

        Args:
            screen (pygame.Surface): The screen where the button will be displayed.
            normal_image_source (pygame.Surface): Image of the button's normal state.
            hover_image_source (pygame.Surface): Image of the button's hover state.
            pressed_image_source (pygame.Surface): Image of the button's pressed state.
            x_percent (float): The horizontal position of the button as a percentage of the screen width.
            y_percent (float): The vertical position of the button as a percentage of the screen height.
            scale_factor (float): Scaling factor for the button images. Defaults to 1.0.
            text (str): text to display on the button.
            font_path (str): The path to the font used to render the text.
            font_size (int): The size of the font.
            text_color (tuple): Color of the text in RGB format. Defaults to black.
            anchor (str): Anchor point for positioning. Defaults to "topleft".
        """
        self.normal_image = Image(screen, normal_image_source, x_percent, y_percent, scale_factor, anchor=anchor)
        super().__init__(screen, self.normal_image.image, x_percent, y_percent, anchor)

        self.text = None

        width, height = self.rect.width, self.rect.height
        if text is not None:
            self.text = Textbox(screen, text, x_percent, y_percent, width, height, text_color=text_color, font_path=font_path, font_size=font_size * scale_factor, anchor=anchor)


        self.hover_image = Image(screen, hover_image_source if hover_image_source else normal_image_source, x_percent, y_percent, scale_factor, anchor=anchor)
        self.pressed_image = Image(screen, pressed_image_source if pressed_image_source else normal_image_source, x_percent, y_percent, scale_factor, anchor=anchor)
        self.current_image = self.normal_image
       
        self.is_pressed = False

    def draw(self):
        """
        Draw the button and its text (if any).

        Updates the button's appearance based on its state (normal, hover, pressed) and draws it on the screen.
        If text is provided, it is rendered and displayed at the button's center.
        """
        
        if self.is_pressed:
            self.current_image = self.pressed_image
        elif self.is_hovered():
            self.current_image = self.hover_image
        else:
            self.current_image = self.normal_image

        self.current_image.draw()
        if self.text:
            self.text.draw()

        if DEBUG:
            pygame.draw.rect(self.screen, (255, 0, 0), self.rect, 2)  # Draw a red outline of the clickable region

            
    def in_bound(self):
        """
        Check if the mouse is over the button.

        Returns:
           (bool) True if the mouse position is within the button's bounds; False otherwise.
        """
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def is_hovered(self):
        """
        Check if the mouse is hovering over the button without an outside click in progress.

        Returns:
           (bool) True if the button is hovered and no outside click is active; False otherwise.
        """
        return self.in_bound() and not self.is_pressed

    def handle_event(self, event):
        """
        Handle mouse events for button interactions.

        Processes mouse button events to update the button's state based on clicks and releases.

        Args:
           event (pygame.event.Event): The event to handle, typically of type MOUSEBUTTONDOWN or MOUSEBUTTONUP.

        Returns:
           (bool): True if the button was clicked (i.e., pressed and released within bounds); False otherwise.
        """

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.in_bound():
                self.is_pressed = True
            else:
                self.is_pressed = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed:
                self.is_pressed = False
                return self.in_bound()
        return False  