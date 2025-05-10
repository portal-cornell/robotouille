from declarations import Vec2, Item, Station, ItemInstance, StationInstance
from typing import List, Optional, Tuple


class NoStationAtLocationError(Exception):
    """Raised when trying to place an item at a location without a station."""

    pass


class LevelState:
    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self._stations: List[List[Optional[StationInstance]]] = [
            [None for _ in range(height)] for _ in range(width)
        ]
        self._items: List[List[List[ItemInstance]]] = [
            [[] for _ in range(height)] for _ in range(width)
        ]

    def get_station_at(self, pos: Vec2) -> Optional[StationInstance]:
        return self._stations[pos.x][pos.y]

    def get_items_at(self, pos: Vec2) -> List[ItemInstance]:
        return self._items[pos.x][pos.y]

    def get_all_stations(self) -> List[StationInstance]:
        stations = []
        for x in range(self.width):
            for y in range(self.height):
                station = self._stations[x][y]
                if station:
                    stations.append(station)
        return stations

    def get_all_items(self) -> List[ItemInstance]:
        items = []
        for x in range(self.width):
            for y in range(self.height):
                for item in self._items[x][y]:
                    items.append(item)
        return items

    def put_station_at(self, station: StationInstance):
        pos = station.pos
        self._stations[pos.x][pos.y] = station

    def put_item_at(self, item: ItemInstance):
        pos = item.pos
        existing_station = self.get_station_at(pos)
        if existing_station is None:
            raise NoStationAtLocationError(
                "Cannot place item at location without a station"
            )
        self._items[pos.x][pos.y].append(item)

    def serialize(self) -> dict:
        stations_json = []
        for station in self.get_all_stations():
            stations_json.append(
                {
                    "name": station.source_station.name,
                    "x": station.pos.x,
                    "y": self.height - 1 - station.pos.y,
                }
            )

        items_json = []
        for x in range(self.width):
            for y in range(self.height):
                for i, item in enumerate(self._items[x][y]):
                    items_json.append(
                        {
                            "name": item.source_item.name,
                            "x": item.pos.x,
                            "y": self.height - 1 - item.pos.y,
                            "stack-level": i,
                            "predicates": list(item.predicates),
                        }
                    )

        level_json = {
            "version": "1.0.0",
            "width": self.width,
            "height": self.height,
            "config": {
                "num_cuts": {"lettuce": 3, "default": 3},
                "cook_time": {"patty": 3, "default": 3},
            },
            "stations": stations_json,
            "items": items_json,
            "players": [{"name": "robot", "x": 0, "y": 0, "direction": [0, 1]}],
            "goal_description": "Make a cheese burger with cheese on top of the patty",
            "goal": [
                {"predicate": "iscooked", "args": ["patty"], "ids": [1]},
                {"predicate": "atop", "args": ["topbun", "cheese"], "ids": [2, 3]},
                {"predicate": "atop", "args": ["cheese", "patty"], "ids": [3, 1]},
                {"predicate": "atop", "args": ["patty", "bottombun"], "ids": [1, 4]},
            ],
        }
        return level_json
