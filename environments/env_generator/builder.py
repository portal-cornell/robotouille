import argparse
import json
import os
import copy
import itertools
from .object_enums import Item, Player, Station, Container, Meal, str_to_typed_enum, TYPES
from .procedural_generator import randomize_environment
import random

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "examples")
PROBLEM_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "robotouille")

STATION_FIELD = "stations"
ITEM_FIELD = "items"
PLAYER_FIELD = "players"
MEAL_FIELD = "meals"
CONTAINER_FIELD = "containers"

ENTITY_FIELDS = [STATION_FIELD, ITEM_FIELD, PLAYER_FIELD, CONTAINER_FIELD, MEAL_FIELD]

def entity_to_entity_field(entity):
    """
    Converts an entity into the corresponding entity field.

    An entity could either be converted into a typed_enum if referring to a specific
    entity or could be a wild card representing any entity.

    Note, wild cards are singular forms of the entity fields (which are plural)

    Args:
        entity (str): A string representation of an entity.
    
    Returns:
        entity_field (str): Entity field corresponding to the typed enum.

    Raises:
        ValueError: If the entity cannot be converted into an entity field.
    """
    try:
        typed_enum = str_to_typed_enum(entity)
        # Convert entities into entity fields
        if isinstance(typed_enum, Station): return STATION_FIELD
        elif isinstance(typed_enum, Item): return ITEM_FIELD
        elif isinstance(typed_enum, Player): return PLAYER_FIELD
        elif isinstance(typed_enum, Meal): return MEAL_FIELD
        elif isinstance(typed_enum, Container): return CONTAINER_FIELD
    except ValueError:
        # Convert wild card entities into entity fields
        if entity == STATION_FIELD[:-1]: return STATION_FIELD
        elif entity == ITEM_FIELD[:-1]: return ITEM_FIELD
        elif entity == PLAYER_FIELD[:-1]: return PLAYER_FIELD
        elif entity == MEAL_FIELD[:-1]: return MEAL_FIELD
        elif entity == CONTAINER_FIELD[:-1]: return CONTAINER_FIELD
    raise ValueError(f"Cannot convert {entity} into an entity field.")

def load_environment(json_filename, seed=None):
    """
    Loads an Robotouille environment from a JSON file in the examples folder.

    The JSON file should contain the initial stations, items, and player location.
    These will be sorted in the (x, y) order from left to right, bottom to top order.

    If a seed is provided, the environment will be randomized based on the seed.

    Args:
        json_filename (str): Name of the JSON file in the examples folder
        seed (int): Seed for the environment.
    
    Returns:
        environment (dict): JSON containing the initial stations, items, and player location.
    """
    # Get json file based on current file directory
    with open(os.path.join(EXAMPLES_DIR, json_filename), "r") as f:
        environment_json = json.load(f)
    sorting_key = lambda entity: (entity["x"], entity["y"])
    # TODO (chalo2000): Breaks seed that gives consistent layout
    valid_entity_fields = [field for field in ENTITY_FIELDS if field in environment_json]
    for field in valid_entity_fields:
        environment_json[field].sort(key=sorting_key)
        for entity in environment_json[field]:
            if entity["name"] == field[:-1]:
                entity["name"] = random.choice(list(TYPES[field[:-1]])).value
    return environment_json

def build_objects(environment_dict):
    """
    Builds a PDDL objects string from an environment dictionary.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, 
            and player location.
    
    Returns:
        objects_str (str): PDDL objects string.
        updated_environment_dict (List[str, Enum]): The original environment dictionary with the 
            names updated to include the IDs and the typed enums added.
    """
    objects_str = ""
    updated_environment_dict = copy.deepcopy(environment_dict)
    valid_entity_fields = [field for field in ENTITY_FIELDS if field in environment_dict]
    for field in valid_entity_fields:
        object_type = field[:-1]
        seen = {}
        updated_environment_dict[field].sort(key=lambda entity: (entity["x"], entity["y"]))
        for i, entity in enumerate([entity["name"] for entity in updated_environment_dict[field]]):
            updated_environment_dict[field][i]["typed_enum"] = str_to_typed_enum(entity)
            seen[entity] = seen.get(entity, 0) + 1
            entity_with_id = f"{entity}{seen[entity]}"
            updated_environment_dict[field][i]["name"] = entity_with_id
            objects_str += f"    {entity_with_id} - {object_type}\n"
    return objects_str, updated_environment_dict

