from predicate import Predicate

class Action(object):
    """
    The action class is used to represent actions in robotouille.

    Action definitions are given in the domain file. Each action has a name, 
    preconditions, immediate effects, and delayed effects.

    For an action to be performed, arguments must be given to the action, and
    applied to the appropriate preconditions, immediate effects, and special
    effects. The action is then performed on the state, and the successor state
    is returned.
    """

    def __init__(self, name, precons, immediate_effects, special_effects):
        """
        Initializes an action object.

        Args:
            name (str): The name of the action.
            precons (Dictionary[Predicate, bool]): The preconditions of the
                action, where the key is the predicate with placeholder
                parameters, and the value is a bool indicating whether the
                predicate is negated or not.
            immediate_effects (Dictionary[Predicate, bool]): The immediate
                effects of the action, where the key is the predicate with
                placeholder parameters, and the value is a bool indicating
                whether the predicate is negated or not.
            special_effects (List[SpecialEffect]): The special effects of the
                action.
        """
        self.name = name
        self.precons = precons
        self.immediate_effects = immediate_effects
        self.special_effects = special_effects

    def __eq__(self, other):
        """
        Checks if two actions are equal.

        Requires that all action names defined in the domain are unique.

        Args:
            other (Action): The action to compare to.

        Returns:
            bool: True if the actions are equal, False otherwise.
        """
        return self.name == other.name 
        
    def __hash__(self):
        """
        Returns the hash of the action.

        Returns:
            hash (int): The hash of the action.
        """
        return hash((self.name, tuple(self.precons), 
                     tuple(self.immediate_effects), tuple(self.special_effects)))
    
    def __str__(self):
        """
        Returns the string representation of the action.

        Returns:
            string (str): The string representation of the action.
        """
        return self.name
    
    def __repr__(self):
        """
        Returns the string representation of the action.

        Returns:
            string (str): The string representation of the action.
        """
        return self.name
    
    def get_all_params(self):
        """
        Returns all unique parameters of the action.

        Returns:
            params (List[Object]): The parameters of the action.
        """
        params = set()
        for precon in self.precons:
            params.update(precon.params)
        for effect in self.immediate_effects:
            params.update(effect.params)
        for special_effect in self.special_effects:
            params.update(special_effect.params)
        return list(params)
    
    def check_if_valid(self, state, args):
        """
        Checks if the action is valid in the given state.

        Args:
            state (State): The state to check.
            args (Dictionary[str, Object]): The arguments of the action.

        Returns:
            bool: True if the action is valid, False otherwise.
        """
        # Check if all arguments are present
        for value in args.values():
            if value is None:
                return False
            
        params = self.get_all_params()
        # Check if all arguments are valid
        for param in params:
            if param not in args:
                return False
            
        # Check if all preconditions are satisfied
        for precon, value in self.precons.items():
            pred = Predicate(precon.name, precon.types, [args[param] for param in precon.params])
            if not state.check_predicate(pred, value):
                return False
        return True

    def perform_action(self, state, args):
        """
        Performs the action on the given state.

        This is used to generate the successor state of the current state, given
        that all preconditions of the action are satisfied.

        First, it asserts that the action is valid in the current state.
        If valid, the immediate effects are applied to the state, and the 
        special effects are added to the state.

        Args:
            state (State): The state to perform the action on.
            args (Dictionary[str, Object]): The arguments of the action.

        Returns:
            new_state (State): The successor state.
        """
        assert self.check_if_valid(state, args)
            
        for effect, value in self.immediate_effects.items():
            pred = Predicate(effect.name, effect.types, [args[param] for param in effect.params])
            state.update_predicate(pred, value)

        for special_effect in self.special_effects:
            state.update_special_effect(special_effect)

        return state


        
        
        


