from robotouille import simulator
import argparse
import pygame
from frontend.constants import SETTINGS, MAIN_MENU, GAME, ENDGAME, LOADING, LOGO, MATCHMAKING
from frontend.main_menu import MenuScreen
from frontend.settings import SettingScreen
from frontend.loading import LoadingScreen
from frontend.logo import LogoScreen
from frontend.endgame import EndScreen
from frontend.matchmaking import MatchMakingScreen
from frontend.pause import PauseScreen


parser = argparse.ArgumentParser()
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None)
parser.add_argument("--noisy_randomization", action="store_true", help="Whether to use 'noisy randomization' for procedural generation")
args = parser.parse_args()


pygame.init()
screen_size = (1440, 1024)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Game")

screens = {
    MAIN_MENU: MenuScreen(screen),
    SETTINGS: SettingScreen(screen),
    LOGO: LogoScreen(screen),
    LOADING: LoadingScreen(screen),
    ENDGAME: EndScreen(screen),
    MATCHMAKING: MatchMakingScreen(screen)
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
        if simulator(screen, args.environment_name, args.seed, args.noisy_randomization):
            current_screen = MAIN_MENU
            screen = pygame.display.set_mode(screen_size)
    else:
        if current_screen == MATCHMAKING:
            screens[current_screen].setPlayers(["Player1", "Player2"])
        
        if current_screen == ENDGAME:
            screens[current_screen].createProfile([(1,  "Player 1"), (2, "Player 1"), (3, "Player 1")])
            screens[current_screen].setStars(1)
            screens[current_screen].setCoin(12)
            screens[current_screen].setBell(121)
        update_screen()

    pygame.display.flip()
    
pygame.quit()
