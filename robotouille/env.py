from backend.predicate import Predicate
from backend.object import Object
from backend.domain import Domain
from backend.state import State
from environments.env_generator.builder import entity_to_entity_field, create_unique_and_combination_preds, create_combinations
import copy
from domain.domain_builder import build_domain
import gym
import json
    
def build_identity_predicates(environment_dict, entity_fields):
    """
    Builds identity predicates string from an environment dictionary.

    Note that if the typed enum is a cuttable/cookable item, then that identity 
    predicate will be added in this function.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, 
            and player location.
        entity_fields (List[Str]): A list of object types defined in the domain.
    
    Returns:
        identity_predicates (List): Identity predicates list.
    """
    identity_predicates = []
    for field in entity_fields:
        for entity in environment_dict[field]:
            name = entity['name']
            while name[-1].isdigit():
                name = name[:-1]
            obj = Object(entity['name'], field[:-1])
            identity_predicates.append(Predicate().initialize("is"+name, [field[:-1]], [obj]))
            for predicate in entity.get("predicates", []):
                pred = Predicate().initialize(predicate, [field[:-1]], [obj])
                identity_predicates.append(pred)
    return identity_predicates

def build_station_location_predicates(environment_dict):
    """
    Builds station location predicates string from an environment dictionary.

    These include the (empty), (vacant), (loc) and (at) predicates.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, 
            and player location.
    
    Returns:
        predicates (List): Station location predicates string.
    """
    predicates = []
    for station in environment_dict["stations"]:
        station_obj = Object(station["name"], "station")
        for field in ["items", "players"]:
            match = False
            no_match_predicate = "empty" if field == "items" else "vacant"
            predicate = "at" if field == "items" else "loc"
            for entity in environment_dict[field]:
                x = entity["x"] + entity["direction"][0] if field == "players" else entity["x"]
                y = entity["y"] + entity["direction"][1] if field == "players" else entity["y"]
                if x == station["x"] and y == station["y"]:
                    name = entity["name"]
                    obj = Object(name, field[:-1])
                    pred = Predicate().initialize(predicate, [field[:-1], "station"], [obj, station_obj])
                    predicates.append(pred)
                    match = True
            if not match:
                pred = Predicate().initialize(no_match_predicate, ["station"], [station_obj])
                predicates.append(pred)
    return predicates

def build_player_location_predicates(environment_dict):
    """
    Builds player location predicates string from an environment dictionary.

    These include the (nothing) and (has) predicates.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, 
            and player location.
    
    Returns:
        predicates (List): Player location predicates string.
    """
    predicates = []
    for player in environment_dict["players"]:
        player_obj = Object(player["name"], "player")
        match = False
        for item in environment_dict["items"]:
            if player["x"] == item["x"] and player["y"] == item["y"]:
                obj = Object(item["name"], "item")
                pred = Predicate().initialize("has", ["player", "item"], [player_obj, obj])
                predicates.append(pred)
                match = True
                break
        if not match:
            pred = Predicate().initialize("nothing", ["player"], [player_obj])
            predicates.append(pred)
    return predicates

def build_location_predicates(environment_dict):
    """
    Builds location predicates string from an environment dictionary.

    The most explicit location predicates are the (loc) and (at) predicates
    which specify the location of players and items relative to stations respectively.
    There are other implicit location predicates such as (nothing), (has), (empty) and
    (vacant) which all imply the location of the player or item.

    Note that the (clear), (on) and (atop) predicates are added in the build_stacking_predicates function. 

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, and player location.
    
    Returns:
        location_predicates (List): PDDL location predicates string.
    """
    location_predicates = []
    location_predicates += build_station_location_predicates(environment_dict)
    location_predicates += build_player_location_predicates(environment_dict)
    return location_predicates

