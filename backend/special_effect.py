class SpecialEffect(object):
    """
    This class represents special effects in Robotouille.

    Some effects are not easily represented by immediate effects. For example,
    some effects may need repeated actions to be performed, or may only kick in
    after a certain amount of time has passed, or may create new predicates or 
    objects not already present in the state. These effects are represented by
    this class.

    The SpecialEffect class should not be directly instantiated, but rather 
    should be inherited by one of its subclasses. 
    """

    def __init__(self, obj, effects, completed):
        """
        Initializes a special effect.

        Args:
            obj (Object): The object that the effect is applied to.
            effects (Dictionary[Predicate, bool]): The effects of the action,
            represented by a dictionary of predicates and bools.
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

        Raises:
            NotImplementedError: If the method is not implemented in the 
            subclass.
        """
        raise NotImplementedError
        
class RepetitiveEffect(SpecialEffect):
    """
    This class represents repetitive effects in Robotouille.

    A repetitive effect is an effect that is only applied after an action has
    been performed a certain number of times.
    """
    
    def __init__(self, obj, effects, completed, goal_repetitions):
        """
        Initializes a repetitive effect.

        Args:
            obj (Object): The object that the effect is applied to.
            effects (Dictionary[Predicate, bool]): The effects of the action,
            represented by a dictionary of predicates and bools.
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
    
    def __hash__(self):
        """
        Returns the hash of the repetitive effect.

        Returns:
            hash (int): The hash of the repetitive effect.
        """
        return hash((self.obj, tuple(self.effects), self.completed, 
                     self.goal_repetitions))
    
    def __repr__(self):
        """
        Returns the string representation of the repetitive effect.

        Returns:
            string (str): The string representation of the repetitive effect.
        """
        return f"RepetitiveEffect({self.obj}, {self.completed}, {self.current_repetitions})"
    
    def replace_params_with_args(self, obj, args):
        """
        Returns a copy of the repetitive effect, replacing the parameter object
        with the argument object.

        Args:
            obj (Object): The object to replace the object in the effect with.
            args (Dictionary[Object, Object]): The dictionary of objects to
                replace for the effects. 

        Returns:
            copy (RepetitiveEffect): The copy of the repetitive effect.
        """
        new_effects = {}
        for effect, value in self.effects.items():
            new_effects[effect.replace_params_with_args(args)] = value
        return RepetitiveEffect(obj, new_effects, self.completed, 
                                self.goal_repetitions)
        

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
            for effect, value in self.effects.items():
                state.update_predicate(effect, value)
            self.completed = True

class DelayedEffect(SpecialEffect):
    """
    This class represents delayed effects in Robotouille.

    A delayed effect is an effect that is only applied after a certain amount
    of time has passed.
    """

    def __init__(self, obj, effects, completed, goal_time):
        """
        Initializes a delayed effect.

        Args:
            obj (Object): The object that the effect is applied to.
            effects (Dictionary[Predicate, bool]): The effects of the action,
            represented by a dictionary of predicates and bools.
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
    
    def __hash__(self):
        """
        Returns the hash of the delayed effect.

        Returns:
            hash (int): The hash of the delayed effect.
        """
        return hash((self.obj, tuple(self.effects), self.completed, 
                     self.goal_time))
    
    def __repr__(self):
        """
        Returns the string representation of the delayed effect.

        Returns:
            string (str): The string representation of the delayed effect.
        """
        return f"DelayedEffect({self.obj}, {self.completed}, {self.current_time})"
    
    def replace_params_with_args(self, obj, args):
        """
        Returns a copy of the delayed effect, replacing the parameter object
        with the argument object.

        Args:
            obj (Object): The object to replace the object in the effect with.
            args (Dictionary[Object, Object]): The dictionary of objects to
                replace for the effects. 

        Returns:
            copy (DelayedEffect): The copy of the delayed effect.
        """
        new_effects = {}
        for effect, value in self.effects.items():
            new_effects[effect.replace_params_with_args(args)] = value
        return DelayedEffect(obj, new_effects, self.completed, self.goal_time)
    
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
            for effect, value in self.effects.items():
                state.update_predicate(effect, value)
            self.completed = True
            
class ConditionalEffect(SpecialEffect):
    """
    This class represents a conditional effect in Robotouille.

    A conditional effect is an immediate effect that is only applied if a 
    certain condition is met.

    For example, some food items can only be fried if they are cut. 
    Then, the condition predicate would be:
        - "isfryableifcut"
    And the effect predicate would be:
        - "isfryable"

    """
    def __init__(self, obj, effects, completed, conditions):
        """
        Initializes a conditional effect.

        Args:
            obj (Object): The object that the effect is applied to.
            effects (Dictionary[Predicate, bool]): The effects of the action,
            represented by a dictionary of predicates and bools.
            completed (bool): Whether or not the effect has been completed.
            conditions (Dictionary[Predicate, bool]): The conditions of the
            effect, represented by a dictionary of predicates and bools.
        """
        super().__init__(obj, effects, completed)
        self.condition = conditions

    def __eq__(self, other):
        """
        Checks if two conditional effects are equal.

        Args:
            other (ConditionalEffect): The conditional effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.obj == other.obj and self.effects == other.effects \
            and self.completed == other.completed \
                and self.condition == other.condition
    
    def __hash__(self):
        """
        Returns the hash of the conditional effect.

        Returns:
            hash (int): The hash of the conditional effect.
        """
        return hash((self.obj, tuple(self.effects), self.completed, 
                     tuple(self.condition)))
    
    def __repr__(self):
        """
        Returns the string representation of the conditional effect.

        Returns:
            string (str): The string representation of the conditional effect.
        """
        return "ConditionalEffect({}, {}, {})".format(self.obj, self.completed, self.condition)
    
    def replace_params_with_args(self, obj, args):
        """
        Returns a copy of the conditional effect, replacing the parameter object
        with the argument object.

        Args:
            obj (Object): The object to replace the object in the effect with.
            args (Dictionary[Object, Object]): The dictionary of objects to
                replace for the effects. 

        Returns:
            copy (ConditionalEffect): The copy of the conditional effect.
        """
        new_effects = {}
        for effect, value in self.effects.items():
            new_effects[effect.replace_params_with_args(args)] = value
        new_conditions = {}
        for condition, value in self.condition.items():
            new_conditions[condition.replace_params_with_args(args)] = value
        return ConditionalEffect(obj, new_effects, self.completed, new_conditions)
    
    def update(self, state, active=False):
        """
        Updates the state with the effect.

        Args:
            state (State): The state to update.
            active (bool): Whether or not the update is due to an action being
            performed.
        """
        if active: return
        for condition, value in self.condition.items():
            if state.predicates[condition] != value:
                return
        for effect, value in self.effects.items():
            state.update_predicate(effect, value)
        self.completed = True

class CreationEffect(SpecialEffect):

    pass