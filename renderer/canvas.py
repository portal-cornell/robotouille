import os
import pygame
import numpy as np
from copy import deepcopy

from utils.robotouille_utils import trim_item_ID
import json

class RobotouilleCanvas:
    """
    This class is responsible for drawing the game state on a pygame surface. Some of
    the rendered information isn't necessarily provided by the game state (e.g. the
    location of the stations) so it is necessary to provide a layout upon initialization.
    """

    # The directory containing the assets
    ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

    def __init__(self, config, layout, tiling, players, window_size=np.array([512,512])):
        """
        Initializes the canvas.

        Args:
            layout (List[List[Optional[str]]]): 2D array of station names (or None)
            tiling (Dict): Dictionary with tiling data
            window_size (np.array): (width, height) of the window
        """
        # The layout of the game
        self.layout = layout
        # The player's position and direction (assuming one player)
        self.player_pose = {}
        for player in players:
            player_pos = (player["x"], len(layout) - player["y"] - 1)
            self.player_pose[player["name"]] = {"position": player_pos, "direction": tuple(player["direction"])}
        grid_dimensions = np.array([len(layout[0]), len(layout)])
        # The scaling factor for a grid square
        self.pix_square_size = window_size / grid_dimensions
        # A dictionary which maps image names to loaded images
        self.asset_directory = {}
        # A dictionary which maps floor, players, items, and stations to their assets and constants
        self.config = config
        # Reference to tiling data
        self.tiling = tiling
        # Reference to the ground tileset
        self.ground_tileset = None
        self.furniture_tileset = None # TODO(chalo2000): Remove this is not used anymore
        # Raw tiling matrices
        self.ground_matrix = None
        self.furniture_matrix = None # TODO(chalo2000): Remove this is not used anymore
    
    def __deepcopy__(self, memo):
        """
        This function is called by the deepcopy function in the copy module.

        This function carries over references to objects that are not deepcopyable (PyGame surfaces)
        """
        new_canvas = RobotouilleCanvas(self.config, self.layout, self.tiling, [], np.array([1,1]))
        new_canvas.player_pose = deepcopy(self.player_pose, memo)
        new_canvas.pix_square_size = self.pix_square_size # Constant
        new_canvas.asset_directory = self.asset_directory # References to PyGame surfaces
        memo[id(self)] = new_canvas
        return new_canvas
        
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
            self.asset_directory[image_name] = pygame.image.load(os.path.join(RobotouilleCanvas.ASSETS_DIRECTORY, image_name)).convert_alpha()
        image = self.asset_directory[image_name]
        image = pygame.transform.smoothscale(image, scale)
        surface.blit(image, position)

    def _choose_item_asset(self, item_image_name, obs):
        """
        Helper function to chooses the right asset for an item based on the current predicates on the item.

        In the configuration file, each item has a dictionary of assets. Depending on the predicates on the item, 
        a different asset may be chosen. This helper takes the current set of predicates in the game state and 
        chooses the asset with the most matches, and ensures that all predicates for that asset are also true. 
        This assumes that there is no ambigiuous asset choices (i.e. two assets have the same number of matches). 
        If more than one asset has the same number of matches (and all predicates are currently true), the default
        asset is used.

        For example, an onion may have a default state, a fried state, and a cut state. If the onion is currently fried
        and also cut, but there is no asset for a fried and cut onion, the default asset will be used.
        
        Args:
            item_image_name (str): Name of the item
            obs (List[Literal]): Game state predicates

        Returns:
            chosen_asset (str): Name of the chosen asset
        """
        # Get the name of the item and store its id
        item_image_name, item_id = trim_item_ID(item_image_name)

        # Get predicates of item in current game state
        item_predicates = []        
        for literal, is_true in obs.predicates.items():   
            if is_true and literal.params[0].name == item_image_name + item_id:
                item_predicates.append(literal.name)
        
        item_config = self.config["item"]["entities"][item_image_name]

        # Find the the asset with most matches to current game state. If two or 
        # more assets have the same number of matches, the default asset is used. 
        max_matches = 0
        asset_config = item_config["assets"]
        chosen_asset = asset_config["default"]
        for asset in asset_config:
            if asset == "default":
                continue
            matches = 0
            for predicate in asset_config[asset]["predicates"]:
                if predicate in item_predicates:
                    matches += 1
            if all(predicate in item_predicates for predicate in asset_config[asset]["predicates"]):
                if matches > max_matches:
                    max_matches = matches
                    chosen_asset = asset_config[asset]["asset"]
                elif matches == max_matches:
                    chosen_asset = asset_config["default"]

        return chosen_asset

    def _draw_item_image(self, surface, item_name, obs, position):
        """
        Helper to draw a item image on the canvas.

        Args:
            surface (pygame.Surface): Surface to draw on
            item_name (str): Name of the item
            obs (List[Literal]): Game state predicates
            position (np.array): (x, y) position of the item (with pix_square_size factor accounted for)
        """
        item_image_name = self._choose_item_asset(item_name, obs)
        x_scale_factor = self.config["item"]["constants"]["X_SCALE_FACTOR"]
        y_scale_factor = self.config["item"]["constants"]["Y_SCALE_FACTOR"]

        self._draw_image(surface, f"{item_image_name}", position + self.pix_square_size * x_scale_factor, self.pix_square_size * y_scale_factor)

    def _load_tiles(self, tilings):
        """
        Load tile assets and calculate tile mappings for multiple tile spritesheets.
        
        Returns a catalog of: sprites, mappings

        Args:
            tilings (List[String]: List of paths to the tiling asset folder

        Returns:
            sprites_mappings (Dict): Dictionary where key "sprites" maps to a list of all tile sprites 
            and key "mappings" maps to a dictionary between edge corner configurations and the corresponding tile ID in the tilesheet
        """
        catalogs = []
        for t in tilings:
            catalogs.append(self._load_tiles_single(t))
        
        # It's convenient to aggregate all the separate tilesheets into a single logical one for the rest of the code
        union_sprites = []
        union_mappings = {}
        for c in catalogs:
            offset = len(union_sprites)
            union_sprites.extend(c["sprites"])
            for lk, lv in c["mappings"].items():
                for wk, wv in lv.items():
                    for ck, cv in wv.items():
                        c["mappings"][lk][wk][ck] = cv + offset
            union_mappings.update(c["mappings"])
        
        return {"sprites": union_sprites, "mappings": union_mappings}
    
    def _load_tiles_single(self, tiling):
        """
        Load tile assets and calculate tile mappings.

        Returns a catalog of: config, sprites, mappings

        Args:
            tiling (String): Path to the tiling asset folder

        Returns:
            catalog (Dict): Dictionary where key "sprites" maps to a list of all tile sprites 
            and key "mappings" maps to a dictionary between edge corner configurations and the corresponding tile ID in the tilesheet
            and key "config" maps to the json for this tileset
        """
        # Load floor config
        tiling_config_path = "tileset/" + tiling + "/config.json" # Assumes the name of the json is standardized as config.json
        with open(os.path.join(RobotouilleCanvas.ASSETS_DIRECTORY, tiling_config_path), "r") as f:
            tiling_config = json.load(f)

        # Load and slice flooring spritesheet
        spritesheet_path = "tileset/" + tiling + "/" + tiling_config["asset"]
        spritesheet = pygame.image.load(os.path.join(RobotouilleCanvas.ASSETS_DIRECTORY, spritesheet_path)).convert_alpha()
        num_sprites_x = tiling_config["columns"]
        num_sprites_y = tiling_config["rows"]
        sprite_width = spritesheet.get_width() // num_sprites_x
        sprite_height = spritesheet.get_height() // num_sprites_y
        sprites = []
        for y in range(num_sprites_y):
            for x in range(num_sprites_x):
                rect = pygame.Rect(x * sprite_width, y * sprite_height, sprite_width, sprite_height)
                sprite = spritesheet.subsurface(rect).convert_alpha()
                sprites.append(sprite)
        # Add empty sprite for index -1
        empty = pygame.Surface((1, 1), flags=pygame.SRCALPHA)
        empty.fill((0, 0, 0, 0))
        sprites.append(empty)
                
        # Parse tile ID mappings
        mappings = {}
        for word, walls in tiling_config["mappings"].items():
            entry = {}
            for data in walls:
                wall = data[0]
                corners = {}
                for t in data[1]:
                    corners[t[0]] = t[1]
                entry[wall] = corners
            mappings[word] = entry

        # Store loaded values in catalog
        catalog = {}
        catalog["config"] = tiling_config
        catalog["sprites"] = sprites
        catalog["mappings"] = mappings
        return catalog
    
    def _parse_abstract_tile_matrix(self, abstract_matrix, tiling_catalog):
        """
        Parse the given abstract tile matrix into a matrix of raw tile IDs suitable for drawing

        Args:
            abstract_matrix (List[String]): List of strings whose characters represent abstract tiles
            tiling_catalog (Dict): Catalog to reference when translating tilings
        """
        raw_matrix = [[-1] * len(abstract_matrix[0]) for _ in range(len(abstract_matrix))]
        mappings = tiling_catalog["mappings"]

        for row in range(len(abstract_matrix)):
            for column in range(len(abstract_matrix[row])):
                letter = abstract_matrix[row][column]
                if not letter in mappings:
                    continue

                # Mark north wall if at top row or a foreign tile is above this tile
                N_wall = "1" if row == 0 or abstract_matrix[row - 1][column] != letter else "0"
                # Likewise for other sides and corners
                S_wall = "1" if row == len(abstract_matrix) - 1 or abstract_matrix[row + 1][column] != letter else "0"
                W_wall = "1" if column == 0 or abstract_matrix[row][column - 1] != letter else "0"
                E_wall = "1" if column == len(abstract_matrix[row]) - 1 or abstract_matrix[row][column + 1] != letter else "0"

                NE_corner = "1" if row == 0 or column == len(abstract_matrix[row]) - 1 or abstract_matrix[row - 1][column + 1] != letter else "0"
                SE_corner = "1" if row == len(abstract_matrix) - 1 or column == len(abstract_matrix[row]) - 1 or abstract_matrix[row + 1][column + 1] != letter else "0"
                NW_corner = "1" if row == 0 or column == 0 or abstract_matrix[row - 1][column - 1] != letter else "0"
                SW_corner = "1" if row == len(abstract_matrix) - 1 or column == 0 or abstract_matrix[row + 1][column - 1] != letter else "0"

                # corners covered by a wall are redundant
                if N_wall == "1":
                    NE_corner = "0"
                    NW_corner = "0"
                if S_wall == "1":
                    SE_corner = "0"
                    SW_corner = "0"
                if W_wall == "1":
                    NW_corner = "0"
                    SW_corner = "0"
                if E_wall == "1":
                    NE_corner = "0"
                    SE_corner = "0"

                wall_key = N_wall + E_wall + S_wall + W_wall
                corner_key = NE_corner + SE_corner + SW_corner + NW_corner

                letter_mappings = mappings[letter]
                wall_data = letter_mappings[wall_key] if wall_key in letter_mappings else letter_mappings["0000"]
                tile_ID = wall_data[corner_key] if corner_key in wall_data else wall_data["0000"]
                raw_matrix[row][column] = tile_ID - 1
        return raw_matrix


    def _draw_tiles(self, surface, sprites, raw_tile_matrix):
        """
        Draw tiles on the canvas.

        Args:
            surface (pygame.Surface): Surface to draw on
            sprites (List[pygame.Surface]): List of tile sprites
            raw_tile_matrix (List[List[int]]): Matrix of tile IDs (corresponding to sprites indices) 
        """
        clamped_pix_square_size = np.ceil(self.pix_square_size) # Necessary to avoid 1 pixel gaps from decimals
        for row in range(len(self.layout)):
            for col in range(len(self.layout[0])):
                # draws the image directly instead of calling _draw_images since tile sprites are not individually in asset_directory
                image = pygame.transform.smoothscale(sprites[raw_tile_matrix[row][col]], clamped_pix_square_size)
                surface.blit(image, np.array([col, row]) * clamped_pix_square_size)


    def _choose_container_asset(self, container_image_name, obs):
        """
        Helper function to choose the container asset based on the current 
        true predicates in the state.

        Meals can only be in containers, and cannot be drawn on their own. In the
        state, the predicate "in" determines whether a meal is in a container.
        Only one meal can be in each container at any point in time, so this 
        helper function chooses the container asset based on the current
        state of the meal. 

        Args:
            container_image_name (str): Name of the container
            obs (List[Literal]): Game state predicates

        Returns:
            chosen_asset (str): Name of the chosen asset
        """
        container_image_name, container_id = trim_item_ID(container_image_name)
        container_config = self.config["container"]["entities"][container_image_name]

        # Get the name of the meal in the container
        meal_name = None
        for literal, is_true in obs.predicates.items():
            if is_true and literal.name == "in" and literal.params[1].name == container_image_name + container_id:
                meal_name = literal.params[0].name
                break
        
        # If there is no meal in the container, use the default asset
        if meal_name is None:
            return container_config["assets"]["default"]
        
        # If there is a meal in the container, choose the asset based on the meal
        # Find the predicates of the meal in the current game state
        item_predicates = {}
        for literal, is_true in obs.predicates.items():
            if is_true:
                literal_args = [param.name for param in literal.params]
                if meal_name in literal_args:
                    item_predicates[literal.name] = [param.name for param in literal.params]
        
        meal_name, _ = trim_item_ID(meal_name)
        max_matches = 0
        meal_config = container_config["assets"][meal_name]
        chosen_asset = meal_config["default"]
        for asset in meal_config:
            if asset == "default":
                continue
            matches = 0
            # Find the number of matches between the current predicates and the meal's predicates
            for predicate in meal_config[asset]["predicates"]:
                if predicate["name"] in item_predicates:
                    params = []
                    pred_params = [trim_item_ID(param)[0] for param in item_predicates[predicate["name"]]]
                    for param in predicate["params"]:
                        if param == "":
                            param = pred_params[predicate["params"].index("")]
                        params.append(param)
                    if params == pred_params:
                        matches += 1

            # If all predicates are true, choose the asset with the most matches
            if matches == len(meal_config[asset]["predicates"]):
                if matches > max_matches:
                    max_matches = matches
                    chosen_asset = meal_config[asset]["asset"]
                elif matches == max_matches:
                    chosen_asset = meal_config["default"]

        return chosen_asset
    
    def _draw_container_image(self, surface, container_name, obs, position):
        """
        Helper to draw a container image on the canvas.

        Args:
            surface (pygame.Surface): Surface to draw on
            container_name (str): Name of the container
            obs (List[Literal]): Game state predicates
            position (np.array): (x, y) position of the container (with pix_square_size factor accounted for)
        """
        container_image_name = self._choose_container_asset(container_name, obs)
        x_scale_factor = self.config["container"]["constants"]["X_SCALE_FACTOR"]
        y_scale_factor = self.config["container"]["constants"]["Y_SCALE_FACTOR"]

        self._draw_image(surface, f"{container_image_name}", position + self.pix_square_size * x_scale_factor, self.pix_square_size * y_scale_factor)

    def _draw_floor(self, surface):
        """
        Draw the floor on the canvas.

        Note the game state is not necessary to draw the floor as this rendering information
        is provided by the layout.

        Args:
            surface (pygame.Surface): Surface to draw on
        """
        if not self.ground_tileset:
            # Check if the environment has a defined custom ground tiling
            if "ground" in self.tiling:
                # load ground tile data
                self.ground_tileset = self._load_tiles(self.config["floor"]["ground"])
                self.ground_matrix = self._parse_abstract_tile_matrix(self.tiling["ground"], self.ground_tileset)
            else:
                # Otherwise, fill floor with default tile
                floor_image_name = self.config["floor"]["default"]
                clamped_pix_square_size = np.ceil(self.pix_square_size) # Necessary to avoid 1 pixel gaps from decimals
                for row in range(len(self.layout)):
                    for col in range(len(self.layout[0])):
                        self._draw_image(surface, floor_image_name, np.array([col, row]) * clamped_pix_square_size, clamped_pix_square_size)
                return

        sprites = self.ground_tileset["sprites"]
        
        self._draw_tiles(surface, sprites, self.ground_matrix)

    def _draw_furniture(self, surface):
        """
        Draw the furniture on the canvas.

        Args:
            surface (pygame.Surface): Surface to draw on
        """
        if not self.furniture_tileset:
            # load ground tile data
            self.furniture_tileset = self._load_tiles(self.config["floor"]["furniture"])
            abstract_tile_matrix = self.tiling["furniture"]
            abstract_tile_matrix = self._extract_stations_to_furniture(abstract_tile_matrix)
            self.furniture_matrix = self._parse_abstract_tile_matrix(abstract_tile_matrix, self.furniture_tileset)

        sprites = self.furniture_tileset["sprites"]
        
        self._draw_tiles(surface, sprites, self.furniture_matrix)

    def _choose_station_asset(self, station_image_name):
        """
        Helper function to get the asset name of a station. Stations imagery can
        either be images or tiles. Images are preferred over tiles.

        Args:
            station_image_name (str): Name of the station

        Returns:
            asset_info (Dict): Dictionary where "name" maps to the name of the 
            asset and "type" is "image" if the station is represented by an image
            or "tile" if represented by a tile
        """
        station_image_name, _ = trim_item_ID(station_image_name)
        station_config = self.config["station"]["entities"][station_image_name]
        if "default" in station_config["assets"]:
            return {"name": station_config["assets"]["default"], "type": "image"}
        elif "tile" in station_config["assets"]:
            return {"name": station_config["assets"]["tile"], "type": "tile"}
        else:
            raise RuntimeError("Empty station asset config: " + station_config)

    def _draw_stations(self, surface):
        """
        Draws the stations on the canvas.
        
        Note the game state is not necessary to draw the floor as this rendering information
        is provided by the layout.

        Args:
            surface (pygame.Surface): Surface to draw on
        """
        
        station_offset = self.config["station"]["constants"]["STATION_OFFSET"]
        for i, row in enumerate(self.layout):
            for j, col in enumerate(row):
                if col is not None:
                    asset_info = self._choose_station_asset(col)
                    if asset_info["type"] == "image":
                        name, _ = trim_item_ID(col)
                        offset = self.config["station"]["entities"][name]["constants"].get("STATION_OFFSET", station_offset)
                        self._draw_image(surface, asset_info["name"], np.array([j, i - offset]) * self.pix_square_size, self.pix_square_size)


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
            return self.config["player"]["robot"]["back"]
        elif direction == (0, -1):
            return self.config["player"]["robot"]["front"]
        elif direction == (1, 0):
            return self.config["player"]["robot"]["right"]
        elif direction == (-1, 0):
            return self.config["player"]["robot"]["left"]
        assert False, "Invalid player direction"
    
    def _draw_player(self, surface, obs):
        """
        Draws the player on the canvas. This implementation assumes one player.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            obs (State): Game state predicates
        """
        players = obs.get_players()
        for player in players:
            player_pos = None
            held_item_name = None
            for literal, is_true in obs.predicates.items():
                if is_true and literal.name == "loc" and literal.params[0].name == player.name:
                    player_station = literal.params[1].name
                    station_pos = self._get_station_position(player_station)
                    player_pos = self.player_pose[player.name]["position"]
                    player_pos, player_direction = self._move_player_to_station(player_pos, tuple(station_pos), self.layout)
                    self.player_pose[player.name] = {"position": player_pos, "direction": player_direction}
                    #pos[1] += 1 # place the player below the station
                    #player_pos = pos
                    robot_image_name = self._get_player_image_name(player_direction)
                    self._draw_image(surface, robot_image_name, player_pos * self.pix_square_size, self.pix_square_size)
                if is_true and literal.name == "has_item" and literal.params[0].name == player.name:
                    player_pos = self.player_pose[player.name]["position"]
                    held_item_name = literal.params[1].name
            if held_item_name:
                self._draw_item_image(surface, held_item_name, obs, player_pos * self.pix_square_size)

    def _draw_item(self, surface, obs):
        """
        This helper draws item on the canvas.

        Since item can be stacked, the stack information must first be determined with the on and atop predicates.
        Any item with an on predicate is the bottom of a stack and is drawn first. The items with atop predicates
        are then drawn in the correct order afterward.

        Args:
            surface (pygame.Surface): Surface to draw on
            obs (State): Game state predicates
        """
        stack_list = [] # In the form (x, y) such that x is stacked on y
        stack_number = {} # Stores the item item and current stack number
        station_item_offset = self.config["item"]["constants"]["STATION_ITEM_OFFSET"]
        for literal, is_true in obs.predicates.items():
            if is_true and literal.name == "item_on":
                item = literal.params[0].name
                stack_number[item] = 1
                item_station = literal.params[1].name
                pos = self._get_station_position(item_station)
                # Place the item slightly above the station
                pos[1] -= station_item_offset 
                self._draw_item_image(surface, item, obs, pos * self.pix_square_size)
            if is_true and literal.name == 'atop':
                stack = (literal.params[0].name, literal.params[1].name)
                stack_list.append(stack)
        
        # Add stacked items
        while len(stack_list) > 0:
            i = 0
            while i < len(stack_list):
                item_above, item_below = stack_list[i]
                if item_below in stack_number:
                    stack_list.remove(stack_list[i])
                    stack_number[item_above] = stack_number[item_below] + 1
                    # Get location of station
                    for literal, is_true in obs.predicates.items():
                        if is_true and literal.name == "item_at" and literal.params[0].name == item_below:
                            station_pos = self._get_station_position(literal.params[1].name)
                            break
                    item_name, _ = trim_item_ID(item_above)
                    # Check if item has a stack offset
                    stack_offset = self.config["item"]["entities"][item_name]["constants"].get("STACK_OFFSET", 0)
                    station_pos[1] -= station_item_offset + 0.1 * (stack_number[item_above] - 1) + stack_offset
                    self._draw_item_image(surface, item_above, obs, station_pos * self.pix_square_size)
                else:
                    i += 1

    def _draw_container(self, surface, obs):
        """
        This helper draws containers on the canvas.

        Args:
            surface (pygame.Surface): Surface to draw on
            obs (State): Game state predicates

        Side effects:
            Draws the containers to surface
        """
        station_container_offset = self.config["container"]["constants"]["STATION_CONTAINER_OFFSET"]
        for literal, is_true in obs.predicates.items():
            if is_true and literal.name == "container_at":
                container = literal.params[0].name
                station = literal.params[1].name
                container_pos = self._get_station_position(station)
                name, _ = trim_item_ID(container)
                container_pos[1] -= self.config["container"]["entities"][name]["constants"].get("STATION_CONTAINER_OFFSET", station_container_offset)
                self._draw_container_image(surface, container, obs, container_pos * self.pix_square_size)
            if is_true and literal.name == "has_container":
                container = literal.params[1].name
                player = literal.params[0].name
                container_pos = self.player_pose[player]["position"]
                self._draw_container_image(surface, container, obs, container_pos * self.pix_square_size)
    
    def _add_platforms_underneath_stations(self, stations, abstract_tile_matrix):
        """
        This helper adds a counter or a table underneath a station.

        If the "underneath" constant is not present for a station, the station remains unchanged. 
        Otherwise, platforms (tables or counters) are placed underneath the station based on the 
        number of adjacent platforms or the preconfigured "underneath" constant if no adjacent 
        platforms are found.

        Args:
            stations (List[Tuple[int, int, str]]): List of tuples, where each tuple contains the coordinates 
                (x, y) of the station and the station's name.
            abstract_tile_matrix (List[List[str]]): A matrix where each element represents a tile in the layout. 
                'T' represents a table, 'C' represents a counter.

        Side effects:
            Updates abstract_tile_matrix with platforms (tables or counters) added 
            underneath the apprioriate stations.
        """
        directions = [(1,0), (0,1), (-1,0), (0, -1)]

        row = len(abstract_tile_matrix)
        col = len(abstract_tile_matrix[0])
        for (x,y, station_name) in stations:
            tables = 0
            counters = 0
            underneath = self.config["station"]["entities"][station_name]["constants"].get("underneath", None)

            if underneath is None:
                continue 
            
            # counts the number of adjacent tables and counters
            for dx,dy in directions: 
                if 0 <= dx + x < row and 0 <= dy + y < col:
                    if abstract_tile_matrix[dx + x][dy +y] == 'T':
                        tables += 1
                    elif abstract_tile_matrix[dx + x][dy +y] == 'C':
                        counters += 1 
            
            if counters or tables:
                abstract_tile_matrix[x][y] = 'C' if counters > tables else 'T'
            else:
                abstract_tile_matrix[x][y] = underneath

    def _extract_stations_to_furniture(self, abstract_tile_matrix):
        """
        Searches for all stations with single letter names and places corresponding tiles in the furniture layer.
        It is assumed that stations with single letter names wish to undergo this processing step.
        The tile letter chosen is the same as the name of the station.

        Args:
            abstract_tile_matrix (List[String]): List of strings whose characters represent abstract tiles

        Returns:
        
            asbtract_tile_matrix (List[List[String]]): matrix with furniture tiles added
        """

        stations = []
        abstract_tile_matrix = [[abstract_tile_matrix[i][j] for j in range(len(abstract_tile_matrix[i]))]for i in range(len(abstract_tile_matrix))]
        for i, row in enumerate(self.layout):
            for j, col in enumerate(row):
                if col is not None:
                    asset_info = self._choose_station_asset(col)
                    if asset_info["type"] == "tile":
                        abstract_tile_matrix[i][j] = asset_info["name"]
                    else:
                        name, _ = trim_item_ID(col)
                        stations.append((i,j, name))
        self._add_platforms_underneath_stations(stations, abstract_tile_matrix)
        return abstract_tile_matrix


    def draw_to_surface(self, surface, obs):
        """
        Draws the game state to the surface.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            obs (List[Literal]): Game state predicates
        """
        self._draw_floor(surface)
        self._draw_furniture(surface)
        self._draw_stations(surface)
        self._draw_player(surface, obs)
        self._draw_item(surface, obs)
        self._draw_container(surface, obs)