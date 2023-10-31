import pygame
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env


def simulator(environment_name: str, seed: int=42, noisy_randomization: bool=False):
    # Your code for robotouille goes here
    env, json, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
    obs, info = env.reset()
    env.render(mode='human')
    done = False
    interactive = False # Set to True to interact with the environment through terminal REPL (ignores input)

    while not done:
        # Construct action from input
        pygame_events = pygame.event.get()
        # Mouse clicks for movement and pick/place stack/unstack
        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        # Keyboard events ('e' button) for cut/cook ('space' button) for noop
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        action = create_action_from_control(env, obs, mousedown_events+keydown_events, renderer)
        if not interactive and action is None:
            # Retry for keyboard input
            continue
        obs, reward, done, info = env.step(action=action, interactive=interactive)
        env.render(mode='human')