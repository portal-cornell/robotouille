from predicate import Predicate
import itertools
class State(object):
    '''
    This class represents a state in the Robotouille game.

    States are created by the game, and are updated by the game when actions are
    performed.
    '''

    def _build_predicates(self, domain, objects, true_predicates):
        """
        Builds a dictionary of predicates.

        The dictionary is populated with all possible predicates in the state 
        using the predicates in the domain and the objects in the problem file. 
        All predicates are set to False, except for the predicates that are true 
        in the problem file, which are passed in as the argument 
        [true_predicates] and set to True.

        Args:
            domain (Domain): The domain of the game.
            objects (List[Object]): The objects in the state.
            true_predicates (List[Predicate]): The predicates that are true in
                the state, as defined by the problem file. 
        """
        # convert predicates to strings in true_predicates, and convert list to set
        true_predicates = set([str(pred) for pred in true_predicates])

        # Create a dictionary, with the key as object types in the domain and 
        # value being a list of objects of that type in the problem file
        object_dict = {}
        for object_type in domain.object_types:
            object_dict[object_type] = []
        for obj in objects:
            if obj.object_type not in object_dict:
                raise ValueError("Type {} is not defined in the domain.".format(obj.object_type))
            object_dict[obj.object_type].append(obj)

        # Create a list of all possible predicates in the state.
            
        # Loop through the predicates in the domain
        predicates = {}
        for predicate in domain.predicates:
            # Check the types of the parameters in the domain. For each type, 
            # get the objects of that type in the problem file. Then create a 
            # list of all possible combinations of objects for the parameters.
            param_objects = []
            for type_ in predicate.types:
                param_objects.append(object_dict[type_])
            param_combinations = list(itertools.product(*param_objects))
            # For each combination of objects, create a predicate and add it to
            # the list of predicates.
            for combination in param_combinations:
                # if combination repeats an object, skip it
                if len(set(combination)) != len(combination):
                    continue
                pred = Predicate(predicate.name, predicate.types, combination)
                predicates[pred] = False
                if str(pred) in true_predicates:
                    predicates[pred] = True

        return predicates

    def __init__(self, domain, objects, true_predicates, goal, special_effects=set()):
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
            true_predicates (List[Predicate]): The predicates that are true in
                the state, as defined by the problem file. 
            goal (List[Predicate]): The goal predicates of the game.
            special_effects (HashSet[Special_effects]): The special effects that 
                are active in the state.
        """
        self.domain = domain
        self.objects = objects
        # check if objects have types defined in domain
        for object in self.objects:
            if object.object_type not in self.domain.object_types:
                raise ValueError("Type {} is not defined in the domain.".format(object.object_type))

        self.predicates = self._build_predicates(domain, objects, true_predicates)
        
        self.goal = goal
        # check if goal predicates are defined in domain
        for goal in self.goal:
            if goal.name not in self.domain.predicates:
                raise ValueError("Predicate {} is not defined in the domain.".format(goal.name))
            domain.check_types(goal.types)
        self.special_effects = special_effects
        
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

    def check_predicate(self, predicate, value=True):
        """
        Checks if a predicate is in the state with the correct value.

        Args:
            predicate (Predicate): The predicate to check.
            value (bool): The value of the predicate to check for.

        Returns:
            bool: True if the predicate is in the state with the correct 
            value, False otherwise.
        """
        return predicate in self.predicates and self.predicates[predicate] == value
        
    def update_predicate(self, predicate, value):
        """
        Updates a predicate in the state with a new value.

        Args:
            predicate (Predicate): The predicate to update.
            value (bool): The new value of the predicate.
        """
        self.predicates[predicate] = value
    
    def update_special_effect(self, special_effect):
        """
        Updates a special effect in the state.
        If the special effect is not in the state, it is added.
        The special effect is then updated as an active update.

        Args:
            special_effect (SpecialEffect): The special effect to add.
        """
        if special_effect not in self.special_effects:
            self.special_effects.add(special_effect)
        current = self.special_effects.get(special_effect)
        current.update(self, active=True)

    def check_goal(self, goal):
        """
        Checks if the state satisfies the goal.

        Args:
            goal (Predicate): The goal to check.

        Returns:
            bool: True if the state satisfies the goal, False otherwise.
        """
        for goal in self.goal:
            if not self.check_predicate(goal):
                return False
        return True

    def step(self, action):
        """
        Steps the state forward by applying the effects of the action.

        Args:
            action (Action): The action to apply the effects of.
        
        Returns:
            new_state (State): The successor state.
        """
        for special_effect in self.special_effects:
            special_effect.update(self)
            if special_effect.completed:
                self.special_effects.remove(special_effect)
        
        if action.check_if_valid(self.state):
            new_state = action.perform_action(self.state)
        
        if new_state.check_goal(self.domain.goal):
            return new_state #TODO: eventually change this to end the game with a 'finish' state/ screen

        return new_state
    