def build_stacking_predicates(environment_dict):
    """
    Build stacking predicates string from an environment dictionary.

    These include the (clear), (on) and (atop) predicates.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, and player location.
    
    Returns:
        stacking_predicates (List): Stacking predicates string.
    """
    stacking_predicates = []
    stacks = {}
    # Sort items into stacks ordered by stacking order
    sorting_key = lambda item: item["stack-level"]
    for item in environment_dict["items"]:
        for station in environment_dict["stations"]:
            if item["x"] == station["x"] and item["y"] == station["y"]:
                stacks[station["name"]] = stacks.get(station["name"], []) + [item]
                stacks[station["name"]].sort(key=sorting_key)
                break
    # Add stacking predicates
    for station_name, items in stacks.items():
        station_obj = Object(station_name, "station")
        first_item_obj = Object(items[0]["name"], "item")
        pred = Predicate().initialize("on", ["item", "station"], [first_item_obj, station_obj])
        stacking_predicates.append(pred)
        for i in range(1, len(items)):
            obj = Object(items[i]["name"], "item")
            obj_below = Object(items[i-1]["name"], "item")
            pred = Predicate().initialize("atop", ["item", "item"], [obj, obj_below])
            stacking_predicates.append(pred)
        last_obj = Object(items[-1]["name"], "item")
        pred = Predicate().initialize("clear", ["item"], [last_obj])
        stacking_predicates.append(pred)
    return stacking_predicates

def create_conjunction(predicates):
    """
    Creates a list of all possible conjunctions of the given predicates.

    Args:
        predicates (list[list[str]]): List of predicates separated into a list of arguments.
    
    Returns:
        conjunction ([List[Predicate]]): List of all possible conjunctions of the given predicates.
    """
    conjunction = []
    for pred in predicates:
        args = []
        types = []
        for arg in pred[1:]:
            name = arg[:-1]
            while name[-1].isdigit():
                name = name[:-1]
            arg_type = entity_to_entity_field(name)[:-1]
            obj = Object(arg, arg_type)
            args.append(obj)
            types.append(arg_type)
        new_pred = Predicate().initialize(pred[0], types, args)
        conjunction.append(new_pred)
    return conjunction

def build_goal(environment_dict):
    """
    Builds a list of possible goal predicates from an environment dictionary.

    This goal is constructed as a disjunction to allow for all possible
    combinations of items to satisfy a goal. For example, if a goal calls
    for a regular hamburger to be arranged on a table and there are two
    patties, the goal will accommodate for either patty being used.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, and player location.
    
    Returns:
        goal (List[List[Predicate]]): List of all possible goal predicates.
    """
    goal =  []
    unique_preds, combination_preds, combination_dict = create_unique_and_combination_preds(environment_dict)
    combinations, id_order = create_combinations(combination_dict)
    assert len(combinations) > 0, "Object in goal missing from environment"
    for combination in combinations:
        # Combination predicates with the combination ID arguments filled in
        filled_combination_preds = copy.deepcopy(combination_preds)
        for i, combination_pred in enumerate(filled_combination_preds):
            for j, arg in enumerate(combination_pred):
                if arg.isdigit(): # Combination ID argument
                    id_idx = id_order.index(arg)
                    filled_combination_preds[i][j] = combination[id_idx]
        goal.append(create_conjunction(unique_preds + filled_combination_preds))
    return goal

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
        for entity in environment_json[field]:
            objects.append(Object(entity["name"], field[:-1]))

    true_predicates = []
    true_predicates += build_identity_predicates(environment_json, entity_fields)
    true_predicates += build_location_predicates(environment_json)
    true_predicates += build_stacking_predicates(environment_json)
    goal = build_goal(environment_json)

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

class RobotouilleEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, domain_json, environment_json, render_fn, render_mode=None, size=5):        
        self.size = size
        self.window_size = 512

        initial_state = build_state(domain_json, environment_json)

        self.initial_state = initial_state

        self.observation_space = initial_state

        self.action_space = initial_state.domain.actions

        self.input_json = build_input_json(domain_json)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.window = None
        self.clock = None

        self.render_fn = render_fn

    def get_state(self):
        return self.observation_space
    
    def set_state(self, state):
        self.observation_space = state

    def step(self, action, args, interactive):
        obs, done = self.observation_space.step(action, args)
        return obs, 0, done, {}

    def reset(self, seed=None, options=None):
        return self.initial_state, {}
    
    def render(self):
        return super().render()

        

