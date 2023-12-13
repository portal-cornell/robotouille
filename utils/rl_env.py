import gym
from gym import spaces
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_utils as robotouille_utils
from gym.spaces import Box
import numpy as np


class RLEnv(gym.Env):
    def __init__(self, state, valid_actions, all_actions):
        self.valid_actions = valid_actions
        self.all_actions = all_actions

        shortened_action_names, shortened_action_truths = self._get_action_space()
        self.shortened_action_names = shortened_action_names
        self.shortened_action_truths = shortened_action_truths

        self.action_space = spaces.Discrete(len(self.shortened_action_names))
        self.state = np.concatenate((state, shortened_action_truths))
        self.observation_space = spaces.Box(
            low=0, high=1, shape=self.state.shape, dtype=np.float32
        )

    def _get_action_space(self):
        actions_truth = np.isin(
            np.array(self.all_actions), np.array(self.valid_actions)
        ).astype(np.float64)

        shortened_action_names = []
        shortened_action_truths = []
        for action, valid in zip(self.all_actions, actions_truth):
            action_name = action.predicate.name
            if action_name == "move":
                action_name += "_" + action.variables[2].name
            if action_name not in shortened_action_names:
                shortened_action_names.append(action_name)
                shortened_action_truths.append(valid)
            elif action_name in shortened_action_names and valid == 1.0:
                index = shortened_action_names.index(action_name)
                shortened_action_truths[index] = valid

        return shortened_action_names, shortened_action_truths

    def unwrap_move(self, action):
        if self.shortened_action_truths[action] == 0.0:
            return "invalid"

        attempted_action = self.shortened_action_names[action]

        actions_truth = np.isin(
            np.array(self.all_actions), np.array(self.valid_actions)
        ).astype(np.float64)

        for action, truth in zip(self.all_actions, actions_truth):
            action_name = action.predicate.name
            if action_name == "move":
                action_name += "_" + action.variables[2].name
            if action_name == attempted_action and truth == 1.0:
                return action

        print("ERROR: Action not found")
