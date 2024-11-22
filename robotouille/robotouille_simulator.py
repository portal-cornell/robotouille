import pygame
import time
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env
from backend.movement.player import Player
from backend.movement.movement import Movement, Mode

import networking.server as robotouille_server
import networking.client as robotouille_client
import networking.utils.single_player as robotouille_single_player
import networking.utils.replay as robotouille_replay
import networking.utils.render as robotouille_render

def simulator(environment_name: str, seed: int=42, noisy_randomization: bool=False, movement_mode: str='traverse', role: str="local", display_server: bool=False, host: str="ws://localhost:8765", recording: str=""):
    # We assume that if a recording is provided, then the user would like to replay it
    if recording != "" and role != "replay" and role != "render":
        role = "replay"
    
    if role == "local":
        simulate(environment_name, seed, noisy_randomization, movement_mode)
    elif role == "server":
        robotouille_server.run_server(environment_name, seed, noisy_randomization, movement_mode, display_server)
    elif role == "client":
        robotouille_client.run_client(environment_name, seed, noisy_randomization, movement_mode, host)
    elif role == "single":
        robotouille_single_player.run_single(environment_name, seed, noisy_randomization, movement_mode)
    elif role == "replay":
        robotouille_replay.run_replay(recording)
    elif role == "render":
        robotouille_render.run_render(recording)
    else:
        print("Invalid role:", role)

def simulate(environment_name, seed, noisy_randomization, movement_mode):
    # Your code for robotouille goes here
    env, json, renderer = create_robotouille_env(environment_name, movement_mode, seed, noisy_randomization)
    obs, info = env.reset()
    renderer.render(obs, mode='human')
    done = False
    interactive = False # Set to True to interact with the environment through terminal REPL (ignores input)
    
    players = obs.get_players()
    actions = []
    while not done:
        renderer.render(obs, mode='human')
        pygame_events = pygame.event.get()
        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        player_obj = Player.get_player(obs.current_player.name)
        no_action = True
        
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

    renderer.render(obs, close=True)
