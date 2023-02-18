from structs import Predicate, Literal, Type

def parse(literal_str):
    """
    Parses a string representation of a literal into a Literal object.

    Args:
    literal_str : str
        String representation of a literal. 
        Examples:
        - at(chef:player,stove:station)
        - A(B:1,C:2,D:3,...) where A is the predicate name, B-D are the arguments, and 1-3 are the types
    
    Returns:
        predicate : str
            Predicate name
        args : list of str
            List of arguments
        types : list of Type strings
            List of argument types
    """
    # Split the string into the predicate name and the arguments
    predicate_name, args_str = literal_str.split("(")
    # Split the arguments into a list of strings
    args_str = args_str[:-1] # Remove the trailing ')'
    args_str = args_str.split(",")
    # Convert the arguments into a list of tuples
    args = []
    types = []
    for arg_str in args_str:
        arg_name, arg_type = arg_str.split(":")
        args.append(arg_name)
        types.append(Type(arg_type))
    return predicate_name, args, types

def str_to_literal(literal_str):
    """
    Converts a string representation of a literal to a Literal object.

    literal_str : str
        String representation of a literal. 
        Examples:
        - at(chef:player,stove:station)
        - A(B:1,C:2,D:3,...) where A is the predicate name, B-D are the arguments, and 1-3 are the types
    """
    predicate_name, args, types = parse(literal_str)
    predicate = Predicate(predicate_name, len(args), types)
    # Create the literal
    literal = Literal(predicate, args)
    return literal

