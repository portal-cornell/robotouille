class Player(object):
    """
    This class represents a player in Robotouille. It contains information
    about the player's position and movement. 
    """

    players = {}
    id_counter = 0
    
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
        self.sprite_value = 0
        self.action = None
        self.id = Player.id_counter
        Player.id_counter += 1

    def build_players(environment_json):
        """
        Builds the players in the environment.

        Args:
            environment_json (dict): The environment json.
        """
        for player in environment_json["players"]:
            name = player["name"]
            pos = (player["x"], player["y"])
            direction = (player["direction"][0], player["direction"][1])
            player_obj = Player(name, pos, direction)
            Player.players[name] = player_obj
    
    def get_player(player_name):
        """
        Gets the player object with the given name.

        Args:
            player_name (str): The name of the player.

        Returns:
            player (Player): The player object.
        """
        return Player.players[player_name]
        