import pddlgym_interface
import overcooked_exceptions
from renderer.renderer import OvercookedRenderer
from overcooked_wrapper import OvercookedWrapper
from environments.env_generator import builder

def print_states(obs):
    """
    This function prints the current state of the environment in a list format.

    Args:
        obs (PDDLGym Observation): The current state of the environment.
    """
    print("Here is the current state:")
    states = obs.literals
    for state in states:
        print(f"- {state}")

def print_actions(env, obs):
    """
    This function prints the currently valid actions in a list format.

    Args:
        env (PDDLGym Environment): The environment.
        obs (PDDLGym Observation): The current state of the environment.
    """
    print("Here are the currently valid actions:")
    actions = list(env.action_space.all_ground_literals(obs))
    actions = sorted(actions, key=lambda x: str(x))
    for i, action in enumerate(actions):
        print(f"{i}) {action}")

def create_action_repl(env, obs):
    """
    This function outputs a valid action inputted by the user.

    This function is meant to be used with the interactive mode of the Overcooked wrapper.
    The user can either type in a custom defined action (e.g. noop), the entire action 
    literal from PDDLGym (e.g. move(robot1:player,stove1:station,board1:station) ) or the
    number corresponding to the action in the list of valid actions (which are printed
    by the print_actions function).

    Since this function is a REPL, it will continue to ask for an action until a valid
    and correctly formatted action is inputted (errors will be printed but the user will
    be reprompted).

    Args:
        env (PDDLGym Environment): The environment.
        obs (PDDLGym Observation): The current state of the environment.
    
    Returns:
        action (str or pddlgym.Literal): The valid action inputted by the user.
    """
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
    """
    This function attempts to create a valid action from the provided action.

    This function is meant to be used to train an agent. As opposed to the create_action_repl
    function, this function takes an action as an argument and will raise an exception if
    the action is invalid or malformatted.

    Args:
        env (PDDLGym Environment): The environment.
        obs (PDDLGym Observation): The current state of the environment.
        action (str): The action to be validated.
    
    Raises:
        OvercookedMalformedActionException: If the action is malformatted.
        OvercookedInvalidActionException: If the action is invalid.
    
    Returns:
        action (pddlgym.Literal): A valid action.
    """
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
    """
    Creates and returns an Overcooked environment.

    Note this function is used to load pre-created environments. These can be located
    in the environments/env_generator/examples folder.

    Args:
        problem_filename (str): The name of the problem file (without extension).
    
    Returns:
        env (OvercookedWrapper): The Overcooked environment.
    """
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
