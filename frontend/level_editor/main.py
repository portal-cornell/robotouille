import tkinter as tk
from tkinter import filedialog
import pygame
import pygame_gui
import os
from typing import Optional
import json

NEUTRAL2 = pygame.Color("#ececec")
NEUTRAL5 = pygame.Color("#656565")
NEUTRAL4 = pygame.Color("#8b8b8b")
NEUTRAL1 = pygame.Color("#ffffff")
NEUTRAL3 = pygame.Color("#cacaca")
RED1 = pygame.Color("#ff4343")
GREEN2 = pygame.Color("#36c536")
NEUTRAL6 = pygame.Color("#474747")
BEIGE4 = pygame.Color("#e5b38f")
BEIGE1 = pygame.Color("#fff1dd")
BEIGE2 = pygame.Color("#ffe7c6")
BEIGE3 = pygame.Color("#f2c8a6")
BLUE4 = pygame.Color("#126dc9")
BLUE2 = pygame.Color("#2e8cea")
BLUE1 = pygame.Color("#58a5f2")
BLUE3 = pygame.Color("#2980d7")
BEIGE6 = pygame.Color("#aa6336")
BEIGE5 = pygame.Color("#c67d5e")
GREEN3 = pygame.Color("#1da21a")
GREEN4 = pygame.Color("#2a881b")
GREEN1 = pygame.Color("#67d13d")
BEIGE7 = pygame.Color("#654c44")
GREENPASTEL = pygame.Color("#8dc57f")
GREEN0 = pygame.Color("#d3fdbf")
BLUE0 = pygame.Color("#d9ecff")
RED3 = pygame.Color("#c91e1e")
RED2 = pygame.Color("#e72121")
RED0 = pygame.Color("#ff5656")
NEUTRALDARK = pygame.Color("#292929")

from declarations import Vec2, Item, Station, ItemInstance, StationInstance
from level_state import LevelState, NoStationAtLocationError, Goal
from editor_state import EditorState


def render_level(
    level: LevelState, tile_size: int, asset_dir_path: str
) -> pygame.Surface:
    # colors
    WHITE = (255, 255, 255)
    width = level.width
    height = level.height
    tile_size = 64

    surface = pygame.Surface((width * tile_size, height * tile_size))
    surface.fill(BEIGE2)

    # Draw border
    pygame.draw.rect(surface, NEUTRAL6, surface.get_rect(), 1)

    # Draw grid
    for x in range(width + 1):
        pygame.draw.line(
            surface,
            NEUTRAL6,
            (x * tile_size, 0),
            (x * tile_size, height * tile_size),
        )
    for y in range(height + 1):
        pygame.draw.line(
            surface,
            NEUTRAL6,
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


def render_goal(tile_size: int, asset_dir_path: str, goal: Goal) -> pygame.Surface:
    # colors
    surface = pygame.Surface((tile_size, tile_size))
    surface.fill(BEIGE2)

    pygame.draw.rect(surface, NEUTRAL6, surface.get_rect(), 1)

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

    item_states = []
    for item in items.values():
        for predicates_frozen in item.state_map.keys():
            predicates = set(predicates_frozen)
            item_states.append((item, predicates))

    return EditorState(
        project_root_path,
        asset_dir_path,
        config_file_path,
        list(items.values()),
        list(stations.values()),
        item_states,
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

    test_level = LevelState(MAX_COLUMNS, ROWS)

    saved_file_path: Optional[str] = None

    # Level surface position
    level_x = 0
    level_y = 0

    # Pygame UI setup
    manager = pygame_gui.UIManager(
        (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN),
    )
    manager.set_visual_debug_mode(True)

    # Side Panels
    item_panel_width = SIDE_MARGIN
    item_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(
            (SCREEN_WIDTH, 0),
            (SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN),
        ),
        manager=manager,
        visible=False,
        container=None,
    )
    item_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 0), (item_panel_width, 30)),
        text="Items",
        manager=manager,
        container=item_panel,
    )

    station_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(
            (SCREEN_WIDTH, 0),
            (SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN),
        ),
        manager=manager,
        visible=False,
        container=None,
    )
    station_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 0), (item_panel_width, 30)),
        text="Stations",
        manager=manager,
        container=station_panel,
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
                container=station_panel,
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
        relative_rect=pygame.Rect((10, 742), (100, 50)),
        text="Save",
        manager=manager,
    )

    goal_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, 682), (100, 50)),
        text="Goal",
        manager=manager,
    )

    # Item Buttons
    item_buttons = {}
    button_width = 50
    button_height = 50
    button_x = 10
    button_y = 10
    for item, predicates in editor_state.get_item_states():
        try:
            asset = item.state_map[frozenset(predicates)]
            item_asset_path = os.path.join(
                editor_state.get_project_root_path(), "assets", asset
            )
            img = pygame.image.load(item_asset_path).convert_alpha()
            img = pygame.transform.scale(img, (button_width, button_height))
            item_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (button_x, button_y), (button_width, button_height)
                ),
                text="",
                manager=manager,
                container=item_panel,
            )
            item_button.normal_image = img
            item_button.hovered_image = img
            item_button.pressed_image = img
            item_button.rebuild()
            item_buttons[(item.name, tuple(predicates))] = item_button

            button_y += button_height + 10
        except FileNotFoundError:
            print(f"Asset not found: {item_asset_path}")
        except KeyError:
            print(f"No asset found for predicates: {predicates} for item {item.name}")

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

            if event.type == pygame.MOUSEWHEEL:
                level_x -= event.x * 10
                level_y += event.y * 10

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
                    for (item_name, predicates), button in item_buttons.items():
                        if event.ui_element == button:
                            selected_item = next(
                                (
                                    item
                                    for item in editor_state.get_items()
                                    if item.name == item_name
                                ),
                                None,
                            )
                            if selected_item:
                                editor_state.set_selected(
                                    (selected_item, set(predicates))
                                )
                                print(
                                    f"Selected item: {item_name} with predicates: {predicates}"
                                )
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
                        x = (x - level_x) // TILE_SIZE
                        y = (y - level_y) // TILE_SIZE
                        if 0 <= x < test_level.width and 0 <= y < test_level.height:
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
                            elif isinstance(editor_state.get_selected(), tuple):
                                item, predicates = editor_state.get_selected()
                                new_item = ItemInstance(
                                    item,
                                    predicates,
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

        window_surface.fill(GREENPASTEL)
        if editing_goal:
            goal_surface = render_goal(
                TILE_SIZE,
                editor_state.get_asset_dir_path(),
                test_level.goal,
            )
            window_surface.blit(goal_surface, (level_x, level_y))
        else:
            level_surface = render_level(
                test_level, TILE_SIZE, editor_state.get_asset_dir_path()
            )
            window_surface.blit(level_surface, (level_x, level_y))
        manager.draw_ui(window_surface)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    editor_state = setup()
    loop(editor_state)
