from enum import Enum
import gym
from gym import spaces
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_utils as robotouille_utils
from gym.spaces import Box
import numpy as np


class MARLEnv(gym.Env):
    """
    This is a converter class that simplifies the environment for the RL agent by converting the state and action space to a format that is easier for the RL agent to learn.
    """

    class observation_size(Enum):
        SMALL = 1
        MEDIUM = 2
        LARGE = 3

    def __init__(
        self, n_agents, expanded_truths, expanded_states, valid_actions, all_actions
    ):
        """
        Initializes the converter based on expanded_truths, expanded_states, valid_actions, and all_actions.

        Args:
            expanded_truths (list): List of expanded truths of the current state.
            expanded_states (list): List of expanded states that correspond to each truth in expanded_truths.
            valid_actions (list): List of valid actions
            all_actions (list): List of all actions
        """

        # Initialize the environment
        self.n_agents = n_agents

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
        self.state = np.zeros(
            (
                self.n_agents,
                len(self.shortened_expanded_truths + self.shortened_action_truths[0]),
            )
        )
        self.state_names = [[]] * self.n_agents
        for i in range(self.n_agents):
            self.state[i] = np.array(
                (self.shortened_expanded_truths + self.shortened_action_truths[i])
            )

            self.state_names[i] = (
                self.shortened_expanded_states + self.shortened_action_names[i]
            )

        # Set the action space and observation space (Note: this is for the individual agent)
        self.action_space = spaces.Discrete(len(self.shortened_action_names[0]))
        self.observation_space = spaces.MultiBinary(len(self.state[0]))

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

        for i in range(self.n_agents):
            self.state[i] = np.array(
                self.shortened_expanded_truths + self.shortened_action_truths[i]
            )
            self.state_names[i] = (
                self.shortened_expanded_states + self.shortened_action_names[i]
            )
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

        shortened_action_names = [[]] * self.n_agents
        shortened_action_truths = [[]] * self.n_agents
        for action, valid in zip(self.all_actions, actions_truth):
            action_name = action.predicate.name
            # Add the action name to the shortened action space. If the action is new, add the truth value to the shortened action truths. If the action is already in the shortened action space, update the truth value if the action is valid.
            if action_name == "select":
                continue
            if action_name == "move":
                action_name += "_" + action.variables[2].name
            elif action_name == "place" or action_name == "stack":
                action_name = "place/stack"
            elif action_name == "pick-up" or action_name == "unstack":
                action_name = "pick-up/unstack"

            player_index = int(action.variables[0].name[-1]) - 1
            if action_name not in shortened_action_names[player_index]:
                shortened_action_names[player_index].append(action_name)
                shortened_action_truths[player_index].append(valid)
            elif action_name in shortened_action_names[player_index] and valid == 1.0:
                index = shortened_action_names[player_index].index(action_name)
                shortened_action_truths[player_index][index] = valid

        return shortened_action_truths, shortened_action_names

    def unwrap_move(self, agent_index, action):
        """
        Returns the action that corresponds to the shortened action space. If it is an invalid action, return "invalid". Otherwise, it returns the pddlgym action that corresponds to the shortened action space.

        Args:
            action (int): The index of the action in the shortened action space.

        """
        # print("valid actions", self.valid_actions)
        # print("index", agent_index)

        if self.shortened_action_truths[agent_index][action] == 0.0:
            # print("invalid: " + self.shortened_action_names[action])
            return "invalid"
        attempted_action = self.shortened_action_names[agent_index][action]

        actions_truth = np.isin(
            np.array(self.all_actions), np.array(self.valid_actions)
        ).astype(np.float64)

        # Find the action in the all_actions list that is valid and corresponds to the attempted action
        for action, truth in zip(self.all_actions, actions_truth):
            if action.variables[0].name != "robot" + str(agent_index + 1):
                continue
            action_name = action.predicate.name
            if action_name == "move":
                action_name += "_" + action.variables[2].name
            if action_name in attempted_action and truth == 1.0:
                return action

        print("ERROR: Action not found ", attempted_action)
        print("hello" + 1)

    def print_state(self):
        """
        Prints the state of the environment.
        """

        output = []
        for truth, state in zip(self.state, self.state_names):
            if truth == 1.0:
                output.append(state)

        print(output)
