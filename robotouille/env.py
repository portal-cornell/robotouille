from typing import List, Optional, Union
from pddlgym.backend.action import Action
from pddlgym.backend.predicate import Predicate
from pddlgym.backend.object import Object
from pddlgym.backend.domain import Domain
from pddlgym.backend.state import State
from pddlgym.backend.special_effect import ConditionalEffect, DelayedEffect, RepetitiveEffect
from environments.env_generator.builder import entity_to_entity_field, create_unique_and_combination_preds, create_combinations
import copy

import gym
from gym import spaces
import pygame
import numpy as np

STATION_FIELD = "stations"
ITEM_FIELD = "items"
PLAYER_FIELD = "players"

ENTITY_FIELDS = [STATION_FIELD, ITEM_FIELD, PLAYER_FIELD]

p1 = Object("p1", "player")
s1 = Object("s1", "station")
s2 = Object("s2", "station")
i1 = Object("i1", "item")
i2 = Object("i2", "item")

move = Action(
            "move",
            {
                Predicate("loc", ["player", "station"], [p1, s1]) : True,
                Predicate("vacant", ["station"], [s2]) : True,
            },
            {
                Predicate("loc", ["player", "station"], [p1, s1]) : False,
                Predicate("loc", ["player", "station"], [p1, s2]) : True,
                Predicate("vacant", ["station"], [s1]) : True,
                Predicate("vacant", ["station"], [s2]) : False,
            },
            []
        )
pick_up = Action(
            "pick-up",
            {
                Predicate("nothing", ["player"], [p1]) : True,
                Predicate("on", ["item", "station"], [i1, s1]) : True,
                Predicate("loc", ["player", "station"], [p1, s1]) : True,
                Predicate("clear", ["item"], [i1]) : True,
            },
            {
                Predicate("has", ["player", "item"], [p1, i1]) : True,
                Predicate("empty", ["station"], [s1]) : True,
                Predicate("nothing", ["player"], [p1]) : False,
                Predicate("at", ["item", "station"], [i1, s1]) : False,
                Predicate("clear", ["item"], [i1]) : False,
                Predicate("on", ["item", "station"], [i1, s1]) : False,
            },
            []
        )
place = Action(
            "place",
            {
                Predicate("has", ["player", "item"], [p1, i1]) : True,
                Predicate("loc", ["player", "station"], [p1, s1]) : True,
                Predicate("empty", ["station"], [s1]) : True,
            },
            {
                Predicate("nothing", ["player"], [p1]) : True,
                Predicate("at", ["item", "station"], [i1, s1]) : True,
                Predicate("clear", ["item"], [i1]) : True,
                Predicate("on", ["item", "station"], [i1, s1]) : True,
                Predicate("has", ["player", "item"], [p1, i1]) : False,
                Predicate("empty", ["station"], [s1]) : False,
            },
            []
        )
cook =  Action(
            "cook",
            {
                Predicate("isstove", ["station"], [s1]) : True,
                Predicate("iscookable", ["item"], [i1]) : True,
                Predicate("on", ["item", "station"], [i1, s1]) : True,
                Predicate("loc", ["player", "station"], [p1, s1]) : True,
                Predicate("clear", ["item"], [i1]) : True,
            },
            {},
            [
                DelayedEffect(
                    i1,
                    {
                        Predicate("iscooked", ["item"], [i1]) : True,
                    },
                    False,
                    4
                )  
            ]
        )
cut = Action(
            "cut",
            {
                Predicate("isboard", ["station"], [s1]) : True,
                Predicate("iscuttable", ["item"], [i1]) : True,
                Predicate("on", ["item", "station"], [i1, s1]) : True,
                Predicate("loc", ["player", "station"], [p1, s1]) : True,
                Predicate("clear", ["item"], [i1]) : True,
            },
            {},
            [
                RepetitiveEffect(
                    i1,
                    {
                        Predicate("iscut", ["item"], [i1]) : True,
                    },
                    False,
                    3
                ),
                ConditionalEffect(
                    i1,
                    {
                        Predicate("isfryable", ["item"], [i1]) : True,
                    },
                    False,
                    {
                        Predicate("isfryableifcut", ["item"], [i1]) : True,
                    }
                )
            ]
        )
fry = Action(
            "fry",
            {
                Predicate("isfryer", ["station"], [s1]) : True,
                Predicate("isfryable", ["item"], [i1]) : True,
                Predicate("on", ["item", "station"], [i1, s1]) : True,
                Predicate("loc", ["player", "station"], [p1, s1]) : True,
                Predicate("clear", ["item"], [i1]) : True,
            },
            {},
            [
                DelayedEffect(
                    i1,
                    {
                        Predicate("isfried", ["item"], [i1]) : True,
                    },
                    False,
                    4
                )  
            ]
        )
stack = Action(
            "stack",
            {
                Predicate("has", ["player", "item"], [p1, i1]) : True,
                Predicate("clear", ["item"], [i2]) : True,
                Predicate("loc", ["player", "station"], [p1, s1]) : True,
                Predicate("at", ["item", "station"], [i2, s1]) : True,
            },
            {
                Predicate("nothing", ["player"], [p1]) : True,
                Predicate("at", ["item", "station"], [i1, s1]) : True,
                Predicate("atop", ["item", "item"], [i1, i2]) : True,
                Predicate("clear", ["item"], [i1]) : True,
                Predicate("clear", ["item"], [i2]) : False,
                Predicate("has", ["player", "item"], [p1, i1]) : False,
            },
            []
        )
