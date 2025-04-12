import pygame
import pygame_gui
from pygame_gui.elements import *

pygame.init()
pygame.display.set_caption("Domain Editor")

# game window
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
LOWER_MARGIN = 300
SIDE_MARGIN = 300

LEFT_WIDTH = 200
RIGHT_WIDTH = 200
CENTER_WIDTH = SCREEN_WIDTH - LEFT_WIDTH - RIGHT_WIDTH

window_surface = pygame.display.set_mode(
    (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN)
)
