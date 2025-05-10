import tkinter as tk
from tkinter import filedialog
import pygame
import pygame_gui
from pygame_gui.elements import UIPanel
import os
from typing import Optional
import json

from declarations import Vec2, Item, Station, ItemInstance, StationInstance
from level_state import LevelState, NoStationAtLocationError

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
    else "renderer/configuration/robotouille_config.json"
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


def render_level(level: LevelState, tile_size: int) -> pygame.Surface:

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
    for item in level.get_all_items():
        item_asset_path = os.path.join(
            asset_dir_path,
            item.source_item.state_map[frozenset(item.predicates)],
        )
        img = pygame.image.load(item_asset_path).convert_alpha()
        img = pygame.transform.scale(img, (tile_size, tile_size))
        surface.blit(img, (item.pos.x * tile_size, item.pos.y * tile_size))

    return surface


def main():
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

    # Side Panel
    item_panel_width = 200
    item_panel = pygame_gui.elements.UIScrollingContainer(
        relative_rect=pygame.Rect((SCREEN_WIDTH, 0), (item_panel_width, SCREEN_HEIGHT)),
        manager=manager,
        visible=False,
    )

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
    selected_mode = "stations"  # user should start drawing stations before objects; floors not implemented yet

    export_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH, 842), (100, 50)),
        text="Save",
        manager=manager,
    )

    # Item Buttons
    item_buttons = {}
    button_width = 50
    button_height = 50
    button_x = 10
    button_y = 10
    for item_name, item in items.items():
        default_asset = item.state_map[frozenset()]
        item_asset_path = os.path.join(project_root_path, "assets", default_asset)
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
            item_buttons[item_name] = item_button

            button_y += button_height + 10
        except FileNotFoundError:
            print(f"Asset not found: {item_asset_path}")

    run_file_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((SCREEN_WIDTH, 816), (100, 50)),
        text="Run Saved",
        manager=manager,
    )

    run_file_button.show()

    import subprocess

    def run_file(file_path):
        filename = file_path.split("/")[-1].replace(".json", "")
        command = f"python main.py ++game.envrionment_name={filename}"
        print(f"Running command: {command}")
        subprocess.Popen(command, shell=True, cwd=project_root_path, env=os.environ)

    stations_button.show()
    items_button.show()
    export_button.show()

    selected_item = None

    def set_selected_item(item_name):
        nonlocal selected_item
        selected_item = item_name

    def toggle_item_panel():
        if selected_mode == "items":
            item_panel.show()
        else:
            item_panel.hide()

    toggle_item_panel()

    def toggle_item_panel():
        if selected_mode == "items":
            item_panel.show()
        else:
            item_panel.hide()

    toggle_item_panel()

    clock = pygame.time.Clock()
    running = True

    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == stations_button:
                    selected_mode = "stations"
                    toggle_item_panel()
                elif event.ui_element == items_button:
                    selected_mode = "items"
                    toggle_item_panel()
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
                elif event.ui_element == run_file_button:
                    if saved_file_path != None:
                        run_file(saved_file_path)
                else:
                    # Check if it's an item button
                    for item_name, button in item_buttons.items():
                        if event.ui_element == button:
                            selected_item = item_name
                            print(f"Selected item: {item_name}")
                            break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    if x > SCREEN_WIDTH or y > SCREEN_HEIGHT:
                        print("Clicked outside grid")
                    else:
                        x = x // TILE_SIZE
                        y = y // TILE_SIZE
                        if selected_mode == "stations":
                            station = Station("fryer", "fryer.png")
                            new_station = StationInstance(station, Vec2(x, y))
                            test_level.put_station_at(new_station)
                        elif selected_mode == "items":
                            if selected_item:
                                new_item = ItemInstance(
                                    items[selected_item],
                                    set(),  # Pass a set of strings
                                    Vec2(x, y),
                                )
                                try:
                                    test_level.put_item_at(new_item)
                                except NoStationAtLocationError:
                                    pass

            manager.process_events(event)
        manager.update(time_delta)

        window_surface.fill(BEIGE)
        level_surface = render_level(test_level, TILE_SIZE)
        window_surface.blit(level_surface, (0, 0))
        manager.draw_ui(window_surface)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()


# def editor_v1():
#     # game window
#     SCREEN_WIDTH = 800
#     SCREEN_HEIGHT = 600
#     LOWER_MARGIN = 300
#     SIDE_MARGIN = 300

#     window_surface = pygame.display.set_mode(
#         (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN)
#     )

#     # game variables
#     ROWS = 12
#     MAX_COLUMNS = 16
#     TILE_SIZE = SCREEN_HEIGHT // ROWS
#     selected_item = 0

#     # colors
#     WHITE = (255, 255, 255)
#     BLACK = (0, 0, 0)
#     GREEN = (144, 201, 120)
#     BEIGE = pygame.Color("#EDE8D0")
#     # load tile images
#     TAB1_TYPES = 8
#     img_list = []
#     for x in range(TAB1_TYPES):
#         image_path = os.path.join(os.path.dirname(__file__), f"{x}.png")
#         img = pygame.image.load(image_path).convert_alpha()
#         img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
#         img_list.append(img)

#     # print(img_list)
#     img_list1 = img_list[:3]
#     # print(img_list1)
#     img_list2 = img_list[3:6]
#     # print(img_list2)
#     img_list3 = img_list[6:]
#     # print(img_list3)

