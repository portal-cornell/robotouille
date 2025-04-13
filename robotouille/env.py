import copy
import gym
import json
import random
import re
import string

from backend.predicate import Predicate
from backend.object import Object
from backend.domain import Domain
from backend.state import State
from environments.env_generator.builder import entity_to_entity_field, create_unique_and_combination_preds, create_combinations
from domain.domain_builder import build_domain
from utils.robotouille_utils import trim_item_ID
    
def build_identity_predicates(domain_dict, environment_dict, entity_fields):
    """
    Builds identity predicates from an environment dictionary.

    Note that if the typed enum is a cuttable/cookable item, then that identity 
    predicate will be added in this function.

    Parameters:
        domain_dict (dict):
            Dictionary containing the domain name, object types, predicate definitions, 
            and action definitions
        environment_dict (dict):
            Dictionary containing the initial stations, items, and player location.
        entity_fields (List[Str]):
            A list of object types defined in the domain.
    
    Returns:
        identity_predicates (List):
            Identity predicates list.
    """
    identity_predicates = []
    valid_entity_fields = [field for field in entity_fields if field in environment_dict.keys()]
    for field in valid_entity_fields:
        if not environment_dict.get(field): continue
        for entity in environment_dict[field]:
            name = entity['name']
            while name[-1].isdigit():
                name = name[:-1]
            obj = Object(entity['name'], field[:-1])
            pred_def = list(filter(lambda x: x["name"] == "is"+name, domain_dict["predicate_defs"]))[0]
            identity_predicates.append(Predicate().initialize("is"+name, [field[:-1]], [obj], pred_def["language_descriptors"]))
            for predicate in entity.get("predicates", []):
                pred_def = list(filter(lambda x: x["name"] == predicate, domain_dict["predicate_defs"]))[0]
                pred = Predicate().initialize(predicate, [field[:-1]], [obj], pred_def["language_descriptors"])
                identity_predicates.append(pred)
    return identity_predicates

def build_container_location_predicates(domain_dict, environment_dict):
    """
    Builds container location predicates form an environment dictionary.

    These include (in) and (container_empty) predicates.

    Parameters:
        domain_dict (dict):
            Dictionary containing the domain name, object types, predicate definitions,
        environment_dict (dict):
            Dictionary containing the initial stations, items, and player location.

    Returns:
        predicates (List):
            Container location predicates.
    """
    predicates = []
    if not environment_dict.get("containers"): return predicates
    for container in environment_dict["containers"]:
        container_obj = Object(container["name"], "container")
        match = False
        for meal in environment_dict["meals"]:
            if meal["x"] == container["x"] and meal["y"] == container["y"]:
                meal_obj = Object(meal["name"], "meal")
                pred_def = list(filter(lambda x: x["name"] == "in", domain_dict["predicate_defs"]))[0]
                pred = Predicate().initialize("in", ["meal", "container"], [meal_obj, container_obj], pred_def["language_descriptors"])
                predicates.append(pred)
                match = True
        if not match:
            pred_def = list(filter(lambda x: x["name"] == "container_empty", domain_dict["predicate_defs"]))[0]
            pred = Predicate().initialize("container_empty", ["container"], [container_obj], pred_def["language_descriptors"])
            predicates.append(pred)
    return predicates

