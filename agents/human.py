"""
This module contains the Human class. While this class inherits from the Agent class, it is not an agent.

This class is useful for collecting in-context examples for few-shot or finetuning experiments. The typical
LLM log output is replaced with a list of user requests and 'LLM' responses for the user to fill in after
playing the game (to avoid disturbing the user during gameplay).
"""
import os
import pygame

from utils.robotouille_input import create_action_from_event
from .agent import Agent

class Human(Agent):
    """A class for human control"""

    def __init__(self, kwargs):
        """Initializes the human 'agent'.

        We use the term 'agent' loosely here, as this class is for human input.
        
        Parameters:
            kwargs (dict)
                The keyword arguments for the agent. See `conf/llm` and `conf/experiments` for more details.
        """
        super().__init__(kwargs)
        self.log_path = kwargs.get("log_path", None)
        if self.log_path:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
        # Complete chat history
        self.chat_history = []
        self.pressed_quit = False
        self.pressed_retry = False
        self.did_retry = False

    def is_done(self):
        """Returns whether the policy is done.
        
        The human is done if they quit an environment by pressing ESC.
        
        Returns:
            done (bool)
                Whether the policy is done.
        """
        return self.pressed_quit

    def is_retry(self, steps_left):
        """Returns whether the agent will retry.
        
        Parameters:
            steps_left (int)
                The number of steps left in the environment.
        
        Returns:
            retry (bool)
                Whether the agent will retry.
        """
        if self.pressed_retry:
            self.pressed_retry = False
            self.did_retry = True
            return True
        return False
    
    def _write_to_log(self, log_path, data):
        """Writes data to a log file.
        
        If the log path is not provided, this function does nothing.

        Parameters:
            log_path (str)
                The name of the log file to write to.
            data (str)
                The data to write to the log file.
        """
        if not log_path: return
        with open(log_path, "a") as f:
            f.write(data + "\n")

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
                The proposed actions to take; humans take one action at a time.
        """
        # Retrieve action from human input
        pygame_events = pygame.event.get()
        # Mouse clicks for movement and pick/place stack/unstack
        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        # Keyboard events ('e' button) for cut/cook ('space' button) for noop
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        # Check if user pressed ESC
        self.pressed_quit = any([e.key == pygame.K_ESCAPE for e in keydown_events])
        # Check if user pressed the ` key to retry
        self.pressed_retry = any([e.key == pygame.K_BACKQUOTE for e in keydown_events])
        # Convert event into action
        action, param_arg_dict = create_action_from_event(env.current_state, mousedown_events+keydown_events, env.input_json, env.renderer)
        if action is None:
            # Retry for keyboard input
            return []
        
        # Get the string representation of the action
        valid_actions, str_valid_actions = env.current_state.get_valid_actions_and_str()
        matching_valid_action = list(filter(lambda x: x == (action, param_arg_dict), valid_actions))
        action_idx = valid_actions.index(matching_valid_action[0])
        matching_str_action = str_valid_actions[action_idx]

        # Log in-context example format
        pair_num = len(self.chat_history) // 2 + 1
        self._write_to_log(self.log_path, f"Interaction {pair_num}\n" + "-"*15)
        self.chat_history.append(obs)
        self._write_to_log(self.log_path, f"\n\nObservation:\n{obs}\n")
        if self.did_retry:
            self._write_to_log(self.log_path, "Reflection: ...\n\n")
        
        reasoning_and_action = f"Reasoning: ...\n\nAction: {matching_str_action}\n\n" # Reasoning is left blank for the user to fill in
        self.chat_history.append(reasoning_and_action)
        self._write_to_log(self.log_path, reasoning_and_action)
        return [(action, param_arg_dict)]
        
