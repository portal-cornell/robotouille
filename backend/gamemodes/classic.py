from backend.gamemode import GameMode
from backend.customer import Customer
from backend.movement.movement import Mode

class Classic(GameMode):
    """
    In this gamemode, the player must satisfy all recipes before a given time
    limit. They win if they do this, and lose otherwise. 
    """

    def __init__(self, state, domain_json, environment_json, recipe_json):
        """
        Initializes the Classic gamemode.

        Args:
            state (State): The game state.
            domain_json (dict): The domain dictionary.
            environment_json (dict): The environment dictionary. 
            recipe_json (dict): The recipe dictionary.   
            movement (Movement): The movement object.
        """
        super().__init__(state, domain_json, environment_json, recipe_json)
        self.time_limit = environment_json["gamemode"]["time"]

    def check_if_player_has_won(self, time):
        """
        Checks if the player has won the game.

        Args:
            clock (pygame.time): The time object.

        Modifies:
            self.win (bool): True if the player has won, False otherwise.
        """
        if all([customer.has_been_served for customer in self.customers.values()]) and time.get_ticks() <= self.time_limit:
            self.win = True
            self.score = 1

    def step(self, actions, time, clock):
        """
        Steps the game mode.

        Args:
            actions (List[Tuple[Action, Dictionary[str, Object]]): A list of
                tuples where the first element is the action to perform, and the
                second element is a dictionary of arguments for the action. The 
                length of the list is the number of players, where actions[i] is
                the action for player i. If player i is not performing an action,
                actions[i] is None.
            time (pygame.time): The time object.
            clock (pygame.time.Clock): The clock object.

        Returns:
            new_state (State): The successor state.
            done (bool): True if the goal is reached, False otherwise.
        """
        
        for customer in self.customers.values():
            action = customer.step(time, self)
    
            if action is not None:
                actions.append(action)

        new_state, done = self.state.step(actions)

        self.movement.step(self, clock, actions)

        if self.movement.mode == Mode.TRAVERSE:
            new_state.current_player = new_state.next_player()

        self.check_if_player_has_won(time)

        return new_state, done


    