from backend.gamemode import GameMode
from backend.customer import Customer

class Classic(GameMode):
    """
    In this gamemode, the player must satisfy all recipes before a given time
    limit. They win if they do this, and lose otherwise. 
    """

    def __init__(self, time_limit, customers):
        """
        Initializes the Classic gamemode.

        Args:
            time_limit (int): The time limit in milliseconds
            customers (List[Customer]): The customers in the game.
        """
        pass

    def player_wins(self, clock):
        """
        Checks if the player has won the game.

        Args:
            clock (pygame.time.Clock): The clock object.

        Returns:
            bool: True if the player has won, False otherwise.
        """
        pass


    