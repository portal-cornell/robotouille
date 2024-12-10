class Station(object):
    """
    This class represents a station in Robotouille. It contains information
    about the station's position.
    """
    
    def __init__(self, name, pos, gamemode):
        """
        Initializes the station object.
        
        Args:
            name (str): The name of the station.
            pos (tuple): The position of the station in the form (x, y).
            gamemode (GameMode): The game mode object.
        """
        self.name = name
        self.pos = pos
        self.id = gamemode.station_id_counter
        gamemode.station_id_counter += 1
        gamemode.stations[name] = self
        
    def build_stations(environment_json, gamemode):
        """
        Builds the stations in the environment.

        Args:
            environment_json (dict): The environment json.
            gamemode (GameMode): The game mode object.
        """
        for station in environment_json["stations"]:
            name = station["name"]
            pos = (station["x"], station["y"])
            Station(name, pos, gamemode)

    def get_station_locations(gamemode):
        """
        Gets the locations of all stations in the layout.

        Args:
            gamemode (GameMode): The game mode object.
        
        Returns:
            station_locations (List[tuple]): List of (x, y) positions of stations
        """
        station_locations = []
        for station in gamemode.stations.values():
            station_locations.append(station.pos)
        return station_locations