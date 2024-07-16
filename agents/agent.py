"""
This module contains the Agent class. All agents should inherit from this class.

To create a custom agent, 
1) create a Python file in this directory
2) create a custom class that inherits from Agent that implements the following functions:
   - propose_actions
   - select_state
3) modify the NAME_TO_AGENT dictionary in the __init__.py file with an option name and your custom class
"""

class Agent:

    def __init__(self, kwargs):
        """Initializes the agent.
        
        Parameters:
            kwargs (Dict[Any, Any])
                The keyword arguments for the agent.
        """
        self.kwargs = kwargs

    def is_done(self):
        """Returns whether the agent is done.
        
        Returns:
            done (bool)
                Whether the agent is done.
        """
        raise NotImplementedError

    def propose_actions(self, obs):
        """Proposes action(s) to take in order to reach the goal.
        
        Parameters:
            obs (object)
                The observation of the environment.
        
        Raises:
            NotImplementedError
                This function should be implemented in a subclass.
        """
        raise NotImplementedError