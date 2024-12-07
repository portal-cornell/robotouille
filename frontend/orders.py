import pygame
from frontend.image import Image
from frontend.loading import LoadingScreen
from renderer.canvas import RobotouilleCanvas
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))

class Order:
    WIDTH, HEIGHT = 153, 165
    def __init__(self, window_size, config):
        """
        Initialize an Order object.

        Args:
            window_size (tuple): A tuple (width, height) representing the size of the game window.
        """
        self.load_assets()
        self.scale_factor = min(window_size[0]/1440, window_size[1]/1024)
        self.width, self.height = Order.WIDTH * self.scale_factor, Order.HEIGHT * self.scale_factor
        self.screen = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.background = Image(self.screen, self.background_image, self.x_percent(0), self.y_percent(0), self.scale_factor, anchor="topleft")
        self.profile = Image(self.screen, self.profile_image, self.x_percent(6), self.y_percent(6), self.scale_factor, anchor="topleft")

        self.config = config
        self.recipe =[
            {
                "predicate": "iscut",
                "args": ["lettuce"],
                "ids": [1]
            },
            {
                "predicate": "iscooked",
                "args": ["patty"],
                "ids": [2]
            },
            {
                "predicate": "atop",
                "args": ["topbun", "lettuce"],
                "ids": [3, 1]
            },
            {
                "predicate": "atop",
                "args": ["lettuce", "patty"],
                "ids": [1, 2]
            },
            {
                "predicate": "atop",
                "args": ["patty", "bottombun"],
                "ids": [2, 4]
            },
            {
                "predicate": "atop_container",
                "args": ["bottombun", "bowl"],
                "ids": [4, 5]
            },
            {
                "predicate": "container_at",
                "args": ["bowl", "customertable"],
                "ids": [5, 6]
            }
        ]

        self.convert_recipe()

    def get_image(self, image_name):
        return LoadingScreen.ASSET[RobotouilleCanvas.ASSETS_DIRECTORY][image_name + ".png"]
    
    def convert_recipe(self):
        """
        Render the recipe, stacking items nicely on top of each other.
        """

        stack = []
        map_id = {}
        for step in self.recipe:
            pred, arg, ids = step["predicate"], step["args"], step["ids"]
            if pred == "iscooked" or pred == "iscut":
                png = pred[2:] + arg[0] 
                map_id[ids[0]] = png
            elif pred == "atop":
                top_item, bottom_item = arg
                top_id, bottom_id = ids
                if len(stack) == 0:
                    stack.append(map_id.get(top_id, top_item))
                    stack.append(map_id.get(bottom_id, bottom_item))
                else:
                    if top_item not in stack[-1]:
                        raise Exception("RECIPE NOT IN ORDER")
                    stack.append(map_id.get(bottom_id, bottom_item))
        self.draw_stack(stack)


    def draw_stack(self, stack):
        """
        Draw the stack in the correct order based on `self.stack`.
        Each item is rendered centered on the screen, with incremental upward stacking.
        """
        self.stack = [] 
        base_x = 0.5  
        base_y = 0.7 
        stack_offset = self.config["item"]["constants"]["STATION_ITEM_OFFSET"] * (self.scale_factor/2)

        for i, item in enumerate(reversed(stack)): 
            y_percent = base_y - (i * stack_offset)  
            image = Image(
                self.screen,
                self.get_image(item), 
                x_percent=base_x,
                y_percent=y_percent,
                scale_factor=self.scale_factor/2,
                anchor="center",
            )
            self.stack.append(image)  


    def x_percent(self,value):
        """
        Convert a value to a percentage of the width.

        Args:
            value (float): The value to convert.

        Returns:
            float: The percentage of the width.
        """
        return value/self.width
    
    def y_percent(self,value):
        """
        Convert a value to a percentage of the height.

        Args:
            value (float): The value to convert.

        Returns:
            float: The percentage of the height.
        """
        return value/self.height

    def load_assets(self):
        """
        Loads necessary assets.
        """
        # load asset paths then images
        self.background_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["background.png"]
        self.profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["customer-profile.png"]

    
    def draw(self):
        """
        Draw all components of the order onto the screen surface.
        """
        self.background.draw()
        self.profile.draw()
        for item in self.stack:
            item.draw()
    
    def get_screen(self):
        """
        Get the rendered screen of the order.

        Returns:
            pygame.Surface: The surface representing the rendered order.
        """
        return self.screen
  
    

   