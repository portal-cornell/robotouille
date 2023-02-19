import pddlgym
import os
import shutil
from overcooked_renderer import OvercookedRenderer

CURRENT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
ENVIRONMENT_DIR_PATH = os.path.join(CURRENT_DIR_PATH, "environments")
PDDL_DIR_PATH = os.path.join(CURRENT_DIR_PATH, "pddlgym", "pddl")

def add_domain_file(env_name):
    """
    Adds a domain file to the PDDL directory.

    Args:
        env_name : str
            Name of the environment
    
    Returns:
        domain_file_path : str
            Path to the domain file in the PDDL directory
    """
    domain_file_name = f"{env_name}.pddl"
    domain_file_path = os.path.join(ENVIRONMENT_DIR_PATH, domain_file_name)
    shutil.copy2(domain_file_path, PDDL_DIR_PATH)
    new_domain_file_path = os.path.join(PDDL_DIR_PATH, domain_file_name)
    return new_domain_file_path

def add_problem_files(env_name):
    """
    Add problem files to the PDDL directory.

    Args:
        env_name : str
            Name of the environment
    
    Returns:
        problem_dir_path : str
            Path to the problem files in the PDDL directory
    """
    problem_dir_path = os.path.join(ENVIRONMENT_DIR_PATH, env_name)
    pddl_problem_dir_path = os.path.join(PDDL_DIR_PATH, env_name)
    shutil.copytree(problem_dir_path, pddl_problem_dir_path)
    new_problem_dir_path = os.path.join(PDDL_DIR_PATH, env_name)
    return new_problem_dir_path

def create_pddl_env(env_name, is_test_env, kwargs):
    """
    Creates and returns a PDDLGym environment.

    Args:
        env_name : str
            Name of the environment
        is_test_env : bool
            Whether the environment is a test environment
        kwargs : dict
            Keyword arguments to pass to the environment
        domain_file_name : str
            Name of the domain file
        problem_file_name : str
            Name of the problem file
    
    Returns:
        env : pddlgym.PDDLEnv
    """
    pddlgym.register_pddl_env(env_name, is_test_env, kwargs)
    domain_file_path = add_domain_file(env_name)
    problem_dir_path = add_problem_files(env_name)
    env = pddlgym.make(f"PDDLEnv{env_name.capitalize()}-v0")
    os.remove(domain_file_path)
    shutil.rmtree(problem_dir_path)
    return env


def create_overcooked_env():
    """
    Creates and returns an Overcooked environment.

    Returns:
        env : pddlgym.PDDLEnv
    """
    # Register the environment
    env_name = 'overcooked'
    is_test_env = False
    kwargs = {'render': OvercookedRenderer().render,
            'operators_as_actions': True, 
            'dynamic_action_space': True,
            "raise_error_on_invalid_action": False
          }
    return create_pddl_env(env_name, is_test_env, kwargs)

def parse(literal_str):
    """
    Parses a string representation of a literal into a Literal object.

    Args:
    literal_str : str
        String representation of a literal. 
        Examples:
        - at(chef:player,stove:station)
        - A(B:1,C:2,D:3,...) where A is the predicate name, B-D are the arguments, and 1-3 are the types
    
    Returns:
        predicate : str
            Predicate name
        args : list of str
            List of arguments
        types : list of Type strings
            List of argument types
    """
    # Split the string into the predicate name and the arguments
    predicate_name, args_str = literal_str.split("(")
    # Split the arguments into a list of strings
    args_str = args_str[:-1] # Remove the trailing ')'
    args_str = args_str.split(",")
    # Convert the arguments into a list of tuples
    args = []
    types = []
    for arg_str in args_str:
        arg_name, arg_type = arg_str.split(":")
        args.append(arg_name)
        types.append(pddlgym.structs.Type(arg_type))
    return predicate_name, args, types

def str_to_literal(literal_str):
    """
    Converts a string representation of a literal to a Literal object.

    literal_str : str
        String representation of a literal. 
        Examples:
        - at(chef:player,stove:station)
        - A(B:1,C:2,D:3,...) where A is the predicate name, B-D are the arguments, and 1-3 are the types
    """
    predicate_name, args, types = parse(literal_str)
    predicate = pddlgym.structs.Predicate(predicate_name, len(args), types)
    # Create the literal
    literal = pddlgym.structs.Literal(predicate, args)
    return literal

