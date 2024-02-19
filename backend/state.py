from backend.predicate import Predicate
from backend.special_effect import SpecialEffect
import itertools

class State(object):
    '''
    This class represents a state in the Robotouille game.

    States are created by the game, and are updated by the game when actions are
    performed.
    '''

    def __init__(self):
        """
        Creates a state object with default values.
        """
        self.domain = None
        self.objects = []
        self.predicates = {}
        self.actions = {}
        self.goal = []
        self.special_effects = []

    def _build_object_dictionary(self, domain, objects):
        """
        Builds a dictionary of objects.

        The keys of the dictionary are the types of objects in the domain, and
        the values are lists of objects of that type.

        Args:
            domain (Domain): The domain of the game.
            objects (List[Object]): The objects in the state.

        Returns:
            object_dict (Dictionary[str, List[Object]]): A dictionary of objects
                in the state.

        Raises:
            ValueError: If an object type is not defined in the domain.
        """
        object_dict = {k: [] for k in domain.object_types}
        for obj in objects:
            if obj.object_type not in object_dict:
                raise ValueError(f"Type {obj.object_type} is not defined in the domain.")
            object_dict[obj.object_type].append(obj)

        return object_dict

    def _build_predicates(self, domain, objects, true_predicates):
        """
        Builds a dictionary of predicates.

        The dictionary is populated with all possible predicates in the state 
        using the predicates in the domain and the objects in the problem file. 
        All predicates are set to False, except for the predicates that are true 
        in the problem file, which are passed in as the argument 
        [true_predicates].

        Args:
            domain (Domain): The domain of the game.
            objects (List[Object]): The objects in the state.
            true_predicates (Set[Predicate]): The predicates that are true in
                the state, as defined by the problem file. 
        """
        object_dict = self._build_object_dictionary(domain, objects)
            
        # Loop through the predicates in the domain
        predicates = {}
        for predicate in domain.predicates:
            # Check the types of the parameters in the domain. For each type, 
            # get the objects of that type in the problem file. Then create a 
            # list of all possible combinations of objects for the parameters.
            param_objects = [object_dict[object_type] for object_type in predicate.types]
            param_combinations = list(itertools.product(*param_objects))
            # For each combination of objects, create a predicate and add it to
            # the list of predicates.
            for combination in param_combinations:
                # If combination repeats an object, skip it
                if len(set(combination)) != len(combination):
                    continue
                pred = Predicate().initialize(predicate.name, predicate.types, combination)
                predicates[pred] = pred in true_predicates

        return predicates
    
    def _build_actions(self, domain, objects):
        """
        Builds a dictionary of all actions for the state.

        This helper method first builds a dictionary of objects in the state. 
        It then loops through the actions in the domain. For each action, it
        creates every possible combination of objects for the parameters of the
        action.

        Args:
            domain (Domain): The domain of the game.
            objects (List[Object]): The objects in the state.

        Returns:
            actions (Dictionary[Action, Dictionary[str, Object]]): A 
                dictionary of valid actions for the state. The keys are the 
                actions, and the values are the arguments for the actions.
        """
        object_dict = self._build_object_dictionary(domain, objects)
        actions = {}
        
        for action in self.domain.actions:
            params = action.get_all_params()
            param_objects = [object_dict[param.object_type] for param in params]
            param_combinations = list(itertools.product(*param_objects))
            actions[action] = []
            for combination in param_combinations:
                # If combination repeats an object, skip it
                if len(set(combination)) != len(combination):
                    continue
                args = {param:combination[params.index(param)] for param in params}
                actions[action].append(args)

        return actions

    def initialize(self, domain, objects, true_predicates, all_goals, special_effects=[]):
        """
        Initializes a state object.

        Predicates are stored in a dictionary with the predicate as the key, and
        the value as the value. The value is a boolean, where True means that 
        the predicate is true in the state, and False means that the predicate 
        is false in the state.

        The initializer also checks the types of the objects in the state and
        the goal predicates to ensure that they are defined in the domain.

        Args:
            domain (Domain): The domain of the game.
            objects (List[Object]): The objects in the state.
            true_predicates (Set[Predicate]): The predicates that are true in
                the state, as defined by the problem file. 
            all_goals (List[List[Predicate]]): The goal predicates of the game.
            special_effects (List[Special_effects]): The special effects that 
                are active in the state.

        Returns:
            state (State): The initialized state.
        """
        predicates = self._build_predicates(domain, objects, true_predicates)
        # check if objects have types defined in domain
        for object in objects:
            if object.object_type not in domain.object_types:
                raise ValueError("Type {} is not defined in the domain.".format(object.object_type))
        # check if goal predicates are defined in domain
        for goal_set in all_goals:
            for goal in goal_set:
                if goal not in predicates:
                    raise ValueError("Predicate {} is not defined in the state.".format(goal.name))
                domain.are_valid_object_types(goal.types)
        
        self.domain = domain
        self.objects = objects
        self.predicates = predicates
        self.actions = self._build_actions(domain, objects)
        self.goal = all_goals
        self.special_effects = special_effects

        return self
        
    def __eq__(self, other):
        """
        Checks if two states are equal.

        Args:
            other (State): The state to compare to.

        Returns:
            bool: True if the states are equal, False otherwise.
        """
        return self.domain == other.domain and self.objects == other.objects \
            and self.predicates == other.predicates and self.goal == other.goal \
            and self.special_effects == other.special_effects

    def get_predicate_value(self, predicate):
        """
       Returns the value of a predicate in the state.

        Args:
            predicate (Predicate): The predicate to check.
            value (bool): The value of the predicate to check for.

        Returns:
            bool: True if the predicate is True in the state, False otherwise.

        Raises:
            AssertionError: If the predicate is not in the state.
        """
        assert predicate in self.predicates
        return self.predicates[predicate]
        
    def update_predicate(self, predicate, value):
        """
        Updates a predicate in the state with a new value.

        Args:
            predicate (Predicate): The predicate to update.
            value (bool): The new value of the predicate.

        Raises:
            AssertionError: If the predicate is not in the state.
        """
        assert predicate in self.predicates
        self.predicates[predicate] = value
    
    def update_special_effect(self, special_effect, obj, args):
        """
        Updates a special effect in the state.

        If the special effect is not in the state, it is added.
        Otherwise, the special effect is sent an active update.

        Args:
            special_effect (SpecialEffect): The special effect to update.
            obj (Object): The object to update the special effect for.
            args (Dictionary[Object, Object]): The arguments for the special
                effect.
        """
        new_special_effect = special_effect.replace_params_with_args(obj, args)
        if new_special_effect not in self.special_effects:
            self.special_effects.append(new_special_effect)
        current = self.special_effects[self.special_effects.index(new_special_effect)]
        current.update(self, active=True)
        if current.completed:
                self.special_effects.remove(current)

    def is_goal_reached(self):
        """
        Returns whether the goal is satisfied in the current state.
        
        self.goal is a list of lists of predicates. Each list of predicates is a
        goal set, which represents a possible goal state. The state satisfies
        the goal if it satisfies any of the goal sets.

        Returns:
            bool: True if the state satisfies the goal, False otherwise.
        """
        for goal_set in self.goal:
            if all(self.get_predicate_value(goal) for goal in goal_set):
                return True
        return False
        
    
    def get_valid_actions(self):
        """
        Gets all valid actions for the state.

        An empty list is initially assigned to each action. For every possible 
        set of arguments for each action, the arguments that are currently 
        valid for each action are appended to the lists for the relevant action.

        Returns:
            valid_actions (Dictionary[Action, Dictionary[Object, Object]]): A
                dictionary of valid actions for the state. The keys are the
                actions, and the values are the parameter-argument dictionaries
                for the actions.
        """
        valid_actions = {action:[] for action in self.actions}

        for action, args in self.actions.items():
            for arg in args:
                if action.is_valid(self, arg):
                    valid_actions[action].append(arg)

        return valid_actions

    def step(self, action, param_arg_dict):
        """
        Steps the state forward by applying the effects of the action.

        Args:
            action (Action): The action to apply the effects of.
            param_arg_dict (Dictionary[Object, Object]): The dictionary that map
                parameters to arguments.
        
        Returns:
            new_state (State): The successor state.
            done (bool): True if the goal is reached, False otherwise.

        Raises:
            AssertionError: If the action is invalid with the given arguments in
            the given state.
        """
        assert action.is_valid(self, param_arg_dict)
        self = action.perform_action(self, param_arg_dict)

        for special_effect in self.special_effects:
            special_effect.update(self)
            if special_effect.completed:
                self.special_effects.remove(special_effect)
        
        if self.is_goal_reached():
            return self, True

        return self, False
    