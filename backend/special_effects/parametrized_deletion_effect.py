from backend.special_effect import SpecialEffect

class ParametrizedDeletionEffect(SpecialEffect):
    """
    This class represents a parametrized deletion effect.

    Parametrized deletion effects are special effects that delete objects from the
    state based on a parameter. A predicate is provided with an argument, and
    all objects that satisfy the predicate with the argument are deleted from the
    state.
    
    For example, when a customer eats their meal, an effect is that all the items
    on their plate should be deleted, but the number of items is ambiguous since
    different recipes have different numbers of items. So, we use this special 
    effect, with the parameter being the plate (let's call it plate1), and the 
    predicate being "at_container". Then, this special effect checks the predicates
    in the state, and for any true predicate at_container(x, plate1), it deletes x.    
    
    """

    def __init__(self, param, predicate, effects, special_effects, arg=None):
        """
        Initializes a parametrized deletion effect.

        Args:
            param (Object): The parameter of the deletion effect. 
            predicate (Predicate): The predicate that defines the condition for
                deletion.
            effects (Dictionary[Predicate, bool]): The effects of the action,
                represented by a dictionary of predicates and bools.
            special_effects (List[SpecialEffect]): The nested special effects of
                the action.
            arg (Object): The object that deleted. If the
                special effect is not applied to an object, arg is None.
        """
        super().__init__(param, effects, special_effects, False, arg)
        self.predicate = predicate

    def __eq__(self, other):
        """
        Checks if two parametrized deletion effects are equal.

        Args:
            other (ParametrizedDeletionEffect): The deletion effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.param == other.param and self.predicate == other.predicate \
            and self.effects == other.effects and self.special_effects == other.special_effects \
            and self.arg == other.arg
    
    def __hash__(self):
        """
        Returns the hash of the parametrized deletion effect.

        Returns:
            hash (int): The hash of the parametrized deletion effect.
        """
        return hash((self.param, self.predicate, tuple(self.effects), tuple(self.special_effects), 
                     self.completed, self.arg))
    
    def __repr__(self):
        """
        Returns the string representation of the parametrized deletion effect.

        Returns:
            string (str): The string representation of the parametrized deletion effect.
        """
        return f"ParametrizedDeletionEffect({self.param}, {self.predicate}, {self.completed}, {self.arg})"
    
    def apply_sfx_on_arg(self, arg, param_arg_dict):
        """
        Returns a copy of the special effect definition, but applied to an 
        argument.

        Args:
            arg (Object): The object to apply the special effect to.
            param_arg_dict (Dictionary[Object, Object]): A dictionary mapping 
                parameters to arguments. 

        Returns:
            ParametrizedDeletionEffect: The special effect with the argument applied.
        """
        new_effects = {}
        for effect, value in self.effects.items():
            new_effects[effect.replace_pred_params_with_args(param_arg_dict)] = value
        new_special_effects = []
        for special_effect in self.special_effects:
            new_special_effects.append(special_effect.apply_sfx_on_arg(arg, param_arg_dict))
        return ParametrizedDeletionEffect(self.param, self.predicate, new_effects, new_special_effects, arg)
    
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
        for predicate, value in state.predicates.items():
            if value and predicate.name == self.predicate.name and \
                self.arg in predicate.params:
                    for param in predicate.params:
                        if param != self.arg:
                            state.delete_object(param)

        for effect, value in self.effects.items():
            state.update_predicate(effect, value)

        for special_effect in self.special_effects:
            special_effect.update(state, active)
        
        self.completed = True