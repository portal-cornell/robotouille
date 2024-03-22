import gym
import utils.robotouille_exceptions as robotouille_exceptions
import utils.pddlgym_interface as pddlgym_interface


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


def print_actions(env, obs, renderer):
    """
    This function prints the currently valid actions in a list format.

    Args:
        env (PDDLGym Environment): The environment.
        obs (PDDLGym Observation): The current state of the environment.
    """
    print("Here are the currently valid actions:")
    actions = get_valid_moves(env, obs, renderer)
    actions = sorted(actions, key=lambda x: str(x))
    for i, action in enumerate(actions):
        print(f"{i}) {action}")


def create_action_repl(env, obs, renderer):
    """
    This function outputs a valid action inputted by the user.

    This function is meant to be used with the interactive mode of the Robotouille wrapper.
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
    valid_actions = get_valid_moves(env, obs, renderer)
    valid_actions = sorted(valid_actions, key=lambda x: str(x))
    while True:
        try:
            action = input()
            if action == "noop":
                return action
            try:
                action = str(valid_actions[int(action)])
            except:
                pass
            action = pddlgym_interface.str_to_literal(action)
            assert action in valid_actions
            break
        except ValueError:
            print(
                f"Your action [{action}] is malformatted. It must be in the form A(B:1,C:2,...)"
            )
            continue
        except AssertionError:
            print(
                f"Your action [{action}] is invalid. Please choose from the list of valid actions."
            )
    return action


def create_action(env, obs, action, renderer):
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
        RobotouilleMalformedActionException: If the action is malformatted.
        RobotouilleInvalidActionException: If the action is invalid.

    Returns:
        action (pddlgym.Literal): A valid action.
    """
    if action == "noop":
        return action

    valid_actions = get_valid_moves(env, obs, renderer)
    try:
        action = pddlgym_interface.str_to_literal(action)
        assert action in valid_actions
    except ValueError:
        raise robotouille_exceptions.RobotouilleMalformedActionException(
            f"Your action [{action}] is malformatted."
        )
    except AssertionError:
        raise robotouille_exceptions.RobotouilleInvalidActionException(
            f"Your action [{action}] is invalid."
        )
    return action


def trim_item_ID(item):
    """
    Returns the item name and item ID separated.

    For example, trim_item_ID("lettuce2") returns "lettuce" and "2".

    Args:
        item_name (str): The item name.

    Returns:
        item_name (str): The item name.
        item_ID (str): The item ID.
    """
    index = None
    for i, char in enumerate(item):
        if char.isdigit():
            index = i
            break
    assert index is not None  # Item must have an ID
    item_name = item[:index]
    item_ID = item[index:]
    return item_name, item_ID


def _get_reverse_move(action):
    """
    Returns the reverse of the given action.

    Args:
        action (pddlgym.Literal): The action to reverse.

    Returns:
        reverse_action (pddlgym.Literal): The reverse of the given action.
    """
    reverse_action = f"move({action.variables[0].name}:{action.variables[0].var_type},{action.variables[2].name}:{action.variables[2].var_type},{action.variables[1].name}:{action.variables[1].var_type})"
    reverse_action = pddlgym_interface.str_to_literal(reverse_action)
    return reverse_action


def get_valid_moves(env, obs, renderer):
    """
    Returns the valid moves for the robot. This is a helper function to filter out moves that are valid in the pddl environment, but not on the renderer (as the robot can not pass through other robots or stations)

    Args:
        env (PDDLGym Environment): The environment.

    Returns:
        valid_moves (list): A list of valid moves for the robot.
    """
    valid_actions = list(env.action_space.all_ground_literals(obs))
    for action in valid_actions:
        if "move" == action.predicate.name:
            reverse_action = _get_reverse_move(action)
            if type(env) != gym.wrappers.order_enforcing.OrderEnforcing:
                try:
                    obs, _, _, _ = env.test_step(action)
                    renderer.canvas.test_new_positions(obs)

                except AssertionError:
                    print(str(action) + " is invalid")
                    valid_actions.remove(action)
                try:
                    env.test_step(reverse_action)
                except AssertionError:
                    pass

            else:
                try:
                    obs, _, _, _ = env.step(action)
                    renderer.canvas.test_new_positions(obs)
                except AssertionError:
                    print(str(action) + " is invalid")
                    valid_actions.remove(action)
                finally:
                    env.step(reverse_action)

    return valid_actions
