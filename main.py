from robotouille import simulator
import argparse
import pygame
from frontend.constants import SETTINGS, MAIN_MENU, GAME  
from frontend.main_menu import MenuScreen  
from frontend.settings import SettingScreen  


parser = argparse.ArgumentParser()
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None)
parser.add_argument("--noisy_randomization", action="store_true", help="Whether to use 'noisy randomization' for procedural generation")
args = parser.parse_args()


pygame.init()
screen_size = (800, 400)
screen_size = (1440, 1024)
screen = pygame.display.set_mode(screen_size)
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
        if main_menu.next_screen is not None:
            current_screen = main_menu.next_screen 
            main_menu.set_next_screen(None) 

    elif current_screen == SETTINGS:
        settings.update()
        if settings.next_screen is not None:
            current_screen = settings.next_screen
            settings.set_next_screen(None) 
        
    elif current_screen == GAME:
        if simulator(args.environment_name, args.seed, args.noisy_randomization):
            current_screen = MAIN_MENU
            screen = pygame.display.set_mode(screen_size)
    pygame.display.flip()  

pygame.quit()




   
