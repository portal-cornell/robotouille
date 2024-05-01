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
    
    if animate:
        players = obs.get_players()
        actions = []
        i = 0
        while not done:
            i += 1
            if i%200000 != 0:
                continue
            pygame_events = pygame.event.get()
            mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
            keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
            player_obj = obs.movement.get_player(obs.current_player.name)
            no_action = True
            
            # If player is moving, do not allow any action; action will be None
            if player_obj.is_moving():
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
                print(actions)
                obs, reward, done, info = env.step(actions, interactive=interactive)
                renderer.render(obs, mode='human')
                actions = []
    
    else:
        while not done:
            # Construct action from input
            pygame_events = pygame.event.get()
            # Mouse clicks for movement and pick/place stack/unstack
            mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
            # Keyboard events ('e' button) for cut/cook ('space' button) for noop
            keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
            # Check if player has made an action
            action, args = create_action_from_control(env, obs, obs.current_player, mousedown_events+keydown_events, renderer)
            if not interactive and action is None:
                # Retry for keyboard input
                continue
            # Construct actions for all players
            actions = []
            # Set action for current player, and None for others
            for player in obs.get_players():
                if player == obs.current_player:
                    actions.append((action, args))
                else:
                    actions.append((None, None))
            obs, reward, done, info = env.step(actions, interactive=interactive)
            renderer.render(obs, mode='human')
    renderer.render(obs, close=True)