def build_identity_predicates(environment_dict):
    """
    Builds PDDL identity predicates string from an environment dictionary.

    Note that if the typed enum is a cuttable/cookable item, then that identity 
    predicate will be added in this function.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, 
            and player location.
    
    Returns:
        identity_predicates_str (str): PDDL identity predicates string.
    """
    identity_predicates_str = ""
    valid_entity_fields = [field for field in ENTITY_FIELDS if field in environment_dict]
    for field in valid_entity_fields:
        for entity in environment_dict[field]:
            typed_enum = entity['typed_enum']
            name = entity['name']
            identity_predicates_str += f"    (is{typed_enum.value} {name})\n"
            for predicate in entity.get("predicates", []):
                identity_predicates_str += f"    ({predicate} {name})\n"
    return identity_predicates_str

def build_station_location_predicates(environment_dict):
    """
    Builds PDDL station location predicates string from an environment dictionary.

    These include the (empty), (vacant), (loc) and (at) predicates.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, 
            and player location.
    
    Returns:
        predicates_str (str): PDDL station location predicates string.
    """
    predicates_str = ""
    for station in environment_dict["stations"]:
        valid_fields = [field for field in ["items", "players"] if field in environment_dict]
        for field in valid_fields:
            match = False
            no_match_predicate = "empty" if field == "items" else "vacant"
            predicate = "item_at" if field == "items" else "loc"
            for entity in environment_dict[field]:
                x = entity["x"] + entity["direction"][0] if field == "players" else entity["x"]
                y = entity["y"] + entity["direction"][1] if field == "players" else entity["y"]
                if x == station["x"] and y == station["y"]:
                    name = entity["name"]
                    predicates_str += f"    ({predicate} {name} {station['name']})\n"
                    match = True
            if not match:
                predicates_str += f"    ({no_match_predicate} {station['name']})\n"
    return predicates_str

def build_player_location_predicates(environment_dict):
    """
    Builds PDDL player location predicates string from an environment dictionary.

    These include the (nothing) and (has) predicates.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, 
            and player location.
    
    Returns:
        predicates_str (str): PDDL player location predicates string.
    """
    predicates_str = ""
    for player in environment_dict["players"]:
        match = False
        for item in environment_dict.get("items", []):
            if player["x"] == item["x"] and player["y"] == item["y"]:
                predicates_str += f"    (has {player['name']} {item['name']})\n"
                match = True
                break
        if not match:
            predicates_str += f"    (nothing {player['name']})\n"
    return predicates_str

def build_location_predicates(environment_dict):
    """
    Builds PDDL location predicates string from an environment dictionary.

    The most explicit location predicates are the (loc) and (at) predicates
    which specify the location of players and items relative to stations respectively.
    There are other implicit location predicates such as (nothing), (has), (empty) and
    (vacant) which all imply the location of the player or item.

    Note that the (clear), (on) and (atop) predicates are added in the build_stacking_predicates function. 

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, and player location.
    
    Returns:
        location_predicates_str (str): PDDL location predicates string.
    """
    location_predicates_str = ""
    location_predicates_str += build_station_location_predicates(environment_dict)
    location_predicates_str += build_player_location_predicates(environment_dict)
    return location_predicates_str

