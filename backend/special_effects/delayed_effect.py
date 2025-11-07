from backend.special_effect import SpecialEffect
from utils.robotouille_utils import trim_item_ID

class DelayedEffect(SpecialEffect):
    """
    This class represents delayed effects in Robotouille.

    A delayed effect is an effect that is only applied after a certain amount
    of time has passed.
    """

    def __init__(self, param, effects, special_effects, default_goal_time=4, arg=None, config_key=None):
        """
        Initializes a delayed effect.

        Args:
            param (Object): The parameter of the special effect.
            effects (Dictionary[Predicate, bool]): The effects of the action,
                represented by a dictionary of predicates and bools.
            special_effects (List[SpecialEffect]): The nested special effects of
                the action.
            sfx_config (Dict[str, Any]):
                The environment configuration for the specific special effect.
            default_goal_time (int): The time it takes for the effect to be applied.
            arg (Object): The object that the effect is applied to. If the
                special effect is not applied to an object, arg is None.
            config_key (str): The key to use when looking up the goal time in the config.
        """
        super().__init__(param, effects, special_effects, False, arg)
        
        self.default_goal_time = default_goal_time
        self.goal_time = None
        self.current_time = 0
        self.config_key = config_key

    def __eq__(self, other):
        """
        Checks if two delayed effects are equal.

        Args:
            other (DelayedEffect): The delayed effect to compare to.

        Returns:
            bool: True if the effects are equal, False otherwise.
        """
        return self.param == other.param and self.effects == other.effects \
            and self.special_effects == other.special_effects \
                and self.default_goal_time == other.default_goal_time and self.arg == other.arg \
                    and self.config_key == other.config_key
    
    def __hash__(self):
        """
        Returns the hash of the delayed effect.

        Returns:
            hash (int): The hash of the delayed effect.
        """
        return hash((self.param, tuple(self.effects), tuple(self.special_effects), 
                     self.completed, self.current_time, self.arg, self.config_key))
    
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
        new_special_effects = [se.apply_sfx_on_arg(arg, param_arg_dict) for se in self.special_effects]
        return DelayedEffect(self.param, new_effects, new_special_effects,
                             self.default_goal_time, arg, config_key=self.config_key)
    
    def _resolve_goal_time_if_needed(self, state):
        """
        Resolves the goal time for the effect if it has not already been
        resolved.

        Args:
            state (State): The current state. 
        """
        if self.goal_time is not None:
            return
        if self.arg is None:
            self.goal_time = self.default_goal_time
            return
        base_name, _ = trim_item_ID(self.arg.name)
        table = state.config.get(self.config_key, {}) if self.config_key else {}
        raw = table.get(base_name, table.get("default", self.default_goal_time))
        self.goal_time = max(1, raw)


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
        self._resolve_goal_time_if_needed(state)
        self.increment_time()
        if self.current_time == self.goal_time:
            for effect, value in self.effects.items():
                state.update_predicate(effect, value)
            for special_effect in self.special_effects:
                special_effect.update(state)
            self.completed = True