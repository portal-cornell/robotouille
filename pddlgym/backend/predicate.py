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

    def __init__(self, name, types, params=[], value=False):
        """
        Initializes a predicate object.

        Args:
            name (str): The name of the predicate.
            types (list[str]): The types of the parameters, represented by a 
            list of strings of object types.
            params (list[Object]): The parameters of the predicate, represented 
            by a list of objects. If the predicate is a predicate definition,
            params is empty.
            value (bool): The value of the predicate; If the predicate is true,
            value is True, and if the predicate is false, value is False.
        """
        self.name = name
        self.types = types
        self.params = params
        self.value = value

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
            and self.types == other.types and self.value == other.value

    def set_value(self, value):
        """
        Sets the value of the predicate.

        Args:
            value (bool): The value to set the predicate to.
        """
        self.value = value

    def pred_without_objs(self):
        """
        Returns the predicate without the objects.

        Returns:
            pred (Predicate): The predicate without the objects.
        """
        return Predicate(self.name, self.types, value=self.value)