#     background = pygame.Surface(
#         (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN)
#     )
#     background.fill(BEIGE)
#     clock = pygame.time.Clock()
#     button_path = os.path.join(os.path.dirname(__file__), "button.json")
#     manager = pygame_gui.UIManager(
#         (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN),
#         theme_path=button_path,
#     )
#     manager.set_visual_debug_mode(True)

#     is_running = True

#     # create empty tile list
#     grid_data = []
#     for i in range(ROWS):
#         r = [-1] * MAX_COLUMNS
#         grid_data.append(r)

#     # draw grid
#     def draw_grid():
#         # vertical lines
#         for col in range(MAX_COLUMNS + 1):
#             pygame.draw.line(
#                 background,
#                 WHITE,
#                 (col * TILE_SIZE, 0),
#                 (col * TILE_SIZE, SCREEN_HEIGHT),
#             )
#         # horizontal lines
#         for row in range(ROWS + 1):
#             pygame.draw.line(
#                 background, WHITE, (0, row * TILE_SIZE), (SCREEN_WIDTH, row * TILE_SIZE)
#             )

#     # draw items on grid
#     def draw_items_grid():
#         for y_coord, row in enumerate(grid_data):
#             for x_coord, tile in enumerate(row):
#                 if tile >= 0:
#                     font = pygame.font.SysFont(None, 24)
#                     text = font.render("" + str(tile), True, (0, 0, 0))
#                     background.blit(
#                         text, (x_coord * TILE_SIZE + 10, y_coord * TILE_SIZE + 15)
#                     )

#     # button list
#     button_list = []
#     button_list1 = []
#     button_list2 = []
#     button_list3 = []
#     caption_list = []
#     caption_list1 = []
#     caption_list2 = []
#     caption_list3 = []
#     button_col = 0
#     button_row = 0

#     side_panel = UIPanel(
#         relative_rect=pygame.Rect(SCREEN_WIDTH, 0, SIDE_MARGIN + 200, SCREEN_HEIGHT),
#         manager=manager,
#     )

#     # item buttons
#     for i in range(8):
#         tile_button = pygame_gui.elements.UIButton(
#             relative_rect=pygame.Rect(
#                 (SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 100), (50, 50)
#             ),
#             text="item" + str(i + 1),
#             manager=manager,
#         )
#         # caption_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(((75 * button_col) + 40, 75 * button_row + 150), (75, 25)), text='item' + str(i + 1), manager=manager, container=side_panel)
#         button_list.append(tile_button)
#         # caption_list.append(caption_list1)
#         button_col += 1
#         if button_col == 3:
#             button_row += 1
#             button_col = 0

#     # layering text
#     layer_label = pygame_gui.elements.UILabel(
#         relative_rect=pygame.Rect((0, SCREEN_HEIGHT), (100, 50)),
#         text="Layers",
#         manager=manager,
#     )

#     # button tabs
#     layer_list = []
#     for i in range(3):
#         layer_button = pygame_gui.elements.UIButton(
#             relative_rect=pygame.Rect((25, SCREEN_HEIGHT + 75 * i + 50), (100, 50)),
#             text="type" + str(i + 1),
#             manager=manager,
#         )
#         layer_list.append(layer_button)

#     selected_tab = 0
#     while is_running:
#         time_delta = clock.tick(60) / 1000.0
#         draw_grid()
#         draw_items_grid()
#         # draw tile panel and tiles
#         pygame.draw.rect(
#             background, BLACK, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT)
#         )

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 is_running = False
#             if event.type == pygame_gui.UI_BUTTON_PRESSED:
#                 print(layer_list, selected_tab)
#                 if side_panel is not None:
#                     side_panel.kill()
#                 for i in range(len(button_list)):
#                     if event.ui_element == button_list[i]:
#                         selected_item = i + 1
#                         print(f"Selected: item {selected_item}")
#                 for i in range(len(layer_list)):
#                     if event.ui_element == layer_list[i]:
#                         selected_tab = i + 1
#                         print(f"Selected: type {selected_tab}")
#                         tab_label = pygame_gui.elements.UILabel(
#                             relative_rect=pygame.Rect((40, 50), (75, 25)),
#                             text="type" + str(selected_tab),
#                             manager=manager,
#                             container=side_panel,
#                         )
#                         button_col = 0
#                         button_row = 0
#                         start = 0
#                         end = 0
#                         # have preexisting lists
#                         if selected_tab == 1:
#                             end = 3
#                         elif selected_tab == 2:
#                             start = 3
#                             end = 6

#                         else:
#                             start = 6
#                             end = 8
#                         for i in range(len(button_list)):
#                             button_list[i].hide()
#                         for i in range(start, end):
#                             print(i)
#                             print("showing")
#                             button_list[i].show()

#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if event.button == 1:
#                     x, y = event.pos
#                     if x > SCREEN_WIDTH or y > SCREEN_HEIGHT:
#                         print("Clicked outside grid")
#                     else:
#                         x = x // TILE_SIZE
#                         y = y // TILE_SIZE
#                         grid_data[y][x] = selected_item
#                         print(f"Placed: item {selected_item} at ({x}, {y})")

#             manager.process_events(event)
#         manager.update(time_delta)

#         window_surface.blit(background, (0, 0))
#         manager.draw_ui(window_surface)
#         pygame.display.update()
