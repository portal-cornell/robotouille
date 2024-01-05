from pddlgym.backend import Predicate, State

class Action(object):
    """
    The action class is used to represent actions in robotouille.

    It has the following attributes:
    - name: the name of the action
    - precons: the preconditions of the action, represented as a list of
    predicates
    - immediate_effects: the immediate effects of the action, represented as a list of predicates
    - delayed_effects: the delayed effects of the action, represented by a tuple of (time, list of predicates)

    Special effect: create new object,

    """

    def __init__(self, name, precons, immediate_effects, delayed_effects):
        """
        Initializes an action object.

        Args:
            name (str): The name of the action.
            precons (list): The preconditions of the action, represented by a list
            of predicates.
            immediate_effects (list): The immediate effects of the action, represented by a list of predicates.
            delayed_effects (list): The delayed effects of the action, represented by a tuple of (time, list of predicates)
        """
        self.name = name
        self.precons = precons
        self.immediate_effects = immediate_effects
        self.delayed_effects = delayed_effects

    def perform_action(self, state):
        """
        Performs the action on the given state.

        This is used to generate the successor state of the current state, given
        that all preconditions of the action are satisfied.

        Args:
            state (State): The state to perform the action on.

        Returns:
            State: The successor state.
        """
        for precon in self.precons:
            if state.check_predicate(precon) == False:
                return state
            
        for effect in self.immediate_effects:
            state.add_predicate(effect)
            # state should have a function if a predicate is negated, it is removed automatically,or some way to handle removing predicates

        for del_effect in self.delayed_effects:
            if state.check_predicate(del_effect) == False:
                for effect in del_effect[1]:
                    new_predicate = Predicate(effect.name, effect.params, effect.types, effect.negation, 0)
                    state.add_predicate(new_predicate)

            state_predicate = state.find_predicate(del_effect)
            if state_predicate.time == del_effect[0]:
                for effect in del_effect[1]:
                    state.add_predicate(effect)
    
            else:
                new_predicate = Predicate(state_predicate.name, state_predicate.params, state_predicate.types, state_predicate.negation, state_predicate.time + 1)
                state.add_predicate(new_predicate)
                state.remove_predicate(state_predicate)

        return state


        
        
        


