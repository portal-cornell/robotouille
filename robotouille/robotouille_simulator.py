import numpy as np
import pygame
from utils.rl_wrapper import RLWrapper
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env
from stable_baselines3 import A2C, PPO
from stable_baselines3.common.env_util import make_vec_env
import wandb


def simulator(
    environment_name: str,
    seed: int = 42,
    noisy_randomization: bool = False,
    use_rl: bool = True,
    load: bool = True,
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

    if use_rl:
        config = {
            "num_cuts": {"lettuce": 3, "default": 3},
            "cook_time": {"patty": 3, "default": 3},
        }

        rl_env = RLWrapper(env, config)
        obs, info = rl_env.reset()
        rl_env.render(mode="human")

        if load:
            agent = PPO.load("ppo_100k-rl_10-0")
        else:
            agent = PPO("MlpPolicy", rl_env, verbose=1, n_steps=1024)
            agent.learn(
                total_timesteps=100000, reset_num_timesteps=False, progress_bar=True
            )
            agent.save("ppo_robotouille")

        obs, info = rl_env.reset()
    while not done and not truncated:
        if use_rl:
            pygame_events = pygame.event.get()
            keydown_events = list(
                filter(lambda e: e.type == pygame.KEYDOWN, pygame_events)
            )

            if len(keydown_events) == 0:
                continue

            if keydown_events[0].key == pygame.K_SPACE:
                action, _states = agent.predict(obs)
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
