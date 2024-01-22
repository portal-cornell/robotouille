class Domain(object):
    '''
    The domain class represents the domain of the game, and is created by the user
    in the domain file.
    '''

    def check_types(self, types):
        """
        Checks if the list of types are valid, as defined by the domain.

        Args:
            types (list[str]): The types to check.

        Raises:
            ValueError: If the types are not valid.
        """
        for type_ in types:
            if type_ not in self.object_types:
                raise ValueError("Type {} is not defined in the domain.".format(type_))

    def __init__(self, name, object_types, predicate_def, action_def):
        """
        Initializes a domain object.

        Args:
            name (str): The name of the domain.
            object_types (list[str]): The types in the domain.
            predicate_def (list[Predicate]): The predicate definitions in the
            domain.
            action_def (list[Action]): The action definitions in the domain.
        """
        self.name = name
        self.object_types = object_types
        self.predicates = predicate_def
        self.actions = action_def

        # Check if predicates and actions have valid parameter types
        for pred in self.predicates:
            self.check_types(pred.types)

        for action in self.actions:
            for precon in action.precons:
                self.check_types(precon.types)
            for effect in action.immediate_effects:
                self.check_types(effect.types)
            for special_effect in action.special_effects:
                for effect in special_effect.effects:
                    self.check_types(effect.types)
