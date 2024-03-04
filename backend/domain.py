class Domain(object):
    '''
    The domain class represents the domain of the game, and is created by the user
    in the domain json.

    It includes the name of the domain, object types, predicate definitions,
    and action definitions.
    '''

    def __init__(self):
        """
        Initializes a domain object with default values.
        """
        self.name = ""
        self.object_types = []
        self.predicates = []
        self.actions = []

    def are_valid_object_types(self, object_types):
        """
        Checks if the list of types are valid, as defined by the domain.

        Args:
            object_types (List[str]): The types to check.

        Returns:
            bool: True if the types are valid, False otherwise.
        """
        for object_type in object_types:
            if object_type not in self.object_types:
                return False
        return True
            
    def _are_valid_types(self, object_types, type_definitions):
        """
        This function does the same thing as are_valid_object_types(), except 
        that the object types are not yet defined in the domain. As such, it
        checks the object types against type_definitions, which are passed in 
        as a parameter.

        Args:
            object_types (List[str]): The types to check.
            type_definitions (List[str]): The types to check against.

        Returns:
            bool: True if the types are valid, False otherwise.
        """
        for object_type in object_types:
            if object_type not in type_definitions:
                return False
        return True
        
            
    def initialize(self, name, object_types, predicate_def, action_def):
        """
        Initializes a domain object and performs checks on all types in the
        predicate and action definitions.

        Args:
            name (str): The name of the domain.
            object_types (List[str]): The types in the domain.
            predicate_def (List[Predicate]): The predicate definitions in the
            domain.
            action_def (List[Action]): The action definitions in the domain.

        Returns:
            Domain: The initialized domain object.

        Raises:
            ValueError: If the types in the predicate and action definitions are
            not valid.
        """
        # Check if predicates and actions have valid parameter types
        for pred in self.predicates:
            if not self._are_valid_types(pred.types, object_types):
                raise ValueError(f"Predicate {pred.name} has invalid types.")

        for action in self.actions:
            for precon in action.precons:
                if not self._are_valid_types(precon.types, object_types):
                    raise ValueError(f"Precondition {precon.name} has invalid types.")
            for effect in action.immediate_effects:
                if not self._are_valid_types(effect.types, object_types):
                    raise ValueError(f"Immediate effect {effect.name} has invalid types.")
            for special_effect in action.special_effects:
                for effect in special_effect.effects:
                    if not self._are_valid_types(effect.types, object_types):
                        raise ValueError(f"Special effect {special_effect.name} has invalid types.")

        self.name = name
        self.object_types = object_types
        self.predicates = predicate_def
        self.actions = action_def

        return self
    
    def get_entity_fields(self):
        """
        Returns the object types of the domain.

        Returns:
            object_types (List[str]): The object types of the domain.
        """
        return [object_type + "s" for object_type in self.object_types]