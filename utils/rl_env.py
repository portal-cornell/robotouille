import gym
from gym import spaces
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_utils as robotouille_utils
from gym.spaces import Box
import numpy as np


class RLEnv(gym.Env):
    def __init__(self, expanded_truths, expanded_states, valid_actions, all_actions):
        self.valid_actions = valid_actions
        self.all_actions = all_actions

        shortened_action_truths, shortened_action_names = self._get_action_space()
        self.shortened_action_names = shortened_action_names
        self.shortened_action_truths = shortened_action_truths

        self.expanded_truths = expanded_truths
        self.expanded_states = expanded_states

        (
            shortened_expanded_truths,
            shortened_expanded_states,
        ) = self._get_observation_space()

        self.state = shortened_expanded_truths + shortened_action_truths

        # print(shortened_expanded_states + shortened_action_names)

        self.action_space = spaces.Discrete(len(self.shortened_action_names))
        self.observation_space = spaces.MultiBinary(len(self.state))

    def step(self, expanded_truths, valid_actions):
        self.valid_actions = valid_actions

        shortened_action_truths, shortened_action_names = self._get_action_space()
        self.shortened_action_truths = shortened_action_truths
        self.shortened_action_names = shortened_action_names

        self.expanded_truths = expanded_truths

        shortened_expanded_truths, shortened_expanded_states = (
            self._get_observation_space()
        )

        self.state = shortened_expanded_truths + shortened_action_truths

        # names = shortened_expanded_states + self.shortened_action_names
        # for i in range(len(self.state)):
        #     if self.state[i] == 1.0:
        #         print(names[i])

    def _get_observation_space(self):
        desired_truths = ["iscut", "iscooked"]
        desired_items = ["lettuce", "patty"]
        # desired_truths = ["iscut", "iscooked", "has", "loc"]
        # desired_items = ["lettuce", "patty", "robot", "robot"]
        # desired_order = ["topbun", "lettuce", "patty", "bottombun"]

        shortened_expanded_truths = []
        shortened_expanded_states = []

        for truth, state in zip(self.expanded_truths, self.expanded_states):
            predicate = state.predicate.name
            item = state.variables[0].name

            for i in range(len(desired_items)):
                if predicate in desired_truths[i] and desired_items[i] in item:
                    shortened_expanded_truths.append(truth)
                    shortened_expanded_states.append(state)
                    break
            # if predicate == "atop":
            #     item2 = state.variables[1].name
            #     for i in range(len(desired_order) - 1):
            #         if desired_order[i] in item and desired_order[i + 1] in item2:
            #             shortened_expanded_truths.append(truth)
            #             shortened_expanded_states.append(state)
            #             break

        return shortened_expanded_truths, shortened_expanded_states

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

        return shortened_action_truths, shortened_action_names

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
