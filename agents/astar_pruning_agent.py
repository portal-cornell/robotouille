"""
This module contains the AStarAgent class. This agent does not use LLMs.

It proposes an optimal (or near-optimal) plan using the A* search algorithm.
The heuristic used is the minimum number of unmet goal predicates across the
available goal-sets in the state (a simple, optimistic goal-count heuristic).
"""


import heapq
from collections import Counter
from copy import deepcopy

from .agent import Agent


class AStarPruningAgent(Agent):
    """A* search agent)."""

    def __init__(self, kwargs):
        """
        Initializes the human 'agent'.

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

    def is_retry(self, steps_left: int):
        """Returns whether the agent will retry.
        
        Parameters:
            steps_left (int)
                The number of steps left in the environment.
        
        Returns:
            retry (bool)
                Whether the agent will retry.
        """
        return False

    @staticmethod
    def _heuristic(_state) -> int:
        """
        naieve heuristic that returns the number of non-satisfied predicates within environment

        Parameters:
            _state (State): The state to evaluate the heuristic on. Ignored in this heuristic.

        Returns:
            int: The heuristic value, which is always zero for this heuristic.

        """
        def _naive_heuristic(_state) -> int:
            # check every goal set, set unsatisfied count for goal with  

            min_goal_count = 1000000000
            for goal_set in _state.goal:
                satisfied_count = 0
                # find minimum goal, use unsatisfied
                #print(goal_set)
                for goal in goal_set:
                    # make sure to count preds in order
                    #print(goal)
                    if _state.get_predicate_value(goal):
                        satisfied_count += 1
                    else:
                        break

                min_goal_count = min(min_goal_count, len(goal_set) - satisfied_count)

            return min_goal_count

        def _action_heuristic(_state) -> int:
            #  
            pass


        return _naive_heuristic(_state) 

    


    def propose_actions(self, obs, env):
        """Plans actions with A*.

        Parameters:
            obs (str)
                A natural language observation of the current state of the environment.
            env (object)
                The environment to propose actions in.

        Returns:
            actions (list): The action sequence (as (Action, dict) tuples).
        """
        # Trivial case: already at goal
        if env.current_state.is_goal_reached():
            self.done = True
            print("Optimal Plan: []")
            print("Length: 0")
            return []

        # OPEN: min-heap ordered by f = g + h (tie-breaker 'tie' keeps heap stable)
        open_heap = []
        tie = 0
    
        # Start node: g=0, h=0, so f = g + h = 0
        start_env = deepcopy(env)
        start_sig = start_env.current_state.signature()
        start_g = 0
        start_f = start_g + self._heuristic(start_env.current_state)
        
        # Push start into OPEN
        heapq.heappush(open_heap, (start_f, tie, start_g, [], [], start_env))
        tie += 1

        # CLOSED / best_g: if g(s') > g(s) + c(s,s')" then relax; otherwise prune.
        best_g = {start_sig: 0}

        # Allow a few 'waits' per signature even if cost increases
        MAX_WAIT_PER_SIG = 5
        wait_used = Counter()

        while open_heap:
            # Remove s with smallest f(s) = g(s) + h(s) from OPEN
            f, _, g, actions, str_actions, curr_env = heapq.heappop(open_heap)

            # Goal test when node is expanded
            if curr_env.current_state.is_goal_reached():
                print(f"Optimal Plan: {str_actions}")
                print(f"Length: {len(str_actions)}")
                self.done = True
                return actions

            # Get all successors s' via applicable actions from s
            valid_actions, str_valid_actions = curr_env.current_state.get_valid_actions_and_str()

            # For every successor s' of s such that s' not in CLOSED (enforced via best_g logic)
            for (act, par), desc in zip(valid_actions, str_valid_actions):
                # Simulate one step to create successor state
                next_env = deepcopy(curr_env)
                _, _, done, _ = next_env.step([(act, par)], skip_assert=True)  # skip_assert since we already know these actions are valid

                next_actions = actions + [(act, par)]
                next_str_actions = str_actions + [desc]

                # If successor is a goal, return the plan immediately
                if done or next_env.current_state.is_goal_reached():
                    print(f"Optimal Plan: {next_str_actions}")
                    print(f"Length: {len(next_str_actions)}")
                    self.done = True
                    return next_actions

                # Signature identifies logical state (used for CLOSED/best_g)
                sig = next_env.current_state.signature()
                # Edge cost c(s,s') = 1 per action → next_g = g(s) + 1
                next_g = g + 1
                is_wait = (desc.strip().lower() == "do nothing")

                # To allow delayed SFX to complete, we allow a small number of waits even if the signature hasn't improved.
                if is_wait:
                    if wait_used[sig] < MAX_WAIT_PER_SIG:
                        wait_used[sig] += 1
                        next_f = next_g + self._heuristic(next_env.current_state)  # == next_g
                        heapq.heappush(open_heap, (next_f, tie, next_g, next_actions, next_str_actions, next_env))
                        tie += 1
                    # else: exceeded wait budget, drop
                    continue

                # Non-wait actions keep the normal A* pruning by best_g
                # if g(s') > g(s) + c(s,s') then update g(s') and push to OPEN
                if sig not in best_g or next_g < best_g[sig]:
                    best_g[sig] = next_g
                    next_f = next_g + self._heuristic(next_env.current_state)
                    heapq.heappush(open_heap, (next_f, tie, next_g, next_actions, next_str_actions, next_env))
                    tie += 1

        assert False, "No optimal plan found"
