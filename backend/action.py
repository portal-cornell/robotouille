import re

from backend.predicate import Predicate

class Action(object):
    """
    The action class is used to represent actions in Robotouille.

    Action definitions are given in the domain json. Each action has a name, 
    preconditions, immediate effects, and special effects.

    For an action to be performed, arguments must be given to the action, and
    applied to the appropriate preconditions, immediate effects, and special
    effects. The action is then performed on the state, and the successor state
    is returned.
    """

    LANGUAGE_DESCRIPTION_REGEX = re.compile(r'\{(\w+)\}') # Matches {p1}, {s1}, {s2}, etc.

    def __init__(self, name, precons, immediate_effects, special_effects, language_description=""):
        """
        Initializes an action object.

        Parameters:
            name (str)
                The name of the action.
            precons (Dictionary[Predicate, bool])
                The preconditions of the action, where the key is the predicate
                with placeholder parameters, and the value is a bool indicating
                whether the predicate is negated or not.
            immediate_effects (Dictionary[Predicate, bool])
                The immediate effects of the action, where the key is the predicate
                with placeholder parameters, and the value is a bool indicating
                whether the predicate is negated or not.
            special_effects (List[SpecialEffect])
                The special effects of the action.
            language_description (str)
                The language description of the action.
        """
        self.name = name
        self.precons = precons
        self.immediate_effects = immediate_effects
        self.special_effects = special_effects
        self.language_description = language_description

    def __eq__(self, other):
        """
        Checks if two actions are equal.

        Requires that all action names defined in the domain are unique.

        Args:
            other (Action): The action to compare to.

        Returns:
            bool: True if the actions are equal, False otherwise.
        """
        return self.name == other.name 
        
    def __hash__(self):
        """
        Returns the hash of the action.

        Returns:
            hash (int): The hash of the action.
        """
        return hash((self.name, tuple(self.precons), 
                     tuple(self.immediate_effects), tuple(self.special_effects)))
    
    def __repr__(self):
        """
        Returns the string representation of the action.

        Returns:
            string (str): The string representation of the action.
        """
        return self.name
    
    def get_all_params(self):
        """
        Returns all unique parameters of the action.

        Returns:
            params (List[Object]): The parameters of the action.
        """
        params = [param for precon in self.precons for param in precon.params]
        params += [param for effect in self.immediate_effects for param in effect.params]
        params += [effect.param for effect in self.special_effects]
        return list(set(params))
    
    def get_language_description(self, param_arg_dict):
        """
        Returns the language description of the action.

        TODO(chalo2000): A separate ActionDef class and Action class will avoid the need for param_arg_dict.
        Parameters:
            param_arg_dict (Dictionary[str, Object]):
                The dictionary that maps parameters to arguments.
        Returns:
            language_description (str): The language description of the action.
        """
        params = self.get_all_params()
        assert all([param.name in param_arg_dict.keys() for param in params]), "param_arg_dict missing parameters."
        sub_lambda = lambda x: param_arg_dict[x.group(1)].name # Substitutes {\w+} with the name of the object
        return re.sub(Action.LANGUAGE_DESCRIPTION_REGEX, sub_lambda, self.language_description)
    
    def is_valid(self, state, args):
        """
        Returns whether the action is valid in the given state.

        Args:
            state (State): The state to check.
            args (Dictionary[str, Object]): The arguments of the action.

        Returns:
            bool: True if the action is valid, False otherwise.
        """
        # Check if all arguments are present
        for value in args.values():
            if value is None:
                return False

        # Check if all arguments are valid  
        params = self.get_all_params()
        for param in params:
            if param.name not in args:
                return False
            
        # Check if all preconditions are satisfied
        for precon, is_true in self.precons.items():
            pred_args = [args[param.name] for param in precon.params]
            pred = Predicate().initialize(precon.name, precon.types, pred_args)
            if state.get_predicate_value(pred) is not is_true:
                return False
        return True

    def perform_action(self, state, param_arg_dict):
        """
        Performs the action on the given state.

        This is used to generate the successor state of the current state, given
        that all preconditions of the action are satisfied.

        First, it asserts that the action is valid in the current state.
        If valid, the immediate effects are applied to the state, and the 
        special effects are added to the state.

        Args:
            state (State): The state to perform the action on.
            param_arg_dict (Dictionary[Str, Object]): The dictionary that map
                parameters to arguments. 

        Returns:
            new_state (State): The successor state.

        Raises:  
            AssertionError: If the action is invalid with the given arguments in
            the given state.
        """
        assert self.is_valid(state, param_arg_dict)
            
        for effect, value in self.immediate_effects.items():
            pred_args = [param_arg_dict[param.name] for param in effect.params]
            pred = Predicate().initialize(effect.name, effect.types, pred_args, effect.language_descriptors)
            state.update_predicate(pred, value)

        for special_effect in self.special_effects:
            # Retrieve the argument based on the parameter in the special effect
            # definition
            arg = param_arg_dict[special_effect.param.name]
            state.update_special_effect(special_effect, arg, param_arg_dict)

        return state