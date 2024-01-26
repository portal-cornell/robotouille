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

    def __init__(self, name, types, params=[]):
        """
        Initializes a predicate object.

        Args:
            name (str): The name of the predicate.
            types (List[str]): The types of the parameters, represented by a 
                list of strings of object types.
            params (List[Object]): The parameters of the predicate, represented 
                by a list of objects. If the predicate is a predicate 
                definition, params is empty.
        """
        self.name = name
        self.types = types
        self.params = params

        # check if params match types
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
        return self.name == other.name and set(self.params) == set(other.params) \
            and set(self.types) == set(other.types)
    
    def __hash__(self):
        """
        Returns the hash of the predicate.

        Returns:
            hash (int): The hash of the predicate.
        """
        return hash((self.name, tuple(self.types), tuple(self.params)))
    
    def __str__(self):
        """
        Returns the string representation of the predicate.

        Returns:
            string (str): The string representation of the predicate.
        """
        return self.name + str(tuple(self.params))
    
    def __repr__(self):
        """
        Returns the string representation of the predicate.

        Returns:
            string (str): The string representation of the predicate.
        """
        return self.name + str(tuple(self.params))
    
    def copy(self, args):
        """
        Returns a copy of the predicate, with the replaced objects.

        Args:
            args (Dictionary[Object, Object]): The dictionary of objects to
                replace for the predicate. 

        Returns:
            pred (Predicate): The copy of the predicate.
        """
        return Predicate(self.name, self.types, [args.get(param, param) for param in self.params])


    def pred_without_objs(self):
        """
        Returns the predicate without the objects. 

        This is primarily used to compare the equality of a predicate and a 
        predicate definition.

        Returns:
            pred (Predicate): The predicate without the objects.
        """
        return Predicate(self.name, self.types)

