from backend.special_effect import SpecialEffect

class DelayedEffect(SpecialEffect):
    """
    This class represents delayed effects in Robotouille.

    A delayed effect is an effect that is only applied after a certain amount
    of time has passed.
    """

    def __init__(self, param, effects, completed, goal_time=4, arg=None):
        """
        Initializes a delayed effect.

        Args:
            param (Object): The parameter of the special effect.
            effects (Dictionary[Predicate, bool]): The effects of the action,
            represented by a dictionary of predicates and bools.
            completed (bool): Whether or not the effect has been completed.
            goal_time (int): The number of time steps that must pass before the
            effect is applied.
            arg (Object): The object that the effect is applied to. If the
                special effect is not applied to an object, arg is None.
        """
        super().__init__(param, effects, completed, arg)
        self.goal_time = goal_time
        self.current_time = 0

    def __eq__(self, other):
        """
        Checks if two delayed effects are equal.

        Args:
            other (DelayedEffect): The delayed effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.param == other.param and self.effects == other.effects \
            and self.goal_time == other.goal_time\
                and self.arg == other.arg
    
    def __hash__(self):
        """
        Returns the hash of the delayed effect.

        Returns:
            hash (int): The hash of the delayed effect.
        """
        return hash((self.param, tuple(self.effects), self.completed, 
                     self.goal_time, self.arg))
    
    def __repr__(self):
        """
        Returns the string representation of the delayed effect.

        Returns:
            string (str): The string representation of the delayed effect.
        """
        return f"DelayedEffect({self.param}, {self.completed}, {self.current_time}, {self.arg})"
    
    def apply_sfx_on_arg(self, arg, param_arg_dict):
        """
        Returns a copy of the special effect definition, but applied to an 
        argument.

        Args:
            arg (Object): The argument that the special effect is applied to.
            param_arg_dict (Dictionary[Str, Object]): The dictionary mapping
                the parameters to the arguments.

        Returns:
            copy (SpecialEffect): The copy of the special effect definition,
                but applied to an argument.
        """
        new_effects = {}
        for effect, value in self.effects.items():
            new_effects[effect.replace_pred_params_with_args(param_arg_dict)] = value
        return DelayedEffect(self.param, new_effects, self.completed, self.goal_time, arg)

    def increment_time(self):
        """
        Increments the number of time steps that have passed.
        """
        self.current_time += 1

    def update(self, state, active=False):
        """
        Updates the state with the effect.

        Args:
            state (State): The state to update.
            active (bool): Whether or not the update is due to an action being
            performed.
        """
        if active or self.completed: return
        self.increment_time()
        if self.current_time == self.goal_time:
            for effect, value in self.effects.items():
                state.update_predicate(effect, value)
            self.completed = True