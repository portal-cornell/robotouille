import pygame
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env
from stable_baselines3 import PPO  
from stable_baselines3.common.env_util import make_vec_env
from robotouille_wrapper import RobotouilleWrapper



def simulator(environment_name: str, seed: int = 42, noisy_randomization: bool = False, use_rl: bool = True):
    env, json, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
    config = {
        "num_cuts": {
            "default": 5,
        },
        "cook_time": {
            "default": 10,
        },
        "fry_time": {
            "default": 8,
        }
    }

    wrapped_env = RobotouilleWrapper(env, config)
    obs, info = wrapped_env.reset()
    wrapped_env.render(mode='human')

    if use_rl:
        vec_env = make_vec_env(lambda: wrapped_env, n_envs=1, seed=seed)
        agent = PPO("MlpPolicy", vec_env, verbose=1)
        agent.learn(total_timesteps=10000)

    done = False
    interactive = False

    while not done:
        if use_rl:
            action, _states = agent.predict(obs, deterministic=True)
        else:
            pygame_events = pygame.event.get()
            mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
            keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
            action = create_action_from_control(wrapped_env, obs, mousedown_events + keydown_events, renderer)
            if not interactive and action is None:
                continue

        obs, reward, done, info = wrapped_env.step(action=action, interactive=interactive)
        wrapped_env.render(mode='human')

    wrapped_env.render(close=True)
