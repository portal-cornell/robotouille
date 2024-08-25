from backend.special_effect import SpecialEffect

class MultiEffect(SpecialEffect):
    """
    This class represents a multi-effect in Robotouille.

    A predicate-based effect is an immediate effect that is applied to all 
    objects that satisfy a certain condition.

    For example, when picking up a container with an undetermined number of 
    objects, the condition predicate would be:
        - "item_at_container" predicate is true

    Then, all objects that are atop the container would be picked up, and their
    location would be updated. Then, the effect predicate would be:
        - "item_at" predicate is set to false
    """
    def __init__(self, param, filter_dict, effects, special_effects, arg=None):
        """
        Initializes a predicate-based effect.

        Args:
            param (Object): The parameter of the special effect.
            effects (Dictionary[Predicate, bool]): The effects of the action,
                represented by a dictionary of predicates and bools.
            special_effects (List[SpecialEffect]): The nested special effects of
                the action.
            conditions (Dictionary[Predicate, bool]): The conditions of the
                effect, represented by a dictionary of predicates and bools.
            arg (Object): The object that the effect is applied to. If the
                special effect is not applied to an object, arg is None.
        """
        super().__init__(param, effects, special_effects, False, arg)
        self.condition = conditions

    def __eq__(self, other):
        """
        Checks if two predicate-based effects are equal.

        Args:
            other (PredicateBasedEffect): The predicate-based effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.param == other.param and self.effects == other.effects \
            and self.special_effects == other.special_effects \
                and self.condition == other.condition and self.arg == other.arg
    
    def __hash__(self):
        """
        Returns the hash of the predicate-based effect.

        Returns:
            hash (int): The hash of the predicate-based effect.
        """
        return hash((self.param, tuple(self.effects), tuple(self.special_effects), 
                     tuple(self.condition), self.completed, self.arg))
    
    def __repr__(self):
        """
        Returns a string representation of the predicate-based effect.

        Returns:
            str: The string representation of the predicate-based effect.
        """
        return f"PredicateBasedEffect({self.param}, {self.effects}, {self.special_effects}, {self.condition}, {self.arg})"
    
    def apply_sfx_on_arg(self, arg, param_arg_dict, state):
        """
        Updates the predicate-based effect with an arg.

        Args:
            arg (Object): The object to apply the effect to.
            param_arg_dict (Dictionary[Object, Object]): A dictionary that maps
                parameters to arguments.
            state (State): The state of the game.
        """
        new_conditions = {}
        for condition, value in self.conditions.items():
            
        