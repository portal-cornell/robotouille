import pygame
from frontend import image, node

class Button(node.Node):
    def __init__(self, screen, normal_image_source, hover_image_source, pressed_image_source, x_percent, y_percent, scale_factor=1.0, text=None, font=None, text_color=(0, 0, 0), anchor = "center"):
        super().__init__(screen, normal_image_source, x_percent, y_percent, anchor)

        self.normal_image = image.Image(screen, normal_image_source, x_percent, y_percent, scale_factor)
        self.hover_image = image.Image(screen, hover_image_source, x_percent, y_percent, scale_factor)
        self.pressed_image = image.Image(screen, pressed_image_source, x_percent, y_percent, scale_factor)

        self.current_image = self.normal_image
        self.text = text
        self.font = font
        self.text_color = text_color
        self.is_pressed = False
        self.is_pressed_outside = False

    def draw(self):
        """Draw the button and the text (if any) separately."""
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
        """Check if the mouse is over the button."""
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def is_hovered(self):
        """Check if the mouse is over the button and no outside click is in progress."""
        return self.in_bound() and not self.is_pressed_outside

    def handle_event(self, event):
        """Handle mouse events for button interactions."""
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

