import os
import pygame
import numpy as np

class OvercookedCanvas:

    ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

    BACKGROUND_COLOR = (219,219,238)
    LINE_COLOR = (153,178,208)

    STATION_FOOD_OFFSET = 0.25

    # LAYOUT = [
    #     [None,      None,       None,       None,       None,       None    ],
    #     [None,      "table2",   None,       None,       "board",    None    ],
    #     ["table2",  None,       None,       "table3",   None,       None    ],
    #     [None,      None,       None,       None,       None,       "table4"],
    #     [None,      "stove",    None,       None,       None,       None    ],
    #     [None,      None,       None,       None,       None,       None    ],
    # ]

    def __init__(self, layout, window_size=np.array([512,512])):
        """
        Initializes the canvas.

        Args:
            layout : List[List[Optional[str]]]
                2D array of station names (or None)
            window_size : np.array
                (width, height) of the window
        """
        self.layout = layout
        grid_dimensions = np.array([len(layout[0]), len(layout)])
        self.pix_square_size = window_size / grid_dimensions
        self.asset_directory = {}
        # self.surface = 0#pygame.Surface(window_size)

    def _get_station_position(self, station_name):
        """
        Gets the position of a station.
        
        Args:
            station_name : str
                Name of the station
        
        Returns:
            position : np.array
                (x, y) position of the station
        """
        for i, row in enumerate(self.layout):
            for j, col in enumerate(row):
                if col == station_name:
                    return np.array([j, i], dtype=float)

    def _draw_image(self, canvas, image_name, position, pix_square_size):
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
        if image_name not in self.asset_directory:
            self.asset_directory[image_name] = pygame.image.load(os.path.join(OvercookedCanvas.ASSETS_DIRECTORY, image_name))
        image = self.asset_directory[image_name]
        image = pygame.transform.scale(image, pix_square_size)
        canvas.blit(image, position)

    def _draw_food_image(self, canvas, food_name, obs, position, pix_square_size):
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

        self._draw_image(canvas, f"{food_image_name}.png", position + pix_square_size * 0.125, pix_square_size * 0.75)
    
    def _draw_floor(self, canvas, obs, pix_square_size):
        """
        Draw the floor on the canvas.

        Args:
            canvas : pygame.Surface
                Canvas to draw on
            obs : dict
                Environment observation (unused)
            pix_square_size : np.array
                (width, height) of the grid square
        """
        for row in range(len(self.layout)):
            for col in range(len(self.layout[0])):
                self._draw_image(canvas, "floorkitchen.png", np.array([col, row]) * pix_square_size, pix_square_size)
                print(f"position at ({col}, {row}) is {np.array([col, row]) * pix_square_size})")

    def _draw_stations(self, canvas, obs, pix_square_size):
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
        for i, row in enumerate(self.layout):
            for j, col in enumerate(row):
                if col is not None:
                    while col[-1].isdigit():
                        col = col[:-1]
                    self._draw_image(canvas, f"{col}.png", np.array([j, i]) * pix_square_size, pix_square_size)

    def _draw_player(self, canvas, obs, pix_square_size):
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
                pos = self._get_station_position(player_station)
                pos[1] += 1 # place the player below the station
                player_pos = pos
                self._draw_image(canvas, "robot.png", pos * pix_square_size, pix_square_size)
            if literal.predicate == "has":
                held_food_name = literal.variables[1].name
        if held_food_name:
            self._draw_food_image(canvas, held_food_name, obs, player_pos * pix_square_size, pix_square_size)

    def _draw_food(self, canvas, obs, pix_square_size):
        stack_list = [] # In the form (x, y) such that x is stacked on y
        stack_number = {} # Stores the food item and current stack number
        for literal in obs:
            if literal.predicate == "on":
                food = literal.variables[0].name
                stack_number[food] = 1
                food_station = literal.variables[1].name
                pos = self._get_station_position(food_station)
                pos[1] -= OvercookedCanvas.STATION_FOOD_OFFSET # place the food slightly above the station
                self._draw_food_image(canvas, food, obs, pos * pix_square_size, pix_square_size)
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
                            station_pos = self._get_station_position(literal.variables[1].name)
                            break
                    station_pos[1] -= self.STATION_FOOD_OFFSET + 0.1 * (stack_number[food_above] - 1)
                    self._draw_food_image(canvas, food_above, obs, station_pos * pix_square_size, pix_square_size)
                else:
                    i += 1

    def make_canvas(self, surface, obs):
        """
        Creates a canvas for rendering the environment.
        
        Args:
            surface : pygame.Surface
                Surface to draw on
            obs : dict
                Environment observation
        """
        self._draw_floor(surface, obs, self.pix_square_size)
        self._draw_stations(surface, obs, self.pix_square_size)
        self._draw_player(surface, obs, self.pix_square_size)
        self._draw_food(surface, obs, self.pix_square_size)
        return surface
