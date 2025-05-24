from declarations import Item, Station, Container
from typing import Optional, Union, Tuple, Set


class EditorState:
    def __init__(
        self,
        project_root_path: str,
        asset_dir_path: str,
        config_file_path: str,
        items: list[Item],
        stations: list[Station],
        containers: list[Container],
        item_states: list[Tuple[Item, Set[str]]],
        saved_file: Optional[str] = None,
    ):
        self._project_root_path: str = project_root_path
        self._asset_dir_path: str = asset_dir_path
        self._config_file_path: str = config_file_path
        self._items: list[Item] = items
        self._stations: list[Station] = stations
        self._containers: list[Container] = containers
        self._item_states: list[Tuple[Item, Set[str]]] = item_states
        self._saved_file: Optional[str] = saved_file
        self._selected: Optional[Union[Station, Tuple[Item, Set[str]], Container]] = None

    def get_item_states(self) -> list[Tuple[Item, Set[str]]]:
        return self._item_states

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

    def get_containers(self) -> Container:
        return self._containers

    def get_saved_file(self) -> Optional[str]:
        return self._saved_file

    def set_saved_file(self, saved_file: Optional[str]) -> None:
        self._saved_file = saved_file

    def get_selected(self) -> Optional[Union[Station, Tuple[Item, Set[str]], Container]]:
        return self._selected

    def set_selected(
        self, selected: Optional[Union[Station, Tuple[Item, Set[str]], Container]]
    ) -> None:
        if selected is not None:
            if isinstance(selected, tuple):
                if selected[0] not in self._items:  # check if item in tuple is in items
                    raise ValueError(
                        "selected item must be None or an item from _items or a station from _stations"
                    )
            elif (
                selected not in self._stations and selected not in self._containers
            ):  # if not a tuple, check if it is a station or container
                raise ValueError(
                    "selected must be None or an item from _items or a station from _stations or a container from _containers"
                )

        self._selected = selected
