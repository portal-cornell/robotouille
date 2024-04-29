import pygame
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env


def simulator(environment_name: str, seed: int=42, noisy_randomization: bool=False):
    # Your code for robotouille goes here
    animate = False # Set to True to enable animate mode
    env, json, renderer = create_robotouille_env(environment_name, animate, seed, noisy_randomization)
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
        
        if not animate:
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