def build_station_location_predicates(domain_dict, environment_dict):
    """
    Builds station location predicates from an environment dictionary.

    These include the (station_empty), (vacant), (loc) and (at) predicates.

    Parameters:
        domain_dict (dict):
            Dictionary containing the domain name, object types, predicate definitions, 
            and action definitions
        environment_dict (dict):
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        predicates (List):
            Station location predicates.
    """
    predicates = []
    for station in environment_dict["stations"]:
        station_obj = Object(station["name"], "station")
        match = False
        # Check if there are any players at the station
        for player in environment_dict.get("players", []):
            x = player["x"] + player["direction"][0]
            y = player["y"] + player["direction"][1]
            if x == station["x"] and y == station["y"]:
                name = player["name"]
                obj = Object(name, "player")
                pred_def = list(filter(lambda x: x["name"] == "loc", domain_dict["predicate_defs"]))[0]
                pred = Predicate().initialize("loc", ["player", "station"], [obj, station_obj], pred_def["language_descriptors"])
                predicates.append(pred)
                match = True
        # If no players are at the station, add a vacant predicate
        if not match:
            pred_def = list(filter(lambda x: x["name"] == "vacant", domain_dict["predicate_defs"]))[0]
            pred = Predicate().initialize("vacant", ["station"], [station_obj], pred_def["language_descriptors"])
            predicates.append(pred)
        match = False
        # Check if there are any items or containers at the station
        for field in ["items", "containers"]:
            predicate = "item_at" if field == "items" else "container_at"
            for entity in environment_dict.get(field, []):
                x = entity["x"]
                y = entity["y"]
                if x == station["x"] and y == station["y"]:
                    name = entity["name"]
                    obj = Object(name, field[:-1])
                    pred_def = list(filter(lambda x: x["name"] == predicate, domain_dict["predicate_defs"]))[0]
                    pred = Predicate().initialize(predicate, [field[:-1], "station"], [obj, station_obj], pred_def["language_descriptors"])
                    predicates.append(pred)
                    match = True
        # If no items or containers are at the station, add a station_empty predicate
        if not match:
            pred_def = list(filter(lambda x: x["name"] == "station_empty", domain_dict["predicate_defs"]))[0]
            pred = Predicate().initialize("station_empty", ["station"], [station_obj], pred_def["language_descriptors"])
            predicates.append(pred)
    return predicates

def build_player_location_predicates(domain_dict, environment_dict):
    """
    Builds player location predicates from an environment dictionary.

    These include the (nothing) and (has) predicates.

    Parameters:
        domain_dict (dict):
            Dictionary containing the domain name, object types, predicate definitions, 
            and action definitions
        environment_dict (dict):
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        predicates (List): Player location predicates.
    """
    predicates = []
    for player in environment_dict["players"]:
        player_obj = Object(player["name"], "player")
        match = False
        if environment_dict.get("items"):
            for item in environment_dict["items"]:
                if player["x"] == item["x"] and player["y"] == item["y"]:
                    obj = Object(item["name"], "item")
                    pred_def = list(filter(lambda x: x["name"] == "has_item", domain_dict["predicate_defs"]))[0]
                    pred = Predicate().initialize("has_item", ["player", "item"], [player_obj, obj], pred_def["language_descriptors"])
                    predicates.append(pred)
                    match = True
                    break
        if not match and environment_dict.get("containers"): 
            for container in environment_dict["containers"]:
                if player["x"] == container["x"] and player["y"] == container["y"]:
                    obj = Object(container["name"], "container")
                    pred_def = list(filter(lambda x: x["name"] == "has_container", domain_dict["predicate_defs"]))[0]
                    pred = Predicate().initialize("has_container", ["player", "container"], [player_obj, obj], pred_def["language_descriptors"])
                    predicates.append(pred)
                    match = True
                    break
        if not match:
            pred_def = list(filter(lambda x: x["name"] == "nothing", domain_dict["predicate_defs"]))[0]
            pred = Predicate().initialize("nothing", ["player"], [player_obj], pred_def["language_descriptors"])
            predicates.append(pred)
    return predicates

def build_location_predicates(domain_dict, environment_dict):
    """
    Builds location predicates from an environment dictionary.

    The most explicit location predicates are the (loc) and (at) predicates
    which specify the location of players and items relative to stations respectively.
    There are other implicit location predicates such as (nothing), (has), (station_empty) and
    (vacant) which all imply the location of the player or item.

    Note that the (clear), (on) and (atop) predicates are added in the build_stacking_predicates function. 

    Parameters:
        domain_dict (dict):
            Dictionary containing the domain name, object types, predicate definitions, 
            and action definitions
        environment_dict (dict):
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        location_predicates (List):
            PDDL location predicates.
    """
    location_predicates = []
    location_predicates += build_container_location_predicates(domain_dict, environment_dict)
    location_predicates += build_station_location_predicates(domain_dict, environment_dict)
    location_predicates += build_player_location_predicates(domain_dict, environment_dict)
    return location_predicates

