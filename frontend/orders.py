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
    
    def __init__(self, window_size, config, time, recipe):
        """
        Initialize an Order object with the necessary parameters.

        Args:
            window_size (tuple): A tuple (width, height) representing the size of the game window.
            time (int): duration of the order in seconds.
            config (dict): Configuration details for the game.
            recipe (list): List of steps or actions required for this order.
        """
        self.load_assets()  
        self.scale_factor = min(window_size[0]/1440, window_size[1]/1024)  
        self.create_screen()  
        self.background = Image(self.screen, self.background_image, self.x_percent(0), self.y_percent(0), self.scale_factor, anchor="topleft")
        self.profile = Image(self.screen, self.profile_image, self.x_percent(6), self.y_percent(6), self.scale_factor, anchor="topleft")
        self.time = time 
        self.status = Order.PENDING  
        self.config = config # robotouille_env.json
        self.recipe = recipe
        self.default_item = {}
        self.generate_images()  

    def create_screen(self):
        """
        Create a surface representing the order's screen.

        This screen will have a size scaled based on the scale factor and the default width/height.
        """
        self.width, self.height = Order.WIDTH * self.scale_factor, Order.HEIGHT * self.scale_factor
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
        Generate images for the steps in the recipe starting with "IS".

        The function processes the recipe and identifies which images should be used based on the predicates and arguments.
        """
        id_item = defaultdict(str)
        id_pred = defaultdict(list)
        
        # Iterate through the recipe and extracts predicates for steps starting with "is"
        for step in self.recipe:
            pred, arg, ids = step["predicate"], step["args"], step["ids"]
            for i in range(len(arg)):
                self.default_item[ids[i]] = arg[i]

            if pred.startswith("is"): 
                id_item[ids[0]] = arg
                id_pred[ids[0]].append(pred)
        
        # Generate a mapping of ID to image based on the predicates
        self.id_image = {}
        for id in id_item:
            assets = self.config["item"]["entities"][id_item[id][0]]["assets"]
            for pred, map in assets.items():
                if pred == "default":
                    continue
                asset, predicates = map["asset"], map["predicates"]
                if self.array_equal(id_pred[id], predicates):  # Check if predicates match
                    self.id_image[id] = asset
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
