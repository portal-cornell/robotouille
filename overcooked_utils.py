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

def _parse_renderer_layout(environment_json):
    """
    Parses and returns renderer layout from the environment json.

    Args:
        environment_json (dict): The environment json.
    
    Returns:
        grid_size (tuple): The size of the grid.
    """
    # Update environment names with unique versions
    width, height = environment_json["width"], environment_json["height"]
    layout = [[None for _ in range(width)] for _ in range(height)]
    _, updated_environment_json = builder.build_objects(environment_json)
    stations = updated_environment_json["stations"]
    for station in stations:
        x, y = station["x"], height - station["y"] - 1
        layout[y][x] = station["name"]
    return layout

def create_overcooked_env(problem_filename):
    env_name = "overcooked"
    is_test_env = False
    json_filename = f"{problem_filename}.json"
    environment_json = builder.load_environment(json_filename)
    layout = _parse_renderer_layout(environment_json)
    render_fn = OvercookedRenderer(layout=layout).render
    problem_string = builder.build_problem(environment_json)
    builder.write_problem_file(problem_string, f"{problem_filename}.pddl")
    pddl_env = pddlgym_interface.create_pddl_env(env_name, is_test_env, render_fn, f"{problem_filename}.pddl")
    builder.delete_problem_file(f"{problem_filename}.pddl")
    return OvercookedWrapper(pddl_env)
