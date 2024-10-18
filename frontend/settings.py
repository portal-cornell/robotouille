import pygame
from frontend import constants

class SettingScreen:
    def __init__(self, screen):
        """Initialize the settings screen."""
        self.screen = screen
        self.active = False
        self.next_screen = None

        # Define screen size and other attributes
        self.screen.fill(constants.GREY)
        self.font = pygame.font.SysFont(None, 55)
        self.text = self.font.render("Settings", True, constants.WHITE)

    def set_active(self, active):
        """Set the screen as active or inactive."""
        self.active = active

    def set_next_screen(self, next_screen):
        """Set the next screen to transition to."""
        self.next_screen = next_screen

    def update(self):
        """Update the screen while it's active and handle keypress events."""
        self.screen.fill(constants.GREY)
        self.screen.blit(self.text, (100, 100))
        pygame.display.flip()

        # Handle keypresses specific to the settings menu
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            # Transition back to the main menu
            self.set_next_screen(constants.MAIN_MENU)
