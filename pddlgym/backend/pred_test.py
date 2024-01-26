from predicate import Predicate
from object import Object
from domain import Domain
from state import State

is_patty_def = Predicate("is_patty", ["item"])
is_lettuce_def = Predicate("is_lettuce", ["item"])
is_onion_def = Predicate("is_onion", ["item"])
is_table_def = Predicate("is_table", ["station"])
on_def = Predicate("on", ["station", "item"])
atop_def = Predicate("atop", ["item", "item"])

patty1 = Object("patty1", "item")
patty2 = Object("patty2", "item")
lettuce1 = Object("lettuce1", "item")
lettuce2 = Object("lettuce2", "item")
onion1 = Object("onion1", "item")
onion2 = Object("onion2", "item")
table1 = Object("table1", "station")
table2 = Object("table2", "station")

domain = Domain("robotouille", ["item", "station"], [is_patty_def, is_lettuce_def, is_onion_def, is_table_def, on_def, atop_def], [])

state = State(domain, 
            [
                patty1, patty2, lettuce1, lettuce2, onion1, onion2, table1, table2
            ],
            {
                Predicate("is_patty", ["item"], [patty1]),
                Predicate("is_lettuce", ["item"], [lettuce1]),
                Predicate("is_onion", ["item"], [onion1]),
                Predicate("is_table", ["station"], [table1]),
                Predicate("is_patty", ["item"], [patty2]),
                Predicate("is_lettuce", ["item"], [lettuce2]),
                Predicate("is_onion", ["item"], [onion2]),
                Predicate("is_table", ["station"], [table2]),
                Predicate("on", ["station", "item"], [table1, patty1]),
                Predicate("on", ["station", "item"], [table2, lettuce1]),
                Predicate("atop", ["item", "item"], [patty1, lettuce1]),
            },
            [])


print(state.predicates)
print(len(state.predicates))

