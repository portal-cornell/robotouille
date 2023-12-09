import gym
from gym import spaces
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_utils as robotouille_utils
from gym.spaces import Box
import numpy as np


class RLEnv(gym.Env):
    def __init__(self, state, valid_actions, all_actions):
        self.observation_space = spaces.Box(
            low=0, high=1, shape=state.shape, dtype=np.float32
        )

        self.action_space = spaces.Discrete(len(all_actions))

        self.state = state
        self.valid_actions = valid_actions
        self.all_actions = all_actions

        print(len(valid_actions))
        print(len(all_actions))

    def unwrap_move(self, action):
        action = self.all_actions[action]
        return action if action in self.valid_actions else "noop"
