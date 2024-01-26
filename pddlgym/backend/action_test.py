from predicate import Predicate
from object import Object
from domain import Domain
from state import State
from action import Action
from special_effect import SpecialEffect

is_lettuce_def = Predicate("is_lettuce", ["item"])
is_table_def = Predicate("is_table", ["station"])
is_cutting_board_def = Predicate("is_cutting_board", ["station"])
is_cut_def = Predicate("is_cut", ["item"])
is_cuttable_def = Predicate("is_cuttable", ["item"])
on_def = Predicate("on", ["station", "item"])
is_player_def = Predicate("is_player", ["player"])
loc_def = Predicate("loc", ["player", "station"])

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
                 Predicate("is_cuttable", ["item"], [i1]) : True,
                 Predicate("is_cutting_board", ["station"], [s1]) : True,
                 Predicate("on", ["station", "item"], [s1, i1]) : True,
                 Predicate("is_player", ["player"], [p1]) : True,
                 Predicate("loc", ["player", "station"], [p1, s1]) : True,
                 Predicate("is_cut", ["item"], [i1]) : False,
             },
             {
                 Predicate("is_cut", ["item"], [i1]) : True,
             },
             [])

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

domain = Domain("robotouille", ["item", "station", "player"], [is_lettuce_def, is_table_def, is_cutting_board_def, is_cut_def, is_cuttable_def, on_def, is_player_def, loc_def], [cut, move])

state = State(domain,
                [
                    lettuce1, table1, cutting_board1, player1
                ],
                {
                    Predicate("is_lettuce", ["item"], [lettuce1]),
                    Predicate("is_table", ["station"], [table1]),
                    Predicate("is_cuttable", ["item"], [lettuce1]),
                    Predicate("is_cutting_board", ["station"], [cutting_board1]),
                    Predicate("on", ["station", "item"], [cutting_board1, lettuce1]),
                    Predicate("is_player", ["player"], [player1]),
                    Predicate("loc", ["player", "station"], [player1, table1]),
                },
                [])

print("Beginning test\n")
print("Checking state initialization")
print("State predicates: {}".format(state.predicates))
print("Number of predicates: {}".format(len(state.predicates)))
print("\nValid actions: {}".format(state._build_valid_actions()))
print("\nPerforming move")
state.step(move)
assert state.check_predicate(Predicate("loc", ["player", "station"], [player1, cutting_board1]))
print("Move successful")
print("State predicates: {}".format(state.predicates))
print("\nValid actions: {}".format(state._build_valid_actions()))
print("\nPerforming cut")
state.step(cut)
assert state.check_predicate(Predicate("is_cut", ["item"], [lettuce1]))
print("Cut successful")
print("State predicates: {}".format(state.predicates))
print("\nValid actions: {}".format(state._build_valid_actions()))
print("\nPerforming move again")
state.step(move)
assert state.check_predicate(Predicate("loc", ["player", "station"], [player1, table1]))
print("Move successful")
print("State predicates: {}".format(state.predicates))