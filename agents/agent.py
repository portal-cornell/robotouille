"""
This module contains the Agent class. All agents should inherit from this class.

To create a custom agent, 
1) create a Python file in this directory
2) create a custom class that inherits from Agent that implements the following functions:
   - propose_actions
   - select_state
3) modify the NAME_TO_AGENT dictionary in the __init__.py file with an option name and your custom class
"""
import re

from .in_context_examples.retrieve_example import retrieve_example

from .prompt_builder.constants import PROMPT_HISTORY_PATH
from .prompt_builder.serializer import serialize_into_messages
from .prompt_builder.utils import get_prompt_path
class Agent:

    @staticmethod
    def fetch_messages(prompt_params, request_regex=None, response_regex=None, example_dir_path=None, num_examples=0):
        """Fetches the messages for the prompt from the version control directory.

        If the environment name is provided, in-context examples are fetched for
        the environment.

        Parameters:
            prompt_params (Dict)
                The parameters for the prompt, including:
                    experiment_name (str)
                        The name of the experiment for the prompt.
                    prompt_description (str)
                        The description of the prompt.
                    prompt_version (str)
                        The version of the prompt.
            request_regex (Pattern)
                The regex pattern to match the request in the example.
            response_regex (Pattern)
                The regex pattern to match the response in the example.
            example_dir_path (str)
                The name of the directory containing the in-context examples
            num_examples (int)
                The number of examples to fetch.

        Returns:
            messages (List[Dict[str, str]])
                The messages to query the LLM with.
        """
        experiment_name = prompt_params["experiment_name"]
        prompt_description = prompt_params["prompt_description"]
        prompt_version = prompt_params["prompt_version"]
        prompt_path = get_prompt_path(PROMPT_HISTORY_PATH, experiment_name, prompt_description, prompt_version)
        messages = serialize_into_messages(prompt_path)
        if example_dir_path and num_examples > 0:
            examples = retrieve_example(example_dir_path, num_examples, request_regex, response_regex)
            messages += examples
        return messages
    
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
    
    def is_retry(self, steps_left):
        """Returns whether the agent will retry.
        
        Parameters:
            steps_left (int)
                The number of steps left in the environment.
        
        Returns:
            retry (bool)
                Whether the agent will retry.
        """
        raise NotImplementedError

    def propose_actions(self, obs, env):
        """Proposes action(s) to take in order to reach the goal.
        
        This function only proposes actions, it does not take steps in the environment.
        
        Parameters:
            obs (object)
                The observation of the environment.
            env (object)
                The environment to propose actions in.
        
        Raises:
            NotImplementedError
                This function should be implemented in a subclass.
        """
        raise NotImplementedError