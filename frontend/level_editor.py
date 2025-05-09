import pygame
import pygame_gui
from pygame_gui.elements import UIPanel
from frontend import editor_button
import os
import json
import numpy as np

from frontend.button import Button
from frontend.loading import LoadingScreen
from robotouille import robotouille_env
from environments.env_generator import builder
from renderer.canvas import RobotouilleCanvas
from robotouille import env

pygame.init()
pygame.display.set_caption('Level Editor')

# game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LOWER_MARGIN = 300
SIDE_MARGIN = 300

window_surface = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))

# game variables
ROWS = 12
MAX_COLUMNS = 16
TILE_SIZE = SCREEN_HEIGHT // ROWS
selected_item = 0

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (144, 201, 120)
BEIGE = pygame.Color('#EDE8D0')

# world tile array
grid_data = []
for i in range(ROWS):
    r = [-1] * MAX_COLUMNS
    grid_data.append(r)

# button list
button_list = []
caption_list = []
button_col = 0
button_row = 0

background = pygame.Surface((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
background.fill(BEIGE)
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
manager.set_visual_debug_mode(True)

is_running = True

# side_panel = UIPanel(relative_rect=pygame.Rect(SCREEN_WIDTH, 0, SIDE_MARGIN + 200, SCREEN_HEIGHT), manager=manager)
side_panel = pygame.Surface((SIDE_MARGIN, SCREEN_HEIGHT))
side_panel.fill(GREEN)


# layering text
layer_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, SCREEN_HEIGHT), (100, 50)), text='Layers', manager=manager)

# button tabs
layer_list = []
layer_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((25, SCREEN_HEIGHT + 75 * 0 + 50), (100, 50)), text="stations", manager=manager)
layer_list.append(layer_button)
layer_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((25, SCREEN_HEIGHT + 75 * 1 + 50), (100, 50)), text="items", manager=manager)
layer_list.append(layer_button)
layer_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((25, SCREEN_HEIGHT + 75 * 2 + 50), (100, 50)), text="containers", manager=manager)
layer_list.append(layer_button)


loading = LoadingScreen((SCREEN_WIDTH, SCREEN_HEIGHT))
loading.load_all_assets()
ASSET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
# canvas drawer
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renderer")
with open(os.path.join(os.path.join(CONFIG_DIR, "configuration"), "robotouille_config.json"), "r") as f:
    config_file = json.load(f)
environment_json = builder.load_environment("level.json")
layout, tiling = robotouille_env._parse_renderer_layout(environment_json)
canvas = RobotouilleCanvas(config_file, layout, tiling, environment_json["players"])
_, environment_json = builder.build_problem(environment_json)
DOMAIN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "domain")
with open(os.path.join(DOMAIN_DIR, "robotouille.json"), "r") as f:
    config_file1 = json.load(f)
# initial_state = env.build_state(config_file1, environment_json, layout, False)

# draw grid
def draw_grid():
    # vertical lines
    for col in range(MAX_COLUMNS + 1):
        pygame.draw.line(background, WHITE, (col * TILE_SIZE, 0), (col * TILE_SIZE, SCREEN_HEIGHT))
    # horizontal lines
    for row in range(ROWS + 1):
        pygame.draw.line(background, WHITE, (0, row * TILE_SIZE), (SCREEN_WIDTH, row * TILE_SIZE))

# get config and asset info
def get_config_info(config_file):
    config_list = []
    for object_type in config_file:
        if object_type == "station":
            button_col1 = 0
            button_row1 = 0
            for button_name in config_file[object_type]["entities"]:
                for image_type in config_file[object_type]["entities"][button_name]["assets"]:
                    if image_type == "default":
                        station_button_image = config_file[object_type]["entities"][button_name]["assets"]["default"]
                        print("image name: " + station_button_image)
                    image = loading.ASSET[ASSET_DIR][station_button_image]
                    image_scale = 0.1
                    if image.get_width() != 512 and image.get_height() != 512:
                        image_scale = 0.03
                    font = pygame.font.SysFont(None, 20)
                    text = font.render(button_name, True, (0, 0, 0))
                    button = editor_button.Button((75 * button_col1) + 50, 75 * button_row1 + 50, image, image_scale, text, 75 * button_col1 + 55, 75 * button_row1 + 100)
                    button_col1 += 1
                    if button_col1 % 3 == 0:
                        button_row1 += 1
                        button_col1 = 0
                    button_dict = {"type": "station", "name": button_name, "button": button}
                    config_list.append(button_dict)
        if object_type == "item":
            button_col = 0
            button_row = 0
            for button_name in config_file[object_type]["entities"]:
                for image_type in config_file[object_type]["entities"][button_name]["assets"]:
                    if image_type == "default":
                        item_button_image = config_file[object_type]["entities"][button_name]["assets"]["default"]
                        predicates = []
                    else:
                        item_button_image = config_file[object_type]["entities"][button_name]["assets"][image_type]["asset"]
                        predicates = config_file[object_type]["entities"][button_name]["assets"][image_type]["predicates"]
                    print("image name:" + item_button_image)
                    image = loading.ASSET[ASSET_DIR][item_button_image]
                    image_scale = 0.1
                    if image.get_width() != 512 and image.get_height() != 512:
                        image_scale = 0.4
                    font = pygame.font.SysFont(None, 20)
                    text = font.render(button_name, True, (0, 0, 0))
                    button = editor_button.Button((75 * button_col) + 50, 75 * button_row + 50, image, image_scale, text, 75 * button_col + 55, 75 * button_row + 100)
                    button_col += 1
                    if button_col % 3 == 0:
                        button_row += 1
                        button_col = 0
                    button_dict = {"type": "item", "name": button_name, "button": button, "predicates": predicates}
                    config_list.append(button_dict)
    return config_list

