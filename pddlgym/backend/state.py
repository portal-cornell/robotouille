from pddlgym.backend import Predicate, RepetitiveEffect
class State(object):
    '''
    This class represents a state in the Robotouille game.

    States are created by the game, and are updated by the game when actions are
    performed.
    '''

    def __init__(self, domain, objects, predicates, goal, special_effects=set()):
        """
        Initializes a state object.

        Args:
            domain (Domain): The domain of the game.
            objects (list[Object]): The objects in the state.
            predicates (HashSet[Predicate]): The predicates in the state.
            goal (list[Predicate]): The goal of the game.
            special_effects (HashSet[Special_effects]): The special effects that 
            are active in the state.
        """
        self.domain = domain
        self.objects = objects
        for object in self.objects:
            if object.object_type not in self.domain.object_types:
                raise ValueError("Type {} is not defined in the domain.".format(object.object_type))
        self.predicates = predicates
        for pred in self.predicates:
            if pred.pred_without_objs() not in self.domain.predicates:
                raise ValueError("Predicate {} is not defined in the domain.".format(pred.name))
        self.goal = goal
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
        return self.domain == other.domain and \
            self.predicates == other.predicates and \
                self.special_effects == other.special_effects

    def check_predicate(self, predicate):
        """
        Checks if a predicate is true in the state.

        Args:
            predicate (Predicate): The predicate to check.

        Returns:
            bool: True if the predicate is in the state with the correct 
            value, False otherwise.
        """
        if predicate in self.predicates:
            return True
        
    def update_predicate(self, predicate):
        """
        Updates a predicate in the state.

        Args:
            predicate (Predicate): The predicate to update.
        """
        negated_pred = predicate.set_value(not predicate.value)
        if negated_pred in self.predicates:
            self.predicates.remove(negated_pred)
            self.predicates.add(predicate)
    
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
        for predicate in goal:
            if predicate not in self.predicates:
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
    