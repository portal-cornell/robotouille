import pygame
from frontend import image, node

class Button(node.Node):
    def __init__(self, screen, normal_image_source, x_percent, y_percent, scale_factor=1.0, hover_image_source = None, pressed_image_source = None, text=None, font=None, text_color=(0, 0, 0), anchor="center"):
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
           text (str): Optional text to display on the button.
           font (pygame.font.Font): Optional font for rendering the button's text.
           text_color (tuple): Color of the text in RGB format. Defaults to black.
           anchor (str): Anchor point for positioning. Defaults to "center".
        """
        super().__init__(screen, normal_image_source, x_percent, y_percent, anchor)

        self.normal_image = image.Image(screen, normal_image_source, x_percent, y_percent, scale_factor)
        
        self.hover_image = image.Image(screen, hover_image_source if hover_image_source else normal_image_source, x_percent, y_percent, scale_factor)
        self.pressed_image = image.Image(screen, pressed_image_source if pressed_image_source else normal_image_source, x_percent, y_percent, scale_factor)

        self.current_image = self.normal_image
        self.text = text
        self.font = font
        self.text_color = text_color
        self.is_pressed = False
        self.is_pressed_outside = False

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
        if self.text and self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            self.screen.blit(text_surface, text_rect)

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
        return self.in_bound() and not self.is_pressed_outside

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
                self.is_pressed_outside = False
            else:
                self.is_pressed = False
                self.is_pressed_outside = True 
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.in_bound():
                self.is_pressed = False
                self.is_pressed_outside = False
                return True  
            self.is_pressed = False
            self.is_pressed_outside = False
        else:
            self.is_pressed = False
        return False  
