from backend.movement.player import Player
from backend.movement.station import Station

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

    def __init__(self, layout, animate, environment_json):
        """
        Initializes the Movement object.
        
        Args:
            layout (list): The layout of the environment.
            animate (bool): Whether or not to enable animate mode.
        """
        self.layout = layout
        self.animate = animate
        Player.build_players(environment_json)
        Station.build_stations(environment_json)
    
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
        other_station_locations = Station.get_station_locations()
        player_locations = [p.pos for p in Player.players.values() if p != player]
        player_destinations = [p.path[-1] for p in Player.players.values() if p != player and p.path != []]
        width, height = len(self.layout[0]), len(self.layout)
        for i, j in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_pos = (destination[0] + i, destination[1] + j)
            # Skipping - out of range
            if next_pos[0] < 0 or next_pos[0] >= width or next_pos[1] < 0 or next_pos[1] >= height:
                continue
            # Skipping - inside stations or players current/future locations
            if next_pos in other_station_locations or next_pos in player_locations or next_pos in player_destinations:
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

        Raises:
            AssertionError: If the player cannot reach the destination.
        """
        width, height = len(self.layout[0]), len(self.layout)
        obstacle_locations = Station.get_station_locations()
        visited = set()
        path = []
        queue = [(player.pos, path)]
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
        assert current in destinations, "Player cannot reach the destination."
        return path
    
    def move(self, state, player, destination, action, param_arg_dict):
        """
        Moves the player to the destination.

        If animate mode is disabled, the player is immediately moved to the
        destination. If animate mode is enabled, the player path is calculated
        and the player moves the first step in the path.

        Args:
            state (State): The state of the environment.
            player (Player): The player to move.
            destination (Object): The destination station.
            action (Action): The move action.
            param_arg_dict (Dictionary[str, Object]): The arguments of the action.

        Modifies:
            player (Player): Modifies the path and pos fields of the player.
        """
        player_obj = Player.players[player.name]
        destination_pos = Station.stations[destination.name].pos
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
            # Animate the movement by moving the player by one step in the path
            player_obj.path = path
            next_pos = player_obj.path.pop(0)
            player_obj.direction = (next_pos[0] - player_obj.pos[0], next_pos[1] - player_obj.pos[1])
            player_obj.pos = next_pos
            # If player has reached the destination, perform the action
            if player_obj.path == []:
                action.perform_action(state, param_arg_dict)
                destination = param_arg_dict["s2"]
                station_pos = Station.stations[destination.name].pos
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
        for player in Player.players.values():
            other_player_pos = [p.pos for p in Player.players.values() if p != player]
            if player.path != [] and not (len(player.path) == 1 and player.path[0] in other_player_pos):
                next_pos = player.path.pop(0)
                player.direction = (next_pos[0] - player.pos[0], next_pos[1] - player.pos[1])
                player.pos = next_pos
                player.sprite_value += 1
                if player.path == []:
                    player.motion = False
                    player.action[0].perform_action(state, player.action[1])
                    destination = player.action[1]["s2"]
                    station_pos = Station.stations[destination.name].pos
                    player.direction = (station_pos[0] - player.pos[0], station_pos[1] - player.pos[1])
                    player.action = None
                    player.sprite_value = 0