def build_stacking_predicates(domain_dict, environment_dict):
    """
    Build stacking predicates from an environment dictionary.

    These include the (clear), (on) and (atop) predicates.

    Parameters:
        domain_dict (dict):
            Dictionary containing the domain name, object types, predicate definitions, 
            and action definitions
        environment_dict (dict):
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        stacking_predicates (List):
            Stacking predicates.
    """
    stacking_predicates = []
    stacks = {}
    # Sort items into stacks ordered by stacking order
    sorting_key = lambda item: item["stack-level"]
    if not environment_dict.get("items"): return stacking_predicates
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
        pred_def = list(filter(lambda x: x["name"] == "item_on", domain_dict["predicate_defs"]))[0]
        pred = Predicate().initialize("item_on", ["item", "station"], [first_item_obj, station_obj], pred_def["language_descriptors"])
        stacking_predicates.append(pred)
        for i in range(1, len(items)):
            obj = Object(items[i]["name"], "item")
            obj_below = Object(items[i-1]["name"], "item")
            pred_def = list(filter(lambda x: x["name"] == "atop", domain_dict["predicate_defs"]))[0]
            pred = Predicate().initialize("atop", ["item", "item"], [obj, obj_below], pred_def["language_descriptors"])
            stacking_predicates.append(pred)
        last_obj = Object(items[-1]["name"], "item")
        pred_def = list(filter(lambda x: x["name"] == "clear", domain_dict["predicate_defs"]))[0]
        pred = Predicate().initialize("clear", ["item"], [last_obj], pred_def["language_descriptors"])
        stacking_predicates.append(pred)
    return stacking_predicates

