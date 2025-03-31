import pygame
from frontend.image import Image
from frontend.loading import LoadingScreen
from renderer.canvas import RobotouilleCanvas
import os
from collections import defaultdict

# Set up the assets directory for the frontend orders
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))

class Order:
    # Order statuses: COMPLETE, PENDING, and DISCARDED
    COMPLETE, PENDING, DISCARDED = 0, 1, 2
    
    # Default dimensions for an order (in pixels)
    WIDTH, HEIGHT = 153, 165
    
    PREDICATES = {"atop", "addedto", "in"}

    def __init__(self, window_size, config, time, recipe, offset_x, offset_y):
        """
        Initialize an Order object with the necessary parameters.

        Args:
            window_size (tuple): A tuple (width, height) representing the size of the game window.
            time (int): duration of the order in seconds.
            config (dict): Configuration details for the game.
            recipe (list): List of steps or actions required for this order.
        """
        self.load_assets() 
        self.seen = set()
        self.id_stack = []
        self.time = time 
        self.status = Order.PENDING  
        self.config = config # robotouille_env.json
        self.recipe = recipe
        self.id_to_item = {} # maps id to the name of the item
        self.id_to_image = {} # maps id to image (based on predicates)
        self.hover = False
        self.offset_y = offset_y
        self.offset_x = offset_x
        self.valid_items = set(self.config["item"]["entities"].keys()) # list of ingredients that are in the config
        self.items = defaultdict(int) # list of id in the recipe that are contained in valid_items
        self.scale_factor = min(window_size[0]/1440, window_size[1]/1024)  
        self.generate_images() 
        self.convert_recipe_to_list() 
        self.create_screen()  
        self.background = Image(self.screen, self.background_image, self.x_percent(0), self.y_percent(0), self.scale_factor, anchor="topleft")
        self.profile = Image(self.screen, self.profile_image, self.x_percent(6), self.y_percent(6), self.scale_factor, anchor="topleft")


    def check_hover(self):
        """
        Check whether mouse is over the recipe
        """
        pass

    def adjusted_mouse_position(self, mouse_pos):
        """
        Adjusts the global mouse position to account for the position of this node,
        allowing for local interaction within the node's surface.
        Args:
            mouse_pos (tuple): The current mouse position in global screen coordinates (x, y).
        Returns:
            tuple: The adjusted mouse position relative to this node's surface.
        """
        # Unpack global mouse position.
        mouse_x, mouse_y = mouse_pos

        # Adjust the position relative to the node's position.
        local_x = mouse_x - self.offset_x
        local_y = mouse_y - self.offset_y
        return (local_x, local_y)
    
    def _in_bound(self, mouse_pos):
        """
        Check if the mouse is over the object.

        Returns:
           (bool) True if the  position is within the objects's bounds; False otherwise.
        """
        mouse_x, mouse_y = mouse_pos
        local_x = mouse_x - self.offset_x
        local_y = mouse_y - self.offset_y
        return self.background._in_bound(self.adjusted_mouse_position((local_x, local_y)))
    
    def set_offset(self, offset_x, offset_y):
        """
        Set the screen offset relative to parent
        """
        self.offset_x = offset_x
        self.offset_y = offset_y
        
    def _add_item(self, item, id):
        """
        Add new ingredient to the item list
        """
        if item in self.valid_items and id not in self.seen:
            self.items[id] += 1
            self.seen.add(id)
        
    def convert_recipe_to_list(self):
        """
        Converts the recipe into a ordered list. For stackable orders, the 
        list is from bottom to top. For combination order, the list in order
        of how it's cooked: (i.e bowl-water-tomato)
        """
        for step in self.recipe:
            pred, arg, ids = step["predicate"], step["args"], step["ids"]
            if pred in Order.PREDICATES:
                top, bottom = arg
                top_id, bottom_id = ids
                if len(self.id_stack) == 0:
                    self.id_stack.append(top_id)
                    self.id_stack.append(bottom_id)
                    self._add_item(top, top_id)
                    self._add_item(bottom, bottom_id)
                else:
                    if top_id != self.id_stack[-1]:
                        raise Exception("RECIPE NOT IN ORDER")
                    self.id_stack.append(bottom_id)      
                    self._add_item(bottom, bottom_id)

        self.items = self.items
        self.id_stack = list(reversed(self.id_stack)) # id stack 

    def create_screen(self):
        """
        Create a surface representing the order's screen.

        This screen will have a size scaled based on the scale factor and the default width/height.
        """
        self.width, self.height = self.WIDTH * self.scale_factor, self.HEIGHT * self.scale_factor
        self.screen = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def array_equal(self, arr1, arr2):
        """
        Compare two arrays by checking if they contain the same elements, case-insensitive.

        Args:
            arr1 (list): First array to compare.
            arr2 (list): Second array to compare.

        Returns:
            bool: True if both arrays have the same elements (case-insensitive), False otherwise.
        """
        return sorted(s.lower() for s in arr1) == sorted(s.lower() for s in arr2)

    def generate_images(self):
        """
        Generate images for items that have been modified with predicate.
        Currently only handles predicates that begin with "IS".

        The function processes the recipe and identifies which images 
        should be used based on the predicates and arguments.
        """
        id_pred = defaultdict(list)
        
        # Iterate through the recipe and extracts predicates for steps starting with "is"
        for step in self.recipe:
            pred, arg, ids = step["predicate"], step["args"], step["ids"]
            for i in range(len(arg)):
                self.id_to_item[ids[i]] = arg[i]

            if pred.startswith("is"): 
                id_pred[ids[0]].append(pred)
        
        # Generate a mapping of ID to image based on the predicates
        for id in id_pred:
            assets = self.config["item"]["entities"][self.id_to_item[id]]["assets"]
            for pred, map in assets.items():
                if pred == "default":
                    continue
                asset, predicates = map["asset"], map["predicates"]
                if self.array_equal(id_pred[id], predicates):  # Check if predicates match
                    self.id_to_image[id] = asset
                    break

    def get_image(self, image_name):
        """
        Retrieve an image from the asset directory.

        Args:
            image_name (str): The name of the image file.

        Returns:
            str: Path to the image asset.
        """
        if image_name.endswith(".png"):
            return LoadingScreen.ASSET[RobotouilleCanvas.ASSETS_DIRECTORY][image_name]
        return LoadingScreen.ASSET[RobotouilleCanvas.ASSETS_DIRECTORY][image_name + ".png"]        

    def x_percent(self, value):
        """
        Convert a value to a percentage of the screen width.

        Args:
            value (float): The value to convert.

        Returns:
            float: The corresponding percentage of the width.
        """
        return value / self.width
    
    def y_percent(self, value):
        """
        Convert a value to a percentage of the screen height.

        Args:
            value (float): The value to convert.

        Returns:
            float: The corresponding percentage of the height.
        """
        return value / self.height

    def load_assets(self):
        """
        Load necessary assets (images) for the order, such as the background and profile images.
        """
        self.background_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["background.png"]
        self.profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["customer-profile.png"]

    def draw(self):
        """
        Draw all components of the order onto the screen surface.
        """
        self.screen.fill((0,0,0,0))
        self.background.draw() 
        self.profile.draw() 

    def get_screen(self):
        """
        Get the rendered screen of the order.

        Returns:
            pygame.Surface: The surface representing the rendered order.
        """
        return self.screen
  
    def update(self, dt):
        """
        Update the order's state based on the delta time.

        Decrease the remaining time for the order and change its status to COMPLETE or DISCARDED when necessary.

        Args:
            dt (float): The delta time in milliseconds.

        Returns:
            dt (float): The same delta time passed in the arguments.
        """
        self.time -= dt  
        if self.time <= 0:  
            self.status = Order.DISCARDED
    
    def check_order(self, array):
        """
        Check the order's status or validate against a given condition.

        This method should be overridden in subclasses to provide specific order checking functionality.
        """
        pass  
