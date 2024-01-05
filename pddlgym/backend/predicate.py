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

    def __init__(self, name, params, types, negation=False, time=None):
        """
        Initializes a predicate object.

        Args:
            name (str): The name of the predicate.
            params (list): The parameters of the predicate, represented by a list
            of objects.
            types (list): The types of the parameters, represented by a list of
            strings of object types.
            negation (bool): Whether the predicate is negated or not.
            time (int): If the predicate is a timed predicate, this attribute
            represents the amount of time the predicate has been true for. If not,
            this attribute is None.
        """
        self.name = name
        self.params = params
        self.types = types
        self.negation = negation
        self.time = time

        # check if params match types
        if len(params) != len(types):
            raise ValueError("Number of parameters and types do not match.")
        for param in params:
            tpe = types[params.index(param)]
            if param.type != tpe:
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
            and self.types == other.types and self.negation == other.negation \
                and self.time == other.time



