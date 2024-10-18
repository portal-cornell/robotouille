from robotouille import simulator
import argparse
import pygame
from frontend.constants import SETTINGS, MAIN_MENU, GAME  # Import specific constants
from frontend.main_menu import MenuScreen  # Import MenuScreen class
from frontend.settings import SettingScreen  # Import SettingScreen class



parser = argparse.ArgumentParser()
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None)
parser.add_argument("--noisy_randomization", action="store_true", help="Whether to use 'noisy randomization' for procedural generation")
args = parser.parse_args()


# Screen logic 

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Game")

# Create the screens
main_menu = MenuScreen(screen)
settings = SettingScreen(screen)

# Initialize the current screen state; could also make this hold the current screen instead
current_screen = MAIN_MENU

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Transition logic based on current_screen
    if current_screen == MAIN_MENU:
        main_menu.update()
        if main_menu.next_screen == SETTINGS:
            current_screen = SETTINGS
            main_menu.set_next_screen(None) 

        elif main_menu.next_screen == GAME:
            current_screen = GAME
            main_menu.set_next_screen(None)

    elif current_screen == SETTINGS:
        settings.update()
        if settings.next_screen == MAIN_MENU:
            current_screen = MAIN_MENU
            settings.set_next_screen(None) 
        
    elif current_screen == GAME:
        simulator(args.environment_name, args.seed, args.noisy_randomization)

    # This line updates the screen display for the latest changes
    pygame.display.flip()  # Ensures the display is updated after rendering

pygame.quit()




   
