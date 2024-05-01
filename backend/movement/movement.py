from backend.movement.player import Player

class Movement(object):
    """
    This class is responsible for the movement in Robotouille.

    This class keeps track of the positions of all objects in the environment, 
    as well as the layout of the environment. 

    It also handles the movement actions of Robotouille. Eacj call to the step
    function in the State class represents 1 time step. Every action other than 
    move take 1 time step. When animate mode is disabled, move actions are 
    instantaneous and take 1 time step. When animate mode is enabled, movement 
    is animated. The movement action takes 1 time step for each tile moved.
    
    During gameplay, every player must make an action before the step method is 
    called (including "wait" actions). If a player is in motion, they cannot 
    make another action until they have reached their destination, and their 
    action is automatically set to "wait". 
    
    If a player is in motion and another player is in motion to the same station, 
    the player that arrived first will take priority and the other player will 
    be forced to wait at their current location. 
    """

    def __init__(self, layout, animate):
        """
        Initializes the Movement object.
        
        Args:
            layout (list): The layout of the environment.
            animate (bool): Whether or not to enable animate mode.
        """
        self.layout = layout
        self.animate = animate
        self.players = {}
        self.stations = {}

    def _build_players(self, environment_json):
        """
        Builds the players in the environment.

        Args:
            environment_json (dict): The environment json.

        Returns:
            players (Dictionary[str, Player]): The list of players mapping
                player name to player object.
        """
        players = {}
        for player in environment_json["players"]:
            name = player["name"]
            pos = (player["x"], player["y"])
            direction = (player["direction"][0], player["direction"][1])
            players[name] = Player(name, pos, direction)
        return players
    
    def _build_stations(self, environment_json):
        """
        Builds the stations in the environment.

        Args:
            environment_json (dict): The environment json.

        Returns:
            stations (Dictionary[str, Station]): The list of stations mapping
                station name to station object.
        """
        stations = {}
        for station in environment_json["stations"]:
            name = station["name"]
            pos = (station["x"], station["y"])
            stations[name] = pos
        return stations
    
    def initialize(self, environment_json):
        """
        Initializes the movement.

        Args:
            animate (bool): Whether or not to enable animate mode.

        Returns:
            movement (Movement): The movement object.
        """
        self.players = self._build_players(environment_json)
        self.stations = self._build_stations(environment_json)

        return self

    def _get_station_locations(self):
        """
        Gets the locations of all stations in the layout.
        
        Returns:
            station_locations (List[tuple]): List of (x, y) positions of stations
        """
        station_locations = []
        for i, row in enumerate(self.layout):
            for j, col in enumerate(row):
                if col is not None:
                    station_locations.append((j, len(self.layout) - i - 1))
        return station_locations
    
    def _get_possible_destinations(self, player, destination):
        """
        Gets the possible destination positions for a player.

        Args:
            player (Player): The player.
            destination (tuple): The destination position.

        Returns:
            possible_destinations (List[tuple]): The possible destination positions.
        """
        possible_destinations = []
        other_station_locations = self._get_station_locations()
        player_locations = [(p.pos[0], p.pos[1]) for p in self.players.values() if p != player]
        width, height = len(self.layout[0]), len(self.layout)
        for i, j in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_pos = (destination[0] + i, destination[1] + j)
            if next_pos[0] < 0 or next_pos[0] >= width or next_pos[1] < 0 or next_pos[1] >= height:
                continue
            if next_pos in other_station_locations or next_pos in player_locations:
                continue
            possible_destinations.append(next_pos)
        return possible_destinations

    def _get_player_path(self, player, destinations):
        """
        Gets the path for the player to move to the destination.

        Args:
            player (Player): The player.
            destinations (List[tuple]): The possible destination positions
                (accounts for other player locations and station locations when
                the move action is first called)

        Returns:
            path (list[Tuple]): The path to the destination. Each 
                element in the list is a tuple representing the (x, y) position.
        """
        width, height = len(self.layout[0]), len(self.layout)
        obstacle_locations = self._get_station_locations()
        visited = set()
        path = []
        queue = [(player.pos, path)]
        while queue:
            current, path = queue.pop(0)
            if current in destinations:
                return path
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
        assert False, "No path found"
    
    def move(self, state, player, destination, action, param_arg_dict):
        """
        Moves the player to the destination.

        If animate mode is disabled, the player is immediately moved to the
        destination. If animate mode is enabled, the player path is calculated
        and the player moves the first step in the path.

        Args:
            state (State): The state of the environment.
            player (Object): The player to move.
            destination (Object): The destination station.
            action (Action): The move action.
            param_arg_dict (Dictionary[str, Object]): The arguments of the action.

        Modifies:
            player (Player): Modifies the path and pos fields of the player.
        """
        player_obj = self.players[player.name]
        destination_pos = self.stations[destination.name]
        possible_destinations = self._get_possible_destinations(player_obj, destination_pos)
        # If player is already at the destination, perform move action immediately
        if player_obj.pos in possible_destinations:
            action.perform_action(state, param_arg_dict)
            player_obj.direction = (destination_pos[0] - player_obj.pos[0], destination_pos[1] - player_obj.pos[1])
            return
        # Get the path to the destination
        path = self._get_player_path(player_obj, possible_destinations)
        # If animate mode is disabled, move player to destination immediately
        if not self.animate:
            player_obj.pos = path[-1]
            player_obj.direction = (destination_pos[0] - player_obj.pos[0], destination_pos[1] - player_obj.pos[1])
            action.perform_action(state, param_arg_dict)
        else:
            # Animate the movement by moving the player by on step in the path
            player_obj.path = path
            next_pos = player_obj.path.pop(0)
            player_obj.direction = (next_pos[0] - player_obj.pos[0], next_pos[1] - player_obj.pos[1])
            player_obj.pos = next_pos
            # If player has reached the destination, perform the action
            if player_obj.path == []:
                action.perform_action(state, param_arg_dict)
                destination = param_arg_dict["s2"]
                station_pos = self.stations[destination.name]
                player_obj.direction = (station_pos[0] - next_pos[0], station_pos[1] - next_pos[1])
            # Else, the player is still currently moving and waits for the next step
            else:
                player_obj.motion = True
                player_obj.action = (action, param_arg_dict)
        
    def step(self, state):
        """
        This function represents one time step in the environment.

        Args:
            state (State): The state of the environment.
        """
        for player in self.players.values():
            other_player_pos = [p.pos for p in self.players.values() if p != player]
            if player.path != [] and not (len(player.path) == 1 and player.path[0] in other_player_pos):
                next_pos = player.path.pop(0)
                player.direction = (next_pos[0] - player.pos[0], next_pos[1] - player.pos[1])
                player.pos = next_pos
                if player.path == []:
                    player.motion = False
                    player.action[0].perform_action(state, player.action[1])
                    destination = player.action[1]["s2"]
                    station_pos = self.stations[destination.name]
                    player.direction = (station_pos[0] - player.pos[0], station_pos[1] - player.pos[1])
                    player.action = None


    def get_player(self, player_name):
        """
        Gets the player object with the given name.

        Args:
            player_name (str): The name of the player.

        Returns:
            player (Player): The player object.
        """
        return self.players[player_name]