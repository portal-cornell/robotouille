import gym
from gym import spaces
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_utils as robotouille_utils
from gym.spaces import Box
import numpy as np


class RLEnv(gym.Env):
    def __init__(self, state, valid_actions, all_actions):
        self.action_space = spaces.Discrete(len(valid_actions))

        self.valid_actions = valid_actions
        self.all_actions = all_actions

        actions_truth = np.isin(np.array(all_actions), np.array(valid_actions)).astype(
            np.float64
        )

        self.state = np.concatenate((state, actions_truth))
        self.observation_space = spaces.Box(
            low=0, high=1, shape=self.state.shape, dtype=np.float32
        )

    def unwrap_move(self, action):
        return self.valid_actions[action]
