from declarations import Vec2, Item, Station, ItemInstance, StationInstance
from typing import List, Optional


class NoStationAtLocationError(Exception):
    """Raised when trying to place an item at a location without a station."""

    pass


class LevelState:
    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self._stations: List[StationInstance] = []
        self._items: List[ItemInstance] = []

    def get_station_at(self, pos: Vec2) -> Optional[StationInstance]:
        for station in self._stations:
            if station.pos.x == pos.x and station.pos.y == pos.y:
                return station
        return None

    def get_item_at(self, pos: Vec2) -> Optional[ItemInstance]:
        for item in self._items:
            if item.pos.x == pos.x and item.pos.y == pos.y:
                return item
        return None

    def get_all_stations(self) -> List[StationInstance]:
        return self._stations

    def get_all_items(self) -> List[ItemInstance]:
        return self._items

    def put_station_at(self, station: StationInstance):
        pos = station.pos
        existing_station = self.get_station_at(pos)
        if existing_station is None:
            self._stations.append(station)
        else:
            self._stations.remove(existing_station)
            self._stations.append(station)

    def put_item_at(self, item: ItemInstance):
        pos = item.pos
        existing_station = self.get_station_at(pos)
        if existing_station is None:
            raise NoStationAtLocationError(
                "Cannot place item at location without a station"
            )

        existing_item = self.get_item_at(pos)
        if existing_item is None:
            self._items.append(item)
        else:
            self._items.remove(existing_item)
            self._items.append(item)

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
        for item in self.get_all_items():
            items_json.append(
                {
                    "name": item.source_item.name,
                    "x": item.pos.x,
                    "y": self.height - 1 - item.pos.y,
                    "stack-level": 0,  # This is hardcoded for now
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
