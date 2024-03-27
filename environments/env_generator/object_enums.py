from enum import Enum

class Item(Enum):
    BOTTOMBUN = "bottombun"
    LETTUCE = "lettuce"
    PATTY = "patty"
    TOPBUN = "topbun"
    BREAD = "bread"
    CHEESE = "cheese"
    TOMATO = "tomato"
    ONION = "onion"
    CHICKEN = "chicken"
    POTATO = "potato"

class Player(Enum):
    ROBOT = "robot"

class Station(Enum):
    BOARD = "board"
    STOVE = "stove"
    TABLE = "table"
    FRYER = "fryer"
    SINK = "sink"

class Container(Enum):
    POT = "pot"
    BOWL = "bowl"

class Meal(Enum):
    WATER = "water"
    BOILING_WATER = "boiling_water"
    SOUP = "soup"

TYPES = {"item": Item, "player": Player, "station": Station, "container": Container, "meal": Meal}

def str_to_typed_enum(s):
    """
    Attempts to convert a string into any of the typed enums.

    Args:
        s (str): String to convert.
    
    Raises:
        ValueError: If the string cannot be converted into any of the typed enums.
    
    Returns:
        typed_enum (Enum): Enum of the string.
    """
    for typed_enum in [Item, Player, Station, Container, Meal]:
        try:
            return typed_enum(s)
        except ValueError:
            pass
    raise ValueError(f"Could not convert {s} into any of the typed enums.")