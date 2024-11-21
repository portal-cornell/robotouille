from robotouille.robotouille_simulator import RobotouilleSimulator
import argparse
import pygame
from frontend.constants import SETTINGS, MAIN_MENU, GAME, ENDGAME, LOADING, LOGO, MATCHMAKING
from frontend.main_menu import MenuScreen
from frontend.settings import SettingScreen
from frontend.loading import LoadingScreen
from frontend.logo import LogoScreen
from frontend.endgame import EndScreen
from frontend.matchmaking import MatchMakingScreen

parser = argparse.ArgumentParser()
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None)
parser.add_argument("--noisy_randomization", action="store_true", help="Whether to use 'noisy randomization' for procedural generation")
parser.add_argument("--movement_mode", help="The movement mode to use for the environment.", default="traverse")
args = parser.parse_args()


pygame.init()
pygame.display.init()
screen_size = (1440, 1024)
# screen_size = (512, 512)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Robotouille Simulator')

screens = {
    LOGO: LogoScreen(screen_size),
    LOADING: LoadingScreen(screen_size),
}

current_screen = LOGO
clock = pygame.time.Clock()
running = True
simulator_instance = None

def update_screen():
    global current_screen
    if current_screen in screens:
        screen_obj = screens[current_screen]
        screen_obj.update()
        screen.blit(screen_obj.get_screen(), (0, 0))

        if current_screen == LOADING and screen_obj.next_screen is not None:
            screens[MAIN_MENU] = MenuScreen(screen_size)
            screens[SETTINGS] = SettingScreen(screen_size)
            screens[ENDGAME] = EndScreen(screen_size)
            screens[MATCHMAKING] = MatchMakingScreen(screen_size)

        if screen_obj.next_screen is not None:
            current_screen = screen_obj.next_screen
            screen_obj.set_next_screen(None)

while running:
    if current_screen == GAME:
        if simulator_instance is None:
            simulator_instance = RobotouilleSimulator(
                    canvas=screen,
                    environment_name=args.environment_name,
                    seed=args.seed,
                    noisy_randomization=args.noisy_randomization,
                    movement_mode=args.movement_mode
                )
        nxt = simulator_instance.update()
        if nxt is not None:
            current_screen = nxt
            simulator_instance = None 
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
