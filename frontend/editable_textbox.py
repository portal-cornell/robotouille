import pygame
from frontend.textbox import Textbox
from frontend.constants import FONT_PATH
from frontend.constants import GREY, LIGHT_GREY

class EditableTextbox(Textbox):
    def __init__(self, screen, text, x_percent, y_percent, width, height, char_limit = 10, text_color=GREY, font_path=FONT_PATH, font_size= 60, scale_factor=1.0, align_text="center", anchor="topleft"):
        """
        Initialize a Editable Textbox (user's can modify the content inside the textbox) object.

        Args:
            screen (pygame.Surface): The main display surface where the textbox will be rendered.
            text (str): The text to be displayed within the textbox.
            x_percent (float): X-axis position as a percentage of the screen width. Controls the horizontal placement of the rectangle.
            y_percent (float): Y-axis position as a percentage of the screen height. Controls the vertical placement of the rectangle.
            width (int): The width of the textbox rectangle.
            height (int): The height of the textbox rectangle.
            char_limit (int): Max number of characters in textbox
            text_color (tuple, optional): The RGB color of the text. Defaults to Grey.
            font_path (str): The path to the font used to render the text.
            font_size (int): The size of the font.
            scale_factor (float): Scale factor for resizing the text. Defaults to 1.0.
            align_text (str): The alignment of the text within the textbox. Options are "left", "center", or "right". Defaults to "center".
            anchor (str): Determines how the textbox rectangle is anchored on the screen. Options are "center" or "topleft". Defaults to "topleft".
        """
        
        super().__init__(screen, text, x_percent, y_percent, width, height, text_color, font_path, font_size, scale_factor, align_text, anchor)
        self.is_editing = False
        self.original_font_size = int(font_size * scale_factor)
        self.font_path = font_path
        self.old = self.text
        self.char_limit = char_limit

    def set_text(self, new_text):
        """Update the text, adjust font size, and refresh the text surface.
        
         Args:
            new_text (str): The text to be displayed within the editable textbox. 
        """
        self.text = new_text
        self.adjust_font_size()
        self.update_text_rect()
    
    def adjust_font_size(self):
        """Dynamically adjust font size to ensure text fits within the textbox width."""
        current_font_size = self.original_font_size
        self.font = pygame.font.Font(self.font_path, current_font_size)
        
        while self.font.size(self.text)[0] > self.surface.get_width() and current_font_size > 10:
            current_font_size -= 1
            self.font = pygame.font.Font(self.font_path, current_font_size)
    
    def handle_event(self, event):
        """Handle key and mouse events for editing the textbox text.
        
        Args:
            event (pygame.event.Event): An instance of the Event class in Pygame, usually a keypress or mouse click.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.toggle_editing()
        
        if event.type == pygame.KEYDOWN and self.is_editing:
            if event.key == pygame.K_RETURN:
                self.toggle_editing()
            elif event.key == pygame.K_BACKSPACE:
                self.set_text(self.text[:-1])
            elif event.unicode.isalnum() and len(self.text) < self.char_limit: 
                self.set_text(self.text + event.unicode)
    

    def is_text_valid(self):
        """
        Check if the current text is appropriate based on defined validation criteria.

        Returns:
            bool: True if the current text is deemed valid; otherwise, False.
        """
        # TODO 
        return len(self.text) > 0
    
    def confirm_text(self):
        """Confirm the text. If not valid, revert to old text. """
        if not self.is_text_valid():
            self.set_text(self.old)
    
    def toggle_editing(self):
        """Toggle editing mode, adjust background color, and confirm text if exiting."""
        self.is_editing = not self.is_editing
        if self.is_editing:
            self.old = self.text  
            self.text_color = LIGHT_GREY
        else:
            self.text_color = GREY
            self.confirm_text() 
        self.update_text_rect()
