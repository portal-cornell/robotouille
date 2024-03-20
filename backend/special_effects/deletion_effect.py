from backend.special_effect import SpecialEffect

class DeletionEffect(SpecialEffect):
    """
    This class represents deletion effects in Robotouille.

    A creation effect is an effect that delets an object in the state.
    """

    def __init__(self, param, arg=None):
        """
        Initializes a deletion effect.

        Args:
            param (Object): The parameter of the deletion effect. 
            arg (Object): The object that deleted. If the
                special effect is not applied to an object, arg is None.
        """
        super().__init__(param, {}, [], False, arg)
    
    def __eq__(self, other):
        """
        Checks if two deletion effects are equal.

        Args:
            other (DeletionEffect): The deletion effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.param == other.param and self.arg == other.arg
    
    def __hash__(self):
        """
        Returns the hash of the deletion effect.

        Returns:
            hash (int): The hash of the deletion effect.
        """
        return hash((self.param, self.completed, self.arg))
    
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
                parameters to arguments. Since the creation effect does not have
                any immediate effects, this dictionary is not used.

        Returns:
            DeletionEffect: A copy of the special effect definition, but applied
                to an argument.
        """
        return DeletionEffect(self.param, arg)
    
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
        state.remove_object(self.arg, active)
        self.completed = True