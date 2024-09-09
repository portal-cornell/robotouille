"""
This module contains the IOAgent class. This LLM agent outputs an entire
action sequence given an observation of the environment.
"""
import os
import openai
import re

from copy import deepcopy

from .prompt_builder.prompt_llm import prompt_llm
from .agent import Agent

class IOAgent(Agent):
    """An agent that queries an LLM and outputs a plan given an observation."""

    EXAMPLE_REQUEST_REGEX = re.compile(r"^Observation:\s*(.+?)Plan:", re.M | re.S)
    EXAMPLE_RESPONSE_REGEX = re.compile(r"(^Plan:\s*\n.+)", re.M | re.S)
    
    PLAN_REGEX = re.compile(r"^Plan:\s*(.+)", re.M)

    def __init__(self, kwargs):
        """Initializes the IO agent.
        
        Parameters:
            kwargs (dict)
                The keyword arguments for the agent. See `conf/llm` and `conf/experiments` for more details.
        """
        super().__init__(kwargs)
        self.log_path = kwargs.get("log_path", None)
        if self.log_path:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        # IO prompt
        assert kwargs["prompts"]["action_proposal_prompt"], "The action proposal prompt is missing."
        self.action_proposal_prompt_params = kwargs["prompts"].get("action_proposal_prompt", {})
        num_examples = kwargs.get("num_examples", 0)
        example_dir_path = kwargs.get("example_dir_path", None)
        messages = Agent.fetch_messages(self.action_proposal_prompt_params, IOAgent.EXAMPLE_REQUEST_REGEX, IOAgent.EXAMPLE_RESPONSE_REGEX, example_dir_path=example_dir_path, num_examples=num_examples)
        self.action_proposal_prompt_params["messages"] = messages
        self.action_feedback_msg = "" # Error feedback to insert into the next prompt
        
        # Complete chat history
        self.chat_history = []
        # Whether the agent is done
        self.done = False

    def is_done(self):
        """Returns whether the policy is done.
        
        The ReAct policy is done when its final action is 'Finish'. This
        
        Returns:
            done (bool)
                Whether the policy is done.
        """
        return self.done
    
    def _prompt_llm(self, user_prompt, params, history=[]):
        """Prompts the LLM with messages and parameters.
        
        Parameters:
            user_prompt (str)
                The user prompt to query the LLM with.
            params (dict)
                The parameters to prompt the LLM with.
            history (list)
                The history of the conversation.
        
        Returns:
            response (str)
                The response from the LLM.
            truncated_history (list)
                The truncated history that fits within the context length.
        """
        success = False
        truncated_history = history
        while not success:
            try:
                response = prompt_llm(user_prompt, **params, history=truncated_history)
                success = True
            except openai.BadRequestError as e:
                error_code = e.code
                if error_code == 'context_length_exceeded':
                    assert len(truncated_history) == 2, "The starter prompt is too long."
                    truncated_history = truncated_history[2:] # Remove oldest user-assistant pair
                else:
                    raise e # Raise other errors for user to handle
        return response, truncated_history

    def _write_to_log(self, log_path, data):
        """Writes data to a log file.
        
        Parameters:
            log_path (str)
                The name of the log file to write to.
            data (str)
                The data to write to the log file.
        """
        with open(log_path, "a") as f:
            f.write(data + "\n\n")
    
    def _regex_match(self, regex, string):
        """Returns the first match of a regex in a string, or None
        
        Parameters:
            regex (str)
                The regex pattern to match.
            string (str)
                The string to search for the regex pattern.
        
        Returns:
            match (Union[str, None])
                The first match of the regex pattern in the string, or None if no match.
        """
        match = re.search(regex, string)
        if not match:
            return None
        return match.group(1)

    def propose_actions(self, obs, env):
        """Proposes an action(s) to take in order to reach the goal.
        
        This function only proposes actions, it does not take steps in the environment.
        
        Parameters:
            obs (str)
                A natural language observation of the current state of the environment.
            env (object)
                The environment to propose actions in.
        
        Returns:
            actions (list)
                The proposed actions to take; for IO this is an action sequence
        """
        action_proposal_response, _ = self._prompt_llm(obs, self.action_proposal_prompt_params)
            
        # Update and log user-assistant pair
        self._write_to_log(self.log_path, f"ACTION PROPOSAL PROMPT\n" + "-"*20)
        self._write_to_log(self.log_path, obs)
        self.chat_history.append(obs)
        self._write_to_log(self.log_path, f"ACTION PROPOSAL RESPONSE\n" + "-"*20)
        self._write_to_log(self.log_path, action_proposal_response)
        self.chat_history.append(action_proposal_response)
            
        # Extract actions
        actions = self._regex_match(IOAgent.PLAN_REGEX, action_proposal_response)
        if not actions:
            # IO misformatted output - terminate
            self.done = True
            return []

        # Transform string action into valid action
        # TODO(chalo2000): Simplify code below by creating Robotouille ActionDef/Action class
        valid_actions, str_valid_actions = env.current_state.get_valid_actions_and_str()
        matching_str_actions = list(filter(lambda x: x in actions, str_valid_actions))
        if len(matching_str_actions) != len(actions):
            # IO invalid action - terminate
            self.done = True
            return []
        action_idxs = [str_valid_actions.index(matching_str_action[0]) for matching_str_action in matching_str_actions]
        matching_actions = [valid_actions[action_idx] for action_idx in action_idxs]
        self.done = True
        return matching_actions