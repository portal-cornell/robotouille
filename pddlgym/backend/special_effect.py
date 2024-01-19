class SpecialEffect(object):
    """
    This class represents special effects in Robotouille.
    """

    def __init__(self, obj, effects, completed):
        """
        Initializes a special effect.

        Args:
            object (Object): The object that the effect is applied to.
            effects (list[Predicate]): The effects of the action, represented by
            a list of predicates.
            completed (bool): Whether or not the effect has been completed.
        """
        self.obj = obj
        self.effects = effects
        self.completed = completed

    def update(self, state, active=False):
        """
        Updates the state with the effect.

        Args:
            state (State): The state to update.
            active (bool): Whether or not the update is due to an action being
            performed.
        """
        raise NotImplementedError
        
class RepetitiveEffect(SpecialEffect):
    """
    This class represents repetitive effects in Robotouille.

    A repepitive effect is an effect that is only applied after am action has
    been performed a certain number of times.
    """
    
    def __init__(self, obj, effects, completed, goal_repetitions):
        """
        Initializes a repetitive effect.

        Args:
            object (Object): The object that the effect is applied to.
            effects (list[Predicate]): The effects of the action, represented by
            a list of predicates.
            completed (bool): Whether or not the effect has been completed.
            goal_repetitions (int): The number of times the action must be 
            performed before the effect is applied.
        """
        super().__init__(obj, effects, completed)
        self.goal_repetitions = goal_repetitions
        self.current_repetitions = 0

    def __eq__(self, other):
        """
        Checks if two repetitive effects are equal.

        Args:
            other (RepetitiveEffect): The repetitive effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.obj == other.obj and self.effects == other.effects \
            and self.completed == other.completed \
                and self.goal_repetitions == other.goal_repetitions 

    def increment_repetitions(self):
        """
        Increments the number of times the action has been performed.
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
        if not active: return
        self.increment_repetitions()
        if self.current_repetitions == self.goal_repetitions:
            for effect in self.effects:
                state.update_predicate(effect)
            self.completed = True

class DelayedEffect(SpecialEffect):
    """
    This class represents delayed effects in Robotouille.

    A delayed effect is an effect that is only applied after a certain amouny
    of time has passed.
    """

    def __init__(self, obj, effects, completed, goal_time):
        """
        Initializes a delayed effect.

        Args:
            object (Object): The object that the effect is applied to.
            effects (list[Predicate]): The effects of the action, represented by
            a list of predicates.
            completed (bool): Whether or not the effect has been completed.
            goal_time (int): The number of time steps that must pass before the
            effect is applied.
        """
        super().__init__(obj, effects, completed)
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
        return self.obj == other.obj and self.effects == other.effects \
            and self.completed == other.completed \
                and self.goal_time == other.goal_time
    
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
        if active: return
        self.increment_time()
        if self.current_time == self.goal_time:
            for effect in self.effects:
                state.update_predicate(effect)
            self.completed = True
            
class ConditionalEffect(SpecialEffect):

    pass

class CreationEffect(SpecialEffect):

    pass