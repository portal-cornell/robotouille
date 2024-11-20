import pygame
import time
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env
from frontend.pause import PauseScreen
from frontend.constants import *
from backend.movement.player import Player
from backend.movement.movement import Movement, Mode


def simulator(surface, environment_name: str, seed: int=42, noisy_randomization: bool=False, movement_mode: str='traverse'):
    # Your code for robotouille goes here
    env, json, renderer = create_robotouille_env(environment_name, movement_mode, seed, noisy_randomization)
    obs, info = env.reset()
    renderer.render(obs, mode='human')
    done = False
    interactive = False # Set to True to interact with the environment through terminal REPL (ignores input)
    screen_size = surface.get_size()
    intermediate = pygame.Surface(screen_size)
    pause = PauseScreen(screen_size)
    flag = True
    clock = pygame.time.Clock()
    
    players = obs.get_players()
    actions = []
    while not done:
        renderer.render(obs, mode='human')
        pygame_events = pygame.event.get()
        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        player_obj = Player.get_player(obs.current_player.name)
        no_action = True

        # Handle keypresses 
        for event in pygame_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return ENDGAME
                if event.key == pygame.K_p:
                    flag = True
                    pause.toggle()

        if pause.next_screen is not None:
            current_screen = pause.next_screen
            pause.set_next_screen(None)
            return current_screen

        pause.update(pygame_events)  
             
        actions = []
        action, args = create_action_from_control(env, obs, obs.current_player, mousedown_events+keydown_events, renderer)
        for player in obs.get_players():
            if player == obs.current_player:
                actions.append((action, args))
            else:
                actions.append((None, None))

        if not interactive and action is None and not flag:
            # Retry for keyboard input
            continue
        
        if interactive or action:
            # If player is moving, do not allow any action; action will be None
            if Movement.is_player_moving(player_obj.name):
                action, args = None, None
                no_action = False
            # If player is not moving, allow action
            else:
                action, args = create_action_from_control(env, obs, obs.current_player, mousedown_events+keydown_events, renderer)
                if action is not None:
                    no_action = False

            if not interactive and no_action:
                # Retry for keyboard input
                continue
            
            # Construct actions for all players
            actions.append((action, args))
            obs.current_player = obs.next_player()

            # If all players have made an action, step the environments
            if len(actions) == len(players):
                obs, reward, done, info = env.step(actions, clock=renderer.clock, interactive=interactive)
                renderer.render(obs, mode='human')
                actions = []


        intermediate.fill((0, 0, 0))
        intermediate.blit(renderer.surface, (0, 0))
        intermediate.blit(pause.get_screen(), (0, 0))

        surface.blit(intermediate, (0,0))
        pygame.display.flip()
        
        flag = False
        clock.tick(60)
        player_obj = Player.get_player(obs.current_player.name)
        no_action = True
        
    
    renderer.render(obs, close=True)
