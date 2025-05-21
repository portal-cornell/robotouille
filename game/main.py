import argparse
import pygame
import asyncio

from game.simulator import RobotouilleSimulator

from frontend.constants import SETTINGS, MAIN_MENU, GAME, ENDGAME, LOADING, LOGO, MATCHMAKING
from frontend.main_menu import MenuScreen
from frontend.settings import SettingScreen
from frontend.loading import LoadingScreen
from frontend.logo import LogoScreen
from frontend.endgame import EndScreen
from frontend.matchmaking import MatchMakingScreen

from omegaconf import DictConfig, OmegaConf
from networking.client_networking import NetworkManager

pygame.init()
pygame.display.init()
screen_size = (1440, 1024)
screen = pygame.display.set_mode(screen_size)
simulator_screen_size = (512, 512) # TODO: Make this scale based on screen size
# simulator_screen_size = screen_size
fps = 60
pygame.display.set_caption('Robotouille Simulator')
clock = pygame.time.Clock()

def game(args):
    global screen_size, screen, simulator_screen_size, fps
    screens = {
        LOGO: LogoScreen(screen_size),
        LOADING: LoadingScreen(screen_size),
    }
    # TODO create websocket for client (could also be in the loading screen)
    
    current_screen = LOGO
    running = True


    def update_screen():
        """
        transitions the game between different screens
        """
        nonlocal current_screen, args
        if current_screen in screens:
            screen_obj = screens[current_screen]
            screen_obj.update()
            screen.blit(screen_obj.get_screen(), (0, 0))

            if current_screen == LOADING and screen_obj.next_screen is not None:
                # init screens
                screens[MAIN_MENU] = MenuScreen(screen_size)
                screens[SETTINGS] = SettingScreen(screen_size)

            if screen_obj.next_screen is not None:
                # screen transition
                current_screen = screen_obj.next_screen
                screen_obj.set_next_screen(None)

            if current_screen == MATCHMAKING:
                # transfer control to async world
                env_name = args.environment_name
                seed = args.seed
                noisy = args.noisy_randomization
                movement = args.movement_mode
                host = "ws://localhost:8765"
                nm = NetworkManager(env_name, seed, noisy, movement, host, args, screen, fps, clock, screen_size, simulator_screen_size)
                print('entre async world')
                asyncio.run(nm.connect()) 

                # Reinitialize screen elements after async block exits
                print("exit async world")
                if MAIN_MENU not in screens:
                    screens[MAIN_MENU] = MenuScreen(screen_size)
                current_screen = MAIN_MENU
                print('back to main menu')

    while running:
        screen.fill((0,0,0))
        update_screen()
        pygame.display.flip()
        clock.tick(fps)
        
    pygame.quit()

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--environment_name", type=str, default="original")
    argparser.add_argument("--seed", type=int, default=None)
    argparser.add_argument("--noisy_randomization", action="store_true")
    argparser.add_argument("--movement_mode", type=str, default="traverse")
    args = argparser.parse_args()
    game(args)