
class GameMode(object):
    """
    The GameMode class handles how the player achieves victory in the game,
    and keeps track of their score. 
    """
    
    def __init__(self):
        """
        Initializes the GameMode object.
        """
        self.score = 0
        self.win = False

    def player_wins(self, clock):
        """
        Checks if the player has won the game.

        Args:
            clock (pygame.time.Clock): The clock object.

        Returns:
            bool: True if the player has won, False otherwise.
        """
        pass

