from typing import List, Optional, Union
import gym
import numpy as np
import pddlgym
from rl.marl.marl_env import MARLEnv
from utils.robotouille_utils import get_valid_moves
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_wrapper as robotouille_wrapper
import wandb

# wandb.login()


class MARLWrapper(robotouille_wrapper.RobotouilleWrapper):
    """
    This class is a wrapper around the Robotouille environment to make it compatible with stable-baselines3. It simplifies the environment for the RL agent by converting the state and action space to a format that is easier for the RL agent to learn.
    """

    def __init__(self, env, config, renderer, n_agents):
        super().__init__(env, config, renderer)
        self.pddl_env = env
        self.n_agents = n_agents

        self.max_steps = 80
        self.episode_reward = 0
        self.renderer = renderer
        # Configuration dictionary for tracking metrics
        self.metrics_config = {
            "ep_rew_mean": None,  # Mean episode reward
            "total_timesteps": 0,  # Total number of timesteps
            "iterations": 0,  # Number of iterations
            "ep_len_mean": None,  # Mean episode length
            "loss": None,  # Loss,
            "entropy_loss": None,  # Entropy loss
        }

        self._wrap_env()

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
        """
        Wrap the environment to make it compatible with epymarl.
        """
        expanded_truths, expanded_states = pddlgym_utils.expand_state(
            self.pddl_env.prev_step[0].literals, self.pddl_env.prev_step[0].objects
        )

        valid_actions = get_valid_moves(
            self.pddl_env, self.pddl_env.prev_step[0], self.renderer
        )
        all_actions = list(
            self.pddl_env.action_space.all_ground_literals(
                self.pddl_env.prev_step[0], valid_only=False
            )
        )

        # if the environment is a RobotouilleWrapper, we need to change it to MARLEnv. Otherwise, just step the MARLEnv
        if not isinstance(self.env, MARLEnv):
            self.env = MARLEnv(
                self.n_agents,
                expanded_truths,
                expanded_states,
                valid_actions,
                all_actions,
            )
        else:
            self.env.step(expanded_truths, valid_actions)

        self.observation_space = self.env.observation_space

    def step(self, actions=None, interactive=False, debug=False):
        """
        Take a step in the environment.

        Returns:
            state (list): The state of the environment after the step.
            reward (float): The reward obtained from the step.
            done (bool): Whether the episode is done.
            truncated (bool): Whether the episode was truncated.
            info (dict): A dictionary containing information about the environment.
        """

        rewards = []
        for i in range(len(actions)):
            action = self.env.unwrap_move(i, actions[i])
            if debug:
                print(action)
            if action == "invalid":
                obs, reward, done, info = self.pddl_env.prev_step
                obs, _, _, _ = self.pddl_env._change_selected_player(obs)
                reward = 0
                self.pddl_env.prev_step = (obs, reward, done, info)
                self.pddl_env.timesteps += 1
                reward -= 2
                rewards.append(reward)
                info["timesteps"] = self.pddl_env.timesteps
            else:
                action = str(action)
                obs, reward, done, info = self.pddl_env.step(action, interactive)
                self.pddl_env.prev_step = (obs, reward, done, info)
                rewards.append(reward)
            self._wrap_env()

        # reward -= 1

        wandb.log({"reward per step": reward})

        self.episode_reward += reward
        if self.pddl_env.timesteps > self.max_steps:
            wandb.log({"reward per episode": self.episode_reward})

        return (
            self.env.state,
            rewards,
            done,
            info,
        )

    def reset(self, seed=42, options=None):
        """
        Reset the environment to its initial state.

        Returns:
            state (list): The initial state of the environment.
            info (dict): A dictionary containing information about the environment.
        """
        obs, info = self.pddl_env.reset()
        self.episode_reward = 0
        self._wrap_env()
        # print("self.env.state", self.env.state)
        return self.env.state, info

    def render(self, *args, **kwargs):
        self.pddl_env.render()
