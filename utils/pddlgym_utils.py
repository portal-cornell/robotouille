import pddlgym
import utils.pddlgym_interface as pddlgym_interface
import itertools
import re
import numpy as np


# TODO: Extract these from the domain file to make it more general
PREDICATE_STRINGS = [
    # Identity Predicates
    "istable(?:station)",
    "isstove(?:station)",
    "isboard(?:station)",
    "isbun(?:item)",
    "islettuce(?:item)",
    "iscuttable(?:item)",
    "iscut(?:item)",
    "ispatty(?:item)",
    "iscookable(?:item)",
    "iscooked(?:item)",
    # State Predicates
    "loc(?:player,?:station)",
    "at(?:item,?:station)",
    "nothing(?:player)",
    "empty(?:station)",
    "on(?:item,?:station)",
    "vacant(?:station)",
    "clear(?:item)",
    "atop(?:item,?:item)",
    "has(?:player,?:item)",
]

def expand_state(partial_state, objects, literals_to_string = False):
    """
    Expands the state provided by PDDLGym to include all possible literals.

    PDDLGym provides us with the current literals that are true. This function
    returns all the possible literals including those that are false.
    
    Args:
        partial_state (frozenset[Literal]): List of true literals provided by PDDLGym
        objects (frozenset[TypedEntity]): List of objects provided by PDDLGym
        literals_to_string (bool): Whether to convert the literals to strings
    
    Returns:
        expanded_truths (np.array): Array of 0s and 1s where 1 indicates the literal is true
        expanded_state (np.array or None): Array of literals corresponding to the expanded truths.
    """
    # Group objects
    objs = {}
    for obj in objects:
        objs[obj.var_type] = objs.get(obj.var_type, []) + [obj.name]
    
    # Create all possible literals
    expanded_state = []
    for predicate_string in PREDICATE_STRINGS:
        type_names = re.findall(r":([a-z]+)", predicate_string)
        types = [pddlgym.structs.Type(arg) for arg in type_names]
        combination_list = [objs.get(arg) for arg in type_names]
        if None in combination_list:
            # This predicate is not applicable to this state
            continue
        for args in itertools.product(*[objs[arg] for arg in type_names]):
            predicate_name = re.findall(r"([a-z]+)", predicate_string)[0]
            predicate = pddlgym.structs.Predicate(predicate_name, len(args), types)
            expanded_state.append(pddlgym.structs.Literal(predicate, list(args)))
            expanded_state[-1] = str(expanded_state[-1]) if literals_to_string else expanded_state[-1]

    # Create expanded truths
    expanded_truths = np.zeros(len(expanded_state))
    for i, literal in enumerate(expanded_state):
        if literal in partial_state:
            expanded_truths[i] = 1

    return expanded_truths, expanded_state

def create_toggle_array(expanded_truths, expanded_state, partial_state, literals_to_string = False):
    """
    Creates an array that represents the predicates that changed.

    The partial_state provided by PDDLGym only includes the predicates that
    are true. If we want to know which predicates changed from time step t to
    time step t+1, we need to compare the expanded_state to the partial_state.

    If the literal in the expanded_state is True but not found in the partial_state,
    then the literal changed from True to False from time step t to time step t+1. If
    the literal in the expanded_state is False but found in the partial_state, then
    the literal changed from False to True from time step t to time step t+1.

    Note that to determine the truthy value of the literal, we need the expanded_truths 
    array which is aligned with the expanded_state array.

    Args:
        expanded_truths (np.array): Array of 0s and 1s where 1 indicates the literal is true from time step t.
        expanded_state (np.array): Array of literals corresponding to the expanded truths from time step t.
        partial_state (frozenset[Literal]): List of true literals provided by PDDLGym from time step t+1.
        literals_to_string (bool): Whether to convert the literals to strings
    
    Returns:
        toggle_array (np.array): Array of 0s and 1s where 1 indicates the literal changed from time step t to t+1.
    """
    toggle_array = np.zeros(len(expanded_state))
    for i, old_literal in enumerate(expanded_state):
        old_literal = str(old_literal) if literals_to_string else old_literal
        found = False
        for new_literal in partial_state:
            new_literal = str(new_literal) if literals_to_string else new_literal
            if old_literal == new_literal:
                found = True
                break
        if expanded_truths[i] == 1 and not found or expanded_truths[i] == 0 and found:
            toggle_array[i] = 1
    return toggle_array

def str_to_literal(literal_str):
    """
    Wrapper for pddlgym_interface.str_to_literal which converts a string to a PDDLGym Literal type.

    Args:
        literal_str (str): String representation of a literal.
    
    Returns:
        predicate : str
            Predicate name
        args : list of str
            List of arguments
        types : list of Type strings
            List of argument types
    """
    return pddlgym_interface.str_to_literal(literal_str)