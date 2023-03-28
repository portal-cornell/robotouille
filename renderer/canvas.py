import os
import pygame
import numpy as np

ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

BACKGROUND_COLOR = (219,219,238)
LINE_COLOR = (153,178,208)

STATION_FOOD_OFFSET = 0.25

LAYOUT = [
    [None,      None,       None,       None,       None,       None    ],
    [None,      "table2",   None,       None,       "board",    None    ],
    ["table1",  None,       None,       "table3",   None,       None    ],
    [None,      None,       None,       None,       None,       "table4"],
    [None,      "stove",    None,       None,       None,       None    ],
    [None,      None,       None,       None,       None,       None    ],
]

def get_station_position(station_name):
    """
    Gets the position of a station.
    
    Args:
        station_name : str
            Name of the station
    
    Returns:
        position : np.array
            (x, y) position of the station
    """
    for i, row in enumerate(LAYOUT):
        for j, col in enumerate(row):
            if col == station_name:
                return np.array([j, i], dtype=float)

def draw_image(canvas, image_name, position, pix_square_size):
    """
    Draws an image on the canvas.
    
    Args:
        canvas : pygame.Surface
            Canvas to draw on
        image_name : str
            Name of the image
        position : np.array
            (x, y) position of the image
        pix_square_size : np.array
            (width, height) of the image
    """
    image = pygame.image.load(os.path.join(ASSETS_DIRECTORY, image_name))
    image = pygame.transform.scale(image, pix_square_size)
    canvas.blit(image, position)

def draw_food_image(canvas, food_name, obs, position, pix_square_size):
    """
    Helper to draw a food image on the canvas.

    Args:
        canvas : pygame.Surface
            Canvas to draw on
        food_name : str
            Name of the food
        obs : list
            List of literals
        position : np.array
            (x, y) position of the food (with pix_square_size factor accounted for)
        pix_square_size : np.array
            (width, height) of the food
    """
    food_image_name = food_name
    # Check if cut or cooked
    for literal in obs:
        if literal.predicate == "iscut" and literal.variables[0] == food_image_name:
            food_image_name = "cut" + food_image_name
        if literal.predicate == "iscooked" and literal.variables[0] == food_image_name:
            food_image_name = "cooked" + food_image_name
    
    # Remove and store ID
    food_id = ""
    while food_image_name[-1].isdigit():
        food_id += food_image_name[-1]
        food_image_name = food_image_name[:-1]

    draw_image(canvas, f"{food_image_name}.png", position + pix_square_size * 0.125, pix_square_size * 0.75)
        
def draw_stations(canvas, obs, pix_square_size):
    """
    Draws the stations on the canvas.
    
    Args:
        canvas : pygame.Surface
            Canvas to draw on
        obs : dict
            Environment observation (unused)
        pix_square_size : np.array
            (width, height) of the grid square
    """
    for i, row in enumerate(LAYOUT):
        for j, col in enumerate(row):
            if col is not None:
                while col[-1].isdigit():
                    col = col[:-1]
                draw_image(canvas, f"{col}.png", np.array([j, i]) * pix_square_size, pix_square_size)

def draw_player(canvas, obs, pix_square_size):
    """
    Draws the player on the canvas. This implementation assumes one player.
    
    Args:
        canvas : pygame.Surface
            Canvas to draw on
        obs : dict
            Environment observation
        pix_square_size : np.array
            (width, height) of the grid square
    """
    player_pos = None
    held_food_name = None
    for literal in obs:
        if literal.predicate == "loc":
            player_station = literal.variables[1].name
            pos = get_station_position(player_station)
            pos[1] += 1 # place the player below the station
            player_pos = pos
            draw_image(canvas, "robot.png", pos * pix_square_size, pix_square_size)
        if literal.predicate == "has":
            held_food_name = literal.variables[1].name
    if held_food_name:
        draw_food_image(canvas, held_food_name, obs, player_pos * pix_square_size, pix_square_size)

def draw_food(canvas, obs, pix_square_size):
    stack_list = [] # In the form (x, y) such that x is stacked on y
    stack_number = {} # Stores the food item and current stack number
    for literal in obs:
        if literal.predicate == "on":
            food = literal.variables[0].name
            stack_number[food] = 1
            food_station = literal.variables[1].name
            pos = get_station_position(food_station)
            pos[1] -= STATION_FOOD_OFFSET # place the food slightly above the station
            draw_food_image(canvas, food, obs, pos * pix_square_size, pix_square_size)
        if literal.predicate == 'atop':
            stack = (literal.variables[0].name, literal.variables[1].name)
            stack_list.append(stack)
    
    # Add stacked items
    while len(stack_list) > 0:
        i = 0
        while i < len(stack_list):
            food_above, food_below = stack_list[i]
            if food_below in stack_number:
                stack_list.remove(stack_list[i])
                stack_number[food_above] = stack_number[food_below] + 1
                # Get location of station
                for literal in obs:
                    if literal.predicate == "at" and literal.variables[0].name == food_below:
                        station_pos = get_station_position(literal.variables[1].name)
                        break
                station_pos[1] -= STATION_FOOD_OFFSET + 0.1 * (stack_number[food_above] - 1)
                draw_food_image(canvas, food_above, obs, station_pos * pix_square_size, pix_square_size)
            else:
                i += 1

def make_canvas(grid_dimensions, window_size, obs):
    """
    Creates a canvas for rendering the environment.
    
    Args:
        grid_size : np.array
            (col, row) dimensions of the grid
        window_size : np.array
            (width, height) of the window
        obs : dict
            Environment observation
    """
    canvas = pygame.Surface(window_size)
    canvas.fill(BACKGROUND_COLOR)

    # The size of a single grid square in pixels
    pix_square_size = window_size / grid_dimensions

    # Finally, add some gridlines
    for x in range(grid_dimensions[0] + 1):
        pygame.draw.line(
            canvas,
            LINE_COLOR,
            (0, pix_square_size[1] * x),
            (window_size[0], pix_square_size[1] * x),
            width=3,
        )
        pygame.draw.line(
            canvas,
            LINE_COLOR,
            (pix_square_size[0] * x, 0),
            (pix_square_size[0] * x, window_size[1]),
            width=3,
        )
    
    draw_stations(canvas, obs, pix_square_size)
    draw_player(canvas, obs, pix_square_size)
    draw_food(canvas, obs, pix_square_size)

    return canvas
