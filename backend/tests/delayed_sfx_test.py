"""
This test is for the DelayedEffect class.

To run this test, run the following command from 'robotouille' directory:

$ python -m backend.tests.delayed_sfx_test

An action, fry, is tested with a delayed effect. The test asserts that after 
the action is performed, the delayed effect is applied to the object in the 
state, no matter the action being performed. 

It asserts that the effects of the action are only applied after the correct
number of steps have been taken.
"""

from backend.predicate import Predicate
from backend.object import Object
from backend.domain import Domain
from backend.state import State
from backend.action import Action
from backend.special_effects.delayed_effect import DelayedEffect

is_chicken_def = Predicate().initialize("is_chicken", ["item"])
is_table_def = Predicate().initialize("is_table", ["station"])
is_fryer_def = Predicate().initialize("is_fryer", ["station"])
is_fried_def = Predicate().initialize("is_fried", ["item"])
is_fryable_def = Predicate().initialize("is_fryable", ["item"])
on_def = Predicate().initialize("on", ["station", "item"])
is_player_def = Predicate().initialize("is_player", ["player"])
loc_def = Predicate().initialize("loc", ["player", "station"])

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
                    Predicate().initialize("is_fryable", ["item"], [i1]) : True,
                    Predicate().initialize("is_fryer", ["station"], [s1]) : True,
                    Predicate().initialize("on", ["station", "item"], [s1, i1]) : True,
                    Predicate().initialize("is_player", ["player"], [p1]) : True,
                    Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                    Predicate().initialize("is_fried", ["item"], [i1]) : False,
                },
                {},
                [
                    DelayedEffect(i1, {Predicate().initialize("is_fried", ["item"], [i1]) : True}, False, 3)
                ])

move = Action("move",
                {
                    Predicate().initialize("is_player", ["player"], [p1]) : True,
                    Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                },
                {
                    Predicate().initialize("loc", ["player", "station"], [p1, s1]) : False,
                    Predicate().initialize("loc", ["player", "station"], [p1, s2]) : True,
                },
                [])

domain = Domain().initialize("robotouille", ["item", "station", "player"], [is_chicken_def, is_table_def, is_fryer_def, is_fried_def, is_fryable_def, on_def, is_player_def, loc_def], [fry, move])

state = State().initialize(domain,
                [
                    chicken1, table1, fryer1, player1
                ],
                {
                    Predicate().initialize("is_chicken", ["item"], [chicken1]),
                    Predicate().initialize("is_fryable", ["item"], [chicken1]),
                    Predicate().initialize("is_table", ["station"], [table1]),
                    Predicate().initialize("is_fryer", ["station"], [fryer1]),
                    Predicate().initialize("is_player", ["player"], [player1]),
                    Predicate().initialize("loc", ["player", "station"], [player1, table1]),
                    Predicate().initialize("on", ["station", "item"], [fryer1, chicken1]),
                },
                [
                    [Predicate().initialize("is_fried", ["item"], [chicken1]),
                    Predicate().initialize("loc", ["player", "station"], [player1, table1]),]
                ])

print("Beginning test\n")
print("Checking state initialization")
print("State predicates: {}".format(state.predicates))
print("Number of predicates: {}".format(len(state.predicates)))
print("\nActions: {}".format(state._build_actions(domain, [chicken1, table1, fryer1, player1])))
print("\nPerforming move")
state.step(move, {p1: player1, s1: table1, s2: fryer1})
assert state.get_predicate_value(Predicate().initialize("loc", ["player", "station"], [player1, fryer1]))
print("Move successful")
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
print("\nPerforming fry (1st time)")
state.step(fry, {s1: fryer1, p1: player1, i1: chicken1})
assert not state.get_predicate_value(Predicate().initialize("is_fried", ["item"], [chicken1]))
print("State special effects: {}".format(state.special_effects))
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
print("\nPerforming fry (2nd time)")
state.step(move, {p1: player1, s1: fryer1, s2: table1})
assert not state.get_predicate_value(Predicate().initialize("is_fried", ["item"], [chicken1]))
print("State special effects: {}".format(state.special_effects))
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
print("\nPerforming fry (3rd time)")
state.step(move, {p1: player1, s1: table1, s2: fryer1})
assert state.get_predicate_value(Predicate().initialize("is_fried", ["item"], [chicken1]))
print("Fry successful")
print("State special effects: {}".format(state.special_effects))
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
