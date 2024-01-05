class Object(object):
    '''
    This class represents objects in Robotouille.

    An object on Robotouille must be one of four types:
        - Floor
        - Item
        - Player
        - Station
    '''

    class ObjectTypes(object):
        '''
        This class represents the types of objects in Robotouille.
        '''
        FLOOR = "floor"
        ITEM = "item"
        PLAYER = "player"
        STATION = "station"

    def __init__(self, name, tpe):
        """
        Initializes an object.

        Args:
            name (str): The name of the object.
            tpe (str): The type of the object.
        """

        self.name = name
        self.type = tpe

        # ensure that the type is valid
        if tpe not in [Object.ObjectTypes.FLOOR, Object.ObjectTypes.ITEM, Object.ObjectTypes.PLAYER, Object.ObjectTypes.STATION]:
            raise ValueError("Invalid object type.")