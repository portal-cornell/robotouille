from enum import Enum
import gym
from gym import spaces
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_utils as robotouille_utils
from gym.spaces import Box
import numpy as np


class RLEnv(gym.Env):
    """
    This is a custom Environment that follows gym interface. This allows us to use stable-baselines3 by converting pddl-gym environment to gym environment. Instead of using the states and actions from the pddl-gym environment, we simplify the state and action space to make it easier for the RL agent to learn. We also use the RLWrapper class to simplify the environment for the RL agent.
    """

    class observation_size(Enum):
        SMALL = 1
        MEDIUM = 2
        LARGE = 3

    def __init__(self, expanded_truths, expanded_states, valid_actions, all_actions):
        """
        Initializes the RLenv based on expanded_truths, expanded_states, valid_actions, and all_actions.

        Args:
            expanded_truths (list): List of expanded truths of the current state.
            expanded_states (list): List of expanded states that correspond to each truth in expanded_truths.
            valid_actions (list): List of valid actions
            all_actions (list): List of all actions
        """

        # Initialize the environment
        self.valid_actions = valid_actions
        self.all_actions = all_actions
        self.expanded_truths = expanded_truths
        self.expanded_states = expanded_states

        # Get shortened action space and shortened observation space
        self.shortened_action_truths, self.shortened_action_names = (
            self._get_action_space()
        )

        (
            self.shortened_expanded_truths,
            self.shortened_expanded_states,
        ) = self._get_observation_space()

        # Set the state space. This is a binary array of the shortened expanded truths and shortened action truths
        self.state = self.shortened_expanded_truths + self.shortened_action_truths

        # Set the action space and observation space
        self.action_space = spaces.Discrete(len(self.shortened_action_names))
        self.observation_space = spaces.MultiBinary(len(self.state))

    def step(self, expanded_truths, valid_actions):
        """
        Updates the environment based on the action taken by the agent.

        Args:
            expanded_truths (list): List of expanded truths of the state after the update.
            valid_actions (list): List of valid actions after the update
        """
        self.expanded_truths = expanded_truths
        self.valid_actions = valid_actions

        self.shortened_action_truths, self.shortened_action_names = (
            self._get_action_space()
        )

        self.shortened_expanded_truths, self.shortened_expanded_states = (
            self._get_observation_space()
        )

        self.state = self.shortened_expanded_truths + self.shortened_action_truths
        self.state_names = self.shortened_expanded_states + self.shortened_action_names
        # self.print_state()

    def _get_observation_space(self, mode=observation_size.LARGE):
        """
        Returns the shortened observation space based on the expanded truths and expanded states. If the observation size is SMALL, the observation space will only include the iscut and iscooked predicates. If the observation size is MEDIUM, the observation space will also include the location of the robot, the held item of the robot and the order of the ingredients. If the observation size is LARGE, the observation space will also include the location of the ingredients.

        Args:
            mode (observation_size): The size of the observation space.

        Returns:
            shortened_expanded_truths (list): List of truth values for each predicate in the shortened observation space.
            shortened_expanded_states (list): List of states in the shortened observation space.
        """

        desired_truths = ["iscut", "iscooked"]
        desired_items = ["lettuce", "patty"]

        if mode != self.observation_size.SMALL:
            desired_truths = ["iscut", "iscooked", "has", "loc"]
            desired_items = ["lettuce", "patty", "robot", "robot"]
            desired_order = ["topbun", "lettuce", "patty", "bottombun"]

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

            if predicate == "atop" and mode != self.observation_size.SMALL:
                item2 = state.variables[1].name
                for i in range(len(desired_order) - 1):
                    if desired_order[i] in item and desired_order[i + 1] in item2:
                        shortened_expanded_truths.append(truth)
                        shortened_expanded_states.append(state)
                        break
            if predicate == "at" and mode == self.observation_size.LARGE:
                shortened_expanded_truths.append(truth)
                shortened_expanded_states.append(state)

        return shortened_expanded_truths, shortened_expanded_states

    def _get_action_space(self):
        """
        Returns the shortened action space based on the valid actions. The shortened action space includes the following actions: moving to each location, cook, cut, pick-up, place, stack, unstack. We take advantage of the fact that at any point in time, these actions are deterministic.

        Returns:
            shortened_action_truths (list): List of truth values for each action in the shortened action space.
            shortened_action_names (list): List of action names in the shortened action space.
        """
        actions_truth = np.isin(
            np.array(self.all_actions), np.array(self.valid_actions)
        ).astype(np.float64)

        shortened_action_names = []
        shortened_action_truths = []
        for action, valid in zip(self.all_actions, actions_truth):
            action_name = action.predicate.name
            # Add the action name to the shortened action space. If the action is new, add the truth value to the shortened action truths. If the action is already in the shortened action space, update the truth value if the action is valid.
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
        """
        Returns the action that corresponds to the shortened action space. If it is an invalid action, return "invalid". Otherwise, it returns the pddlgym action that corresponds to the shortened action space.

        Args:
            action (int): The index of the action in the shortened action space.

        """
        if self.shortened_action_truths[action] == 0.0:
            # print("invalid: " + self.shortened_action_names[action])
            return "invalid"

        attempted_action = self.shortened_action_names[action]

        actions_truth = np.isin(
            np.array(self.all_actions), np.array(self.valid_actions)
        ).astype(np.float64)

        # Find the action in the all_actions list that is valid and corresponds to the attempted action
        for action, truth in zip(self.all_actions, actions_truth):
            action_name = action.predicate.name
            if action_name == "move":
                action_name += "_" + action.variables[2].name
            if action_name == attempted_action and truth == 1.0:
                return action

        print("ERROR: Action not found")

    def print_state(self):
        """
        Prints the state of the environment.
        """

        output = []
        for truth, state in zip(self.state, self.state_names):
            if truth == 1.0:
                output.append(state)

        print(output)
