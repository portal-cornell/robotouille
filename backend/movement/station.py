class Station(object):
    """
    This class represents a station in Robotouille. It contains information
    about the station's position.
    """
    
    stations = {}
    id_counter = 0
    
    def __init__(self, name, pos):
        """
        Initializes the station object.
        
        Args:
            pos (tuple): The position of the station in the form (x, y).
        """
        self.name = name
        self.pos = pos
        self.id = Station.id_counter
        Station.id_counter += 1
        
    def build_stations(environment_json):
        """
        Builds the stations in the environment.

        Args:
            environment_json (dict): The environment json.
        """
        for station in environment_json["stations"]:
            name = station["name"]
            pos = (station["x"], station["y"])
            station_obj = Station(name, pos)
            Station.stations[name] = station_obj

    def get_station_locations():
        """
        Gets the locations of all stations in the layout.
        
        Returns:
            station_locations (List[tuple]): List of (x, y) positions of stations
        """
        station_locations = []
        for station in Station.stations.values():
            station_locations.append(station.pos)
        return station_locations