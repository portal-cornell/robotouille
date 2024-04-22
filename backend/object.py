class Object(object):
    '''
    This class represents objects in Robotouille.

    Objects are created by the user in the domain json, and are created using
    this class for the game to use.

    Each object also has an object_type, which is also defined in the domain json. 
    This will be used for type checking when creating predicates.
    '''

    def __init__(self, name, object_type):
        """
        Initializes an object.

        Args:
            name (str): The name of the object.
            object_type (str): The type of the object.
        """

        self.name = name
        self.object_type = object_type

    def __eq__(self, other):
        """
        Checks if two objects are equal.

        Args:
            other (Object): The object to compare to.

        Returns:
            bool: True if the objects are equal, False otherwise.
        """
        return self.name == other.name and self.object_type == other.object_type
    
    def __hash__(self):
        """
        Returns the hash of the object.

        Returns:
            hash (int): The hash of the object.
        """
        return hash((self.name, self.object_type))
    
    def __repr__(self):
        """
        Returns the string representation of the object.

        Returns:
            string (str): The string representation of the object.
        """
        return self.name