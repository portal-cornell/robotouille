from pddlgym.backend import Predicate, State

class Action(object):
    """
    The action class is used to represent actions in robotouille.

    Actions are created by the user in the domain file, and are created using
    this class for the game to use. 

    Each action has a list of precondition predicates, which if true, can be 
    performed on the current state.
    """

    def __init__(self, name, precons, immediate_effects, special_effects):
        """
        Initializes an action object.

        Args:
            name (str): The name of the action.
            precons (list[Predicate]): The preconditions of the action, 
            represented by a list of predicates.
            immediate_effects (list[Predicate]): The immediate effects of the 
            action, represented by a list of predicates.
            special_effects (list[SpecialEffect]): The delayed effects of the 
            action, represented by a list of SpecialEffect objects.
        """
        self.name = name
        self.precons = precons
        self.immediate_effects = immediate_effects
        self.special_effects = special_effects

    def check_if_valid(self, state):
        """
        Checks if the action is valid on the given state.

        Args:
            state (State): The state to check the action on.

        Returns:
            bool: True if the action is valid, False otherwise.
        """
        for precon in self.precons:
            if state.check_predicate(precon) == False:
                return False
        return True

    def perform_action(self, state):
        """
        Performs the action on the given state.

        This is used to generate the successor state of the current state, given
        that all preconditions of the action are satisfied.

        First, it asserts that the action is valid in the current state.
        If valid, the immediate effects are applied to the state, and the 
        special effects are added to the state.

        Args:
            state (State): The state to perform the action on.

        Returns:
            new_state (State): The successor state.
        """
        assert self.check_if_valid(state)
            
        for effect in self.immediate_effects:
            state.update_predicate(effect)

        state.add_special_effects(self.special_effects)

        return state


        
        
        


