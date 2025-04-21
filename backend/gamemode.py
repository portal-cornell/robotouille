from backend.customer import Customer
from abc import ABC, abstractmethod

class GameMode(ABC):
    """
    The GameMode class handles how the player achieves victory in the game,
    and keeps track of their score. 
    """
    
    def __init__(self, state, domain_json, environment_json, recipe_json):
        """
        Initializes the GameMode object.

        Args:
            state (State): The game state.
            domain_json (dict): The domain dictionary.
            environment_json (dict): The environment dictionary.
            recipe_json (dict): The recipe dictionary.
        """
        self.environment_json = environment_json
        self.recipe_json = recipe_json

        self.score = 0
        self.win = False

        self.state = state

        self.movement = None

        # Player information
        self.players = {}
        self.player_id_counter = 0

        # Station information
        self.stations = {}
        self.station_id_counter = 0

        # Customer information
        self.customers = {}
        self.customer_id_counter = 0
        self.customer_queue = []
        Customer.build_customers(domain_json, environment_json, recipe_json, self)

    def get_state(self):
        """
        Gets the current state of the game.

        Returns:
            state (State): The current state of the game.
        """
        return self.state
    
    def get_movement(self):
        """
        Gets the movement object.

        Returns:
            movement (Movement): The movement object.
        """
        return self.movement

    @abstractmethod
    def check_if_player_has_won(self):
        """
        Checks if the player has won the game.

        Returns:
            bool: True if the player has won, False otherwise.
        """
        pass
    
    @abstractmethod
    def step(self, actions, clock):
        """
        Steps the game mode.

        Args:
            actions (List[Tuple[Action, Dictionary[str, Object]]): A list of
                tuples where the first element is the action to perform, and the
                second element is a dictionary of arguments for the action. The 
                length of the list is the number of players, where actions[i] is
                the action for player i. If player i is not performing an action,
                actions[i] is None.
            clock (pygame.time.Clock): The clock object.

        Returns:
            new_state (State): The successor state.
            done (bool): True if the goal is reached, False otherwise.
        """
        pass

