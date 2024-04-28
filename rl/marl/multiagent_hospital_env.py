import numpy as np
from rl.marl.marl_env import MARLEnv
from rl.rl_converter import RLConverter
from utils.robotouille_utils import get_valid_moves
from multiagentenv import MultiAgentEnv
import utils.pddlgym_utils as pddlgym_utils

import gym
import torch as th


class MAHospital_robotouille(MultiAgentEnv):
    def __init__(
        self,
        env,
        config,
        renderer,
        num_agents=3,
    ):

        self.pddl_env = MARLEnv(env, config, renderer, num_agents)
        self.converter = RLConverter(
            self.pddl_env.prev_step[0].literals,
            self.pddl_env.prev_step[0].objects,
            self.pddl_env.valid_actions,
            self.pddl_env.all_actions,
        )
        self.n_agents = num_agents

        self.action_space = [
            gym.spaces.Discrete(self.env.action_space.nvec[1])
            for _ in range(self.n_agents)
        ]

        self.observation_space = [
            gym.spaces.Discrete(
                self.shortened_action_names,
                dtype=self.env.observation_space.dtype,
            )
            for _ in range(self.n_agents)
        ]

        self.n_actions = self.action_space[0].n
        self.obs = None

    def _wrap_env(self):
        """
        Wrap the environment to make it compatible with stable-baselines3.
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

        if self.env is None:
            self.env = RLConverter(
                expanded_truths, expanded_states, valid_actions, all_actions
            )

        self.env.step(expanded_truths, valid_actions)

    def step(self, _actions):
        """Returns reward, terminated, info."""
        if th.is_tensor(_actions):
            actions = _actions.cpu().numpy()
        else:
            actions = _actions
        self.time_step += 1
        obs, rewards, done, infos = self.env.step(actions.tolist())

        self.obs = obs

        if self.time_step >= self.episode_limit:
            done = True

        return sum(rewards), done, infos

    def get_obs(self):
        """Returns all agent observations in a list."""
        return self.obs.reshape(self.n_agents, -1)

    def get_obs_agent(self, agent_id):
        """Returns observation for agent_id."""
        return self.obs[agent_id].reshape(-1)

    def get_obs_size(self):
        """Returns the size of the observation."""
        obs_size = np.array(self.env.observation_space.shape[1:])
        return int(obs_size.prod())

    def get_global_state(self):
        return self.obs.flatten()

    def get_state(self):
        """Returns the global state."""
        return self.get_global_state()

    def get_state_size(self):
        """Returns the size of the global state."""
        return self.get_obs_size() * self.n_agents

    def get_avail_actions(self):
        """Returns the available actions of all agents in a list."""
        return [[1 for _ in range(self.n_actions)] for agent_id in range(self.n_agents)]

    def get_avail_agent_actions(self, agent_id):
        """Returns the available actions for agent_id."""
        return self.get_avail_actions()[agent_id]

    def get_total_actions(self):
        """Returns the total number of actions an agent could ever take."""
        return self.action_space[0].n

    def reset(self):
        """Returns initial observations and states."""
        self.time_step = 0
        self.obs = self.env.reset()

        return self.get_obs(), self.get_global_state()

    def render(self):
        pass

    def close(self):
        self.env.close()

    def seed(self):
        pass

    def save_replay(self):
        """Save a replay."""
        pass

    def get_stats(self):
        return {}
