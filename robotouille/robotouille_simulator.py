import pygame
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env
from frontend.pause import PauseScreen

def simulator(surface, screen_size, environment_name: str, seed: int=42, noisy_randomization: bool=False):
    # Your code for robotouille goes here
    intermediate = pygame.Surface((512,512))
    env, json, renderer = create_robotouille_env(environment_name, intermediate, seed, noisy_randomization)
    obs, info = env.reset()
    renderer.render(obs, mode='human')
    done = False
    interactive = False # Set to True to interact with the environment through terminal REPL (ignores input)

    screen_size = intermediate.get_size()
    pause = PauseScreen(screen_size)
    flag = True
    while not done:
        # Handle keypresses 
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return True
                if event.key == pygame.K_p:
                    flag = True
                    pause.toggle()
                

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
        
        pause.update()  

        if not interactive and action is None and not flag:
            # Retry for keyboard input
            continue

        obs, reward, done, info = env.step(actions, interactive=interactive)
        renderer.render(obs, mode='human')
        intermediate.blit(pause.get_screen(), (0, 0))
        surface.blit(intermediate, (0,0))
        pygame.display.flip()
        flag = False

    renderer.render(obs, close=True)
