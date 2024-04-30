import pygame
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env


def simulator(environment_name: str, seed: int=42, noisy_randomization: bool=False):
    # Your code for robotouille goes here
    animate = True # Set to True to enable animate mode
    env, json, renderer = create_robotouille_env(environment_name, animate, seed, noisy_randomization)
    obs, info = env.reset()
    renderer.render(obs, mode='human')
    done = False
    interactive = False # Set to True to interact with the environment through terminal REPL (ignores input)

    i = 0
    while not done:
        i += 1
        if i%200000 != 0:
            continue
        # Construct action from input
        pygame_events = pygame.event.get()
        # Mouse clicks for movement and pick/place stack/unstack
        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        # Keyboard events ('e' button) for cut/cook ('space' button) for noop
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        players = obs.get_players()
        actions = []
        no_actions = True
        if not animate:
            action, args = create_action_from_control(env, obs, obs.current_player, mousedown_events+keydown_events, renderer)
            if action is not None:
                no_actions = False
            for player in players:
                if player == obs.current_player:
                    actions.append((action, args))
                else:
                    actions.append((None, None))
        else:
            for player in players:
                player_obj = obs.movement.get_player(player.name)
                if player_obj.is_moving():
                    action, args = (None, None)
                    no_actions = False
                else:
                    action, args = create_action_from_control(env, obs, player, mousedown_events+keydown_events, renderer)
                    if action is not None:
                        no_actions = False
                actions.append((action, args))
        if not interactive and no_actions:
            # Retry for keyboard input
            continue
        obs, reward, done, info = env.step(actions, interactive=interactive)
        renderer.render(obs, mode='human')
    renderer.render(obs, close=True)
