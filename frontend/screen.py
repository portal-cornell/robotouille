from abc import ABC, abstractmethod
from frontend import constants

class ScreenInterface(ABC):
    def __init__(self):
        self.next_screen = None

    def set_next_screen(self, next_screen):
        """Set the next screen to transition to."""
        self.next_screen = next_screen

    @abstractmethod
    def draw(self):
        """Draws all the screen components."""
        pass

    def update(self):
        """Update the screen and handle keypress events."""
        self.screen.fill((0, 0, 0))  # Clear screen after changing the state
