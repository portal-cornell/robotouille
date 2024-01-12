from pddlgym.backend import Predicate, RepetitiveEffect
class State(object):
    '''
    This class represents a state in the Robotouille game.

    States are created by the game, and are updated by the game when actions are
    performed.
    '''

    def __init__(self, domain, special_effects=[]):
        """
        Initializes a state object.

        Args:
            domain (Domain): The domain of the game.
            special_effects (list[Special_effects]): The special effects that 
            are active in the state.
        """
        self.domain = domain
        self.predicates = domain.predicates
        for obj in domain.objects:
            self.predicates.add(Predicate("is", [obj], [obj.object_type]))
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
            negation value, False otherwise.
        """
        if predicate in self.predicates:
            return True
        
    def update_predicate(self, predicate):
        """
        Updates a predicate in the state.

        Args:
            predicate (Predicate): The predicate to update.
        """
        current_predicate = predicate.switch_negation()
        if current_predicate in self.predicates:
            self.predicates[current_predicate].switch_negation()
    
    def add_special_effect(self, special_effect):
        """
        Adds a special effect to the state.

        Args:
            special_effect (SpecialEffect): The special effect to add.
        """
        if special_effect not in self.special_effects:
            self.special_effects.append(special_effect)
        elif type(special_effect) == RepetitiveEffect:
            current = self.special_effects[self.special_effects.index(special_effect)]
            current.increment_repetitions()

    def check_goal(self, goal):
        """
        Checks if the state satisfies the goal.

        Args:
            goal (Predicate): The goal to check.

        Returns:
            bool: True if the state satisfies the goal, False otherwise.
        """
        if goal in self.predicates:
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
            special_effect.update(self.state)
            if special_effect.completed:
                self.special_effects.remove(special_effect)
        
        if action.check_if_valid(self.state):
            new_state = action.perform_action(self.state)
        
        if new_state.check_goal(self.domain.goal):
            return new_state # eventually change this to end the game with a 'finish' state/ screen

        return new_state

            
    def add_predicate(self, predicate):
        """
        Adds a predicate to the state.

        Args:
            predicate (Predicate): The predicate to add.
        """
        pass

    def remove_predicate(self, predicate):
        """
        Removes a predicate from the state.

        Args:
            predicate (Predicate): The predicate to remove.
        """
        pass


# step(update) function -> just update special effects and apply effects of action if valid, check goal function
    