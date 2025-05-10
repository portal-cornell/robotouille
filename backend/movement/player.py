class Player(object):
    """
    This class represents a player in Robotouille. It contains information
    about the player's position and movement. 
    """
    
    def __init__(self, name, pos, direction, gamemode):
        """
        Initializes the player object.
        
        Args:
            name (str): The name of the player.
            pos (tuple): The position of the player in the form (x, y).
            direction (tuple): The unit vector of the player's direction.
            gamemode (GameMode): The game mode object.
        """
        self.name = name
        self.pos = pos
        self.direction = direction
        self.sprite_value = 0
        self.action = None
        self.id = gamemode.player_id_counter
        gamemode.player_id_counter += 1
        gamemode.players[name] = self

    def build_players(environment_json, gamemode):
        """
        Builds the players in the environment.

        Args:
            environment_json (dict): The environment json.
            gamemode (GameMode): The game mode object.
        """
        for player in environment_json["players"]:
            name = player["name"]
            pos = (player["x"], player["y"])
            direction = (player["direction"][0], player["direction"][1])
            Player(name, pos, direction, gamemode)
    
    def get_player(gamemode, player_name):
        """
        Gets the player object with the given name.

        Args:
            gamemode (GameMode): The game mode object.
            player_name (str): The name of the player.

        Returns:
            player (Player): The player object.
        """
        return gamemode.players[player_name]
        