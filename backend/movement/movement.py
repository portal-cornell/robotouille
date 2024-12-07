from backend.movement.player import Player
from backend.movement.station import Station
from backend.customer import Customer
from enum import Enum

class MetaData(object):
    """
    This class represents the metadata of a player or customer's movement. 
    """
    def __init__(self, path, time):
        """
        Initializes the metadata object.

        Args:
            path (list[Tuple]): The path to the destination. Each 
                element in the list is a tuple representing the (x, y) position.
            time (int): The time elapsed since the movement started.
        """
        self.path = path
        self.time = time

class Mode(Enum):
    """
    This class represents the different movement modes in Robotouille.
    """
    IMMEDIATE = "immediate" # The player moves immediately to the destination
    TRAVERSE = "traverse" # The player traverses to the destination
    

class Movement(object):
    """
    This class is responsible for the movement in Robotouille.

    This class keeps track of the positions of all objects in the environment, 
    as well as the layout of the environment. 

    It also handles the movement actions of Robotouille. During gameplay, every 
    player must make an action before the step method is 
    called (including "wait" actions). If a player is in motion, they cannot 
    make another action until they have reached their destination, and their 
    action is automatically set to "wait". 
    
    If a player is in motion and another player is in motion to the same station, 
    the player that arrived first will take priority and the other player will 
    be forced to wait at their current location. 
    """

    def __init__(self, layout, mode, environment_json, gamemode, ms_per_tile=100):
        """
        Initializes the Movement object.
        
        Args:
            layout (list): The layout of the environment.
            mode (str): The movement mode.
            environment_json (dict): The environment JSON.
            gamemode (GameMode): The game mode object.
            ms_per_tile (int): The number of milliseconds it takes for a player to move one tile.
        """
        self.layout = layout
        self.mode = Mode(mode)
        self.ms_per_tile = ms_per_tile
        Player.build_players(environment_json, gamemode)
        Station.build_stations(environment_json, gamemode)
        
        # (Dict[str, MetaData]) The player movement data, with the key being the player name
        self.metadata = {}

    def _get_possible_destinations(self, player_or_customer, destination, gamemode):
        """
        Gets the possible destination positions for a player.

        Args:
            player_or_customer (Player or Customer): The player or customer.
            destination (tuple): The destination position.
            gamemode (GameMode): The game mode object.

        Returns:
            possible_destinations (List[tuple]): The possible destination positions.

        Raises:
            AssertionError: If both player and customer are None, or if both player
                and customer are not None.
        """
        # Get the locations of all stations, players, and customers
        other_station_locations = Station.get_station_locations(gamemode)
        player_customer_locations = [p.pos for p in gamemode.players.values() if p != player_or_customer]
        player_customer_locations += [c.pos for c in gamemode.customers.values() if c != player_or_customer and c.in_game]
        
        # Get the destinations of all other players and customers in motion
        player_customer_destinations = []
        for name, data in self.metadata.items():
            if data.path and name != player_or_customer.name:
                    player_customer_destinations.append(data.path[-1])
        
        possible_destinations = []
        width, height = len(self.layout[0]), len(self.layout)
        for i, j in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_pos = (destination[0] + i, destination[1] + j)
            # Skipping - out of range
            if next_pos[0] < 0 or next_pos[0] >= width or next_pos[1] < 0 or next_pos[1] >= height:
                continue
            # Skipping - inside stations or players current/future locations
            if next_pos in other_station_locations or next_pos in player_customer_locations or next_pos in player_customer_destinations:
                continue
            possible_destinations.append(next_pos)
        return possible_destinations

    def _get_path(self, player_or_customer, destinations, gamemode):
        """
        Gets the path for the player or customer to move to the destination.

        The destinations account for other player locations, customer locations,
        and station locations when the move action is first called

        Args:
            player_or_customer (Player or Customer): The player or customer to move.
            destinations (List[tuple]): The possible destination positions
            gamemode (GameMode): The game mode object.

        Returns:
            path (list[Tuple]): The path to the destination. Each 
                element in the list is a tuple representing the (x, y) position.

        Raises:
            AssertionError: If the player or customer cannot reach the destination.
        """
        width, height = len(self.layout[0]), len(self.layout)
        obstacle_locations = Station.get_station_locations(gamemode)
        visited = set()
        current = player_or_customer.pos
        path = [current]
        queue = [(current, path)]
        while queue:
            current, path = queue.pop(0)
            if current in destinations:
                break
            if current[0] < 0 or current[0] >= width or current[1] < 0 or current[1] >= height:
                continue
            if current in obstacle_locations:
                continue
            if current in visited:
                continue
            visited.add(current)
            for i, j in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_pos = (current[0] + i, current[1] + j)
                new_path = path.copy()
                new_path.append(next_pos)
                queue.append((next_pos, new_path))
        assert current in destinations, "Player or Customer cannot reach the destination."
        return path
    
    def _move(self, gamemode, player_or_customer, destination, action, param_arg_dict, clock):
        """
        Moves the player or customer to the destination.

        If the movement mode is immediate, the player moves to the destination
        immediately.

        If the movement mode is traverse, the player path is calculated
        and the player moves the first step in the path.

        Args:
            gamemode (GameMode): The game mode object.
            player_or_customer (Player or Customer): The player or customer to move.
            destination (Object): The destination station.
            action (Action): The move action.
            param_arg_dict (Dictionary[str, Object]): The arguments of the action.
            clock (pygame.time.Clock): The pygame clock.

        Modifies:
            player (Player): Modifies the direction and pos fields of the player
                if the movement mode is for a player.
            customer (Customer): Modifies the destination field of the customer
                if the movement mode is for a customer.

        Raises:
            AssertionError: If both player and customer are None, or if both player
                and customer are not None.
        """
        state = gamemode.get_state()

        if gamemode.players.get(player_or_customer.name) is not None:
            obj = gamemode.players[player_or_customer.name]
        else:
            obj = gamemode.customers[player_or_customer.name]

        destination_pos = gamemode.stations[destination.name].pos
        possible_destinations = self._get_possible_destinations(obj, destination_pos, gamemode)
        # If player is already at the destination, the state predicates are immediately updated
        if obj.pos in possible_destinations:
            action.perform_action(state, param_arg_dict)
            obj.direction = (destination_pos[0] - obj.pos[0], destination_pos[1] - obj.pos[1])
            return
        # Get the path to the destination
        path = self._get_path(obj, possible_destinations, gamemode)
        # If movement mode is immediate, move the player to the destination
        if self.mode == Mode.IMMEDIATE:
            obj.pos = path[-1]
            obj.direction = (destination_pos[0] - obj.pos[0], destination_pos[1] - obj.pos[1])
            action.perform_action(state, param_arg_dict)
        else:
            # Animate the movement by updating the player's position depending on the time
            prev_pos = path[0]
            next_pos = path[1]
            data = MetaData(path, 0)
            self.metadata[obj.name] = data
            obj.direction = (next_pos[0] - prev_pos[0], next_pos[1] - prev_pos[1])
            data.time += clock.get_time()
            dt = data.time/self.ms_per_tile
            current_x = prev_pos[0] + dt * (next_pos[0] - prev_pos[0])
            current_y = prev_pos[1] + dt * (next_pos[1] - prev_pos[1])
            obj.pos = (current_x, current_y)
            obj.action = (action, param_arg_dict)

    def _step_player_and_customer(self, gamemode, clock):
        """
        This helper function steps each player and customer in the environment 
        that is currently in motion.

        Args:
            gamemode (GameMode): The game mode object.
            clock (pygame.time.Clock): The pygame clock.
        
        Modifies:
            gamemode.players: Modifies the direction, pos, sprite_value, and 
                action fields of the player.
            gamemode.customers: Modifies the pos and sprite_value fields of the 
                customer.
            self.metadata: Modifies the path and time fields of the player 
                or customer.
        """
        state = gamemode.get_state()
        ending_movement = []
        for name, data in self.metadata.items():
            is_player = name in gamemode.players
            if is_player:
                obj = gamemode.players[name]
            else:
                obj = gamemode.customers[name]
            next_pos = data.path[1]
            prev_pos = data.path[0]
            obj.direction = (next_pos[0] - prev_pos[0], next_pos[1] - prev_pos[1])
            obj.sprite_value += 1
            data.time += clock.get_time()
            dt = data.time/self.ms_per_tile
            if dt >= 1:
                data.path.pop(0)
                data.time = 0
                obj.pos = next_pos
            else:
                current_x = prev_pos[0] + dt * (next_pos[0] - prev_pos[0])
                current_y = prev_pos[1] + dt * (next_pos[1] - prev_pos[1])
                obj.pos = (current_x, current_y)
            if len(data.path) == 1:
                obj.action[0].perform_action(state, obj.action[1])
                destination = obj.action[1]["s2"]
                station_pos = gamemode.stations[destination.name].pos
                obj.direction = (station_pos[0] - next_pos[0], station_pos[1] - next_pos[1])
                obj.sprite_value = 0
                obj.action = None
                ending_movement.append(name)
        for name in ending_movement:
            del self.metadata[name]
        
    def step(self, gamemode, clock, actions):
        """
        This function represents one time step in the environment.

        Args:
            gamemode (GameMode): The game mode object.
            clock (pygame.time.Clock): The pygame clock.
            actions (List[Tuple[Action, Dictionary[str, Object]]): A list of
                tuples where the first element is the action to perform, and the
                second element is a dictionary of arguments for the action. The 
                length of the list is the number of players, where actions[i] is
                the action for player i. If player i is not performing an action,
                actions[i] is None.
        """
        self._step_player_and_customer(gamemode, clock)

        for action, param_arg_dict in actions:
            if not action:
                continue
            # If the action is a movement action, use the movement module
            if action.name == "move":
                player = param_arg_dict["p1"]
                destination = param_arg_dict["s2"]
                self._move(gamemode, player, destination, action, param_arg_dict, clock)
            elif action.name == "customer_move":
                customer = param_arg_dict["npc1"]
                destination = param_arg_dict["s2"]
                self._move(gamemode, customer, destination, action, param_arg_dict, clock)
            elif action.name == "customer_leave":
                customer = param_arg_dict["npc1"]
                destination = param_arg_dict["s2"]
                self._move(gamemode, customer, destination, action, param_arg_dict, clock)
        

    def is_player_moving(self, player_name):
        """
        Returns True if the player is in motion, False otherwise.

        Args:
            player_name (str): The name of the player.

        Returns:
            is_moving (bool): True if the player is in motion, False otherwise.
        """
        return player_name in self.metadata