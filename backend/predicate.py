import re

from backend.object import Object


# TODO(chalo2000): Separate into PredicateDef and Predicate class to remove confusing param_args_dict
class Predicate(object):
    '''
    This class represents a predicate in Robotouille. 

    Predicates are properties that are True or False in a given state. 
    Predicates are defined by the user in the domain json, and are created using
    this class for the game to use.
    '''

    LANGUAGE_DESCRIPTOR_REGEX = re.compile(r'\{(\d+)\}') # Matches {0}, {1}, etc.

    def __init__(self):
        """
        Creates a predicate object with default values.
        """
        self.name = ""
        self.types = []
        self.params = []
        self.language_descriptors = {}

    def initialize(self, name, types, params=[], language_descriptors={}):
        """
        Initializes a predicate object.

        Parameters:
            name (str):
                The name of the predicate.
            types (List[str]):
                The types of the parameters, represented by a list of strings of object types.
            params (List[Object]): 
                The parameters of the predicate, represented by a list of objects. If the 
                predicate is a predicate definition, params is empty.
            language_descriptors (Dict[str, str]):
                The language descriptors of parameter types where the key is the index of
                the parameter and the value is the index-parametrized descriptor.
        
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
        self.language_descriptors = language_descriptors

        return self
    
    def get_language_description(self, object):
        """
        Returns the language description given the provided object.

        Parameters:
            object (Object): The object to get the language description for.
        
        Returns:
            language_description (str):
                The language description for the provided object predicate.
        
        Raises:
            AssertionError: If the object is not in the predicate.
        """
        assert object in self.params, "Object not in predicate."
        index = self.params.index(object)
        language_descriptor = self.language_descriptors[str(index)]
        sub_lambda = lambda x: self.params[int(x.group(1))].name # Substitutes {\d+} with the name of the object
        return re.sub(Predicate.LANGUAGE_DESCRIPTOR_REGEX, sub_lambda, language_descriptor)

    def __eq__(self, other):
        """
        Checks if two predicates are equal.

        Parameters:
            other (Predicate): The predicate to compare to.

        Returns:
            bool: True if the predicates are equal, False otherwise.
        """
        return self.name == other.name and list(self.types) == list(other.types) \
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

        Parameters:
            param_arg_dict (Dictionary[Str, Object]): The dictionary mapping
                parameters to arguments.

        Returns:
            pred (Predicate): The copy of the predicate.
        """
        pred_args = [param_arg_dict[param.name] for param in self.params]
        new_pred_args = []
        for arg in pred_args:
            new_pred_args.append(Object(arg.name, arg.object_type))
        return Predicate().initialize(self.name, self.types, new_pred_args, self.language_descriptors)