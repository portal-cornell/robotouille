import pygame
from frontend import constants

class MenuScreen:
    def __init__(self, screen):
        """Initialize the main menu screen."""
        self.screen = screen
        self.active = False
        self.next_screen = None

        # Define screen size and other attributes
        self.screen.fill(constants.BLUE)
        self.font = pygame.font.SysFont(None, 55)
        self.text = self.font.render("Main Menu", True, constants.WHITE)

    def set_active(self, active):
        """Set the screen as active or inactive."""
        self.active = active

    def set_next_screen(self, next_screen):
        """Set the next screen to transition to."""
        self.next_screen = next_screen

    def update(self):
        """Update the screen while it's active and handle keypress events."""
        self.screen.fill(constants.BLUE)
        self.screen.blit(self.text, (100, 100))
        pygame.display.flip()

        # Handle keypresses specific to the main menu
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            # Transition to the settings screen
            self.set_next_screen(constants.SETTINGS)

        elif keys[pygame.K_r]:
            # Call the simulator function (trigger transition to game)
            self.set_next_screen(constants.GAME)