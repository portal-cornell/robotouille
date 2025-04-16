from backend.special_effect import SpecialEffect

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
    def __init__(self, param, effects, special_effects, conditions, arg=None):
        """
        Initializes a conditional effect.

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
        Checks if two conditional effects are equal.

        Args:
            other (ConditionalEffect): The conditional effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.param == other.param and self.effects == other.effects \
            and self.special_effects == other.special_effects \
                and self.condition == other.condition and self.arg == other.arg
    
    def __hash__(self):
        """
        Returns the hash of the conditional effect.

        Returns:
            hash (int): The hash of the conditional effect.
        """
        return hash((self.param, tuple(self.effects), tuple(self.special_effects), 
                     tuple(self.condition), self.completed, self.arg))
    
    def __repr__(self):
        """
        Returns the string representation of the conditional effect.

        Returns:
            string (str): The string representation of the conditional effect.
        """
        return f"ConditionalEffect({self.param}, {self.completed}, {self.arg})"
    
    def apply_sfx_on_arg(self, arg, param_arg_dict):
        """
        Updates the conditional effect with an arg.

        Args:
            arg (Object): The argument that the conditional effect is applied to.
            param_arg_dict (Dictionary[Str, Object]): The dictionary mapping
                the parameters to the arguments.

        Returns:
            copy (ConditionalEffect): The updated conditional effect with an arg. 
        """
        new_effects = {}
        for effect, value in self.effects.items():
            new_effects[effect.replace_pred_params_with_args(param_arg_dict)] = value
        new_special_effects = []
        for special_effect in self.special_effects:
            new_special_effects.append(special_effect.apply_sfx_on_arg(arg, param_arg_dict))
        new_conditions = {}
        for condition, value in self.condition.items():
            new_conditions[condition.replace_pred_params_with_args(param_arg_dict)] = value
        return ConditionalEffect(self.param, new_effects, new_special_effects, new_conditions, arg)
    
    def update(self, state, active=False):
        """
        Updates the state with the effect.

        Since this is a conditional effect, the effects are applied whenever the
        condtions are met, irregardless of whether the action is active or not.
        The active parameter is ignored, but still required to match the
        signature of the update method in the SpecialEffect class.

        Args:
            state (State): The state to update.
            active (bool): Whether or not the update is due to an action being
            performed.
        """
        if self.completed: return
        for condition, value in self.condition.items():
            if state.predicates[condition] != value:
                # Negate the effects
                for effect, value in self.effects.items():
                    state.update_predicate(effect, not value)
                return
        for effect, value in self.effects.items():
            state.update_predicate(effect, value)
        for special_effect in self.special_effects:
            special_effect.update(state, active)
        if all([special_effect.completed for special_effect in self.special_effects]):
            self.completed = True
        