import tkinter as tk
from tkinter import filedialog
import pygame
import pygame_gui
import os
from typing import Optional
import json

from declarations import Vec2, Item, Station, ItemInstance, StationInstance
from level_state import LevelState, NoStationAtLocationError, Goal
from editor_state import EditorState


def render_level(
    level: LevelState, tile_size: int, asset_dir_path: str
) -> pygame.Surface:
    # colors
    WHITE = (255, 255, 255)
    BEIGE = pygame.Color("#EDE8D0")
    width = level.width
    height = level.height
    tile_size = 64

    surface = pygame.Surface((width * tile_size, height * tile_size))
    surface.fill(BEIGE)

    # Draw grid
    for x in range(width + 1):
        pygame.draw.line(
            surface,
            pygame.Color("#000000"),
            (x * tile_size, 0),
            (x * tile_size, height * tile_size),
        )
    for y in range(height + 1):
        pygame.draw.line(
            surface,
            pygame.Color("#000000"),
            (0, y * tile_size),
            (width * tile_size, y * tile_size),
        )

    # Draw stations
    for station_instance in level.get_all_stations():
        station_asset_path = os.path.join(
            asset_dir_path, station_instance.source_station.asset_file
        )
        img = pygame.image.load(station_asset_path).convert_alpha()
        img = pygame.transform.scale(img, (tile_size, tile_size))
        surface.blit(
            img,
            (station_instance.pos.x * tile_size, station_instance.pos.y * tile_size),
        )

    # Draw items
    for x in range(level.width):
        for y in range(level.height):
            items = level.get_items_at(Vec2(x, y))
            for i, item in enumerate(items):
                item_asset_path = os.path.join(
                    asset_dir_path,
                    item.source_item.state_map[frozenset(item.predicates)],
                )
                img = pygame.image.load(item_asset_path).convert_alpha()
                img = pygame.transform.scale(img, (tile_size, tile_size))
                surface.blit(
                    img,
                    (
                        item.pos.x * tile_size,
                        item.pos.y * tile_size - i * (tile_size / 4),
                    ),
                )

    return surface


def setup() -> EditorState:
    root = tk.Tk()
    root.withdraw()

    pygame.init()
    pygame.display.set_caption("Level Editor")

    root = tk.Tk()
    root.withdraw()

    dev_mode = True

    project_root_path = os.path.abspath(os.path.join(__file__, "./../../../"))
    asset_dir_path = os.path.join(project_root_path, "assets")
    print(f"[CONFIG] project root path: {project_root_path}")
    print(f"[CONFIG] asset dir path: {asset_dir_path}")
    config_file_path = (
        filedialog.askopenfilename(
            title="Select Robotouille Config", filetypes=[("JSON files", "*.json")]
        )
        if not dev_mode
        else "frontend/level_editor/robotouille_config.json"
    )

    if not config_file_path:
        print("No config file selected. Exiting.")
        exit()
    else:
        print(f"[CONFIG] config path: {config_file_path}")

    with open(config_file_path, "r") as f:
        config_data = json.load(f)

    item_entities = config_data["item"]["entities"]
    items = {}
    for item_name, item_data in item_entities.items():
        assets = item_data["assets"]
        state_map = []
        default_asset = assets.get("default")
        if default_asset:
            state_map.append(([], default_asset))
        for state_name, state_info in assets.items():
            if (
                state_name != "default"
                and "asset" in state_info
                and "predicates" in state_info
            ):
                state_map.append((state_info["predicates"], state_info["asset"]))
        items[item_name] = Item(item_name, state_map)

    stations = {}  # stations not loaded from config, hardcoded in loop()
    station_entities = config_data["station"]["entities"]
    stations = {}
    for station_name, station_data in station_entities.items():
        assets = station_data["assets"]
        default_asset = assets.get("default", "cheese.png")
        stations[station_name] = Station(station_name, default_asset)

    return EditorState(
        project_root_path,
        asset_dir_path,
        config_file_path,
        list(items.values()),
        list(stations.values()),
    )


