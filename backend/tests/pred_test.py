"""
This file tests that the State class correctly initializes the predicates in the
state.

To run this test, run the following command from 'robotouille' directory:

$ python -m backend.tests.pred_test

The State class builds all the possible predicates by looking at all possible
combinations of objects and predicates in the domain.

The test asserts that the number of predicates in the state is correct, and that
the true predicates are correctly set to true in the state.
"""

from backend.predicate import Predicate
from backend.object import Object
from backend.domain import Domain
from backend.state import State

is_patty_def = Predicate().initialize("is_patty", ["item"])
is_lettuce_def = Predicate().initialize("is_lettuce", ["item"])
is_onion_def = Predicate().initialize("is_onion", ["item"])
is_table_def = Predicate().initialize("is_table", ["station"])
on_def = Predicate().initialize("on", ["station", "item"])
atop_def = Predicate().initialize("atop", ["item", "item"])

patty1 = Object("patty1", "item")
patty2 = Object("patty2", "item")
lettuce1 = Object("lettuce1", "item")
lettuce2 = Object("lettuce2", "item")
onion1 = Object("onion1", "item")
onion2 = Object("onion2", "item")
table1 = Object("table1", "station")
table2 = Object("table2", "station")

domain = Domain().initialize("robotouille", ["item", "station"], [is_patty_def, is_lettuce_def, is_onion_def, is_table_def, on_def, atop_def], [])

state = State().initialize(domain, 
            [
                patty1, patty2, lettuce1, lettuce2, onion1, onion2, table1, table2
            ],
            {
                Predicate().initialize("is_patty", ["item"], [patty1]),
                Predicate().initialize("is_lettuce", ["item"], [lettuce1]),
                Predicate().initialize("is_onion", ["item"], [onion1]),
                Predicate().initialize("is_table", ["station"], [table1]),
                Predicate().initialize("is_patty", ["item"], [patty2]),
                Predicate().initialize("is_lettuce", ["item"], [lettuce2]),
                Predicate().initialize("is_onion", ["item"], [onion2]),
                Predicate().initialize("is_table", ["station"], [table2]),
                Predicate().initialize("on", ["station", "item"], [table1, patty1]),
                Predicate().initialize("on", ["station", "item"], [table2, lettuce1]),
                Predicate().initialize("atop", ["item", "item"], [patty1, lettuce1]),
            },
            [])


print(state.predicates)
assert len(state.predicates) == 62
assert state.get_predicate_value(Predicate().initialize("is_patty", ["item"], [patty1]))
assert state.get_predicate_value(Predicate().initialize("is_lettuce", ["item"], [lettuce1]))
assert state.get_predicate_value(Predicate().initialize("is_onion", ["item"], [onion1]))
assert state.get_predicate_value(Predicate().initialize("is_table", ["station"], [table1]))
assert state.get_predicate_value(Predicate().initialize("is_patty", ["item"], [patty2]))
assert state.get_predicate_value(Predicate().initialize("is_lettuce", ["item"], [lettuce2]))
assert state.get_predicate_value(Predicate().initialize("is_onion", ["item"], [onion2]))
assert state.get_predicate_value(Predicate().initialize("is_table", ["station"], [table2]))
assert state.get_predicate_value(Predicate().initialize("on", ["station", "item"], [table1, patty1]))
assert state.get_predicate_value(Predicate().initialize("on", ["station", "item"], [table2, lettuce1]))
assert state.get_predicate_value(Predicate().initialize("atop", ["item", "item"], [patty1, lettuce1]))

