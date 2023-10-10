import robotouille_env
import robotouille_input
import argparse
import pygame

parser = argparse.ArgumentParser()
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None)
parser.add_argument("--noisy_randomization", action="store_true", help="Whether to use 'noisy randomization' for proceudral generation")
args = parser.parse_args()

env, json, renderer = robotouille_env.create_robotouille_env(args.environment_name, args.seed, args.noisy_randomization)
obs, info = env.reset()
env.render(mode='human')
done = False
interactive = False # Set to True to interact with the environment through terminal REPL (ignores input)

while not done:
    # Construct action from input
    pygame_events = pygame.event.get()
    # Mouse clicks for movement and pick/place stack/unstack
    mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
    # Keyboard events ('e' button) for cut/cook
    keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
    action = robotouille_input.create_action_from_control(env, obs, mousedown_events+keydown_events, renderer)

    obs, reward, done, info = env.step(action=action, interactive=interactive)
    env.render(mode='human')