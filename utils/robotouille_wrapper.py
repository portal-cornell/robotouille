import gym
import pddlgym
import utils.robotouille_utils as robotouille_utils
import utils.pddlgym_utils as pddlgym_utils

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
        print('\n' * 10)
        if self.timesteps % 10 == 0:
            print(f"You have made {self.timesteps} steps.")
        robotouille_utils.print_states(self.prev_step[0])
        print('\n')
        robotouille_utils.print_actions(self.env, self.prev_step[0])
        print(f"True Predicates: {expanded_truths.sum()}")
    

    def _handle_action(self, action):
        """
        This function takes an action and performs the step in the environment.

        The simplest case is when the action is noop. In this case, we simply return the previous step.

        If the action is not noop, we need to update the state of the environment. The schema for state is
        as follows
        
        {
            "item_name": {
                "cut": int,
                "cook": {
                    "cooking": bool,
                    "cook_time": int
                },
                "fry": {
                    "frying": bool,
                    "fry_time": int
                }
        }
        
        This function may also update the state of the environment. For example, if an action is pick-up then
        we need to stop cooking the item; however, this is not a PDDL predicate so we need to update the custom
        state.

        Args:
            action (str or pddlgym.Literal): The action to take.
        
        Returns:
            obs (PDDLGym State): The new state of the environment.
            reward (float): The reward for the action.
            done (bool): Whether or not the episode is done.
            info (dict): A dictionary of metadata about the step.
        """
        if action == "noop": return self.prev_step
        return self.env.step(action)
        
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
        expanded_truths, expanded_states = pddlgym_utils.expand_state(self.prev_step[0].literals, self.prev_step[0].objects)
        if interactive:
            self._interactive_starter_prints(expanded_truths)
            action = robotouille_utils.create_action_repl(self.env, self.prev_step[0])
        else:
            action = robotouille_utils.create_action(self.env, self.prev_step[0], action)
        obs, reward, done, _ = self._handle_action(action)
        obs = self._state_update()
        toggle_array = pddlgym_utils.create_toggle_array(expanded_truths, expanded_states, obs.literals)
        if interactive:
            print(f"Predicates Changed: {toggle_array.sum()}")
        info = {
            'timesteps': self.timesteps, 
            "expanded_truths": expanded_truths, 
            "expanded_states": expanded_states, 
            "toggle_array": toggle_array,
            "state": self.state
        }
        self.prev_step = (obs, reward, done, info)
        self.timesteps += 1
        return obs, reward, done, info
        
    def reset(self):
        """
        This function resets the environment.

        Returns:
            obs (PDDLGym State): The initial state of the environment.
            info (dict): A dictionary of metadata about the step.
        """
        obs, _ = self.env.reset()
        info = {
            'timesteps': self.timesteps, 
            "expanded_truths": None, 
            "expanded_states": None, 
            "toggle_array": None,
            "state": {}
        }
        self.prev_step = (obs, 0, False, info)
        self.timesteps = 0
        self.state = {}
        return obs, info