def build_stacking_predicates(environment_dict):
    """
    Build PDDL stacking predicates string from an environment dictionary.

    These include the (clear), (on) and (atop) predicates.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, and player location.
    
    Returns:
        stacking_predicates_str (str): PDDL stacking predicates string.
    """
    stacking_predicates_str = ""
    stacks = {}
    # Sort items into stacks ordered by stacking order
    sorting_key = lambda item: item["stack-level"]
    for item in environment_dict.get("items", []):
        for station in environment_dict["stations"]:
            if item["x"] == station["x"] and item["y"] == station["y"]:
                stacks[station["name"]] = stacks.get(station["name"], []) + [item]
                stacks[station["name"]].sort(key=sorting_key)
                break
    # Add stacking predicates
    for station_name, items in stacks.items():
        stacking_predicates_str += f"    (on {items[0]['name']} {station_name})\n"
        for i in range(1, len(items)):
            stacking_predicates_str += f"    (atop {items[i]['name']} {items[i-1]['name']})\n"
        stacking_predicates_str += f"    (clear {items[-1]['name']})\n"
    return stacking_predicates_str

def create_unique_and_combination_preds(environment_dict):
    """
    Creates lists of unique and combination predicates from an environment dictionary.

    This function is used for goal creation. A goal in PDDL is a conjunction or disjunction
    of predicates. The goal JSON is specified by a predicate name, the arguments it takes, 
    and then an ID for each argument. The ID can be used to specify a specific entity of a particular 
    type (a digit ID) or a unique entity (a non-digit ID).

    Unique predicates are those whose arguments only refer to unique entities. This means that
    the arguments IDs are only non-digits and therefore there is a 1 to 1 mapping between that
    predicate and the entities within the environment_dict. For example, perhaps the goal is
    to hold a specific item or to have a specific item on a specific station. This would be
    a unique predicate.

    Combination predicates are those that contain at least one argument that refers to a specific entity
    of a particular type. This means that at least one argument's ID is a digit. This means that
    any entity of that type can be included in the goal and thus a disjunction must be used to
    include all possible entities. For example, perhaps the goal is to hold any patty or to create a 
    lettuce burger where the ingredients can be any found in the environment. This would be a combination
    predicate.

    To create all the possible combinations of combination predicates, a dictionary is used to
    store all the specific entities of a particular type. The dictionary is keyed by the entity type
    and the value is a mapping from the argument's ID to a list of all the entities of that type. The
    dictionary isn't a direct mapping from argument ID to entities to account for cases such as making
    double cheese burgers where the same entity can be used twice.

    TODO: Allow for combination predicates that aren't specific entities of a particular type but
          any entities of a particular type (wild cards) For example, make a burger and place on 
          any station.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, and player location.

    Returns:
        unique_preds (list): List of unique predicates.
        combination_preds (list): List of combination predicates.
        combination_dict (dict): Dictionary of all the specific entities of a particular type.
    """
    unique_preds = [] # Predicates whose arguments refer to unique entities
    combination_preds = [] # Predicates whose arguments refer to a particular item type
    combination_dict = {} # Dictionary to prepare combination predicates
    for goal in environment_dict["goal"]: # Check out an example under the `examples` directory for JSON structure
        pred = [goal["predicate"]]
        unique_pred = True
        for i, arg in enumerate(goal["args"]):
            arg_id = str(goal["ids"][i])
            entity_field = entity_to_entity_field(arg)
            if arg_id.isdigit():
                # Combination predicate
                unique_pred = False
                pred.append(arg_id)
                if arg not in combination_dict:
                    combination_dict[arg] = {}
                    # Get all entities to prepare the combination
                    arg_entities = list(filter(lambda entity: arg in entity["name"], environment_dict[entity_field]))
                    arg_entity_names = list(map(lambda entity: entity["name"], arg_entities))
                    combination_dict[arg]['entities'] = arg_entity_names if arg_entity_names else []
                    combination_dict[arg]['ids'] = set()
                combination_dict[arg]['ids'].add(arg_id)
            else:
                # Unique predicate
                same_id_entity = list(filter(lambda entity: entity.get("id") == arg_id, environment_dict[entity_field]))
                # If the entity is not found, then it is a wild card entity
                entity_name = same_id_entity[0]["name"]
                pred.append(entity_name)
        if unique_pred:
            unique_preds.append(pred)
        else:
            combination_preds.append(pred)
    return unique_preds, combination_preds, combination_dict

