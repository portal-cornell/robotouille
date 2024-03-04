# TODO: This file is temporary to hardcode the domain and problem for the robotouille environment.
# Values need to be extracted from domain json. 

from backend.predicate import Predicate
from backend.object import Object
from backend.domain import Domain
from backend.state import State
from backend.action import Action
from backend.special_effects.delayed_effect import DelayedEffect
from backend.special_effects.repetitive_effect import RepetitiveEffect
from backend.special_effects.conditional_effect import ConditionalEffect

p1 = Object("p1", "player")
s1 = Object("s1", "station")
s2 = Object("s2", "station")
i1 = Object("i1", "item")
i2 = Object("i2", "item")

move = Action(
            "move",
            {
                Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                Predicate().initialize("vacant", ["station"], [s2]) : True,
            },
            {
                Predicate().initialize("loc", ["player", "station"], [p1, s1]) : False,
                Predicate().initialize("loc", ["player", "station"], [p1, s2]) : True,
                Predicate().initialize("vacant", ["station"], [s1]) : True,
                Predicate().initialize("vacant", ["station"], [s2]) : False,
            },
            []
        )
pick_up = Action(
            "pick-up",
            {
                Predicate().initialize("nothing", ["player"], [p1]) : True,
                Predicate().initialize("on", ["item", "station"], [i1, s1]) : True,
                Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                Predicate().initialize("clear", ["item"], [i1]) : True,
            },
            {
                Predicate().initialize("has", ["player", "item"], [p1, i1]) : True,
                Predicate().initialize("empty", ["station"], [s1]) : True,
                Predicate().initialize("nothing", ["player"], [p1]) : False,
                Predicate().initialize("at", ["item", "station"], [i1, s1]) : False,
                Predicate().initialize("clear", ["item"], [i1]) : False,
                Predicate().initialize("on", ["item", "station"], [i1, s1]) : False,
            },
            []
        )
place = Action(
            "place",
            {
                Predicate().initialize("has", ["player", "item"], [p1, i1]) : True,
                Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                Predicate().initialize("empty", ["station"], [s1]) : True,
            },
            {
                Predicate().initialize("nothing", ["player"], [p1]) : True,
                Predicate().initialize("at", ["item", "station"], [i1, s1]) : True,
                Predicate().initialize("clear", ["item"], [i1]) : True,
                Predicate().initialize("on", ["item", "station"], [i1, s1]) : True,
                Predicate().initialize("has", ["player", "item"], [p1, i1]) : False,
                Predicate().initialize("empty", ["station"], [s1]) : False,
            },
            []
        )
cook =  Action(
            "cook",
            {
                Predicate().initialize("isstove", ["station"], [s1]) : True,
                Predicate().initialize("iscookable", ["item"], [i1]) : True,
                Predicate().initialize("on", ["item", "station"], [i1, s1]) : True,
                Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                Predicate().initialize("clear", ["item"], [i1]) : True,
            },
            {},
            [
                DelayedEffect(
                    i1,
                    {
                        Predicate().initialize("iscooked", ["item"], [i1]) : True,
                    },
                    False,
                    4
                )  
            ]
        )
cut = Action(
            "cut",
            {
                Predicate().initialize("isboard", ["station"], [s1]) : True,
                Predicate().initialize("iscuttable", ["item"], [i1]) : True,
                Predicate().initialize("on", ["item", "station"], [i1, s1]) : True,
                Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                Predicate().initialize("clear", ["item"], [i1]) : True,
            },
            {},
            [
                RepetitiveEffect(
                    i1,
                    {
                        Predicate().initialize("iscut", ["item"], [i1]) : True,
                    },
                    False,
                    3
                ),
                ConditionalEffect(
                    i1,
                    {
                        Predicate().initialize("isfryable", ["item"], [i1]) : True,
                    },
                    False,
                    {
                        Predicate().initialize("isfryableifcut", ["item"], [i1]) : True,
                    }
                )
            ]
        )
