import tkinter as tk
from tkinter import filedialog
import pygame
import pygame_gui
import os
from typing import Optional
import json
import tkinter.messagebox

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
from level_state import (
    LevelState,
    NoStationAtLocationError,
    Goal,
    MissingPlayerPosition,
)
from editor_state import EditorState

from pathlib import Path
import sys

# Go two levels up from current file
sys.path.append(str(Path(__file__).resolve().parents[2]))

from robotouille import robotouille_env
from environments.env_generator import builder
from renderer.canvas import RobotouilleCanvas
from robotouille import env

config_file_path = (
    filedialog.askopenfilename(
        title="Select Robotouille Config", filetypes=[("JSON files", "*.json")]
    )
    if False
    else "frontend/level_editor/robotouille_config.json"
)

if not config_file_path:
    print("No config file selected. Exiting.")
    exit()
else:
    print(f"[CONFIG] config path: {config_file_path}")

with open(config_file_path, "r") as f:
    config_data = json.load(f)

RENDERER_CONFIG_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),  # current file's directory
        "..",
        "..",  # one directory up
        "renderer",  # "domain" folder
        "configuration",
    )
)

with open(os.path.join(RENDERER_CONFIG_DIR, "robotouille_config.json"), "r") as f:
    renderer_data = json.load(f)


DOMAIN_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),  # current file's directory
        "..",
        "..",  # one directory up
        "domain",  # "domain" folder
    )
)

with open(os.path.join(DOMAIN_DIR, "robotouille.json"), "r") as f:
    domain_data = json.load(f)

import json


def open_level() -> LevelState:
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Level JSON", filetypes=[("JSON files", "*.json")]
    )
    if not file_path:
        return None

    with open(file_path, "r") as f:
        level_json = json.load(f)

    width = level_json["width"]
    height = level_json["height"]
    level = LevelState(width, height)

    # Load stations
    if "stations" in level_json:
        for station_data in level_json["stations"]:
            name = station_data["name"]
            x = station_data["x"]
            y = height - 1 - station_data["y"]  # Invert y coordinate
            station = next(
                (s for s in editor_state.get_stations() if s.name == name), None
            )
            if station:
                level.put_station_at(StationInstance(station, Vec2(x, y)))

    # Load items
    if "items" in level_json:
        for item_data in level_json["items"]:
            print(item_data)
            name = item_data["name"]
            x = item_data["x"]
            y = height - 1 - item_data["y"]  # Invert y coordinate
            predicates = (
                set(item_data["predicates"]) if "predicates" in item_data else set()
            )
            item = next((i for i in editor_state.get_items() if i.name == name), None)
            if item:
                level.put_item_at(ItemInstance(item, predicates, Vec2(x, y)))

    # Load player
    if "players" in level_json and len(level_json["players"]) > 0:
        player_data = level_json["players"][0]
        x = player_data["x"]
        y = height - 1 - player_data["y"]  # Invert y coordinate
        level.set_player_pos(Vec2(x, y))

    return level