def create_combinations(combination_dict):
    """
    Creates and returns the combinations of combination predicates along with their ID order.

    This function takes in the combination dict, maintains the order of the IDs, takes permutations
    of the IDs for the same argument type, then takes a combination of all the permutations to create
    all possible combinations of combination predicates.

    Args:
        combination_dict (dict): Dictionary of all the specific entities of a particular type.
    
    Returns:
        combinations (list): List of all possible combinations of combination predicates.
        id_order (list): List of the order of IDs for each combination.
    """
    combination_list = []
    id_order = []
    for arg in combination_dict:
        ids = list(combination_dict[arg]['ids'])
        id_order += ids
        entities = combination_dict[arg]['entities']
        if entities == []:
            id_counter = 1
            for _ in ids:
                entities.append(arg + str(id_counter))
                id_counter += 1
        permutations = list(itertools.permutations(entities, len(ids)))
        combination_list.append(permutations)
    product = itertools.product(*combination_list)
    # Clean up product list
    combinations = [list(itertools.chain.from_iterable(x)) for x in product]
    return combinations, id_order

def create_conjunction(predicates):
    """
    Creates a PDDL conjunction format for all the provided predicates.

    Args:
        predicates (list[list[str]]): List of predicates separated into a list of arguments.
    
    Returns:
        conjunction (str): PDDL conjunction string.
    """
    conjunction = "       (and\n"
    for pred in predicates:
        conjunction += f"           ({' '.join(pred)})\n"
    conjunction += "       )\n"
    return conjunction

def build_goal(environment_dict):
    """
    Builds a PDDL goal string from an environment dictionary.

    This goal is constructed as a disjunction to allow for all possible
    combinations of items to satisfy a goal. For example, if a goal calls
    for a regular hamburger to be arranged on a table and there are two
    patties, the goal will accommodate for either patty being used.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, and player location.
    
    Returns:
        goal (str): PDDL goal string.
    """
    goal =  "   (or\n"
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
        goal += create_conjunction(unique_preds + filled_combination_preds)
    goal += "   )\n"
    return goal

def build_problem(environment_dict):
    """
    Builds a PDDL problem string from an environment dictionary.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, and player location.
    
    Returns:
        problem (str): PDDL problem string.
        new_environment_dict (dict): Dictionary containing IDed stations, items, and player location.
    """
    problem = "(define (problem robotouille)\n"
    problem += "(:domain robotouille)\n"
    problem += "(:objects\n"
    objects_str, new_environment_dict = build_objects(environment_dict)
    problem += objects_str
    problem += ")\n"
    problem += "(:init\n"
    problem += build_identity_predicates(new_environment_dict)
    problem += build_location_predicates(new_environment_dict)
    problem += build_stacking_predicates(new_environment_dict)
    problem += ")\n"
    problem += "(:goal\n"
    problem += build_goal(new_environment_dict)
    problem += ")\n"
    return problem, new_environment_dict

def write_problem_file(problem, filename):
    """
    Writes a PDDL problem string to a file.

    Args:
        problem (str): PDDL problem string.
        filename (str): Name of the PDDL problem file.
    """
    path = os.path.join(PROBLEM_DIR, filename)
    with open(path, "w") as f:
        f.write(problem)

def delete_problem_file(filename):
    """
    Deletes a PDDL problem file.

    Args:
        filename (str): Name of the PDDL problem file.
    """
    path = os.path.join(PROBLEM_DIR, filename)
    os.remove(path)

if __name__ == "__main__":
    # Prints PDDL problem string to terminal
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_filename", type=str, default="test_patties.json", help="JSON file to convert to PDDL")
    parser.add_argument("--seed", default=None, help="Seed for randomization")
    parser.add_argument("--noisy_randomization", help="Whether to use 'noisy randomization' for proceudral generation", default=True)
    args = parser.parse_args()

    environment_dict = load_environment(args.json_filename)

    # Since the environment JSON can have wildcard stations / items, we need to run the
    # procedural generation to choose some
    if args.seed is not None:
        environment_dict = randomize_environment(environment_dict, args.seed, noisy_randomization=args.noisy_randomization)
    problem, problem_dict = build_problem(environment_dict)
    print(problem)