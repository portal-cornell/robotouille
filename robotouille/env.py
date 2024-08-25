from backend.object import Object
from backend.state import State
from domain.domain_builder import build_domain
from backend.gamemodes.classic import Classic
from .env_utils import build_identity_predicates, build_location_predicates, build_stacking_predicates, build_goal
import gym
import json


def build_state(domain_json, environment_json):
    """
    This function is a temporary solution to building the state.

    Args:
        domain_json (dict): Dictionary containing the domain name, object types, predicate definitions, and action definitions.
        environment_json (dict): Dictionary containing the initial stations, items, and player location.

    Returns:
        state (State): The state.
    """
    domain = build_domain(domain_json)

    entity_fields = domain.get_entity_fields()

    objects = []

    for field in entity_fields:
        if environment_json.get(field) is None: continue
        for entity in environment_json[field]:
            objects.append(Object(entity["name"], field[:-1]))

    true_predicates = []
    true_predicates += build_identity_predicates(environment_json, entity_fields)
    true_predicates += build_location_predicates(environment_json)
    true_predicates += build_stacking_predicates(environment_json)
    goal = build_goal(environment_json, environment_json["goal"])

    state = State().initialize(domain, objects, true_predicates, goal)

    return state

def build_input_json(domain_json):
    """
    This function builds the input JSON from the domain JSON.

    Args:
        domain_json (dict): Dictionary containing the domain name, object types, predicate definitions, and action definitions.

    Returns:
        input_json (dict): The input JSON.
    """
    input_json_name = domain_json["input_json"]

    with open(input_json_name, "r") as input_json_file:
        input_json = json.load(input_json_file)

    return input_json

def build_gamemode(environment_json, domain_json, state):
    """
    This function builds the gamemode of the environment. 

    Args:
        environment_json (dict): The environment dictionary
        domain_json (dict): The domain dictionary
        state (State): The state of the environment

    Returns:
        gamemode(GameMode): The gamemmode of the environment
    """
    name = environment_json["gamemode"]["name"]

    recipe_json_name = domain_json["recipe_json"]

    with open(recipe_json_name, "r") as recipe_json_file:
        recipe_json = json.load(recipe_json_file)

    if name == "classic":
        return Classic(state, environment_json, recipe_json)
    return None

class RobotouilleEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, domain_json, environment_json, render_fn, render_mode=None, size=5):        
        self.size = size
        self.window_size = 512

        initial_state = build_state(domain_json, environment_json)

        self.initial_state = initial_state

        self.gamemode = build_gamemode(environment_json, domain_json, initial_state)

        self.action_space = initial_state.domain.actions

        self.input_json = build_input_json(domain_json)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.window = None
        self.clock = None

        self.render_fn = render_fn

    def step(self, time, actions, interactive):
        obs, done = self.gamemode.step(time, actions)
        return obs, 0, done, {}

    def reset(self, seed=None, options=None):
        return self.initial_state, {}
    
    def render(self):
        return super().render()

        

