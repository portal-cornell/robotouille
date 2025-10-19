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

import time
from copy import deepcopy
from collections import Counter


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
    
    def time_deepcopy(self, obj, repeats=20, warmup=3):
        # warmup
        for _ in range(warmup):
            _ = deepcopy(obj)
        times = []
        for _ in range(repeats):
            t0 = time.perf_counter_ns()
            _ = deepcopy(obj)
            t1 = time.perf_counter_ns()
            times.append(t1 - t0)
        total_ns = sum(times)
        print(f"[deepcopy benchmark] repeats={repeats}")
        print(f"  avg: {total_ns/repeats/1e6:.3f} ms")
        print(f"  min: {min(times)/1e6:.3f} ms   max: {max(times)/1e6:.3f} ms")
        return times

    def propose_actions(self, obs, env):
        """Proposes an action(s) to take in order to reach the goal.

        This function only proposes actions, it does not take steps in the environment.

        TODO(chalo2000): Create custom Robotouille deepcopy functions to make this function run tractably.

        Optimise the copy operation so that it happens quickly (start_time = time.time same with end time to find difference and measure the time taken for copy)
        Write a dunder function for deepcopy. 
        
        If still slow, maybe optimise the BFS. It is an undirected graph less actions that you cannot do (moving can be retracted but not cooking)
        We should not do exploration of states that have already been explored. 

        If still slow, investigate a different planing algorithm then BFS. 
        Maybe A Star, need heuristic that needs admissable and consistent
        
        Parameters:
            obs (str)
                A natural language observation of the current state of the environment.
            env (object)
                The environment to propose actions in.
        
        Returns:
            actions (list)
                The optimal plan to reach the goal.
        """
        _ = self.time_deepcopy(env, repeats=30, warmup=5)
        queue = [([], [], deepcopy(env))]
        root_sig = queue[0][2].current_state.signature()
        seen_depth = {root_sig: 0}

        # Allow some "do nothings" even if state has been seen before for special effects to take effect
        MAX_WAIT_PER_SIG = 5
        wait_used = Counter()
        optimal_plan, str_optimal_plan = [], []
        x = 1

        while not optimal_plan and queue:
            actions, str_actions, curr_env = queue.pop(0)
            curr_depth = len(actions)
            valid_actions, str_valid_actions = curr_env.current_state.get_valid_actions_and_str()

            for action, str_action in zip(valid_actions, str_valid_actions):
                # print(f"Looping x={x} - Queue Size: {len(queue)} - Current Plan Length: {curr_depth+1} - Trying Action: {str_action}")
                x += 1

                new_env = deepcopy(curr_env)
                _, _, done, _ = new_env.step([action])
                if done:
                    optimal_plan = actions + [action]
                    str_optimal_plan = str_actions + [str_action]
                    break

                sig = new_env.current_state.signature()
                new_depth = curr_depth + 1
                is_wait = (str_action.strip().lower() == "do nothing")
                if is_wait:
                    # allow a small number of waits even if we've seen the state
                    if wait_used[sig] < MAX_WAIT_PER_SIG:
                        wait_used[sig] += 1
                        queue.append((actions + [action], str_actions + [str_action], new_env))
                    # else drop this branch (exceeded wait budget)
                else:
                    if sig not in seen_depth or new_depth < seen_depth[sig]:
                        seen_depth[sig] = new_depth
                        queue.append((actions + [action], str_actions + [str_action], new_env))

        if not optimal_plan:
            assert False, "No optimal plan found"

        print(f"Optimal Plan: {str_optimal_plan}")
        print(f"Length: {len(str_optimal_plan)}")
        self.done = True
        return optimal_plan
        
