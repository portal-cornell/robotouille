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

# with open(config_file_path, "r") as f:
#     config_data = json.load(f)

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
    surface = pygame.Surface((tile_size * 3, tile_size * 3))
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
                tile_size,
                (2 * tile_size) - i * (tile_size / 4),
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

    item_entities = renderer_data["item"]["entities"]
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
    station_entities = renderer_data["station"]["entities"]
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
        os.path.join(os.path.dirname(__file__), "theme.json"),
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

    # Group items by type
    grouped_items = {}
    item_buttons = {}
    for item, predicates in editor_state.get_item_states():
        if item.name not in grouped_items:
            grouped_items[item.name] = []
        grouped_items[item.name].append((item, predicates))

    # Create item groups with headers
    button_y = 10  # Start at top since there's no search bar
    for item_name, states in grouped_items.items():
        # Add group header
        header_text = f"{item_name.upper()} • {len(states)} STATES"
        group_header = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, button_y), (item_panel_width - 20, 30)),
            text=header_text,
            manager=manager,
            container=item_panel,
            object_id=pygame_gui.core.ObjectID(
                class_id="@label", object_id="#group_header"
            ),
        )
        button_y += 40

        # Create grid of item states (4 per row)
        button_width = 60
        button_height = 60
        spacing = (item_panel_width - 40 - (4 * button_width)) // 3

        for i, (item, predicates) in enumerate(states):
            row = i // 4
            col = i % 4
            button_x = 10 + (col * (button_width + spacing))

            def make_item_callback(item_name, predicates):
                def on_item_click():
                    selected_item = next(
                        (
                            item
                            for item in editor_state.get_items()
                            if item.name == item_name
                        ),
                        None,
                    )
                    if selected_item:
                        editor_state.set_selected((selected_item, set(predicates)))
                        print(
                            f"Selected item: {item_name} with predicates: {predicates}"
                        )

                return on_item_click

            try:
                asset = item.state_map[frozenset(predicates)]
                item_asset_path = os.path.join(
                    editor_state.get_project_root_path(), "assets", asset
                )
                img = pygame.image.load(item_asset_path).convert_alpha()
                img = pygame.transform.scale(
                    img, (button_width - 10, button_height - 10)
                )

                button_container = pygame_gui.elements.UIPanel(
                    relative_rect=pygame.Rect(
                        (button_x, button_y + (row * (button_height + 10))),
                        (button_width + 5, button_height + 5),
                    ),
                    manager=manager,
                    container=item_panel,
                    object_id=pygame_gui.core.ObjectID(
                        class_id="@panel", object_id="#item_button_container"
                    ),
                )

                item_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((0, 0), (button_width, button_height)),
                    text="",
                    manager=manager,
                    container=button_container,
                    command=make_item_callback(item.name, predicates),
                    object_id=pygame_gui.core.ObjectID(
                        class_id="@button", object_id="#item_button"
                    ),
                )

                item_button.normal_image = img
                item_button.hovered_image = img
                item_button.pressed_image = img
                item_button.rebuild()
                item_buttons[(item.name, tuple(predicates))] = item_button

            except FileNotFoundError:
                print(f"Asset not found: {item_asset_path}")
            except KeyError:
                print(
                    f"No asset found for predicates: {predicates} for item {item.name}"
                )

        button_y += ((len(states) - 1) // 4 + 1) * (button_height + 10) + 20

    station_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(
            (SCREEN_WIDTH, 0),
            (SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN),
        ),
        manager=manager,
        visible=False,
        container=None,
    )

    # Station header
    station_header = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 10), (item_panel_width - 20, 30)),
        text="STATIONS",
        manager=manager,
        container=station_panel,
    )

    container_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(
            (SCREEN_WIDTH, 0),
            (SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN),
        ),
        manager=manager,
        visible=False,
        container=None,
    )
    container_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 0), (item_panel_width, 30)),
        text="Containers",
        manager=manager,
        container=station_panel,
    )

    # Station Buttons
    station_buttons = {}
    button_width = 60
    button_height = 60
    button_x = 10
    button_y = 50  # Adjusted since there's no search bar
    spacing = (item_panel_width - 40 - (4 * button_width)) // 3

    for i, station in enumerate(editor_state.get_stations()):
        row = i // 4
        col = i % 4
        button_x = 10 + (col * (button_width + spacing))

        def make_station_callback(station_name):
            def on_station_click():
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

            return on_station_click

        station_asset_path = os.path.join(
            editor_state.get_project_root_path(), "assets", station.asset_file
        )
        try:
            img = pygame.image.load(station_asset_path).convert_alpha()
            img = pygame.transform.scale(img, (button_width - 10, button_height - 10))

            button_container = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(
                    (button_x, button_y + (row * (button_height + 10))),
                    (button_width + 5, button_height + 5),
                ),
                manager=manager,
                container=station_panel,
                object_id=pygame_gui.core.ObjectID(
                    class_id="@panel", object_id="#item_button_container"
                ),
            )

            station_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((0, 0), (button_width, button_height)),
                text="",
                manager=manager,
                container=button_container,
                command=make_station_callback(station.name),
                object_id=pygame_gui.core.ObjectID(
                    class_id="@button", object_id="#station_button"
                ),
            )

            station_button.normal_image = img
            station_button.hovered_image = img
            station_button.pressed_image = img
            station_button.rebuild()
            station_buttons[station.name] = station_button

        except FileNotFoundError:
            print(f"Asset not found: {station_asset_path}")

    # Buttons
    button_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((10, 575), (210, 300)),
        manager=manager,
    )

    def on_export_click():
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

    def on_goal_click():
        nonlocal editing_goal
        editing_goal = not editing_goal

    def on_player_click():
        set_selected_mode("player_position")

    def on_stations_click():
        set_selected_mode("stations")

    def on_items_click():
        set_selected_mode("items")

    def on_load_click():
        nonlocal test_level, TILE_SIZE
        loaded_level = open_level()
        if loaded_level:
            test_level = loaded_level
            TILE_SIZE = int(516 // test_level.width)
            print("Level loaded successfully!")

    export_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 0), (200, 50)),
        text="Save",
        manager=manager,
        container=button_panel,
        command=on_export_click,
    )
    goal_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 50), (200, 50)),
        text="Goal",
        manager=manager,
        container=button_panel,
        command=on_goal_click,
    )
    player_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 100), (200, 50)),
        text="Set Player Position",
        manager=manager,
        container=button_panel,
        command=on_player_click,
    )
    stations_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 150), (200, 50)),
        text="Stations",
        manager=manager,
        container=button_panel,
        command=on_stations_click,
    )
    items_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 200), (200, 50)),
        text="Items",
        manager=manager,
        container=button_panel,
        command=on_items_click,
    )
    load_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 250), (200, 50)),
        text="Load",
        manager=manager,
        container=button_panel,
        command=on_load_click,
    )

    stations_button.show()
    items_button.show()
    export_button.show()
    goal_button.show()
    load_button.show()

    selected_mode = "stations"
    editing_goal = False

    # setting the grid size elements
    button_panel.hide()
    map_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect((SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 200), (400, 400)), manager=manager
    )
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((100, 50), (200, 50)),
        text="Input Map Size", manager=manager, container=map_panel)
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 200), (400, 50)),
        text="Click Enter to Save for each dimension", manager=manager, container=map_panel)
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 100), (200, 50)),
        text="Width: ", manager=manager, container=map_panel)
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 150), (200, 50)),
        text="Height: ", manager=manager, container=map_panel)

    dimension_list = []
    width_entry = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((150, 100), (125, 50)), manager=manager, container=map_panel,
        initial_text="Enter an integer")
    dimension_list.append(width_entry)
    height_entry = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((150, 150), (125, 50)), manager=manager, container=map_panel,
        initial_text="Enter an integer")
    dimension_list.append(height_entry)

    continue_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((150, 300), (100, 50)), text="Continue", manager=manager, container=map_panel)

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

    clock = pygame.time.Clock()
    running = True

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
                relative_rect=pygame.Rect((button_x, button_y + i * 60), (200, 50)),
                text=f"Ignore Order: {item._ignore_order}",
                manager=manager,
                command=(
                    lambda i: lambda: (
                        print(f"ignore_order lambda called with i = {i}"),
                        toggle_ignore_order(i=i),
                    )
                )(i),
            )
            require_top_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (button_x + 210, button_y + i * 60), (200, 50)
                ),
                text=f"Require Top: {item._require_top}",
                manager=manager,
                command=(lambda i: lambda: toggle_require_top(i=i))(i),
            )

            goal_buttons[i] = (ignore_order_button, require_top_button)

    map_width = 0
    map_height = 0
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                try:
                    number = int(event.text)
                    if event.ui_element == dimension_list[0]:
                        map_width = number
                    else:
                        map_height = number
                except ValueError:
                    print("Error: must enter an integer!")
                print("Width: " + str(map_width), "Height: " + str(map_height))

            if event.type == pygame.MOUSEWHEEL:
                level_x -= event.x * 10
                level_y += event.y * 10

            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_s) and (
                    event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META
                ):
                    on_export_click()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == continue_button:
                    print("Final Width: " + str(map_width), "Final Height: " + str(map_height))
                    map_panel.hide()
                    button_panel.show()
                    # if map_width != 0 and map_height != 0:
                    #     print("modified grid")
                    #     test_level = LevelState(map_width, map_height)
                    #     TILE_SIZE = int(516 // map_width)
                    #     print(TILE_SIZE)
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
                            editor_state.set_selected((selected_item, set(predicates)))
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
                            if editing_goal and x >= 0 and x < 3 and y >= 0 and y < 3:
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
        elif not map_panel.visible:
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
