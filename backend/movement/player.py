class Player(object):
    """
    This class represents a player in Robotouille. It contains information
    about the player's position and movement. 
    """
    
    def __init__(self, name, pos, direction):
        """
        Initializes the player object.
        
        Args:
            name (str): The name of the player.
            pos (tuple): The position of the player in the form (x, y).
            direction (tuple): The unit vector of the player's direction.
        """
        self.name = name
        self.pos = pos
        self.direction = direction
        self.motion = False
        self.sprite_value = 0
        self.destination = None
        self.path = []
        self.action = None

    def is_moving(self):
        """
        Returns True if the player is in motion, False otherwise.
        """
        return self.motion
        