fry = Action(
            "fry",
            {
                Predicate().initialize("isfryer", ["station"], [s1]) : True,
                Predicate().initialize("isfryable", ["item"], [i1]) : True,
                Predicate().initialize("on", ["item", "station"], [i1, s1]) : True,
                Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                Predicate().initialize("clear", ["item"], [i1]) : True,
            },
            {},
            [
                DelayedEffect(
                    i1,
                    {
                        Predicate().initialize("isfried", ["item"], [i1]) : True,
                    },
                    False,
                    4
                )  
            ]
        )
stack = Action(
            "stack",
            {
                Predicate().initialize("has", ["player", "item"], [p1, i1]) : True,
                Predicate().initialize("clear", ["item"], [i2]) : True,
                Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                Predicate().initialize("at", ["item", "station"], [i2, s1]) : True,
            },
            {
                Predicate().initialize("nothing", ["player"], [p1]) : True,
                Predicate().initialize("at", ["item", "station"], [i1, s1]) : True,
                Predicate().initialize("atop", ["item", "item"], [i1, i2]) : True,
                Predicate().initialize("clear", ["item"], [i1]) : True,
                Predicate().initialize("clear", ["item"], [i2]) : False,
                Predicate().initialize("has", ["player", "item"], [p1, i1]) : False,
            },
            []
        )
unstack = Action(
            "unstack",
            {
                Predicate().initialize("nothing", ["player"], [p1]) : True,
                Predicate().initialize("clear", ["item"], [i1]) : True,
                Predicate().initialize("atop", ["item", "item"], [i1, i2]) : True,
                Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                Predicate().initialize("at", ["item", "station"], [i2, s1]) : True,
                Predicate().initialize("at", ["item", "station"], [i1, s1]) : True,
            },
            {
                Predicate().initialize("has", ["player", "item"], [p1, i1]) : True,
                Predicate().initialize("clear", ["item"], [i2]) : True,
                Predicate().initialize("nothing", ["player"], [p1]) : False,
                Predicate().initialize("atop", ["item", "item"], [i1, i2]) : False,
                Predicate().initialize("clear", ["item"], [i1]) : False,
                Predicate().initialize("at", ["item", "station"], [i1, s1]) : False,
            },
            []
        )
wait = Action(
            "wait",
            {},
            {},
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
        unstack,
        wait
    ]

PREDICATE_DEF = [
        Predicate().initialize("istable", ["station"]),
        Predicate().initialize("isstove", ["station"]),
        Predicate().initialize("isboard", ["station"]),
        Predicate().initialize("isfryer", ["station"]),
        Predicate().initialize("isrobot", ["player"]),
        Predicate().initialize("istopbun", ["item"]),
        Predicate().initialize("isbottombun", ["item"]),
        Predicate().initialize("isbread", ["item"]),
        Predicate().initialize("islettuce", ["item"]),
        Predicate().initialize("isonion", ["item"]),
        Predicate().initialize("istomato", ["item"]),
        Predicate().initialize("iscuttable", ["item"]),
        Predicate().initialize("iscut", ["item"]),
        Predicate().initialize("ispatty", ["item"]),
        Predicate().initialize("ischicken", ["item"]),
        Predicate().initialize("iscookable", ["item"]),
        Predicate().initialize("iscooked", ["item"]),
        Predicate().initialize("ischeese", ["item"]),
        Predicate().initialize("isfryable", ["item"]),
        Predicate().initialize("isfryableifcut", ["item"]),
        Predicate().initialize("isfried", ["item"]),
        Predicate().initialize("ispotato", ["item"]),
        Predicate().initialize("loc", ["player", "station"]),
        Predicate().initialize("at", ["item", "station"]),
        Predicate().initialize("nothing", ["player"]),
        Predicate().initialize("empty", ["station"]),
        Predicate().initialize("on", ["item", "station"]),
        Predicate().initialize("vacant", ["station"]),
        Predicate().initialize("clear", ["item"]),
        Predicate().initialize("atop", ["item", "item"]),
        Predicate().initialize("has", ["player", "item"]),
    ]

STATION_FIELD = "stations"
ITEM_FIELD = "items"
PLAYER_FIELD = "players"

ENTITY_FIELDS = [STATION_FIELD, ITEM_FIELD, PLAYER_FIELD]

OBJECT_TYPES = ["player", "item", "station"]