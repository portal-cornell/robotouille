import argparse
import pygame

from game.simulator import RobotouilleSimulator

from frontend.constants import SETTINGS, MAIN_MENU, GAME, ENDGAME, LOADING, LOGO, MATCHMAKING
from frontend.main_menu import MenuScreen
from frontend.settings import SettingScreen
from frontend.loading import LoadingScreen
from frontend.logo import LogoScreen
from frontend.endgame import EndScreen
from frontend.matchmaking import MatchMakingScreen

from omegaconf import DictConfig, OmegaConf

pygame.init()
pygame.display.init()
screen_size = (1440, 1024)
screen = pygame.display.set_mode(screen_size)
simulator_screen_size = (512, 512) # TODO: Make this scale based on screen size
# simulator_screen_size = screen_size
fps = 60
pygame.display.set_caption('Robotouille Simulator')
clock = pygame.time.Clock()

def game():
    global screen_size, screen, simulator_screen_size, fps, args
    screens = {
        LOGO: LogoScreen(screen_size),
        LOADING: LoadingScreen(screen_size),
    }

    current_screen = LOGO
    running = True
    simulator_instance = None

    def update_screen():
        nonlocal current_screen
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
        screen.fill((0,0,0))
        if current_screen == GAME:
            if simulator_instance is None:
                screen = pygame.display.set_mode(simulator_screen_size) # TODO: Remove when screen size can scale properly
                simulator_instance = RobotouilleSimulator(
                        screen=screen,
                        environment_name=args.environment_name,
                        seed=args.seed,
                        noisy_randomization=args.noisy_randomization,
                        movement_mode=args.movement_mode,
                        clock=clock,
                        screen_size=simulator_screen_size,
                        render_fps=fps
                    )
                
            simulator_instance.update()
            screen.blit(simulator_instance.get_screen(), (0, 0))
            if simulator_instance.next_screen is not None:
                current_screen = simulator_instance.next_screen
                simulator_instance.set_next_screen(None)
                simulator_instance = None 
                screen = pygame.display.set_mode(screen_size)

        else:
            if current_screen == MATCHMAKING:
                screens[current_screen].set_players(["Player1", "Player2"]) # list of dictionary of profile + names [{name: ----, profile_image: ----.png, id: ___}]
            
            if current_screen == ENDGAME:
                screens[current_screen].create_profile([(1,  "Player 1", "profile"), (2, "Player 2", "profile")]) # [{id, name, profile, status}]
                screens[current_screen].set_stars(1) # 
                screens[current_screen].set_coin(12)
                screens[current_screen].set_bell(121)
            update_screen()

        pygame.display.flip()
        clock.tick(fps)
        
    pygame.quit()

def main():
    global screen_size, screen, simulator_screen_size, fps, args
    loading = LoadingScreen(screen_size)
    loading.load_all_assets()
    
    screen = pygame.display.set_mode(simulator_screen_size) # TODO: Remove when screen size can scale properly
    simulator_instance = RobotouilleSimulator(
        screen=screen,
        environment_name=args.environment_name,
        seed=args.seed,
        noisy_randomization=args.noisy_randomization,
        movement_mode=args.movement_mode,
        clock=clock,
        screen_size=simulator_screen_size,
        render_fps=fps
    )
    
    while not simulator_instance.done:
        screen.fill((0,0,0))
        simulator_instance.update()
        screen.blit(simulator_instance.get_screen(), (0, 0))
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
    game()