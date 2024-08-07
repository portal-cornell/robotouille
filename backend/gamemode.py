from backend.customer import Customer
class GameMode(object):
    """
    The GameMode class handles how the player achieves victory in the game,
    and keeps track of their score. 
    """
    
    def __init__(self, state, environment_json, recipe_json):
        """
        Initializes the GameMode object.

        Args:
            state (State): The game state.
            environment_json (dict): The environment dictionary.
            recipe_json (dict): The recipe dictionary.
        """
        self.score = 0
        self.win = False
        self.state = state
        Customer.build_customers(environment_json, recipe_json)


    def check_if_player_has_won(self):
        """
        Checks if the player has won the game.

        Returns:
            bool: True if the player has won, False otherwise.
        """
        pass

    def step(self, time, actions):
        """
        Steps the game mode.

        Args:
            time (pygame.time): The time object.
            actions (List[Tuple[Action, Dictionary[str, Object]]): A list of
                tuples where the first element is the action to perform, and the
                second element is a dictionary of arguments for the action. The 
                length of the list is the number of players, where actions[i] is
                the action for player i. If player i is not performing an action,
                actions[i] is None.

        Returns:
            new_state (State): The successor state.
            done (bool): True if the goal is reached, False otherwise.
        """
        pass

