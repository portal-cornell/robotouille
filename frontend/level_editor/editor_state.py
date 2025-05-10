from declarations import Item, Station
from typing import Optional, Union


class EditorState:
    def __init__(
        self,
        project_root_path: str,
        asset_dir_path: str,
        config_file_path: str,
        items: Item,
        stations: Station,
        saved_file: Optional[str] = None,
    ):
        self._project_root_path: str = project_root_path
        self._asset_dir_path: str = asset_dir_path
        self._config_file_path: str = config_file_path
        self._items: Item = items
        self._stations: Station = stations
        self._saved_file: Optional[str] = saved_file
        self._selected: Optional[Union[Item, Station]] = None

    def get_project_root_path(self) -> str:
        return self._project_root_path

    def get_asset_dir_path(self) -> str:
        return self._asset_dir_path

    def get_config_file_path(self) -> str:
        return self._config_file_path

    def get_items(self) -> Item:
        return self._items

    def get_stations(self) -> Station:
        return self._stations

    def get_saved_file(self) -> Optional[str]:
        return self._saved_file

    def set_saved_file(self, saved_file: Optional[str]) -> None:
        self._saved_file = saved_file

    def get_selected(self) -> Optional[Union[Item, Station]]:
        return self._selected

    def set_selected(self, selected: Optional[Union[Item, Station]]) -> None:
        if (
            selected is not None
            and selected not in self._items
            and selected not in self._stations
        ):
            raise ValueError(
                "selected must be None or an item from _items or a station from _stations"
            )
        self._selected = selected
