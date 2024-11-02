import pygame
from frontend import image

class Button(image.Image):
    def __init__(self, screen, image_source, x_percent, y_percent, scale_factor=1.0, hover_color=None, click_color=None, text=None, font=None):
        super().__init__(screen, image_source, x_percent, y_percent, scale_factor)
        
        # Set default images for each state
        self.hover_image = self.image.copy()  # Copy to prevent modifying the original
        self.pressed_image = self.image.copy()
        self.text = text

        if hover_color:
            self.hover_image.fill(hover_color, special_flags=pygame.BLEND_RGBA_MULT)
        if click_color:
            self.pressed_image.fill(click_color, special_flags=pygame.BLEND_RGBA_MULT)
        
        # Track button state
        self.is_pressed = False

    def is_hovered(self):
        """Check if the mouse is over the button."""
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self):
        """Draw the button with state-based effects."""
        if self.is_pressed:
            # Show pressed image while the mouse button is down
            self.screen.blit(self.pressed_image, (self.x, self.y))
        elif self.is_hovered():
            # Show hover image if the mouse is over the button
            self.screen.blit(self.hover_image, (self.x, self.y))
        else:
            # Show default image
            self.screen.blit(self.image, (self.x, self.y))

    def handle_event(self, event):
        """Handle mouse events for button state changes."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered():
                self.is_pressed = True  # Set pressed state when clicked
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.is_hovered():
                # Trigger action only if the mouse is released over the button
                self.is_pressed = False
                return True  # Indicates a full click occurred
            self.is_pressed = False  # Reset pressed state if released elsewhere
        return False  # No click action occurred

