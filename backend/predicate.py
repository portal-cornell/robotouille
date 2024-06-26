from backend.object import Object

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

        Raises:
            ValueError: If the type of a parameter does not match the type 
                defined in the domain.
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
        return self.name == other.name and list(self.types) == list(other.types)\
              and list(self.params) == list(other.params)
    
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
    
    def replace_pred_params_with_args(self, param_arg_dict):
        """
        Returns a copy of the predicate, with the replaced objects.

        Args:
            param_arg_dict (Dictionary[Str, Object]): The dictionary mapping
                parameters to arguments.

        Returns:
            pred (Predicate): The copy of the predicate.
        """
        pred_args = [param_arg_dict[param.name] for param in self.params]
        new_pred_args = []
        for arg in pred_args:
            new_pred_args.append(Object(arg.name, arg.object_type))
        return Predicate().initialize(self.name, self.types, new_pred_args)