from backend.special_effect import SpecialEffect
from utils.robotouille_utils import trim_item_ID

class RepetitiveEffect(SpecialEffect):
    """
    This class represents repetitive effects in Robotouille.

    A repetitive effect is an effect that is only applied after an action has
    been performed a certain number of times.
    """
    
    def __init__(self, param, effects, special_effects, default_goal_repetitions=3, arg=None, config_key=None):
        """
        Initializes a repetitive effect.

        Args:
            param (Object): The parameter of the special effect.
            effects (Dictionary[Predicate, bool]): The effects of the action,
                represented by a dictionary of predicates and bools.
            special_effects (List[SpecialEffect]): The nested special effects of
                the action.
            default_goal_repetitions (int): The number of times the action must be 
                performed before the effect is applied by default.
            arg (Object): The object that the effect is applied to. If the
                special effect is not applied to an object, arg is None.
        """
        super().__init__(param, effects, special_effects, False, arg)
        self.default_goal_repetitions = default_goal_repetitions
        self.goal_repetitions = None # This is resolved locally when applying the effect to an argument
        self.current_repetitions = 0
        self.config_key = config_key

    def __eq__(self, other):
        """
        Checks if two repetitive effects are equal.

        Args:
            other (RepetitiveEffect): The repetitive effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.param == other.param and self.effects == other.effects \
            and self.special_effects == other.special_effects \
                and self.default_goal_repetitions == other.default_goal_repetitions \
                    and self.arg == other.arg and self.config_key == other.config_key
    
    def __hash__(self):
        """
        Returns the hash of the repetitive effect.

        Returns:
            hash (int): The hash of the repetitive effect.
        """
        return hash((self.param, tuple(self.effects), tuple(self.special_effects), 
                     self.completed, self.current_repetitions, self.arg, self.config_key))
    
    def __repr__(self):
        """
        Returns the string representation of the repetitive effect.

        Returns:
            string (str): The string representation of the repetitive effect.
        """
        return f"RepetitiveEffect({self.param}, {self.completed}, {self.current_repetitions}, {self.arg})"

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
            new_special_effects = [sfx.apply_sfx_on_arg(arg, param_arg_dict) for sfx in self.special_effects]
            return RepetitiveEffect(self.param, new_effects, new_special_effects,
                                    self.default_goal_repetitions, arg, config_key=self.config_key)
    
    def _resolve_goal_repetitions_if_needed(self, state):
        """
        Resolves the goal repetitions for the effect if it has not already been
        resolved.

        Args:
            state (State): The current state.
        """
        if self.goal_repetitions is not None:
            return
        
        # If there is no bound arg, just use default
        if self.arg is None:
            self.goal_repetitions = self.default_goal_repetitions
            return

        base_name, _ = trim_item_ID(self.arg.name)
        # Read from config
        table = state.config.get(self.config_key, {}) if self.config_key else {}
        raw = table.get(base_name, table.get("default", self.default_goal_repetitions))
        self.goal_repetitions = max(1, raw)
    
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
        if not active or self.completed: return
        self._resolve_goal_repetitions_if_needed(state)
        self.increment_repetitions()
        if self.current_repetitions == self.goal_repetitions:
            for effect, value in self.effects.items():
                state.update_predicate(effect, value)
            for special_effect in self.special_effects:
                special_effect.update(state, active)
            self.completed = True