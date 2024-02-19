class Predicate(object):
    '''
    This class represents a predicate in Robotouille. 

    Predicates are properties that are True or False in a given state. 
    Predicates are defined by the user in the domain json, and are created using
    this class for the game to use.
    '''

    def __init__(self):
        """
        Creates a predicate object with default values.
        """
        self.name = ""
        self.types = []
        self.params = []

    def initialize(self, name, types, params=[]):
        """
        Initializes a predicate object.

        Args:
            name (str): The name of the predicate.
            types (List[str]): The types of the parameters, represented by a 
                list of strings of object types.
            params (List[Object]): The parameters of the predicate, represented 
                by a list of objects. If the predicate is a predicate 
                definition, params is empty.

        Returns:
            pred (Predicate): The initialized predicate.
        """
        # Check if params match types
        for param in params:
            object_type = types[params.index(param)]
            if param.object_type != object_type:
                raise ValueError("Type of parameter does not match type.")
            
        self.name = name
        self.types = types
        self.params = params

        return self

    def __eq__(self, other):
        """
        Checks if two predicates are equal.

        Args:
            other (Predicate): The predicate to compare to.

        Returns:
            bool: True if the predicates are equal, False otherwise.
        """
        return self.name == other.name and list(self.types) == list(other.types) and list(self.params) == list(other.params)
    
    def __hash__(self):
        """
        Returns the hash of the predicate.

        Returns:
            hash (int): The hash of the predicate.
        """
        return hash((self.name, tuple(self.types), tuple(self.params)))
    
    def __repr__(self):
        """
        Returns the string representation of the predicate.

        Returns:
            string (str): The string representation of the predicate.
        """
        return self.name + str(tuple(self.params))
    
    def replace_params_with_args(self, args):
        """
        Returns a copy of the predicate, with the replaced objects.

        Args:
            args (Dictionary[Object, Object]): The dictionary of objects to
                replace for the predicate. 

        Returns:
            pred (Predicate): The copy of the predicate.
        """
        pred_args = [args.get(param, param) for param in self.params]
        return Predicate().initialize(self.name, self.types, pred_args)

