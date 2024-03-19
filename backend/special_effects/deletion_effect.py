from backend.special_effect import SpecialEffect

class DeletionEffect(SpecialEffect):
    """
    This class represents deletion effects in Robotouille.

    A creation effect is an effect that delets an object in the state.
    It can be immediate, or require a delay or repeated actions.
    """

    def __init__(self, param, completed, goal_time=4, goal_repetitions=0, arg=None):
        """
        Initializes a deletion effect.

        Args:
            param (Object): The parameter of the object to be deleted. 
            completed (bool): Whether or not the effect has been completed.
            goal_time (int): The number of time steps that must pass before the
                effect is applied.
            goal_repetitions (int): The number of times the effect must be
                repeated before it is applied.
            arg (Object): The object that the effect is applied to. If the
                special effect is not applied to an object, arg is None.

        Requires:
            goal_time == 0 if goal_repetitions > 0, 
            and goal_repetitions == 0 if goal_time > 0.
        """
        super().__init__(param, {}, completed, arg)
        self.goal_time = goal_time
        self.current_time = 0
        self.goal_repetitions = goal_repetitions
        self.current_repetitions = 0

    def __eq__(self, other):
        """
        Checks if two creation effects are equal.

        Args:
            other (CreationEffect): The creation effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.param == other.param and self.effects == other.effects \
            and self.goal_time == other.goal_time\
                and self.goal_repetitions == other.goal_repetitions and \
                    self.arg == other.arg
        
    def __hash__(self):
        """
        Returns the hash of the creation effect.

        Returns:
            hash (int): The hash of the creation effect.
        """
        return hash((self.param, tuple(self.effects), self.completed, 
                     self.goal_time, self.goal_repetitions, 
                     self.arg))
    
    def __repr__(self):
        """
        Returns the string representation of the creation effect.

        Returns:
            string (str): The string representation of the creation effect.
        """
        return f"CreationEffect({self.param}, {self.completed}, \
            {self.current_repetitions}, {self.current_time}, \
                {self.arg})"
    
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
        return DeletionEffect(param_arg_dict[self.param], self.effects, 
                              self.completed, self.goal_time, 
                              self.goal_repetitions, arg)
    
    def increment_time(self):
        """
        Increments the time of the effect.
        """
        self.current_time += 1

    def increment_repetitions(self):
        """
        Increments the number of repetitions of the effect.
        """
        self.current_repetitions += 1
    
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
        if self.goal_time > 0:
            if active: return
            self.increment_time()
            if self.current_time == self.goal_time:
                state.delete_obj(self.arg)
                self.completed = True
        elif self.goal_repetitions > 0:
            if not active: return
            self.increment_repetitions()
            if self.current_repetitions == self.goal_repetitions:
                state.delet_obj(self.arg)
                self.completed = True