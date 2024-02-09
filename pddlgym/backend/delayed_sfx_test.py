from predicate import Predicate
from object import Object
from domain import Domain
from state import State
from action import Action
from special_effect import SpecialEffect, DelayedEffect

is_chicken_def = Predicate("is_chicken", ["item"])
is_table_def = Predicate("is_table", ["station"])
is_fryer_def = Predicate("is_fryer", ["station"])
is_fried_def = Predicate("is_fried", ["item"])
is_fryable_def = Predicate("is_fryable", ["item"])
on_def = Predicate("on", ["station", "item"])
is_player_def = Predicate("is_player", ["player"])
loc_def = Predicate("loc", ["player", "station"])

player1 = Object("player1", "player")
chicken1 = Object("chicken1", "item")
table1 = Object("table1", "station")
fryer1 = Object("fryer1", "station")

s1 = Object("s1", "station")
s2 = Object("s2", "station")
i1 = Object("i1", "item")
p1 = Object("p1", "player")

fry = Action("fry",
                {
                    Predicate("is_fryable", ["item"], [i1]) : True,
                    Predicate("is_fryer", ["station"], [s1]) : True,
                    Predicate("on", ["station", "item"], [s1, i1]) : True,
                    Predicate("is_player", ["player"], [p1]) : True,
                    Predicate("loc", ["player", "station"], [p1, s1]) : True,
                    Predicate("is_fried", ["item"], [i1]) : False,
                },
                {},
                [
                    DelayedEffect(i1, {Predicate("is_fried", ["item"], [i1]) : True}, False, 2)
                ])

move = Action("move",
                {
                    Predicate("is_player", ["player"], [p1]) : True,
                    Predicate("loc", ["player", "station"], [p1, s1]) : True,
                },
                {
                    Predicate("loc", ["player", "station"], [p1, s1]) : False,
                    Predicate("loc", ["player", "station"], [p1, s2]) : True,
                },
                [])

domain = Domain("robotouille", ["item", "station", "player"], [is_chicken_def, is_table_def, is_fryer_def, is_fried_def, is_fryable_def, on_def, is_player_def, loc_def], [fry, move])

state = State(domain,
                [
                    chicken1, table1, fryer1, player1
                ],
                {
                    Predicate("is_chicken", ["item"], [chicken1]),
                    Predicate("is_fryable", ["item"], [chicken1]),
                    Predicate("is_table", ["station"], [table1]),
                    Predicate("is_fryer", ["station"], [fryer1]),
                    Predicate("is_player", ["player"], [player1]),
                    Predicate("loc", ["player", "station"], [player1, table1]),
                    Predicate("on", ["station", "item"], [fryer1, chicken1]),
                },
                [
                    Predicate("is_fried", ["item"], [chicken1]),
                    Predicate("loc", ["player", "station"], [player1, table1]),
                ])

print("Beginning test\n")
print("Checking state initialization")
print("State predicates: {}".format(state.predicates))
print("Number of predicates: {}".format(len(state.predicates)))
print("\nActions: {}".format(state._build_actions()))
print("\nPerforming move")
state.step(move, {p1: player1, s1: table1, s2: fryer1})
assert state.check_predicate(Predicate("loc", ["player", "station"], [player1, fryer1]))
print("Move successful")
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
print("\nPerforming fry (1st time)")
state.step(fry, {s1: fryer1, p1: player1, i1: chicken1})
print("State special effects: {}".format(state.special_effects))
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
print("\nPerforming fry (2nd time)")
state.step(move, {p1: player1, s1: fryer1, s2: table1})
print("State special effects: {}".format(state.special_effects))
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
print("\nPerforming fry (3rd time)")
state.step(move, {p1: player1, s1: table1, s2: fryer1})
assert state.check_predicate(Predicate("is_fried", ["item"], [chicken1]))
print("fry successful")
print("State special effects: {}".format(state.special_effects))
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
