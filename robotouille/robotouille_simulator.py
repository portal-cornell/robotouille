from enum import Enum
import numpy as np
import pygame
from stable_baselines3 import PPO
from rl.rl_wrapper import RLWrapper
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env

# from stable_baselines3 import A2C, DQN, PPO
from stable_baselines3.common.env_util import make_vec_env


class mode(Enum):
    PLAY = 1
    TRAIN = 2
    LOAD = 3


file = "runs/custom_ppo.zip"


def simulator(
    environment_name: str,
    seed: int = 42,
    noisy_randomization: bool = False,
    mode=mode.TRAIN,
):

    # Your code for robotouille goes here
    env, json, renderer = create_robotouille_env(
        environment_name, seed, noisy_randomization
    )
    obs, info = env.reset()
    env.render(mode="human")
    done = False
    truncated = False
    interactive = False  # Set to True to interact with the environment through terminal REPL (ignores input)

    # Load or train agent
    if mode == mode.TRAIN or mode == mode.LOAD:
        config = {
            "num_cuts": {"lettuce": 3, "default": 3},
            "cook_time": {"patty": 3, "default": 3},
        }

        rl_env = RLWrapper(env, config, renderer)
        rl_env.render(mode="human")
        obs, info = rl_env.reset()

        if mode == mode.LOAD:
            model = PPO.load(file, env=rl_env)

        else:
            model = PPO("MlpPolicy", rl_env, verbose=1, n_steps=1024, ent_coef=0.01)

            model.learn(
                total_timesteps=100000, reset_num_timesteps=False, progress_bar=True
            )
            model.save(file)

        obs, info = rl_env.reset()

    # Simulate the environment
    while not done and not truncated:
        if mode == mode.TRAIN or mode == mode.LOAD:
            pygame_events = pygame.event.get()
            keydown_events = list(
                filter(lambda e: e.type == pygame.KEYDOWN, pygame_events)
            )

            if len(keydown_events) == 0:
                continue

            if keydown_events[0].key == pygame.K_SPACE:
                action, _states = model.predict(obs)
                obs, reward, done, truncated, info = rl_env.step(
                    action=action, debug=True
                )
                env.render(mode="human")
        else:
            # Construct action from input
            pygame_events = pygame.event.get()
            # Mouse clicks for movement and pick/place stack/unstack
            mousedown_events = list(
                filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events)
            )
            # Keyboard events ('e' button) for cut/cook ('space' button) for noop
            keydown_events = list(
                filter(lambda e: e.type == pygame.KEYDOWN, pygame_events)
            )
            action = create_action_from_control(
                env, obs, mousedown_events + keydown_events, renderer
            )

            if not interactive and action is None:
                # Retry for keyboard input
                continue

            obs, reward, done, info = env.step(action=action, interactive=interactive)

            env.render(mode="human")
    env.render(close=True)
