import sys

# Hack to resolve import issue
if "/home/yuki/Documents/llm-to-code/overcooked_sim" not in sys.path:
   sys.path.append("/home/yuki/Documents/llm-to-code/overcooked_sim")

import pddlgym_interface
import overcooked_exceptions

def print_states(obs):
    print("Here is the current state:")
    states = obs.literals
    for state in states:
        print(f"- {state}")

def print_actions(env, obs):
    print("Here are the currently valid actions:")
    actions = list(env.action_space.all_ground_literals(obs))
    actions = sorted(actions, key=lambda x: str(x))
    for i, action in enumerate(actions):
        print(f"{i}) {action}")

def create_action_repl(env, obs):
    action = ""
    valid_actions = list(env.action_space.all_ground_literals(obs))
    valid_actions = sorted(valid_actions, key=lambda x: str(x))
    while True:
        try:
            action = input()
            if action == "noop": return action
            try:
                action = str(valid_actions[int(action)])
            except:
                pass
            action = pddlgym_interface.str_to_literal(action)
            assert action in valid_actions
            break
        except ValueError:
            print(f"Your action [{action}] is malformatted. It must be in the form A(B:1,C:2,...)")
            continue
        except AssertionError:
            print(f"Your action [{action}] is invalid. Please choose from the list of valid actions.")
    return action

def create_action(env, obs, action):
    if action == "noop": return action
    valid_actions = list(env.action_space.all_ground_literals(obs))
    try:
        action = pddlgym_interface.str_to_literal(action)
        assert action in valid_actions
    except ValueError:
        raise overcooked_exceptions.OvercookedMalformedActionException(f"Your action [{action}] is malformatted.")
    except AssertionError:
        raise overcooked_exceptions.OvercookedInvalidActionException(f"Your action [{action}] is invalid.")
    return action

def create_overcooked_env():
    return pddlgym_interface.create_overcooked_env()
