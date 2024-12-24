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
    HOTDOG = "hotdog"
    BUN = "bun"
    SALMON = "salmon"
    TURKEY = "turkey"
    SHRIMP = "shrimp"
    CROISSANT = "croissant"
    ROLLINGPIN = "rollingpin"
    EGG = "egg"
    BUTTER = "butter"
    PANCAKE = "pancake"
    CUPCAKE = "cupcake"
    DUMPLINGDOUGH = "dumplingdough"
    COOKEDDUMPLING = "cookeddumpling"
    GROUNDMEAT = "groundmeat"
    MEATBALLS = "meatballs"
    SPAGHETTI = "spaghetti"
    PORKBELLY = "porkbelly"
    NOODLES = "noodles"

class Player(Enum):
    ROBOT = "robot"

class Station(Enum):
    BOARD = "board"
    STOVE = "stove"
    OVEN = "oven"
    TABLE = "table"
    FRYER = "fryer"
    SINK = "sink"
    COUNTER = "counter"
    BLENDER = "blender"
    GRILL = "grill"
    BATTER_STATION = "batter_station"
    GRINDER = "grinder"

class Container(Enum):
    POT = "pot"
    BOWL = "bowl"
    BLENDERCUP = "blendercup"
    FRYINGPAN = "fryingpan"
    EGGCARTON = "eggcarton"
    CUPCAKETRAY = "cupcaketray"

class Meal(Enum):
    WATER = "water"
    BOILING_WATER = "boiling_water"
    SOUP = "soup"
    PANCAKEBATTER = "pancakebatter"
    CUPCAKEBATTER = "cupcakebatter"
    DUMPLING = "dumpling"
    SPAGHETTIWITHMEATBALLS = "spaghettiwithmeatballs"
    RAMEN = "ramen"

class Package(Enum):
    KETCHUP = "ketchupbottle"
    MUSTARD = "mustardbottle"
    SALT = "salt"
    MILKCARTON = "milkcarton"
    FLOURBAG = "flourbag"
    FROSTINGBAG = "frostingbag"
    CHICKENSTOCK = "chickenstock"

TYPES = {"item": Item, "player": Player, "station": Station, "container": Container, "meal": Meal, "package": Package}

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
    for typed_enum in [Item, Player, Station, Container, Meal, Package]:
        try:
            return typed_enum(s)
        except ValueError:
            pass
    raise ValueError(f"Could not convert {s} into any of the typed enums.")