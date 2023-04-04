import argparse
import json
from enum import Enum
import os
import copy

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "examples")
PROBLEM_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "overcooked")

class Item(Enum):
    BOTTOMBUN = "bottombun"
    COOKEDPATTY = "cookedpatty"
    CUTLETTUCE = "cutlettuce"
    LETTUCE = "lettuce"
    PATTY = "patty"
    TOPBUN = "topbun"

class Player(Enum):
    ROBOT = "robot"

class Station(Enum):
    BOARD = "board"
    STOVE = "stove"
    TABLE = "table"

ENTITY_FIELDS = ["stations", "items", "players"]

def str_to_typed_enum(str):
    """
    Attempts to convert a string into any of the typed enums.

    Args:
        str : str
            String to convert.
    
    Raises:
        ValueError: If the string cannot be converted into any of the typed enums.
    
    Returns:
        typed_enum: Enum
            Enum of the string.
    """
    for typed_enum in [Item, Player, Station]:
        try:
            return typed_enum(str)
        except ValueError:
            pass
    raise ValueError(f"Could not convert {str} into any of the typed enums.")
    
def load_environment(json_filename):
    """
    Loads an Overcooked environment from a JSON file in the examples folder.

    The JSON file should contain the initial stations, items, and player location.
    These will be sorted in the (x, y) order from left to right, bottom to top order.

    Args:
        json_filename : str
            Name of the JSON file in the examples folder
    
    Returns:
        environment: Dict
            JSON containing the initial stations, items, and player location.
    """
    # Get json file based on current file directory
    with open(os.path.join(EXAMPLES_DIR, json_filename), "r") as f:
        environment_json = json.load(f)
    sorting_key = lambda entity: (entity["x"], entity["y"])
    environment_json["stations"].sort(key=sorting_key)
    environment_json["items"].sort(key=sorting_key)
    environment_json["players"].sort(key=sorting_key)
    return environment_json

def build_objects(environment_dict):
    """
    Builds a PDDL objects string from an environment dictionary.

    Args:
        environment_dict : Dict
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        objects_str: str
            PDDL objects string.
        updated_environment_dict: List[str, Enum]
            The original environment dictionary with the names updated to include the IDs
            and the typed enums added.
    """
    objects_str = ""
    updated_environment_dict = copy.deepcopy(environment_dict)
    for field in ENTITY_FIELDS:
        object_type = field[:-1]
        seen = {}
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
        environment_dict : Dict
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        identity_predicates_str: str
            PDDL identity predicates string.
    """
    identity_predicates_str = ""
    for field in ENTITY_FIELDS:
        for entity in environment_dict[field]:
            typed_enum = entity['typed_enum']
            name = entity['name']
            identity_predicates_str += f"    (is{typed_enum.value} {name})\n"
            if typed_enum == Item.LETTUCE or typed_enum == Item.CUTLETTUCE:
                identity_predicates_str += f"    (iscuttable {name})\n"
            elif typed_enum == Item.PATTY or typed_enum == Item.COOKEDPATTY:
                identity_predicates_str += f"    (iscookable {name})\n"
    return identity_predicates_str

def build_station_location_predicates(environment_dict):
    """
    Builds PDDL station location predicates string from an environment dictionary.

    These include the (empty), (vacant), (loc) and (at) predicates.

    Args:
        environment_dict : Dict
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        predicates_str: str
            PDDL station location predicates string.
    """
    predicates_str = ""
    for station in environment_dict["stations"]:
        for field in ["items", "players"]:
            match = False
            no_match_predicate = "empty" if field == "items" else "vacant"
            predicate = "at" if field == "items" else "loc"
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
        environment_dict : Dict
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        predicates_str: str
            PDDL player location predicates string.
    """
    predicates_str = ""
    for player in environment_dict["players"]:
        match = False
        for item in environment_dict["items"]:
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
        environment_dict : Dict
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        location_predicates_str: str
            PDDL location predicates string.
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
        environment_dict : Dict
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        stacking_predicates_str: str
            PDDL stacking predicates string.
    """
    stacking_predicates_str = ""
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
        stacking_predicates_str += f"    (on {items[0]['name']} {station_name})\n"
        for i in range(1, len(items)):
            stacking_predicates_str += f"    (atop {items[i]['name']} {items[i-1]['name']})\n"
        stacking_predicates_str += f"    (clear {items[-1]['name']})\n"
    return stacking_predicates_str

def build_goal(environment_dict):
    """
    Builds a PDDL goal string from an environment dictionary.

    This goal is constructed as a disjunction to allow for all possible
    combinations of items to satisfy a goal. For example, if a goal calls
    for a regular hamburger to be arranged on a table and there are two
    patties, the goal will accommodate for either patty being used.

    Args:
        environment_dict : Dict
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        goal: str
            PDDL goal string.
    """
    # goal = "(or\n"
    # goal += ")\n"
    # TODO: Make this more general
    goal =  "   (and\n"
    goal += "       (iscut lettuce1)\n"
    goal += "       (atop topbun1 lettuce1)\n"
    goal += "       (iscooked patty1)\n"
    goal += "       (atop lettuce1 patty1)\n"
    goal += "       (atop patty1 bottombun1)\n"
    goal += "   )\n"
    return goal

def build_problem(environment_dict):
    """
    Builds a PDDL problem string from an environment dictionary.

    Args:
        environment_dict : Dict
            Dictionary containing the initial stations, items, and player location.
    
    Returns:
        problem: str
            PDDL problem string.
    """
    problem = "(define (problem overcooked)\n"
    problem += "(:domain overcooked)\n"
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
    return problem

def write_problem_file(problem, filename):
    """
    Writes a PDDL problem string to a file.

    Args:
        problem : str
            PDDL problem string.
        filename : str
            Name of the PDDL problem file.
    """
    path = os.path.join(PROBLEM_DIR, filename)
    with open(path, "w") as f:
        f.write(problem)

def delete_problem_file(filename):
    """
    Deletes a PDDL problem file.

    Args:
        filename : str
            Name of the PDDL problem file.
    """
    path = os.path.join(PROBLEM_DIR, filename)
    os.remove(path)

if __name__ == "__main__":
    # take in json name and create file in examples
    parser = argparse.ArgumentParser()
    parser.add_argument("json_filename", help="JSON file to convert to PDDL")
    args = parser.parse_args()

    json_filename = args.json_filename
    environment_dict = load_environment(json_filename)
    problem = build_problem(environment_dict)