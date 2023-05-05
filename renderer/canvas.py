import os
import pygame
import numpy as np

class OvercookedCanvas:
    """
    This class is responsible for drawing the game state on a pygame surface. Some of
    the rendered information isn't necessarily provided by the game state (e.g. the
    location of the stations) so it is necessary to provide a layout upon initialization.
    """

    # The directory containing the assets
    ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

    # The offset to draw food and stations relative to the center of the grid square
    STATION_FOOD_OFFSET = 0.25

    def __init__(self, layout, player, window_size=np.array([512,512])):
        """
        Initializes the canvas.

        Args:
            layout (List[List[Optional[str]]]): 2D array of station names (or None)
            window_size (np.array): (width, height) of the window
        """
        # The layout of the game
        self.layout = layout
        # The player's position and direction (assuming one player)
        player_pos = (player["x"], len(layout) - player["y"] - 1)
        self.player_pose = {"position": player_pos, "direction": tuple(player["direction"])}
        grid_dimensions = np.array([len(layout[0]), len(layout)])
        # The scaling factor for a grid square
        self.pix_square_size = window_size / grid_dimensions
        # A dictionary which maps image names to loaded images
        self.asset_directory = {}

    def _get_station_position(self, station_name):
        """
        Gets the position of a station.
        
        Args:
            station_name (str): Name of the station
        
        Returns:
            position (np.array): (x, y) position of the station
        """
        for i, row in enumerate(self.layout):
            for j, col in enumerate(row):
                if col == station_name:
                    return np.array([j, i], dtype=float)

    def _draw_image(self, surface, image_name, position, scale):
        """
        Draws an image on the canvas.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            image_name (str): Name of the image
            position (np.array): (x, y) position of the image
            scale (np.array): (width, height) to scale the image by
        """
        if image_name not in self.asset_directory:
            self.asset_directory[image_name] = pygame.image.load(os.path.join(OvercookedCanvas.ASSETS_DIRECTORY, image_name))
        image = self.asset_directory[image_name]
        image = pygame.transform.scale(image, scale)
        surface.blit(image, position)

    def _draw_food_image(self, surface, food_name, obs, position):
        """
        Helper to draw a food image on the canvas.

        Args:
            surface (pygame.Surface): Surface to draw on
            food_name (str): Name of the food
            obs (List[Literal]): Game state predicates
            position (np.array): (x, y) position of the food (with pix_square_size factor accounted for)
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

        self._draw_image(surface, f"{food_image_name}.png", position + self.pix_square_size * 0.125, self.pix_square_size * 0.75)
    
    def _draw_floor(self, surface):
        """
        Draw the floor on the canvas.

        Note the game state is not necessary to draw the floor as this rendering information
        is provided by the layout.

        Args:
            surface (pygame.Surface): Surface to draw on
        """
        clamped_pix_square_size = np.ceil(self.pix_square_size) # Necessary to avoid 1 pixel gaps from decimals
        for row in range(len(self.layout)):
            for col in range(len(self.layout[0])):
                self._draw_image(surface, "floorkitchen.png", np.array([col, row]) * clamped_pix_square_size, clamped_pix_square_size)

    def _draw_stations(self, surface):
        """
        Draws the stations on the canvas.
        
        Note the game state is not necessary to draw the floor as this rendering information
        is provided by the layout.

        Args:
            surface (pygame.Surface): Surface to draw on
        """
        for i, row in enumerate(self.layout):
            for j, col in enumerate(row):
                if col is not None:
                    while col[-1].isdigit():
                        col = col[:-1]
                    self._draw_image(surface, f"{col}.png", np.array([j, i]) * self.pix_square_size, self.pix_square_size)

    def _get_station_locations(self, layout):
        """
        Gets the locations of all stations in the layout.

        Args:
            layout (List[List[Optional[str]]]): 2D array of station names (or None)
        
        Returns:
            station_locations (List[tuple]): List of (x, y) positions of stations
        """
        station_locations = []
        for i, row in enumerate(layout):
            for j, col in enumerate(row):
                if col is not None:
                    station_locations.append((j, i))
        return station_locations

    def _move_player_to_station(self, player_position, station_position, layout):
        """
        Moves the player from their current position to a position adjacent to a station using BFS.

        BFS is used to determine the final state. As an additional constraint, the player cannot
        move through a station or out of bounds.

        Args:
            player_position (tuple): (x, y) position of the player
            station_position (tuple): (x, y) position of the station
            layout (List[List[Optional[str]]]): 2D array of station names (or None)
        
        Returns:
            new_player_position (tuple): (x, y) position of the player after moving
            new_player_direction (tuple): unit vector of the player's direction after moving
        
        Raises:
            ValueError: If the player cannot reach the station
        """
        width, height = len(layout[0]), len(layout)
        obstacle_locations = self._get_station_locations(layout)
        curr_prev = (player_position, player_position) # current position, previous position
        queue = [curr_prev]
        visited = set()
        while queue:
            curr_prev = queue.pop(0)
            curr_position = curr_prev[0]
            prev_position = curr_prev[1]
            if curr_position == station_position:
                # Reached target station
                return prev_position, (curr_position[0] - prev_position[0], prev_position[1] - curr_position[1])
            if curr_position[0] < 0 or curr_position[0] >= width or curr_position[1] < 0 or curr_position[1] >= height:
                # Out of bounds
                continue
            if curr_position in obstacle_locations:
                # Cannot move through station
                continue
            if curr_position in visited:
                # Already visited
                continue
            visited.add(curr_position)
            for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_position = (curr_position[0] + direction[0], curr_position[1] + direction[1])
                if next_position != prev_position:
                    queue.append((next_position, curr_position))
        assert False, "Player could not be moved to station"

    def _get_player_image_name(self, direction):
        """
        Returns the image name of the player given their direction.

        Args:
            direction (tuple): Unit vector of the player's direction
        
        Returns:
            image_name (str): Image name of the player
        
        Raises:
            AssertionError: If the direction is invalid
        """
        if direction == (0, 1):
            return "robot_back.png"
        elif direction == (0, -1):
            return "robot_front.png"
        elif direction == (1, 0):
            return "robot_right.png"
        elif direction == (-1, 0):
            return "robot_left.png"
        assert False, "Invalid player direction"
    
    def _draw_player(self, surface, obs):
        """
        Draws the player on the canvas. This implementation assumes one player.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            obs (List[Literal]): Game state predicates
        """
        player_pos = None
        held_food_name = None
        for literal in obs:
            if literal.predicate == "loc":
                player_station = literal.variables[1].name
                station_pos = self._get_station_position(player_station)
                player_pos = self.player_pose["position"]
                player_pos, player_direction = self._move_player_to_station(player_pos, tuple(station_pos), self.layout)
                self.player_pose = {"position": player_pos, "direction": player_direction}
                #pos[1] += 1 # place the player below the station
                #player_pos = pos
                robot_image_name = self._get_player_image_name(player_direction)
                self._draw_image(surface, robot_image_name, player_pos * self.pix_square_size, self.pix_square_size)
            if literal.predicate == "has":
                held_food_name = literal.variables[1].name
        if held_food_name:
            self._draw_food_image(surface, held_food_name, obs, player_pos * self.pix_square_size)

    def _draw_food(self, surface, obs):
        """
        This helper draws food on the canvas.

        Since food can be stacked, the stack information must first be determined with the on and atop predicates.
        Any food with an on predicate is the bottom of a stack and is drawn first. The foods with atop predicates
        are then drawn in the correct order afterward.

        Args:
            surface (pygame.Surface): Surface to draw on
            obs (List[Literal]): Game state predicates
        """
        stack_list = [] # In the form (x, y) such that x is stacked on y
        stack_number = {} # Stores the food item and current stack number
        for literal in obs:
            if literal.predicate == "on":
                food = literal.variables[0].name
                stack_number[food] = 1
                food_station = literal.variables[1].name
                pos = self._get_station_position(food_station)
                pos[1] -= OvercookedCanvas.STATION_FOOD_OFFSET # place the food slightly above the station
                self._draw_food_image(surface, food, obs, pos * self.pix_square_size)
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
                    self._draw_food_image(surface, food_above, obs, station_pos * self.pix_square_size)
                else:
                    i += 1

    def draw_to_surface(self, surface, obs):
        """
        Draws the game state to the surface.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            obs (List[Literal]): Game state predicates
        """
        self._draw_floor(surface)
        self._draw_stations(surface)
        self._draw_player(surface, obs)
        self._draw_food(surface, obs)