def create_conjunction(domain_dict, predicates):
    """
    Creates a list of all possible conjunctions of the given predicates.

    Parameters:
        domain_dict (dict):
            Dictionary containing the domain name, object types, predicate definitions, and action definitions
        predicates (list[list[str]]):
            List of predicates separated into a list of arguments.
    
    Returns:
        conjunction ([List[Predicate]]):
            List of all possible conjunctions of the given predicates.
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
        pred_def = list(filter(lambda x: x["name"] == pred[0], domain_dict["predicate_defs"]))[0]
        new_pred = Predicate().initialize(pred[0], types, args, pred_def["language_descriptors"])
        conjunction.append(new_pred)
    return conjunction

def build_goal(domain_dict, environment_dict):
    """
    Builds a list of possible goal predicates from an environment dictionary.

    This goal is constructed as a disjunction to allow for all possible
    combinations of items to satisfy a goal. For example, if a goal calls
    for a regular hamburger to be arranged on a table and there are two
    patties, the goal will accommodate for either patty being used.

    Parameters:
        domain_dict (dict):
            Dictionary containing the domain name, object types, predicate definitions, and action definitions
        environment_dict (dict):
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        goal (List[List[Predicate]]):
            List of all possible goal predicates.
    """
    goal =  []
    unique_preds, combination_preds, combination_dict = create_unique_and_combination_preds(environment_dict)
    combinations, id_order = create_combinations(combination_dict)
    # assert len(combinations) > 0, "Object in goal missing from environment"
    for combination in combinations:
        # Combination predicates with the combination ID arguments filled in
        filled_combination_preds = copy.deepcopy(combination_preds)
        for i, combination_pred in enumerate(filled_combination_preds):
            for j, arg in enumerate(combination_pred):
                if arg.isdigit(): # Combination ID argument
                    id_idx = id_order.index(arg)
                    filled_combination_preds[i][j] = combination[id_idx]
        goal.append(create_conjunction(domain_dict, unique_preds + filled_combination_preds))
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
        if environment_json.get(field) is None: continue
        for entity in environment_json[field]:
            objects.append(Object(entity["name"], field[:-1]))

    true_predicates = []
    true_predicates += build_identity_predicates(domain_json, environment_json, entity_fields)
    true_predicates += build_location_predicates(domain_json, environment_json)
    true_predicates += build_stacking_predicates(domain_json, environment_json)
    goal = build_goal(domain_json, environment_json)
    goal_description = environment_json["goal_description"]

    state = State().initialize(domain, objects, true_predicates, goal, goal_description)

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

class LanguageSpace(gym.spaces.Text):
    
    @staticmethod
    def state_to_language_description(state):
        """
        Converts a state to a language description.

        Parameters:
            state (State):
                The state to convert to a language description.
        
        Returns:
            language_description (str):
                The language description of the state.
        """
        predicates = [pred for pred, is_true in state.predicates.items() if is_true]
        language_description = ""
        # TODO(chalo2000): Separate Predicate and Action into PredicateDef and ActionDef
        #                  to remove param_arg_dict and simplify retrieving the language 
        #                  description of the action.
        # Object descriptions
        object_descriptions = []
        pred_parser = lambda x: [s.strip() for s in re.findall(r'\(([^()]+)\)', str(x))[0].split(',')]
        for obj in state.objects:
            description_header = f"{obj.object_type.capitalize()} {obj.name}:"
            relevant_preds = [pred for pred in predicates if obj.name in pred_parser(pred)]
            language_descriptions = [pred.get_language_description(obj) for pred in relevant_preds]
            predicate_descriptions = "\n".join(language_descriptions)
            object_descriptions.append(f"{description_header}\n{predicate_descriptions}")
        language_description += "\n\n".join(object_descriptions)
        # Valid Actions
        language_description += "\n\nValid Actions:\n"
        _, str_valid_actions = state.get_valid_actions_and_str()
        language_description += "\n".join(str_valid_actions)
        # Goal
        language_description += f"\n\nGoal: {state.goal_description}"
        return language_description
    
    def __init__(self, initial_state, min_length=1, max_length=32768):
        """
        Initializes the Language space.

        Parameters:
            initial_state (State):
                The initial state of the language environment.
            min_length (int):
                The minimum length of the string. At least one character by default.
            max_length (int):
                The maximum length of the string. At most 8192 * 4 characters by default
                to match most LLM's max context lengths. 
        """
        charset = string.ascii_letters + string.digits + string.punctuation + string.whitespace
        super().__init__(min_length=min_length, max_length=max_length, charset=charset)
        self.initial_state = initial_state
    
    def sample(self):
        """
        Samples a random language description from the state space.

        Note, while this function returns valid language descriptions,
        it is likely to return illegal state descriptions. This function
        should only be used for testing purposes (e.g. generate example
        formats for the initial state).

        Returns:
            language (str): The random language description.
        """
        # TODO(chalo2000): Reimplement this to generate valid language actions ()
        state_copy = copy.deepcopy(self.initial_state)
        for pred in state_copy.predicates:
            state_copy.predicates[pred] = random.choice([True, False])
        return LanguageSpace.state_to_language_description(state_copy)

class RobotouilleEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, domain_json, environment_json, renderer, size=5):        
        self.size = size
        self.window_size = 512
        
        self.domain_json = domain_json
        self.environment_json = environment_json
        self.initial_state = build_state(domain_json, environment_json)
        self.current_state = copy.deepcopy(self.initial_state)

        language_space = LanguageSpace(initial_state=self.initial_state)
        self.observation_space = language_space
        self.action_space = language_space

        self.input_json = build_input_json(domain_json)

        self.window = None
        self.clock = None

        self.renderer = renderer

    def step(self, action):
        done = self.current_state.step(action) # Current state is updated in place
        obs = LanguageSpace.state_to_language_description(self.current_state)
        return obs, 0, done, {}

    def reset(self, seed=None, options=None):
        obs = LanguageSpace.state_to_language_description(self.initial_state)
        self.current_state = copy.deepcopy(self.initial_state)
        self.renderer.reset()
        return obs, {}
    
    def render(self, render_mode, close=False):
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        return self.renderer.render(self.current_state, render_mode, close=close)

    def __deepcopy__(self, memo):
        env = RobotouilleEnv(self.domain_json, self.environment_json, self.renderer)
        env.current_state = copy.deepcopy(self.current_state)
        env.window = self.window
        env.clock = self.clock
        memo[id(self)] = env
        return env

        

