"""
This module contains the ReActAgent class. This LLM agent reasons before generating
a single action to take in the environment. It then receives feedback from the
environment and incorporates it into reasoning for its next action.

The ReAct agent additionally
- maintains all history of THOUGHTs, ACTs, and OBSs in the prompt
- incorporates environment feedback into the OBS
"""
import os
import openai
import re
from copy import deepcopy

from .prompt_builder.prompt_llm import prompt_llm
from .agent import Agent

class ReActAgent(Agent):
    """An agent that queries an LLM to think and act in an environment while receiving feedback."""
    
    FINISH_ACTION = "Finish"

    def __init__(self, kwargs):
        """Initializes the ReAct agent.
        
        Parameters:
            kwargs (dict)
                The keyword arguments for the agent. See `conf/llm` and `conf/experiments` for more details.
        """
        super().__init__(kwargs)
        self.log_file = kwargs.get("log_file", None)
        if self.log_file:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        # ReAct prompt
        assert kwargs["prompts"]["action_proposal_prompt"], "The action proposal prompt is missing."
        self.action_proposal_prompt_params = kwargs["prompts"].get("action_proposal_prompt", {})
        
        self.chat_history = []
        self.truncated_chat_history = [] # Current chat history that fits within the context length
        
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
                    import pdb; pdb.set_trace()
                    assert len(truncated_history) > 2, "The starter user-assistant pair is too long."
                    # Remove one user-assistant pair from the history
                    starter_messages = truncated_history[:2]
                    remaining_messages = truncated_history[4:]
                    truncated_history = starter_messages + remaining_messages
                else:
                    raise e # Raise other errors for user to handle
        return response, truncated_history

    def _write_to_log(self, log_file, data):
        """Writes data to a log file.
        
        Parameters:
            log_file (str)
                The name of the log file to write to.
            data (str)
                The data to write to the log file.
        """
        with open(log_file, "a") as f:
            f.write(data + "\n\n")
    
    def propose_actions(self, obs, env):
        """Proposes an action(s) to take in order to reach the goal.
        
        Parameters:
            obs (str)
                A natural language observation of the current state of the environment.
            env (RobotouilleEnv)
                The current state of the environment to propose actions in.
        
        Returns:
            actions (list)
                The proposed actions to take; for ReAct this is a single action.
        """
        # Get THINK and ACTION from LLM
        thought_and_action, self.truncated_chat_history = self._prompt_llm(obs, self.action_proposal_prompt_params, history=self.truncated_chat_history)
        
        # Update and log user-assistant pair
        self.chat_history.append(obs)
        self.truncated_chat_history.append(obs)
        self._write_to_log(self.log_file, obs)
        self.chat_history.append(thought_and_action)
        self.truncated_chat_history.append(thought_and_action)
        self._write_to_log(self.log_file, thought_and_action)

        # Extract and return ACTION from LLM string response
        regex = r"Action:\s*(.+)"
        match = re.search(regex, thought_and_action)
        if not match:
            # TODO(chalo2000): Should retry, not kill itself
            self.done = True # Malformed response; kill the planner
            return []
        action = match.group(1)
        action = action.replace(" ", "") # Remove spaces
        if action == ReActAgent.FINISH_ACTION:
            self.done = True # Finish action; mark as done
            return []
        valid_actions = env.get_valid_actions()
        matching_action = list(filter(lambda x: str(x) == action, valid_actions))
        return matching_action