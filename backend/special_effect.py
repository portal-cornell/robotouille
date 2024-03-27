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

    def __init__(self, param, effects, special_effects, completed, arg):
        """
        Initializes a special effect.

        Args:
            param (Object): The parameter of the special effect.
            effects (Dictionary[Predicate, bool]): The effects of the action,
                represented by a dictionary of predicates and bools.
            special_effects (List[SpecialEffect]): The nested special effects of
                the action.
            completed (bool): Whether or not the effect has been completed.
            arg (Object): The object that the effect is applied to. If the
                special effect is not applied to an object, arg is None.
        """
        self.arg = arg
        self.param = param
        self.effects = effects
        self.special_effects = special_effects
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
