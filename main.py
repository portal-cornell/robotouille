from robotouille import simulator
import argparse
import pygame
from frontend.constants import SETTINGS, MAIN_MENU, GAME, ENDGAME, LOADING, LOGO, MATCHMAKING
from frontend import main_menu, settings, loading, logo, endgame, matchmaking


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

screens = {
    MAIN_MENU: main_menu.MenuScreen(screen),
    SETTINGS: settings.SettingScreen(screen),
    LOGO: logo.LogoScreen(screen),
    LOADING: loading.LoadingScreen(screen),
    ENDGAME: endgame.EndScreen(screen),
    MATCHMAKING: matchmaking.MatchMakingScreen(screen)
}

current_screen = LOGO
clock = pygame.time.Clock()
running = True

def update_screen():
    global current_screen
    if current_screen in screens:
        screen_obj = screens[current_screen]
        screen_obj.update()
        if screen_obj.next_screen is not None:
            current_screen = screen_obj.next_screen
            screen_obj.set_next_screen(None)

while running:
    if current_screen == GAME:
        if simulator(args.environment_name, args.seed, args.noisy_randomization):
            current_screen = MAIN_MENU
            screen = pygame.display.set_mode(screen_size)
    else:
        update_screen()

    pygame.display.flip()
    # clock.tick(60)
    
pygame.quit()
