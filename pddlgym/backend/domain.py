class Domain(object):
    '''
    The domain class represents the domain of the game, and is created by the user
    in the domain file.
    '''

    def __init__(self, name, objects, predicates, actions, goal):
        """
        Initializes a domain object.

        Args:
            name (str): The name of the domain.
            objects (list[Object]): The objects in the domain.
            predicates (list[Predicate]): The predicates in the domain.
            actions (list[Action]): The actions in the domain.
            goal (Predicate): The goal of the domain.
        """
        self.name = name
        self.objects = objects
        self.predicates = predicates
        self.actions = actions
        self.goal = goal