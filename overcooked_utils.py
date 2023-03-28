import pddlgym_interface
import overcooked_exceptions
from renderer.renderer import OvercookedRenderer
from overcooked_wrapper import OvercookedWrapper
from environments.env_generator import builder

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

def create_overcooked_env(problem_filename):
    env_name = "overcooked"
    is_test_env = False
    # TODO: Get the rendering elements from the loaded JSON from builder.load_environment()
    import numpy as np
    grid_size = np.array([6, 6])
    render_fn = OvercookedRenderer(grid_size=grid_size).render
    pddl_env = pddlgym_interface.create_pddl_env(env_name, is_test_env, render_fn, f"{problem_filename}.pddl")
    return OvercookedWrapper(pddl_env)
