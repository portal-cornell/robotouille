import pygame
from frontend import image

class Button():
    def __init__(self, screen, normal_image_source, hover_image_source, pressed_image_source, x_percent, y_percent, scale_factor=1.0, text=None, font=None, text_color=(0, 0, 0)):
        self.screen = screen
        self.x_percent = x_percent
        self.y_percent = y_percent

        self.normal_image = image.Image(screen, normal_image_source, x_percent, y_percent, scale_factor)
        self.hover_image = image.Image(screen, hover_image_source, x_percent, y_percent, scale_factor)
        self.pressed_image = image.Image(screen, pressed_image_source, x_percent, y_percent, scale_factor)

        self.current_image = self.normal_image
        self.rect = self.normal_image.image.get_rect()
        self.rect.center = (x_percent * screen.get_width(), y_percent * screen.get_height())
        self.text = text
        self.font = font
        self.text_color = text_color
        self.is_pressed = False

    def is_hovered(self):
        """Check if the mouse is over the button."""
        return self.rect.collidepoint(pygame.mouse.get_pos())

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

    def handle_event(self, event):
        """Handle mouse events for button state changes."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered():
                self.is_pressed = True  
            if self.is_pressed and self.is_hovered():
                self.is_pressed = False
                return True  
            self.is_pressed = False 
        return False  
