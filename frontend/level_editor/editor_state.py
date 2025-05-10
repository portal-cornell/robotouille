from declarations import Item
from typing import Optional


class EditorState:
    def __init__(
        self,
        project_root_path: str,
        asset_dir_path: str,
        config_file_path: str,
        items: Item,
        saved_file: Optional[str] = None,
    ):
        self._project_root_path: str = project_root_path
        self._asset_dir_path: str = asset_dir_path
        self._config_file_path: str = config_file_path
        self._items: Item = items
        self._saved_file: Optional[str] = saved_file
        self._selected_item: Optional[Item] = None

    def get_project_root_path(self) -> str:
        return self._project_root_path

    def get_asset_dir_path(self) -> str:
        return self._asset_dir_path

    def get_config_file_path(self) -> str:
        return self._config_file_path

    def get_items(self) -> Item:
        return self._items

    def get_saved_file(self) -> Optional[str]:
        return self._saved_file

    def set_saved_file(self, saved_file: Optional[str]) -> None:
        self._saved_file = saved_file

    def get_selected_item(self) -> Optional[Item]:
        return self._selected_item

    def set_selected_item(self, selected_item: Optional[Item]) -> None:
        if selected_item is not None and selected_item not in self._items:
            raise ValueError("selected_item must be None or an item from _items")
        self._selected_item = selected_item
