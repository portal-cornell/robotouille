from typing import List, Optional


class Vec2:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def __eq__(self, other):
        if not isinstance(other, Vec2):
            return False
        return self.x == other.x and self.y == other.y


class Station:
    def __init__(self, name: str, asset_file: str):
        self.name = name
        self.asset_file = asset_file

class StationInstance:
    def __init__(self, source_station: Station, pos: Vec2):
        self.source_station = source_station
        self.pos = pos

class Container:
    def __init__(self, name: str, asset_file: str):
        self.name = name
        self.asset_file = asset_file

class ContainerInstance:
    def __init__(self, source_container: Container, pos: Vec2):
        self.source_container = source_container
        self.pos = pos

class Bundle:
    def __init__(self, name: str, asset_file: str):
        self.name = name
        self.asset_file = asset_file

class BundleInstance:
    def __init__(self, source_bundle: Bundle, pos: Vec2):
        self.source_bundle = source_bundle
        self.pos = pos


class PredicateDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: set):
        frozenkey: frozenset = frozenset(key) if isinstance(key, set) else key
        return super().__getitem__(frozenkey)

    def __setitem__(self, key: set, value):
        frozenkey: frozenset = frozenset(key) if isinstance(key, set) else key
        return super().__setitem__(frozenkey, value)

    def __contains__(self, key):
        if isinstance(key, set):
            key = frozenset(key)
        return super().__contains__(key)


class Item:
    def __init__(self, name: str, state_map: list[tuple[list[str], str]]):
        self.name = name
        frozen_state_map = {frozenset(k): v for k, v in state_map}
        self.state_map: PredicateDict = PredicateDict(frozen_state_map)


class ItemInstance:
    def __init__(self, source_item: Item, predicates: set[str], pos: Vec2):
        self.source_item = source_item
        self.predicates = predicates
        self.pos = pos

    def get_asset(self) -> Optional[str]:
        """
        This function takes a list of string predicates and returns an option(str)
        representing an some/none filepath.
        """
        try:
            return self.source_item.state_map[frozenset(self.predicates)]
        except KeyError:
            return self.source_item.state_map[frozenset()]