def render_level(
    level: LevelState, tile_size: int, asset_dir_path: str
) -> pygame.Surface:

    width = level.width
    height = level.height
    tile_size = int(516 // width)

    surface = pygame.Surface((width * tile_size, height * tile_size))

    environment_json = level.serialize()
    new_environment_json = json.dumps(environment_json)

    environment_json = json.loads(
        new_environment_json
    )  # converts string to python object
    layout, tiling = robotouille_env._parse_renderer_layout(environment_json)
    _, updated_environment_json = builder.build_problem(environment_json)
    canvas = RobotouilleCanvas(
        renderer_data, layout, tiling, environment_json["players"]
    )
    initial_state = env.build_state(
        domain_data, updated_environment_json, layout, "immediate"
    )
    canvas.draw_to_surface(surface, initial_state)

    # Draw grid
    for x in range(0, width * tile_size, tile_size):
        pygame.draw.line(surface, NEUTRALDARK, (x, 0), (x, height * tile_size))
    for y in range(0, height * tile_size, tile_size):
        pygame.draw.line(surface, NEUTRALDARK, (0, y), (width * tile_size, y))

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
            item.get_asset(),
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

    from frontend.loading import LoadingScreen

    loading = LoadingScreen((SCREEN_WIDTH, SCREEN_HEIGHT))
    loading.load_all_assets()

    # game variables
    ROWS = 6
    COLS = 6
    TILE_SIZE = 86

    test_level = LevelState(COLS, ROWS)

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
    button_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((10, 575), (200, 300)),
        manager=manager,
    )
    export_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 0), (200, 50)),
        text="Save",
        manager=manager,
        container=button_panel,
    )
    goal_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 50), (200, 50)),
        text="Goal",
        manager=manager,
        container=button_panel,
    )
    player_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 100), (200, 50)),
        text="Set Player Position",
        manager=manager,
        container=button_panel,
    )
    stations_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 150), (200, 50)),
        text="Stations",
        manager=manager,
        container=button_panel,
    )
    items_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 200), (200, 50)),
        text="Items",
        manager=manager,
        container=button_panel,
    )
    load_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 250), (200, 50)),
        text="Load",
        manager=manager,
        container=button_panel,
    )

    stations_button.show()
    items_button.show()
    export_button.show()
    goal_button.show()
    load_button.show()

    selected_mode = "stations"
    editing_goal = False

    def set_selected_mode(mode):
        nonlocal selected_mode
        item_panel.hide()
        station_panel.hide()
        selected_mode = mode
        if mode == "items":
            if not isinstance(editor_state.get_selected(), Item):
                editor_state.set_selected(None)
            item_panel.show()
        elif mode == "stations":
            if not isinstance(editor_state.get_selected(), Station):
                editor_state.set_selected(None)
            station_panel.show()
        elif mode == "player_position":
            editor_state.set_selected(None)

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

    clock = pygame.time.Clock()
    running = True

    def save_level():
        root = tk.Tk()
        root.withdraw()
        saved_file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if saved_file_path:
            try:
                level_json = test_level.serialize()
                with open(saved_file_path, "w") as f:
                    json.dump(level_json, f, indent=4)
                filename = saved_file_path.split("/")[-1].replace(".json", "")
                print(f"Level saved to {filename}")
            except MissingPlayerPosition as e:
                tkinter.messagebox.showerror("Error", str(e))

    goal_buttons = {}  # map index in goal state to two buttons

    def redraw_goal_buttons():
        nonlocal goal_buttons
        # Remove old buttons
        for buttons in goal_buttons.values():
            for button in buttons:
                button.kill()
        goal_buttons = {}

        button_x = 250
        button_y = 50
        for i, item in enumerate(test_level.goal._goal_stack):

            def toggle_ignore_order(i):
                test_level.goal._goal_stack[i]._ignore_order = (
                    not test_level.goal._goal_stack[i]._ignore_order
                )
                goal_buttons[i][0].set_text(
                    f"Ignore Order: {test_level.goal._goal_stack[i]._ignore_order}"
                )

            def toggle_require_top(i):
                test_level.goal._goal_stack[i]._require_top = (
                    not test_level.goal._goal_stack[i]._require_top
                )
                goal_buttons[i][1].set_text(
                    f"Require Top: {test_level.goal._goal_stack[i]._require_top}"
                )

            ignore_order_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((button_x, button_y + i * 60), (100, 50)),
                text=f"Ignore Order: {item._ignore_order}",
                manager=manager,
                command=lambda: (
                    print("toggled" + str(i)),
                    toggle_ignore_order(i=i),
                ),
            )
            require_top_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (button_x + 110, button_y + i * 60), (100, 50)
                ),
                text=f"Require Top: {item._require_top}",
                manager=manager,
                command=lambda: (
                    print("toggled_top" + str(i)),
                    toggle_require_top(i=i),
                ),
            )

            goal_buttons[i] = (ignore_order_button, require_top_button)

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
                if event.ui_element == player_button:
                    set_selected_mode("player_position")
                elif event.ui_element == stations_button:
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
                elif event.ui_element == load_button:
                    loaded_level = open_level()
                    if loaded_level:
                        test_level = loaded_level
                        TILE_SIZE = int(516 // test_level.width)
                        print("Level loaded successfully!")
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
                            print(selected_mode)
                            if editing_goal:
                                if isinstance(editor_state.get_selected(), tuple):
                                    item, predicates = editor_state.get_selected()
                                    new_item = ItemInstance(
                                        item,
                                        predicates,
                                        Vec2(x, y),
                                    )
                                    test_level.goal.push_goal(new_item)
                                    redraw_goal_buttons()
                            elif selected_mode == "player_position":
                                try:
                                    test_level.set_player_pos(Vec2(x, y))
                                except Exception as e:
                                    print(e)
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
                elif event.button == 3:
                    if editing_goal:
                        test_level.goal.pop_goal()
                        redraw_goal_buttons()
                    else:
                        x, y = event.pos
                        if x > SCREEN_WIDTH or y > SCREEN_HEIGHT:
                            print("Clicked outside grid")
                        else:
                            x = (x - level_x) // TILE_SIZE
                            y = (y - level_y) // TILE_SIZE
                            if len(test_level.get_items_at(Vec2(x, y))) > 0:
                                test_level.pop_item_at(Vec2(x, y))
                            else:
                                test_level.remove_station_at(Vec2(x, y))

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