asset_list = get_config_info(config_file)

def draw_inventory(object_type, object_list):
    for object in object_list:
        if object["type"] == object_type:
            button = object["button"]
            button.draw(side_panel)

# draw items on grid
def draw_items_grid():
    for y_coord, row in enumerate(grid_data):
        for x_coord, tile in enumerate(row):
            if tile >= 0:
                font = pygame.font.SysFont(None, 24)
                text = font.render("" + str(tile), True, (0, 0, 0))
                background.blit(text, (x_coord * TILE_SIZE + 10, y_coord * TILE_SIZE + 15))

# returns true if can add object onto grid, false if not
def can_add_object(object_type, x_coord, y_coord):
    if object_type == "stations": # can only add station if there is nothing there
        return grid_data[y_coord][x_coord] < 0
    if object_type == "items": # can only add items if there is a station
        return object_on_grid(x_coord, y_coord, "stations")
    if object_type == "containers": # can only add container if there is only a station there
        return object_on_grid(x_coord, y_coord, "stations") and not (object_on_grid(x_coord, y_coord, "containers") or object_on_grid(x_coord, y_coord, "items"))

# returns true if there is already an object at that location, false if not
def object_on_grid(x_coord, y_coord, object_name):
    for element in environment_json[object_name]:
        if element["x"] is x_coord and element["y"] is y_coord:
            return True
    return False


selected_tab = 0
while is_running:
    time_delta = clock.tick(60) / 1000.0
    draw_grid()
    draw_items_grid()
    # draw tile panel and tiles
    # pygame.draw.rect(background, BLACK, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))
    background.blit(side_panel, (SCREEN_WIDTH, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # for i in range(len(button_list)):
                # if event.ui_element == button_list[i]:
                #     selected_item = i + 1
                #     print(f"Selected: item {selected_item}")
            for i in range(len(layer_list)):
                if event.ui_element == layer_list[i]:
                    object_type = ""
                    if i == 0:
                        object_type = "station"
                    elif i == 1:
                        object_type = "item"
                    else:
                        object_type = "container"
                    side_panel.fill(GREEN)
                    print("Selected " + object_type)
                    draw_inventory(object_type, asset_list)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x,y = event.pos
                if x > SCREEN_WIDTH or y > SCREEN_HEIGHT:
                    print("Clicked outside grid")
                else:
                    if selected_item > 0:
                        x = x // TILE_SIZE
                        y = y // TILE_SIZE
                        object = {"name": selected_item, "x": x, "y": y}
                        if selected_tab == 1:
                            key_name = "stations"
                        if selected_tab == 2:
                            key_name = "items"
                            stack_level = 0
                            for item in environment_json["items"]:
                                if item["x"] is x and item["y"] is y: # increase stack level if item is under
                                    stack_level = item["stack-level"] + 1
                            object = {"name": selected_item, "x": x, "y": y, "stack-level": stack_level}
                        if selected_tab == 3:
                            key_name = "containers"
                        object_list = environment_json[key_name]
                        if can_add_object(key_name, x, y):
                            object_list.append(object)
                            grid_data[y][x] = selected_item
                            print(f"Placed: item {selected_item} at ({x}, {y})")
                        else:
                            print("cannot add object")

                        new_environment_json = json.dumps(environment_json)
                        environment_json = json.loads(new_environment_json) # converts string to python object


        manager.process_events(event)
    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)
    pygame.display.update()