unstack = Action(
            "unstack",
            {
                Predicate("nothing", ["player"], [p1]) : True,
                Predicate("clear", ["item"], [i1]) : True,
                Predicate("atop", ["item", "item"], [i1, i2]) : True,
                Predicate("loc", ["player", "station"], [p1, s1]) : True,
                Predicate("at", ["item", "station"], [i2, s1]) : True,
                Predicate("at", ["item", "station"], [i1, s1]) : True,
            },
            {
                Predicate("has", ["player", "item"], [p1, i1]) : True,
                Predicate("clear", ["item"], [i2]) : True,
                Predicate("nothing", ["player"], [p1]) : False,
                Predicate("atop", ["item", "item"], [i1, i2]) : False,
                Predicate("clear", ["item"], [i1]) : False,
                Predicate("at", ["item", "station"], [i1, s1]) : False,
            },
            []
        )

ACTIONS = [
        move,
        pick_up,
        place,
        cook,
        cut,
        fry,
        stack,
        unstack
    ]
    
def build_identity_predicates(environment_dict):
    """
    Builds identity predicates string from an environment dictionary.

    Note that if the typed enum is a cuttable/cookable item, then that identity 
    predicate will be added in this function.

    Args:
        environment_dict (dict): Dictionary containing the initial stations, items, 
            and player location.
    
    Returns:
        identity_predicates (List): Identity predicates list.
    """
    identity_predicates = []
    for field in ENTITY_FIELDS:
        for entity in environment_dict[field]:
            name = entity['name']
            obj = Object(name, field[:-1])
            identity_predicates.append(Predicate("is"+name[:-1], [field[:-1]], [obj]))
            for predicate in entity.get("predicates", []):
                identity_predicates.append(Predicate(predicate, [field[:-1]], [obj]))
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
                    predicates.append(Predicate(predicate, [field[:-1], "station"], [obj, station_obj]))
                    match = True
            if not match:
                predicates.append(Predicate(no_match_predicate, ["station"], [station_obj]))
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
                predicates.append(Predicate("has", ["player", "item"], [player_obj, obj]))
                match = True
                break
        if not match:
            predicates.append(Predicate("nothing", ["player"], [player_obj]))
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
    print(location_predicates)
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
        stacking_predicates.append(Predicate("on", ["item", "station"], [first_item_obj, station_obj]))
        for i in range(1, len(items)):
            obj = Object(items[i]["name"], "item")
            obj_below = Object(items[i-1]["name"], "item")
            stacking_predicates.append(Predicate("atop", ["item", "item"], [obj, obj_below]))
        last_obj = Object(items[-1]["name"], "item")
        stacking_predicates.append(Predicate("clear", ["item"], [last_obj]))
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
            arg_type = entity_to_entity_field(arg[:-1])[:-1]
            obj = Object(arg, arg_type)
            args.append(obj)
            types.append(arg_type)
        conjunction.append(Predicate(pred[0], types, args))
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

def build_state(environment_json):
    """
    This function is a temporary solution to building the state.

    Args:
        environment_json (dict): Dictionary containing the initial stations, items, and player location.

    Returns:
        domain (State): The state.
    """
    object_types = ["player", "item", "station"]
    predicate_def = [
        Predicate("istable", ["station"]),
        Predicate("isstove", ["station"]),
        Predicate("isboard", ["station"]),
        Predicate("isfryer", ["station"]),
        Predicate("isrobot", ["player"]),
        Predicate("istopbun", ["item"]),
        Predicate("isbottombun", ["item"]),
        Predicate("isbread", ["item"]),
        Predicate("islettuce", ["item"]),
        Predicate("isonion", ["item"]),
        Predicate("istomato", ["item"]),
        Predicate("iscuttable", ["item"]),
        Predicate("iscut", ["item"]),
        Predicate("ispatty", ["item"]),
        Predicate("ischicken", ["item"]),
        Predicate("iscookable", ["item"]),
        Predicate("iscooked", ["item"]),
        Predicate("ischeese", ["item"]),
        Predicate("isfryable", ["item"]),
        Predicate("isfryableifcut", ["item"]),
        Predicate("isfried", ["item"]),
        Predicate("ispotato", ["item"]),
        Predicate("loc", ["player", "station"]),
        Predicate("at", ["item", "station"]),
        Predicate("nothing", ["player"]),
        Predicate("empty", ["station"]),
        Predicate("on", ["item", "station"]),
        Predicate("vacant", ["station"]),
        Predicate("clear", ["item"]),
        Predicate("atop", ["item", "item"]),
        Predicate("has", ["player", "item"]),
    ]
    action_def = ACTIONS
    domain = Domain("robotouille", object_types, predicate_def, action_def)

    objects = []

    for field in ENTITY_FIELDS:
        for entity in environment_json[field]:
            objects.append(Object(entity["name"], field[:-1]))

    true_predicates = []
    true_predicates += build_identity_predicates(environment_json)
    true_predicates += build_location_predicates(environment_json)
    true_predicates += build_stacking_predicates(environment_json)
    goal = build_goal(environment_json)

    state = State(domain, objects, true_predicates, goal)

    print("predicates", state.predicates)

    return state

class RobotouilleEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, environment_json, render_fn, render_mode=None, size=5):        
        self.size = size
        self.window_size = 512

        initial_state = build_state(environment_json)

        self.initial_state = initial_state

        self.observation_space = initial_state

        self.action_space = ACTIONS

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

        

