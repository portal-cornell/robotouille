#!/usr/bin/env python3
"""
Profile A* node expansion performance to identify bottlenecks.

This script monkey-patches the A* algorithm to measure:
- Time spent in deepcopy operations
- Time spent computing heuristics
- Time spent in state.signature()
- Time spent in env.step()
- Number of nodes expanded

Usage:
    python profile_astar_performance.py [environment_name]
    
Examples:
    python profile_astar_performance.py 0_cheese_sandwich
    python profile_astar_performance.py  # runs on cheese_sandwich by default
"""

import time
import sys
import os
from collections import defaultdict

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Global performance counters
perf_stats = {
    'deepcopy_time': 0.0,
    'deepcopy_calls': 0,
    'heuristic_time': 0.0,
    'heuristic_calls': 0,
    'signature_time': 0.0,
    'signature_calls': 0,
    'step_time': 0.0,
    'step_calls': 0,
    'valid_actions_time': 0.0,
    'valid_actions_calls': 0,
    'nodes_expanded': 0,
    'heap_operations': 0,
    'total_action_combinations': 0,
    'action_combinations_checked': 0,
    'is_valid_calls': 0,
    'is_valid_time': 0.0
}

def profile_astar_expansion(env_name="synchronous/0_cheese_sandwich"):
    """Profile A* performance focusing on node expansion bottlenecks."""
    
    print(f"PROFILING A* NODE EXPANSION")
    print(f"Environment: {env_name}")
    print("=" * 50)
    
    # Change to robotouille directory first
    original_cwd = os.getcwd()
    robotouille_dir = parent_dir
    
    try:
        os.chdir(robotouille_dir)
        
        # Reset stats
        for key in perf_stats:
            perf_stats[key] = 0
    
        # Import modules we'll patch
        import copy
        import heapq
        from agents.astar_agent import AStarAgent
        from backend.state import State
        from backend.action import Action
    
        # Store original functions
        original_deepcopy = copy.deepcopy
        original_heappush = heapq.heappush
        original_heappop = heapq.heappop
        original_heuristic = AStarAgent._heuristic
        
        # Store original State class methods
        original_signature = State.signature
        original_step = State.step
        original_get_valid_actions = State.get_valid_actions_and_str
        
        # Store original Action method
        original_is_valid = Action.is_valid
        
        # Monkey patch deepcopy to measure time
        def timed_deepcopy(obj, memo=None):
            start = time.perf_counter()
            if memo is None:
                result = original_deepcopy(obj)
            else:
                result = original_deepcopy(obj, memo)
            perf_stats['deepcopy_time'] += time.perf_counter() - start
            perf_stats['deepcopy_calls'] += 1
            return result
        
        # Monkey patch heap operations
        def timed_heappush(heap, item):
            perf_stats['heap_operations'] += 1
            return original_heappush(heap, item)
        
        def timed_heappop(heap):
            perf_stats['heap_operations'] += 1
            perf_stats['nodes_expanded'] += 1
            return original_heappop(heap)
        
        # Monkey patch heuristic
        @staticmethod
        def timed_heuristic(state):
            start = time.perf_counter()
            result = original_heuristic(state)
            perf_stats['heuristic_time'] += time.perf_counter() - start
            perf_stats['heuristic_calls'] += 1
            return result
        
        # Monkey patch State class methods
        def timed_signature(self, include_player=True, include_sfx=True):
            start = time.perf_counter()
            result = original_signature(self, include_player, include_sfx)
            perf_stats['signature_time'] += time.perf_counter() - start
            perf_stats['signature_calls'] += 1
            return result
        
        def timed_step(self, actions):
            start = time.perf_counter()
            result = original_step(self, actions)
            perf_stats['step_time'] += time.perf_counter() - start
            perf_stats['step_calls'] += 1
            return result
        
        def timed_get_valid_actions(self):
            start = time.perf_counter()
            
            # Count total action combinations in this state (do this once per call)
            total_combinations = sum(len(args_list) for args_list in self.actions.values())
            perf_stats['total_action_combinations'] = max(perf_stats['total_action_combinations'], total_combinations)
            
            result = original_get_valid_actions(self)
            perf_stats['valid_actions_time'] += time.perf_counter() - start
            perf_stats['valid_actions_calls'] += 1
            
            # Count how many action combinations we checked
            perf_stats['action_combinations_checked'] += total_combinations
            
            return result
        
        # Monkey patch Action.is_valid to count validity checks
        def timed_is_valid(self, state, args):
            start = time.perf_counter()
            result = original_is_valid(self, state, args)
            perf_stats['is_valid_time'] += time.perf_counter() - start
            perf_stats['is_valid_calls'] += 1
            return result
        
        # Apply patches
        copy.deepcopy = timed_deepcopy
        heapq.heappush = timed_heappush
        heapq.heappop = timed_heappop
        AStarAgent._heuristic = timed_heuristic
        
        # Apply State class patches
        State.signature = timed_signature
        State.step = timed_step
        State.get_valid_actions_and_str = timed_get_valid_actions
        
        # Apply Action class patches
        Action.is_valid = timed_is_valid
        
        # Run the actual test
        try:
            # We already changed directory above
            from robotouille.robotouille_simulator import run_robotouille
            
            # Start timing
            total_start = time.perf_counter()
            
            # Create initial environment to patch methods
            # We'll need to patch during the run since we can't access env beforehand
            
            done, steps = run_robotouille(
                env_name, 
                "astar", 
                max_steps=300,
                render_mode='rgb_array',
                record=False,
                stochastic=False,
                llm_kwargs={}
            )
            
            total_time = time.perf_counter() - total_start
            
        except Exception as e:
            print(f"Error during execution: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            # Restore original functions
            copy.deepcopy = original_deepcopy
            heapq.heappush = original_heappush
            heapq.heappop = original_heappop
            AStarAgent._heuristic = original_heuristic
            
            # Restore original State class methods
            State.signature = original_signature
            State.step = original_step
            State.get_valid_actions_and_str = original_get_valid_actions
            
            # Restore Action class methods
            Action.is_valid = original_is_valid
            
            # Restore original directory
            try:
                os.chdir(original_cwd)
            except:
                pass
        
        # Calculate percentages
        algorithm_time = (perf_stats['deepcopy_time'] + 
                         perf_stats['heuristic_time'] + 
                         perf_stats['signature_time'] + 
                         perf_stats['step_time'] + 
                         perf_stats['valid_actions_time'] + 
                         perf_stats['is_valid_time'])
        
        print(f"RESULTS:")
        print(f"Status: {'SUCCESS' if done else 'FAILED'}")
        print(f"Plan Length: {steps}")
        print(f"Total Time: {total_time:.3f}s")
        print(f"Target: {'✓ MET' if total_time <= 5.0 else '⚠ EXCEEDED'} (5.0s)")
        print()
        
        print(f"ALGORITHM BREAKDOWN:")
        print(f"Nodes Expanded: {perf_stats['nodes_expanded']}")
        print(f"Total Algorithm Time: {algorithm_time:.3f}s ({algorithm_time/total_time*100:.1f}% of total)")
        print()
        
        if algorithm_time > 0:
            print(f"TIME BREAKDOWN:")
            print(f"deepcopy():     {perf_stats['deepcopy_time']:.3f}s ({perf_stats['deepcopy_time']/algorithm_time*100:.1f}%) [{perf_stats['deepcopy_calls']} calls]")
            print(f"heuristic():    {perf_stats['heuristic_time']:.3f}s ({perf_stats['heuristic_time']/algorithm_time*100:.1f}%) [{perf_stats['heuristic_calls']} calls]")
            print(f"signature():    {perf_stats['signature_time']:.3f}s ({perf_stats['signature_time']/algorithm_time*100:.1f}%) [{perf_stats['signature_calls']} calls]")
            print(f"step():         {perf_stats['step_time']:.3f}s ({perf_stats['step_time']/algorithm_time*100:.1f}%) [{perf_stats['step_calls']} calls]")
            print(f"valid_actions():{perf_stats['valid_actions_time']:.3f}s ({perf_stats['valid_actions_time']/algorithm_time*100:.1f}%) [{perf_stats['valid_actions_calls']} calls]")
            print(f"is_valid():     {perf_stats['is_valid_time']:.3f}s ({perf_stats['is_valid_time']/algorithm_time*100:.1f}%) [{perf_stats['is_valid_calls']} calls]")
            print()
            
            print(f"ACTION COMBINATION ANALYSIS:")
            print(f"Max Action Combinations in State: {perf_stats['total_action_combinations']}")
            print(f"Total Action Combinations Checked: {perf_stats['action_combinations_checked']:,}")
            print(f"is_valid() calls per get_valid_actions() call: {perf_stats['is_valid_calls'] / max(perf_stats['valid_actions_calls'], 1):.1f}")
            if perf_stats['valid_actions_calls'] > 0:
                avg_combinations_per_call = perf_stats['action_combinations_checked'] / perf_stats['valid_actions_calls']
                print(f"Average Action Combinations per Call: {avg_combinations_per_call:.1f}")
            print()
            
            # Performance analysis
            if perf_stats['deepcopy_time'] / algorithm_time > 0.3:
                print("⚠ DEEPCOPY BOTTLENECK: >30% time spent in deepcopy")
            if perf_stats['nodes_expanded'] > 1000:
                print(f"⚠ HIGH NODE EXPANSION: {perf_stats['nodes_expanded']} nodes expanded")
            if perf_stats['deepcopy_calls'] != perf_stats['step_calls']:
                print(f"⚠ DEEPCOPY MISMATCH: {perf_stats['deepcopy_calls']} deepcopy vs {perf_stats['step_calls']} steps")
            if perf_stats['is_valid_calls'] > 100000:
                print(f"⚠ HIGH ACTION VALIDATION: {perf_stats['is_valid_calls']:,} validity checks performed")
        
        return done, steps, total_time, perf_stats

    except Exception as setup_error:
        print(f"Setup error: {setup_error}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Always restore original directory
        try:
            os.chdir(original_cwd)
        except:
            pass


def quick_profile_test():
    """Quick test on first 3 synchronous environments."""
    envs = [
        "synchronous/0_cheese_sandwich",
        "synchronous/1_lettuce_sandwich",
        "synchronous/2_lettuce_tomato_sandwich"
    ]
    
    print("QUICK A* PERFORMANCE PROFILE")
    print("=" * 50)
    
    for env in envs:
        env_short = env.split('/')[-1]
        print(f"\nTesting: {env_short}")
        print("-" * 30)
        
        result = profile_astar_expansion(env)
        if result:
            done, steps, total_time, stats = result
            if total_time <= 5.0:
                print(f"✓ {env_short}: {total_time:.2f}s")
            else:
                print(f"⚠ {env_short}: {total_time:.2f}s (SLOW)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        env_name = sys.argv[1]
        if not env_name.startswith('synchronous/'):
            env_name = f'synchronous/{env_name}'
        profile_astar_expansion(env_name)
    else:
        quick_profile_test()