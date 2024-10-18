import pygame
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env
import networking.server as robotouille_server
import networking.client as robotouille_client
import networking.utils.single_player as robotouille_single_player
import networking.utils.replay as robotouille_replay
import networking.utils.render as robotouille_render

def simulator(environment_name: str, seed: int=42, noisy_randomization: bool=False, role: str="local", display_server: bool=False, host: str="ws://localhost:8765", recording: str=""):
    # We assume that if a recording is provided, then the user would like to replay it
    if recording != "" and role != "replay" and role != "render":
        role = "replay"
    
    if role == "local":
        simulate(environment_name, seed, noisy_randomization)
    if role == "server":
        robotouille_server.run_server(environment_name, seed, noisy_randomization, display_server)
    elif role == "client":
        robotouille_client.run_client(environment_name, seed, host, noisy_randomization)
    elif role == "single":
        robotouille_single_player.run_single(environment_name, seed, noisy_randomization)
    elif role == "replay":
        robotouille_replay.run_replay(recording)
    elif role == "render":
        robotouille_render.run_render(recording)
    else:
        print("Invalid role:", role)

def simulate(environment_name, seed, noisy_randomization):
    # Your code for robotouille goes here
    env, json, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
    obs, info = env.reset()
    renderer.render(obs, mode='human')
    done = False
    interactive = False # Set to True to interact with the environment through terminal REPL (ignores input)
    
    while not done:
        # Construct action from input
        pygame_events = pygame.event.get()
        # Mouse clicks for movement and pick/place stack/unstack
        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        # Keyboard events ('e' button) for cut/cook ('space' button) for noop
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        actions = []
        action, args = create_action_from_control(env, obs, obs.current_player, mousedown_events+keydown_events, renderer)
        for player in obs.get_players():
            if player == obs.current_player:
                actions.append((action, args))
            else:
                actions.append((None, None))
        if not interactive and action is None:
            # Retry for keyboard input
            continue
        obs, reward, done, info = env.step(actions, interactive=interactive)
        renderer.render(obs, mode='human')
    renderer.render(obs, close=True)
