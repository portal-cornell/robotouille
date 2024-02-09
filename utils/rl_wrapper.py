from typing import List, Optional, Union
import gym
import numpy as np
import pddlgym
import utils.robotouille_utils as robotouille_utils
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_wrapper as robotouille_wrapper
from utils.rl_env import RLEnv
import wandb

wandb.login()


class RLWrapper(robotouille_wrapper.RobotouilleWrapper):
    def __init__(self, env, config):
        super().__init__(env, config)

        self.pddl_env = env
        self.env = None
        self.max_steps = 50
        self.episode_reward = 0
        # Configuration dictionary for tracking metrics
        self.metrics_config = {
            "ep_rew_mean": None,  # Mean episode reward
            "total_timesteps": 0,  # Total number of timesteps
            "iterations": 0,  # Number of iterations
            "ep_len_mean": None,  # Mean episode length
            "loss": None,  # Loss,
            "entropy_loss": None,  # Entropy loss
        }
        # Initialize WandB with the metrics config
        wandb.init(project="6756-rl-experiments", config=self.metrics_config)

    def log_metrics(self, update_dict):
        """
        Log metrics to the metrics_config and to WandB.
        :param update_dict: A dictionary containing updates to the metrics.
        """
        # Update the metrics configuration with new values
        self.metrics_config.update(update_dict)
        # Log the updated metrics to WandB
        wandb.log(self.metrics_config)

    def _wrap_env(self):
        expanded_truths, expanded_states = pddlgym_utils.expand_state(
            self.pddl_env.prev_step[0].literals, self.pddl_env.prev_step[0].objects
        )

        valid_actions = list(
            self.pddl_env.action_space.all_ground_literals(self.pddl_env.prev_step[0])
        )

        all_actions = list(
            self.pddl_env.action_space.all_ground_literals(
                self.pddl_env.prev_step[0], valid_only=False
            )
        )

        if self.env is None:
            self.env = RLEnv(
                expanded_truths, expanded_states, valid_actions, all_actions
            )
        self.env.step(expanded_truths, valid_actions)

    def step(self, action=None, interactive=False, debug=False):
        action = self.env.unwrap_move(action)
        if debug:
            print(action)
        if action == "invalid":
            obs, reward, done, info = self.pddl_env.prev_step
            reward = 0
            self.pddl_env.prev_step = (obs, reward, done, info)
            self.pddl_env.timesteps += 1

            info["timesteps"] = self.pddl_env.timesteps
        else:
            action = str(action)
            obs, reward, done, info = self.pddl_env.step(action, interactive)
            reward += 2
            self.pddl_env.prev_step = (obs, reward, done, info)

        wandb.log({"reward per step": reward})
        self._wrap_env()
        self.episode_reward += reward
        if self.pddl_env.timesteps > self.max_steps:
            wandb.log({"reward per episode": self.episode_reward})

        return (
            self.env.state,
            reward,
            done,
            self.pddl_env.timesteps > self.max_steps,
            info,
        )

    def reset(self, seed=42, options=None):
        obs, info = self.pddl_env.reset()
        self.episode_reward = 0
        self._wrap_env()
        return self.env.state, info

    def render(self, *args, **kwargs):
        self.pddl_env.render()
