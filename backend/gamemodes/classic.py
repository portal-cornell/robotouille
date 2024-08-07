from backend.gamemode import GameMode
from backend.customer import Customer

class Classic(GameMode):
    """
    In this gamemode, the player must satisfy all recipes before a given time
    limit. They win if they do this, and lose otherwise. 
    """

    def __init__(self, state, environment_json, recipe_json):
        """
        Initializes the Classic gamemode.

        Args:
            state (State): The game state.
            environment_json (dict): The environment dictionary. 
            recipe_json (dict): The recipe dictionary.   
        """
        super().__init__(state, environment_json, recipe_json)
        self.time_limit = environment_json["gamemode"]["time"]
        self.customers = Customer.customers

    def check_if_player_has_won(self, clock):
        """
        Checks if the player has won the game.

        Args:
            clock (pygame.time.Clock): The clock object.

        Modifies:
            self.win (bool): True if the player has won, False otherwise.
        """
        if all([customer.has_been_served for customer in self.customers.values()]) and clock.get_ticks() <= self.time_limit:
            self.win = True
            self.score = 1

    #TODO: GameMode has a step that steps the state, players, and customers, etc.
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
        new_state, done = self.state.step(actions)
        
        for customer in self.customers.values():
            new_state = customer.step(time, self.state)

        self.check_if_player_has_won(time)

        return new_state, done


    