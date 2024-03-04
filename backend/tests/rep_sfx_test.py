"""
This test is for the RepetitiveEffect class.

To run this test, run the following command from 'robotouille' directory:

$ python -m backend.tests.rep_sfx_test

An action, cut, is tested with a repetitive effect. The test asserts that the 
effects of the action are only applied after the action is performed the correct
number of times.
"""

from backend.predicate import Predicate
from backend.object import Object
from backend.domain import Domain
from backend.state import State
from backend.action import Action
from backend.special_effects.repetitive_effect import RepetitiveEffect

is_lettuce_def = Predicate().initialize("is_lettuce", ["item"])
is_table_def = Predicate().initialize("is_table", ["station"])
is_cutting_board_def = Predicate().initialize("is_cutting_board", ["station"])
is_cut_def = Predicate().initialize("is_cut", ["item"])
is_cuttable_def = Predicate().initialize("is_cuttable", ["item"])
on_def = Predicate().initialize("on", ["station", "item"])
is_player_def = Predicate().initialize("is_player", ["player"])
loc_def = Predicate().initialize("loc", ["player", "station"])

player1 = Object("player1", "player")
lettuce1 = Object("lettuce1", "item")
table1 = Object("table1", "station")
cutting_board1 = Object("cutting_board1", "station")

s1 = Object("s1", "station")
s2 = Object("s2", "station")
i1 = Object("i1", "item")
p1 = Object("p1", "player")

cut = Action("cut",
             {
                 Predicate().initialize("is_cuttable", ["item"], [i1]) : True,
                 Predicate().initialize("is_cutting_board", ["station"], [s1]) : True,
                 Predicate().initialize("on", ["station", "item"], [s1, i1]) : True,
                 Predicate().initialize("is_player", ["player"], [p1]) : True,
                 Predicate().initialize("loc", ["player", "station"], [p1, s1]) : True,
                 Predicate().initialize("is_cut", ["item"], [i1]) : False,
             },
             {},
             [
                 RepetitiveEffect(i1, {Predicate().initialize("is_cut", ["item"], [i1]) : True}, False, 3)
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

domain = Domain().initialize("robotouille", ["item", "station", "player"], [is_lettuce_def, is_table_def, is_cutting_board_def, is_cut_def, is_cuttable_def, on_def, is_player_def, loc_def], [cut, move])

state = State().initialize(domain,
                [
                    lettuce1, table1, cutting_board1, player1
                ],
                {
                    Predicate().initialize("is_lettuce", ["item"], [lettuce1]),
                    Predicate().initialize("is_table", ["station"], [table1]),
                    Predicate().initialize("is_cuttable", ["item"], [lettuce1]),
                    Predicate().initialize("is_cutting_board", ["station"], [cutting_board1]),
                    Predicate().initialize("on", ["station", "item"], [cutting_board1, lettuce1]),
                    Predicate().initialize("is_player", ["player"], [player1]),
                    Predicate().initialize("loc", ["player", "station"], [player1, table1]),
                },
                [
                    [Predicate().initialize("is_cut", ["item"], [lettuce1]),
                    Predicate().initialize("loc", ["player", "station"], [player1, table1]),]
                ])

print("Beginning test\n")
print("Checking state initialization")
print("State predicates: {}".format(state.predicates))
print("Number of predicates: {}".format(len(state.predicates)))
print("\nActions: {}".format(state._build_actions(domain, [lettuce1, table1, cutting_board1, player1])))
print("\nPerforming move")
state.step(move, {p1: player1, s1: table1, s2: cutting_board1})
assert state.get_predicate_value(Predicate().initialize("loc", ["player", "station"], [player1, cutting_board1]))
print("Move successful")
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
print("\nPerforming cut (1st time)")
state.step(cut, {p1: player1, s1: cutting_board1, i1: lettuce1})
assert not state.get_predicate_value(Predicate().initialize("is_cut", ["item"], [lettuce1]))
print("State special effects: {}".format(state.special_effects))
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
print("\nPerforming cut (2nd time)")
state.step(cut, {p1: player1, s1: cutting_board1, i1: lettuce1})
assert not state.get_predicate_value(Predicate().initialize("is_cut", ["item"], [lettuce1]))
print("State special effects: {}".format(state.special_effects))
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))
print("\nPerforming cut (3rd time)")
state.step(cut, {p1: player1, s1: cutting_board1, i1: lettuce1})
assert state.get_predicate_value(Predicate().initialize("is_cut", ["item"], [lettuce1]))
print("Cut successful")
print("State special effects: {}".format(state.special_effects))
print("\nState predicates: {}".format(state.predicates))
print("Valid actions: {}".format(state.get_valid_actions()))