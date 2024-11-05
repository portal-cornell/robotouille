import pygame
from frontend import node

class Textbox(node.Node):
    def __init__(self, screen, text, font, x_percent, y_percent, width, height, text_color=(0, 0, 255), scale_factor=1.0):
        super().__init__(screen, pygame.Surface((width, height)), x_percent, y_percent)
        
        self.text = text
        self.font = font
        self.text_color = text_color
        self.scale_factor = scale_factor
        self.text_surface = None  
        self.is_editing = False
    

        self.update_text_rect()

    def update_text_rect(self):
        """Render the text (with cursor if editing) and update rectangle dimensions and position."""
        if self.font:
            self.text_surface = self.font.render(self.text, True, self.text_color)
            scaled_size = (int(self.text_surface.get_width() * self.scale_factor),
                           int(self.text_surface.get_height() * self.scale_factor))
            self.text_surface = pygame.transform.scale(self.text_surface, scaled_size)
            self.rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self):
        """Draw the text surface on the screen."""
        if self.text_surface:
            self.screen.blit(self.text_surface, self.rect)

    def set_text(self, new_text):
        """Update the text and refresh the text surface."""
        self.text = new_text
        self.update_text_rect()
    
    def handle_event(self, event):
        """Handle key events for editing the textbox text."""
        if event.type == pygame.KEYDOWN and self.is_editing:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isalnum(): 
                self.text += event.unicode
            else:
                return
            self.update_text_rect() 

    def toggle_editing(self):
        """Toggle editing mode."""
        self.is_editing = not self.is_editing

