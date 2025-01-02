"""
This module contains the BFSAgent class. This agent does not use LLMs.

This class is useful for getting an optimal plan for a given environment. The agent's 
propose_actions function returns the optimal plan for the environment.
"""
import os
import pygame

from copy import deepcopy

from utils.robotouille_input import create_action_from_event
from .agent import Agent

class BFSAgent(Agent):
    """A class for human control"""

    def __init__(self, kwargs):
        """Initializes the human 'agent'.

        We use the term 'agent' loosely here, as this class is for human input.
        
        Parameters:
            kwargs (dict)
                The keyword arguments for the agent. See `conf/llm` and `conf/experiments` for more details.
        """
        super().__init__(kwargs)
        self.done = False

    def is_done(self):
        """Returns whether the policy is done.
        
        Returns:
            done (bool)
                Whether the policy is done.
        """
        return self.done
    
    def is_retry(self, steps_left):
        """Returns whether the agent will retry.
        
        Parameters:
            steps_left (int)
                The number of steps left in the environment.
        
        Returns:
            retry (bool)
                Whether the agent will retry.
        """
        return False

    def propose_actions(self, obs, env):
        """Proposes an action(s) to take in order to reach the goal.

        This function only proposes actions, it does not take steps in the environment.

        TODO(chalo2000): Create custom Robotouille deepcopy functions to make this function run tractably.
        
        Parameters:
            obs (str)
                A natural language observation of the current state of the environment.
            env (object)
                The environment to propose actions in.
        
        Returns:
            actions (list)
                The optimal plan to reach the goal.
        """
        queue = [([], [], deepcopy(env))]
        optimal_plan = []
        str_optimal_plan = []
        while optimal_plan == []:
            actions, str_actions, curr_env = queue.pop(0)
            valid_actions, str_valid_actions = curr_env.current_state.get_valid_actions_and_str()
            for action, str_action in zip(valid_actions, str_valid_actions):
                print("looping")
                new_env = deepcopy(curr_env)
                _, _, done, _ = new_env.step([action])
                if done:
                    optimal_plan = actions + [action]
                    str_optimal_plan = str_actions + [str_action]
                    break
                else:
                    queue.append((actions + [action], str_actions + [str_action], new_env))
        if optimal_plan == []:
            assert False, "No optimal plan found"
        print(f"Optimal Plan: {str_optimal_plan}")
        print(f"Length: {len(str_optimal_plan)}")
        self.done = True
        return optimal_plan
        
