import pygame
from utils.robotouille_input import create_action_from_event
from robotouille.robotouille_env import create_robotouille_env

def simulator(environment_name: str, seed: int=42, noisy_randomization: bool=False):
    # Your code for robotouille goes here
    env, json, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
    obs, info = env.reset()
    env.render()
    done = False
    
    while not done:
        current_state = env.current_state
        # Construct action from input
        pygame_events = pygame.event.get()
        # Mouse clicks for movement and pick/place stack/unstack
        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        # Keyboard events ('e' button) for cut/cook ('space' button) for noop
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        actions = []
        action, param_arg_dict = create_action_from_event(current_state, mousedown_events+keydown_events, env.input_json, renderer)
        for player in current_state.get_players():
            if player == current_state.current_player:
                actions.append((action, param_arg_dict))
            else:
                actions.append((None, None))
        if action is None:
            # Retry for keyboard input
            continue
        obs, reward, done, info = env.step(actions)
        env.render()
        print(obs)
    env.render(close=True)
