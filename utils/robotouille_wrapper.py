import gym
import pddlgym
import utils.robotouille_utils as robotouille_utils
import utils.pddlgym_utils as pddlgym_utils
from environments.env_generator.object_enums import Item


class RobotouilleWrapper(gym.Wrapper):
    """
    This wrapper wraps around the Robotouille environment from PDDLGym.

    This wrapper is necessary because while the PDDL language is powerful, it can be
    cumbersome to implement data-driven state such as cutting X times or cooking something
    for Y timesteps. This does not mean it is impossible but rather than littering the
    observation space with a bunch of predicates to represent time and number of cuts, we
    offload this to the wrapper's metadata.
    """

    def __init__(self, env, config):
        """
        Initialize the Robotouille wrapper.

        Args:
            env (PDDLGym Environment): The environment to wrap.
            config (dict): A configuration JSON with custom values
        """
        super(RobotouilleWrapper, self).__init__(env)
        # The PDDLGym environment.
        self.env = env
        # The previous step of the environment.
        # This is useful for the interactive mode and for cases where nothing changes (e.g. noop)
        self.prev_step = None
        # The number of timesteps that have passed.
        self.timesteps = 0
        # The state of the environment (for non-PDDL states like cut and cook)
        self.state = {}
        # The configuration for this environment.
        # This is used to specify things such as cooking times and cutting amounts
        self.config = config

    def _interactive_starter_prints(self, expanded_truths):
        """
        This function prints the initial state of the environment and the valid actions.

        Args:
            expanded_truths (np.array): Array of 0s and 1s where 1 indicates the literal is true
        """
        print("\n" * 10)
        if self.timesteps % 10 == 0:
            print(f"You have made {self.timesteps} steps.")
        robotouille_utils.print_states(self.prev_step[0])
        print("\n")
        robotouille_utils.print_actions(self.env, self.prev_step[0])
        print(f"True Predicates: {expanded_truths.sum()}")

    def _state_update(self):
        """
        This function updates the custom non-PDDL state of the environment.

        This function is called after every step in the environment. It can either update
        the custom state (e.g. incrementing the cook time of a cooking item) or directly
        modify the PDDL state (e.g. adding the iscut predicate to an item that has been
        fully cut).

        Returns:
            new_env_state (PDDLGym State): The new state of the environment.
        """
        state_updates = []
        for item, status_dict in self.state.items():
            for status, state in status_dict.items():
                if status == "cut":
                    item_name, _ = robotouille_utils.trim_item_ID(item)
                    # TODO: Might need to trim item name
                    num_cuts = self.config["num_cuts"]
                    max_num_cuts = num_cuts.get(item_name, num_cuts["default"])
                    if state >= max_num_cuts:
                        literal = pddlgym_utils.str_to_literal(f"iscut({item}:item)")
                        state_updates.append(literal)
                elif status == "cook":
                    item_name, _ = robotouille_utils.trim_item_ID(item)
                    cook_time = self.config["cook_time"]
                    max_cook_time = cook_time.get(item_name, cook_time["default"])
                    if state["cooking"]:
                        state["cook_time"] += 1
                    if state["cook_time"] >= max_cook_time:
                        literal = pddlgym_utils.str_to_literal(f"iscooked({item}:item)")
                        state_updates.append(literal)
                elif status == "fry":
                    item_name, _ = robotouille_utils.trim_item_ID(item)
                    fry_time = self.config["fry_time"]
                    max_fry_time = fry_time.get(item_name, fry_time["default"])
                    if state["frying"]:
                        state["fry_time"] += 1
                    if state["fry_time"] >= max_fry_time:
                        literal = pddlgym_utils.str_to_literal(f"isfried({item}:item)")
                        state_updates.append(literal)
        env_state = self.env.get_state()
        new_literals = env_state.literals.union(state_updates)
        new_env_state = pddlgym.structs.State(
            new_literals, env_state.objects, env_state.goal
        )
        self.env.set_state(new_env_state)
        return new_env_state

    def _handle_action(self, action):
        if action == "noop":
            return self.prev_step
        action_name = action.predicate.name
        if action_name == "cut":
            item = next(
                filter(
                    lambda typed_entity: typed_entity.var_type == "item",
                    action.variables,
                )
            )
            item_status = self.state.get(item.name)
            if item_status is None:
                self.state[item.name] = {"cut": 1}
            elif item_status.get("cut") is None:
                item_status["cut"] = 1
            else:
                item_status["cut"] += 1
            return self.prev_step
        elif action_name == "cook":
            item = next(
                filter(
                    lambda typed_entity: typed_entity.var_type == "item",
                    action.variables,
                )
            )
            item_status = self.state.get(item.name)
            if item_status is None:
                self.state[item.name] = {"cook": {"cook_time": -1, "cooking": True}}
            elif item_status.get("cook") is None:
                item_status["cook"] = {"cook_time": -1, "cooking": True}
            else:
                item_status["cook"]["cooking"] = True
            return self.prev_step
        elif action_name == "fry" or action_name == "fry_cut_item":
            item = next(
                filter(
                    lambda typed_entity: typed_entity.var_type == "item",
                    action.variables,
                )
            )
            item_status = self.state.get(item.name)
            if item_status is None:
                self.state[item.name] = {"fry": {"fry_time": -1, "frying": True}}
            elif item_status.get("fry") is None:
                item_status["fry"] = {"fry_time": -1, "frying": True}
            else:
                item_status["fry"]["frying"] = True
            return self.prev_step
        elif action_name == "pick-up":
            item = next(
                filter(
                    lambda typed_entity: typed_entity.var_type == "item",
                    action.variables,
                )
            )
            item_status = self.state.get(item.name)
            if item_status is not None and item_status.get("cook") is not None:
                item_status["cook"]["cooking"] = False
            if item_status is not None and item_status.get("fry") is not None:
                item_status["fry"]["frying"] = False
        # TODO: Probably stop cooking if something is stacked on top of meat
        return self.env.step(action)

    def _handle_stacking_reward(self, action):
        # Check that no incorrect stacking occured
        items = ["patty1", "lettuce1", "topbun1"]
        correct_order = [
            "atop(patty1:item,bottombun1:item)",
            "atop(lettuce1:item,patty1:item)",
            "atop(topbun1:item,lettuce1:item)",
        ]

        expanded_truths = self.prev_step[3]["expanded_truths"]
        expanded_states = self.prev_step[3]["expanded_states"]
        reward = 0

        for truth, state in zip(expanded_truths, expanded_states):
            if (
                truth == 1
                and "atop" == state.predicate
                and action.variables[1].name == state.variables[0].name
                and str(state) not in correct_order
            ):
                reward -= 2

        state_truth_map = self.map_state_to_truth(expanded_truths, expanded_states)

        for stack, item in zip(correct_order, items):
            if state_truth_map[stack]:
                if action.variables[1].name == item:
                    reward += 5
            else:
                break

        return reward

    def _handle_reward(self, action, obs):
        reward = 100
        action_name = action.predicate.name

        # Reward/Penalty for cutting
        if action_name == "cut":
            item = next(
                filter(
                    lambda typed_entity: typed_entity.var_type == "item",
                    action.variables,
                ),
                None,
            )
            if item:
                item_name, _ = robotouille_utils.trim_item_ID(item.name)
                num_cuts = self.config["num_cuts"]
                max_num_cuts = num_cuts.get(item_name, num_cuts["default"])

                item_status = self.state.get(item.name, {})
                num_cuts = item_status.get("cut", 0)

                reward += 5 if num_cuts <= max_num_cuts else -1
        # Reward/Penalty for cooking and frying
        elif action_name in ["cook", "fry"]:
            item = next(
                filter(
                    lambda typed_entity: typed_entity.var_type == "item",
                    action.variables,
                ),
                None,
            )
            if item:
                item_status = self.state.get(item.name, {})
                if action_name == "fry":
                    num_fries = item_status.get("fry", {}).get("fry_time", 0)
                    reward += 5 if num_fries < 1 else -0.1
                elif action_name == "cook":
                    cook_time = item_status.get("cook", {}).get("cook_time", 0)
                    reward += 5 if cook_time < 1 else -0.1
        elif action_name == "pick-up":
            item = next(
                filter(
                    lambda typed_entity: typed_entity.var_type == "item",
                    action.variables,
                ),
                None,
            )
            item_status = self.state.get(item.name, {})
            if item_status is not None and item_status.get("cook") is not None:
                if (
                    item_status["cook"]["cook_time"] > 0
                    and "iscooked(" + item.name not in self.prev_step[0]
                ):
                    reward -= 5
        elif action_name == "stack":
            reward += self._handle_stacking_reward(action)

        # Reward for continuous cooking
        for item, status_dict in self.state.items():
            for status, state in status_dict.items():
                if status == "cook":
                    item_name, _ = robotouille_utils.trim_item_ID(item)
                    cook_time = self.config["cook_time"]
                    max_cook_time = cook_time.get(item_name, cook_time["default"])
                    if state["cooking"] and state["cook_time"] <= max_cook_time:
                        reward += 1
                    elif state["cooking"] and state["cook_time"] > max_cook_time:
                        reward -= 1
        return reward

    def map_state_to_truth(self, expanded_truths, expanded_states):
        if expanded_truths is None or len(expanded_truths) != len(expanded_states):
            print("Error: Mismatch in lengths or None input")  # Debugging
            return {}
        return {
            str(expanded_states[i]): truth for i, truth in enumerate(expanded_truths)
        }

    def get_latest_info(self):
        """
        Get the latest info dictionary from the environment.

        Returns:
            dict: The latest info dictionary.
        """
        return self.prev_step[3] if self.prev_step else None

    def step(self, action=None, interactive=False):
        """
        This function steps the environment forward.

        Most of the output of this function comes from PDDLGym. The observation is a frozenset of
        PDDLGym literals (predicates), objects, and the goal. The reward is 1 if the goal is met and
        0 otherwise. The done flag is True if the goal is met and False otherwise.

        The info metadata is where the wrapper adds the interesting things. The info metadata consists of
        the following:
            - timesteps (int): The number of timesteps that have passed. Currently every action takes
                1 timestep.
            - expanded_truths (np.array): Array of 0s and 1s where 1 indicates the literal is true. PDDLGym
                only provides us with the predicates that are true, but we also need to know which predicates
                are false. This array includes the true and false predicates as a 1D array of 0s and 1s.
            - expanded_states (np.array): Array of literals corresponding to the expanded truths. This is a 1D
                array of the same shape as the expanded truths array. This array's indices map a literal to its
                corresponding truth value in the expanded truths array.
            - toggle_array (np.array): Array of 0s and 1s where 1 indicates the literal changed from time step t
                to t+1. This array is similar to the expanded truths array and it is useful for quickly determining
                how many predicates changed.
            - state (dict): The custom non-PDDL state of the environment. See the state_update function for more
                information.

        Args:
            action (str): The action to take. If None, then it is assumed that interactive is True.
            interactive (bool): Whether or not to use interactive mode.

        Returns:
            obs (PDDLGym State): The new state of the environment.
            reward (float): The reward for the action.
            done (bool): Whether or not the episode is done.
            info (dict): A dictionary of metadata about the step.
        """

        expanded_truths = self.prev_step[3]["expanded_truths"]
        expanded_states = self.prev_step[3]["expanded_states"]

        if interactive:
            self._interactive_starter_prints(expanded_truths)
            action = robotouille_utils.create_action_repl(self.env, self.prev_step[0])
        else:
            action = robotouille_utils.create_action(
                self.env, self.prev_step[0], action
            )

        obs, reward, done, info = self._handle_action(action)
        obs = self._state_update()

        toggle_array = pddlgym_utils.create_toggle_array(
            expanded_truths, expanded_states, obs.literals
        )
        if interactive:
            print(f"Predicates Changed: {toggle_array.sum()}")

        expanded_truths, expanded_states = pddlgym_utils.expand_state(
            obs.literals, obs.objects
        )

        self.timesteps += 1

        info = {
            "timesteps": self.timesteps,
            "expanded_truths": expanded_truths,
            "expanded_states": expanded_states,
            "toggle_array": toggle_array,
            "state": self.state,
        }

        self.prev_step = (obs, self.prev_step[1], done, info)

        reward = self._handle_reward(action, obs)
        reward += self.prev_step[1]

        self.prev_step = (obs, reward, done, info)

        return obs, reward, done, info

    def reset(self):
        """
        This function resets the environment.

        Returns:
            obs (PDDLGym State): The initial state of the environment.
            info (dict): A dictionary of metadata about the step.
        """
        obs, _ = self.env.reset()
        expanded_truths, expanded_states = pddlgym_utils.expand_state(
            obs.literals, obs.objects
        )
        info = {
            "timesteps": self.timesteps,
            "expanded_truths": expanded_truths,
            "expanded_states": expanded_states,
            "toggle_array": None,
            "state": {},
        }
        self.prev_step = (obs, 0, False, info)
        self.timesteps = 0
        self.state = {}
        return obs, info
