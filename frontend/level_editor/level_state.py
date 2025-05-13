from declarations import Vec2, ItemInstance, StationInstance
from typing import List, Optional, Union


class NoStationAtLocationError(Exception):
    """Raised when trying to place an item at a location without a station."""

    pass


class PlayerAtLocationError(Exception):
    """Raised when trying to place a station at the player's position."""

    pass


class InvalidPlayerPosition(Exception):
    """Raised when trying to set the player at an invalid location."""

    pass


class MissingPlayerPosition(Exception):
    """Raised when trying to serialize a level without a player position."""

    pass


class Goal:
    def __init__(self):
        self._goal_stack: List[ItemInstance] = []

    def push_goal(self, item: ItemInstance):
        self._goal_stack.append(item)

    def pop_goal(self) -> Optional[ItemInstance]:
        if self._goal_stack:
            return self._goal_stack.pop()
        return None

    def serialize(self) -> list:
        goal_json = []
        item_id_map = {}
        next_id = 1
        for i, item in enumerate(self._goal_stack):
            item_id = next_id
            next_id += 1
            item_id_map[item] = item_id

            # Add predicates for the item
            for predicate in item.predicates:
                goal_json.append(
                    {
                        "predicate": predicate,
                        "args": [item.source_item.name],
                        "ids": [item_id],
                    }
                )

            # Add atop relation if it's not the bottom item
            if i > 0:
                bottom_item = self._goal_stack[i - 1]
                bottom_item_id = item_id_map[bottom_item]
                goal_json.append(
                    {
                        "predicate": "atop",
                        "args": [item.source_item.name, bottom_item.source_item.name],
                        "ids": [item_id, bottom_item_id],
                    }
                )
        return goal_json


class LevelState:
    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self._player_pos: Optional[Vec2] = Vec2(0, 0)
        self._player_direction: Vec2 = Vec2(0, 1)
        self._stations: List[List[Optional[StationInstance]]] = [
            [None for _ in range(height)] for _ in range(width)
        ]
        self._items: List[List[List[ItemInstance]]] = [
            [[] for _ in range(height)] for _ in range(width)
        ]
        self.goal: Goal = Goal()

    def get_player_pos(self) -> Vec2:
        return self._player_pos

    def get_player_direction(self) -> Vec2:
        return self._player_direction

    def set_player_pos(self, pos: Vec2):
        if self.get_station_at(pos) is not None:
            raise InvalidPlayerPosition(
                "Cannot place player at location with a station"
            )

        # Check for neighboring stations in top, bottom, left, and right directions
        valid_directions = []
        if pos.x > 0 and self.get_station_at(Vec2(pos.x - 1, pos.y)) is not None:
            valid_directions.append(Vec2(-1, 0))  # Left
        if (
            pos.x < self.width - 1
            and self.get_station_at(Vec2(pos.x + 1, pos.y)) is not None
        ):
            valid_directions.append(Vec2(1, 0))  # Right
        if pos.y > 0 and self.get_station_at(Vec2(pos.x, pos.y - 1)) is not None:
            valid_directions.append(Vec2(0, -1))  # Bottom
        if (
            pos.y < self.height - 1
            and self.get_station_at(Vec2(pos.x, pos.y + 1)) is not None
        ):
            valid_directions.append(Vec2(0, 1))  # Top

        if not valid_directions:
            raise InvalidPlayerPosition(
                "Cannot place player at location without neighboring stations (top, bottom, left, right)"
            )

        # Set player direction to face towards the first valid direction
        self._player_direction = valid_directions[0]
        self._player_pos = pos

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
        if station.pos != self._player_pos:
            pos = station.pos
            self._stations[pos.x][pos.y] = station
        else:
            raise PlayerAtLocationError()

    def remove_station_at(self, pos: Vec2):
        self._stations[pos.x][pos.y] = None

    def put_item_at(self, item: ItemInstance):
        pos = item.pos
        existing_station = self.get_station_at(pos)
        if existing_station is None:
            raise NoStationAtLocationError(
                "Cannot place item at location without a station"
            )
        self._items[pos.x][pos.y].append(item)

    def pop_item_at(self, pos: Vec2):
        if len(self._items[pos.x][pos.y]) > 0:
            self._items[pos.x][pos.y].pop()

    def serialize(self) -> dict:
        if self._player_pos is None:
            raise MissingPlayerPosition(
                "Cannot serialize level without a player position"
            )

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
            "players": [
                {
                    "name": "robot",
                    "x": self._player_pos.x,
                    "y": self.height - 1 - self._player_pos.y,
                    "direction": [self._player_direction.x, self._player_direction.y],
                }
            ],
            "goal_description": "Make a cheese burger with cheese on top of the patty",
            "goal": self.goal.serialize(),
        }
        return level_json
