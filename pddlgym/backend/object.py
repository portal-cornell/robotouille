class Object(object):
    '''
    This class represents objects in Robotouille.

    Objects are created by the user in the domain file, and are created using
    this class for the game to use.

    Each object also has an object_type, which is also defined in the user file. 
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
        
        # NO type checking in this class, check if types are valid in the domain class

        # use itertools library 