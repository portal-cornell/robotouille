"""
This module contains the ReflexionAgent class. This LLM agent uses the ReAct
framework to take actions but can retry the same environment upon failure. Before
retrying, the agent reflects on the previous history and incorporates its reflection
into the next attempt's observation.
"""
import os
import openai
import re

from copy import deepcopy

from .prompt_builder.prompt_llm import prompt_llm
from .ReAct_agent import ReActAgent
from .agent import Agent

class ReflexionAgent(ReActAgent):
    """An agent that can query an LLM to interact with an environment in multiple trials."""

    def __init__(self, kwargs):
        """Initializes the Reflexion agent.
        
        Parameters:
            kwargs (dict)
                The keyword arguments for the agent. See `conf/llm` and `conf/experiments` for more details.
        """
        super().__init__(kwargs)
        
        # Reflexion feedback
        self.reflection_prompt_params = kwargs["prompts"].get("reflection_prompt", {})
        messages = Agent.fetch_messages(self.reflection_prompt_params)
        self.reflection_prompt_params["messages"] = messages

        self.reflection = ""

        # Number of retries
        self.retries = kwargs.get("retries", 0)
        self.did_retry = False

    def is_retry(self, steps_left):
        """Returns whether the agent will retry.
        
        Parameters:
            steps_left (int)
                The number of steps left in the environment.
        
        Returns:
            retry (bool)
                Whether the agent will retry.
        """
        if steps_left == 0 and self.retries > 0:
            self.retries -= 1
            self.done = False
            self.did_retry = True
            return True
        return False

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
                The proposed actions to take; for Reflexion this is a single action.
        """
        if self.did_retry:
            self.did_retry = False
            truncated_chat_history = []
            # Truncate all observations minus the final state
            for i, message in enumerate(self.chat_history):
                if i < len(self.chat_history) - 2 and i % 2 == 0: # All user messages except the last one
                    goal_and_reflection = message.split("Goal: ")[1]
                    modified_message = "Observation: ...\n\nValid Actions: ...\n\nGoal: " + goal_and_reflection
                    truncated_chat_history.append(modified_message)
                else: # Agent response
                    truncated_chat_history.append(message)
            # Add Reflexion feedback to observation
            reflexion_prompt = "Please follow the instructions and reflect on the previous history.\n\n"
            reflexion_response, _ = self._prompt_llm(reflexion_prompt, self.reflection_prompt_params, history=truncated_chat_history)
            self._write_to_log(self.log_path, f"REFLEXION RESPONSE\n" + "-"*20)
            self._write_to_log(self.log_path, reflexion_prompt)
            self._write_to_log(self.log_path, reflexion_response)
            # Extract and store reflection
            try:
                self.reflection = reflexion_response.split("Reflection: ")[1]
            except:
                self.reflection = reflexion_response # Put entire response if misformatted
        if self.reflection:
            obs = obs + "\n\nReflection: " + self.reflection
        matching_action = super().propose_actions(obs, env) # Call ReActAgent's propose_actions
        return matching_action
