from backend.special_effect import SpecialEffect

class DeletionEffect(SpecialEffect):
    """
    This class represents deletion effects in Robotouille.

    A creation effect is an effect that deletes an object in the state.
    """

    def __init__(self, param, effects, special_effects, arg=None):
        """
        Initializes a deletion effect.

        Args:
            param (Object): The parameter of the deletion effect. 
            effects (Dictionary[Predicate, bool]): The effects of the action,
                represented by a dictionary of predicates and bools.
            special_effects (List[SpecialEffect]): The nested special effects of
                the action.
            arg (Object): The object that deleted. If the
                special effect is not applied to an object, arg is None.
        """
        super().__init__(param, effects, special_effects, False, arg)
    
    def __eq__(self, other):
        """
        Checks if two deletion effects are equal.

        Args:
            other (DeletionEffect): The deletion effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.param == other.param and self.effects == other.effects \
            and self.special_effects == other.special_effects and self.arg == other.arg
    
    def __hash__(self):
        """
        Returns the hash of the deletion effect.

        Returns:
            hash (int): The hash of the deletion effect.
        """
        return hash((self.param, tuple(self.effects), tuple(self.special_effects), 
                     self.completed, self.arg))
    
    def __repr__(self):
        """
        Returns the string representation of the deletion effect.

        Returns:
            string (str): The string representation of the deletion effect.
        """
        return f"DeletionEffect({self.param}, {self.completed}, {self.arg})"
    
    def apply_sfx_on_arg(self, arg, param_arg_dict):
        """
        Returns a copy of the special effect definition, but applied to an 
        argument.

        Args:
            arg (Object): The object to apply the special effect to.
            param_arg_dict (Dictionary[Object, Object]): A dictionary mapping 
                parameters to arguments. 

        Returns:
            DeletionEffect: A copy of the special effect definition, but applied
                to an argument.
        """
        new_effects = {}
        for effect, value in self.effects.items():
            new_effects[effect.replace_pred_params_with_args(param_arg_dict)] = value
        new_special_effects = []
        for special_effect in self.special_effects:
            new_special_effects.append(special_effect.apply_sfx_on_arg(arg, param_arg_dict))
        deleted_obj = param_arg_dict[self.param.name]
        return DeletionEffect(self.param, new_effects, new_special_effects, deleted_obj)
    
    def update(self, state, active=False):
        """
        Updates the state with the effect.

        Args:
            state (State): The state to update.
            active (bool): Whether or not the update is due to an action being
            performed.
        """
        if self.completed:
            return
        state.delete_object(self.arg)
        for effect, value in self.effects.items():
            state.update_predicate(effect, value, active)
        for special_effect in self.special_effects:
            special_effect.update(state, active)
        self.completed = True