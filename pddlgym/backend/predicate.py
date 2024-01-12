class Predicate(object):
    '''
    This class represents a predicate in the Robotouille game. 

    Predicates are rules that are true or false in a given state. There are two
    main types of predicates:
        - Identity predicates: These predicates inform the game about what the 
        object is. 
        - State predicates: These predicates inform the game about the state of
        the object.
    
    Predicates are defined by the user in the domain file, and are created using
    this class for the game to use.
    '''

    def __init__(self, name, params, types, negation=False):
        """
        Initializes a predicate object.

        Args:
            name (str): The name of the predicate.
            params (list[Object]): The parameters of the predicate, represented 
            by a list of objects.
            types (list[str]): The types of the parameters, represented by a 
            list of strings of object types.
            negation (bool): Whether the predicate is negated or not.
        """
        self.name = name
        self.params = params
        self.types = types
        self.negation = negation

        # check if params match types
        if len(params) != len(types):
            raise ValueError("Number of parameters and types do not match.")
        for param in params:
            object_type = types[params.index(param)]
            if param.object_type != object_type:
                raise ValueError("Type of parameter does not match type.")

    def __eq__(self, other):
        """
        Checks if two predicates are equal.

        Args:
            other (Predicate): The predicate to compare to.

        Returns:
            bool: True if the predicates are equal, False otherwise.
        """
        return self.name == other.name and self.params == other.params \
            and self.types == other.types and self.negation == other.negation

    def switch_negation(self):
        """
        Switches the negation value of the predicate.
        """
        self.negation = not self.negation

