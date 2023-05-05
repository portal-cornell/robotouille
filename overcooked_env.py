import pddlgym_interface
from renderer.renderer import OvercookedRenderer
from overcooked_wrapper import OvercookedWrapper
from environments.env_generator import builder
from environments.env_generator import procedural_generator

def _parse_renderer_layout(environment_json):
    """
    Parses and returns renderer layout from the environment json.

    Args:
        environment_json (dict): The environment json.
    
    Returns:
        layout (list): A 2D list of station names representing where stations are in the environment.
    """
    # Update environment names with unique versions
    width, height = environment_json["width"], environment_json["height"]
    layout = [[None for _ in range(width)] for _ in range(height)]
    _, updated_environment_json = builder.build_objects(environment_json)
    stations = updated_environment_json["stations"]
    for station in stations:
        x, y = station["x"], height - station["y"] - 1 # Origin is in the bottom left corner
        layout[y][x] = station["name"]
    return layout

def _procedurally_generate(environment_json, seed, noisy_randomization):
    """
    Attempts to procedurally generated environment until success and returns the environment.

    Args:
        environment_json (dict): The environment json.
        seed (int): The seed to be used for randomization.
        noisy_randomization (bool): Whether or not to use noisy randomization.
    
    Returns:
        env (OvercookedWrapper): The Overcooked environment.
    """
    generated_environment_json = None
    while generated_environment_json is None:
        try:
            generated_environment_json = procedural_generator.randomize_environment(environment_json, seed, noisy_randomization)
            print(f"Successfully created environment with seed {seed}.")
        except Exception as e:
            print(f"Encountered error when creating environment with seed {seed}.")
            print(e)
            seed += 1
    return generated_environment_json

def create_overcooked_env(problem_filename, seed=None, noisy_randomization=False):
    """
    Creates and returns an Overcooked environment.

    Note this function is used to load pre-created environments. These can be located
    in the environments/env_generator/examples folder.

    Args:
        problem_filename (str): The name of the problem file (without extension).
        seed (int): The seed to be used for randomization or None for the pre-created environment.
        noisy_randomization (bool): Whether or not to use noisy randomization.
    
    Returns:
        env (OvercookedWrapper): The Overcooked environment.
    """
    env_name = "overcooked"
    is_test_env = False
    json_filename = f"{problem_filename}.json"
    environment_json = builder.load_environment(json_filename)
    if seed is not None:
        environment_json = _procedurally_generate(environment_json, seed, noisy_randomization)
    layout = _parse_renderer_layout(environment_json)
    render_fn = OvercookedRenderer(layout=layout, players=environment_json["players"]).render
    problem_string, environment_json = builder.build_problem(environment_json) # IDs objects in environment
    builder.write_problem_file(problem_string, f"{problem_filename}.pddl")
    pddl_env = pddlgym_interface.create_pddl_env(env_name, is_test_env, render_fn, f"{problem_filename}.pddl")
    builder.delete_problem_file(f"{problem_filename}.pddl")
    return OvercookedWrapper(pddl_env), environment_json