def loop(editor_state: EditorState):
    pygame.init()
    pygame.display.set_caption("Level Renderer")

    # game window
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    LOWER_MARGIN = 300
    SIDE_MARGIN = 300

    window_surface = pygame.display.set_mode(
        (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN)
    )

    # game variables
    ROWS = 6
    MAX_COLUMNS = 6
    TILE_SIZE = 64

    # colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (144, 201, 120)
    BEIGE = pygame.Color("#EDE8D0")

    test_level = LevelState(MAX_COLUMNS, ROWS)

    saved_file_path: Optional[str] = None

    # Pygame UI setup
    manager = pygame_gui.UIManager(
        (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN),
    )
    manager.set_visual_debug_mode(True)

    # Side Panels
    item_panel_width = 200
    item_panel = pygame_gui.elements.UIScrollingContainer(
        relative_rect=pygame.Rect((SCREEN_WIDTH, 0), (item_panel_width, SCREEN_HEIGHT)),
        manager=manager,
        visible=False,
    )

    station_panel = pygame_gui.elements.UIScrollingContainer(
        relative_rect=pygame.Rect(
            (SCREEN_WIDTH + item_panel_width, 0), (item_panel_width, SCREEN_HEIGHT)
        ),
        manager=manager,
        visible=False,
    )

    # Station Buttons
    station_buttons = {}
    button_width = 50
    button_height = 50
    button_x = 10
    button_y = 10
    for station in editor_state.get_stations():
        station_asset_path = os.path.join(
            editor_state.get_project_root_path(), "assets", station.asset_file
        )
        try:
            img = pygame.image.load(station_asset_path).convert_alpha()
            img = pygame.transform.scale(img, (button_width, button_height))
            station_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (button_x, button_y), (button_width, button_height)
                ),
                text="",
                manager=manager,
                container=station_panel.get_container(),
            )
            station_button.normal_image = img
            station_button.hovered_image = img
            station_button.pressed_image = img
            station_button.rebuild()
            station_buttons[station.name] = station_button

            button_y += button_height + 10
        except FileNotFoundError:
            print(f"Asset not found: {station_asset_path}")

    # Buttons
    stations_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, 842), (100, 50)),
        text="Stations",
        manager=manager,
    )

    items_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, 802), (100, 50)),
        text="Items",
        manager=manager,
    )

    export_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH, 842), (100, 50)),
        text="Save",
        manager=manager,
    )

    goal_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH, 782), (100, 50)),
        text="Goal",
        manager=manager,
    )

    # Item Buttons
    item_buttons = {}
    button_width = 50
    button_height = 50
    button_x = 10
    button_y = 10
    for item in editor_state.get_items():
        default_asset = item.state_map[frozenset()]
        item_asset_path = os.path.join(
            editor_state.get_project_root_path(), "assets", default_asset
        )
        try:
            img = pygame.image.load(item_asset_path).convert_alpha()
            img = pygame.transform.scale(img, (button_width, button_height))
            item_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (button_x, button_y), (button_width, button_height)
                ),
                text="",
                manager=manager,
                container=item_panel.get_container(),
            )
            item_button.normal_image = img
            item_button.hovered_image = img
            item_button.pressed_image = img
            item_button.rebuild()
            item_buttons[item.name] = item_button

            button_y += button_height + 10
        except FileNotFoundError:
            print(f"Asset not found: {item_asset_path}")

    stations_button.show()
    items_button.show()
    export_button.show()
    goal_button.show()

    selected_mode = "stations"
    editing_goal = False

    def set_selected_mode(mode):
        item_panel.hide()
        station_panel.hide()
        if mode == "items":
            if not isinstance(editor_state.get_selected(), Item):
                editor_state.set_selected(None)
            item_panel.show()
        elif mode == "stations":
            if not isinstance(editor_state.get_selected(), Station):
                editor_state.set_selected(None)
            station_panel.show()

    clock = pygame.time.Clock()
    running = True

    def render_goal(
        surface: pygame.Surface, tile_size: int, asset_dir_path: str, goal: Goal
    ):
        # colors
        BEIGE = pygame.Color("#EDE8D0")
        surface.fill(BEIGE)
        items = goal._goal_stack
        for i, item in enumerate(items):
            item_asset_path = os.path.join(
                asset_dir_path,
                item.source_item.state_map[frozenset(item.predicates)],
            )
            img = pygame.image.load(item_asset_path).convert_alpha()
            img = pygame.transform.scale(img, (tile_size, tile_size))
            surface.blit(
                img,
                (
                    0,
                    0 - i * (tile_size / 4),
                ),
            )

    def save_level():
        root = tk.Tk()
        root.withdraw()
        saved_file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if saved_file_path:
            level_json = test_level.serialize()
            with open(saved_file_path, "w") as f:
                json.dump(level_json, f, indent=4)
            filename = saved_file_path.split("/")[-1].replace(".json", "")
            print(f"Level saved to {filename}")

    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_s) and (
                    event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META
                ):
                    save_level()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == stations_button:
                    set_selected_mode("stations")
                elif event.ui_element == items_button:
                    set_selected_mode("items")
                elif event.ui_element == goal_button:
                    editing_goal = not editing_goal
                elif event.ui_element == export_button:
                    root = tk.Tk()
                    root.withdraw()
                    saved_file_path = filedialog.asksaveasfilename(
                        defaultextension=".json"
                    )
                    if saved_file_path:
                        level_json = test_level.serialize()
                        with open(saved_file_path, "w") as f:
                            json.dump(level_json, f, indent=4)
                        filename = saved_file_path.split("/")[-1].replace(".json", "")
                        print(f"Level saved to {filename}")
                else:
                    # Check if it's an item button
                    for item_name, button in item_buttons.items():
                        if event.ui_element == button:
                            # selected_item = item_name
                            editor_state.set_selected(
                                next(
                                    (
                                        item
                                        for item in editor_state.get_items()
                                        if item.name == item_name
                                    ),
                                    None,
                                )
                            )
                            print(f"Selected item: {item_name}")
                            break
                    # Check if it's a station button
                    for station_name, button in station_buttons.items():
                        if event.ui_element == button:
                            editor_state.set_selected(
                                next(
                                    (
                                        station
                                        for station in editor_state.get_stations()
                                        if station.name == station_name
                                    ),
                                    None,
                                )
                            )
                            print(f"Selected station: {station_name}")
                            break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    if x > SCREEN_WIDTH or y > SCREEN_HEIGHT:
                        print("Clicked outside grid")
                    else:
                        x = x // TILE_SIZE
                        y = y // TILE_SIZE
                        if editing_goal:
                            if isinstance(editor_state.get_selected(), Item):
                                new_item = ItemInstance(
                                    editor_state.get_selected(),
                                    set(),  # Pass a set of strings
                                    Vec2(x, y),
                                )
                                test_level.goal.push_goal(new_item)
                        elif isinstance(editor_state.get_selected(), Station):
                            new_station = StationInstance(
                                editor_state.get_selected(), Vec2(x, y)
                            )
                            test_level.put_station_at(new_station)
                        elif isinstance(editor_state.get_selected(), Item):
                            new_item = ItemInstance(
                                editor_state.get_selected(),
                                set(),  # Pass a set of strings
                                Vec2(x, y),
                            )
                            try:
                                test_level.put_item_at(new_item)
                            except NoStationAtLocationError:
                                pass
                elif event.button == 3 and editing_goal:
                    test_level.goal.pop_goal()

            manager.process_events(event)
        manager.update(time_delta)

        window_surface.fill(BEIGE)
        if editing_goal:
            goal_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
            render_goal(
                goal_surface,
                TILE_SIZE,
                editor_state.get_asset_dir_path(),
                test_level.goal,
            )
            window_surface.blit(goal_surface, (0, 0))
        else:
            level_surface = render_level(
                test_level, TILE_SIZE, editor_state.get_asset_dir_path()
            )
            window_surface.blit(level_surface, (0, 0))
        manager.draw_ui(window_surface)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    editor_state = setup()
    loop(editor_state)
