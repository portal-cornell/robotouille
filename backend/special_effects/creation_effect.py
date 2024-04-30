from backend.special_effect import SpecialEffect
from backend.object import Object

class CreationEffect(SpecialEffect):
    """
    This class represents creation effects in Robotouille.

    A creation effect is an effect that creates a new object in the state.
    """

    def __init__(self, param, created_obj, effects, special_effects, arg=None):
        """
        Initializes a creation effect.

        Args:
            param (Object): The parameter of the creation effect. This is the 
                object that the action is performed on, not the object that is
                created.
            created_obj (Tuple[Str, Object]): A tuple representing the object
                that is created. The first element is the param name of the 
                object, and the second element is the object itself.
            effects (Dictionary[Predicate, bool]): The effects of the action,
                represented by a dictionary of predicates and bools.
            special_effects (List[SpecialEffect]): The nested special effects of
                the action.
            arg (Object): The object that the effect is applied to. If the
                special effect is not applied to an object, arg is None.
        """
        super().__init__(param, effects, special_effects, False, arg)
        self.created_obj = created_obj

    def __eq__(self, other):
        """
        Checks if two creation effects are equal.

        Args:
            other (CreationEffect): The creation effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.param == other.param and \
            self.effects == other.effects and \
                self.special_effects == other.special_effects and \
            self.created_obj == other.created_obj and \
                self.arg == other.arg
        
    def __hash__(self):
        """
        Returns the hash of the creation effect.

        Returns:
            hash (int): The hash of the creation effect.
        """
        return hash((self.param, tuple(self.effects), tuple(self.special_effects),
                        self.completed, self.created_obj, self.arg))
    
    def __repr__(self):
        """
        Returns the string representation of the creation effect.

        Returns:
            string (str): The string representation of the creation effect.
        """
        return f"CreationEffect({self.param}, {self.completed}, {self.created_obj}, {self.arg})"
    
    def apply_sfx_on_arg(self, arg, param_arg_dict):
        """
        Returns a copy of the special effect definition, but applied to an 
        argument.

        Args:
            arg (Object): The argument that the special effect is applied to.
            param_arg_dict (Dictionary[Object, Object]): A dictionary mapping 
                parameters to arguments.

        Returns:
            CreationEffect: A copy of the special effect definition, but applied
                to an argument.
        """
        param_arg_dict[self.created_obj[0]] = self.created_obj[1]
        new_effects = {}
        for effect, value in self.effects.items():
            new_effects[effect.replace_pred_params_with_args(param_arg_dict)] = value
        new_special_effects = []
        for special_effect in self.special_effects:
            new_special_effects.append(special_effect.apply_sfx_on_arg(arg, param_arg_dict))
        return CreationEffect(self.param, self.created_obj, new_effects, new_special_effects, arg)
    
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
        new_obj = state.add_object(self.created_obj[1])
        for effect, value in self.effects.items():
            for param in effect.params:
                if param == self.created_obj[1]:
                    param.name = new_obj.name
            state.update_predicate(effect, value)
        for special_effect in self.special_effects:
            special_effect.update(state, active)
        if all([special_effect.completed for special_effect in self.special_effects]):
            self.completed = True