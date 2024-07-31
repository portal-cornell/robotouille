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
    
    REASONING_REGEX = re.compile(r"^Reasoning:\s*(.+)Action:", re.M | re.S) # Everything up till Action
    ACTION_REGEX = re.compile(r"^Action:\s*(.+)", re.M)
    FINISH_ACTION = "Finish"

    def __init__(self, kwargs):
        """Initializes the ReAct agent.
        
        Parameters:
            kwargs (dict)
                The keyword arguments for the agent. See `conf/llm` and `conf/experiments` for more details.
        """
        super().__init__(kwargs)
        self.log_path = kwargs.get("log_path", None)
        if self.log_path:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        # ReAct prompt
        assert kwargs["prompts"]["action_proposal_prompt"], "The action proposal prompt is missing."
        self.action_proposal_prompt_params = kwargs["prompts"].get("action_proposal_prompt", {})
        num_examples = kwargs.get("num_examples", 0)
        example_dir_path = kwargs.get("example_dir_path", None)
        messages = Agent.fetch_messages(self.action_proposal_prompt_params, example_dir_path=example_dir_path, num_examples=num_examples)
        self.action_proposal_prompt_params["messages"] = messages
        self.action_feedback_msg = "" # Error feedback to insert into the next prompt
        
        # Complete chat history
        self.chat_history = []
        # Chat history that is truncated either by configuration or context length limits
        self.truncated_chat_history = []
        # Maximum number of attempts to provide feedback in case of errors
        self.max_feedback_steps = kwargs.get("feedback_steps", 5)
        # Whether or not to prompt the LLM with no history
        self.is_no_history = kwargs.get("is_no_history", False)
        # Whether or not to prompt the LLM with the last timestep action
        self.is_last_action = kwargs.get("is_last_action", False)
        # Whether or not to prompt the LLM with the last timestep reasoning and action
        self.is_last_reasoning_action = kwargs.get("is_last_reasoning_action", False)
        # Whether or not to prompt the LLM with the last timestep observation, reasoning, and action
        self.is_last_obs_reasoning_action = kwargs.get("is_last_obs_reasoning_action", False)

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
    
    def truncate_history(self, obs, reasoning, action, truncated_chat_history):
        """Returns history truncated according to the configuration.
        
        This function allows for fine control over the history that is passed
        to the LLM.

        The following types of history include:
        - No history
        - Last timestep action
        - Last timestep reasoning and action
        - Last timestep observation, reasoning, and action
        - Complete history

        Parameters:
            obs (str)
                The observation of the environment in the current timestep.
            reasoning (str)
                The reasoning of the agent in the current timestep.
            action (str)
                The action of the agent in the current timestep.
            truncated_chat_history (list)
                The chat history containing at least the complete interaction in the last timestep.
        
        Returns:
            new_truncated_chat_history (list)
                The new chat history to pass to the LLM.
        """
        if self.is_no_history:
            return []
        omitted_observation = f"Previous Observation: Omitted"
        previous_action = f"Previous Action: {action}"
        if self.is_last_action:
            return [omitted_observation, previous_action]
        previous_reasoning = f"Previous Reasoning: {reasoning}\n"
        if self.is_last_reasoning_action:
            return [omitted_observation, previous_reasoning + previous_action]
        previous_observation = f"Previous Observation: {obs}\n"
        if self.is_last_obs_reasoning_action:
            return [previous_observation, previous_reasoning + previous_action]
        return truncated_chat_history # Return full history by default

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
                The proposed actions to take; for ReAct this is a single action.
        """
        feedback_steps = 0
        matching_action = []
        while len(matching_action) == 0 and feedback_steps < self.max_feedback_steps:
            action_proposal_prompt = ""
            if self.action_feedback_msg:
                action_proposal_prompt += f"Error Feedback: {self.action_feedback_msg}\n"
                self.action_feedback_msg = ""
            action_proposal_prompt += obs
            # Get response from LLM
            action_proposal_response, self.truncated_chat_history = self._prompt_llm(action_proposal_prompt, self.action_proposal_prompt_params, history=self.truncated_chat_history)
            
            # Update and log user-assistant pair
            self._write_to_log(self.log_path, f"ACTION PROPOSAL PROMPT\n" + "-"*20)
            self._write_to_log(self.log_path, action_proposal_prompt)
            self.chat_history.append(action_proposal_prompt)
            self.truncated_chat_history.append(action_proposal_prompt)
            self._write_to_log(self.log_path, f"ACTION PROPOSAL RESPONSE\n" + "-"*20)
            self._write_to_log(self.log_path, action_proposal_response)
            self.chat_history.append(action_proposal_response)
            self.truncated_chat_history.append(action_proposal_response)
            
            # Extract reasoning
            reasoning = self._regex_match(ReActAgent.REASONING_REGEX, action_proposal_response)
            if not reasoning:
                self.action_feedback_msg = "The reasoning was malformed. Please provide a valid reasoning in the form 'Reasoning: <reasoning>'."
                feedback_steps += 1
                continue

            # Extract action
            action = self._regex_match(ReActAgent.ACTION_REGEX, action_proposal_response)
            if not reasoning:
                self.action_feedback_msg = "The action was malformed. Please provide a valid action in the form 'Action: <action>'."
                feedback_steps += 1
                continue

            # Truncate history according to configuration
            self.truncated_chat_history = self.truncate_history(obs, reasoning, action, self.truncated_chat_history)
            
            # Transform string action into valid action
            if action == ReActAgent.FINISH_ACTION:
                self.done = True # Finish action; mark as done
                return []
            # TODO(chalo2000): Simplify code below by creating Robotouille ActionDef/Action class
            valid_actions, str_valid_actions = env.current_state.get_valid_actions_and_str()
            matching_str_action = list(filter(lambda x: x == action, str_valid_actions))
            if len(matching_str_action) == 0:
                self.action_feedback_msg = f"The action '{action}' is not valid. Please provide a valid action."
                feedback_steps += 1
                continue
            action_idx = str_valid_actions.index(matching_str_action[0])
            matching_action = [valid_actions[action_idx]]
        return matching_action