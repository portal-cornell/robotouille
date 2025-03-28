import pygame
from frontend.image import Image
from frontend.button import Button
from frontend.loading import LoadingScreen
from renderer.canvas import RobotouilleCanvas
import os
from collections import defaultdict
from frontend.orders import Order

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))

class CombinationOrder(Order):
    COMPLETE, PENDING, DISCARDED = 0, 1, 2
    WIDTH, HEIGHT = 153, 199
    def __init__(self, window_size, config, time, recipe):
        """
        Initialize an Order object.

        Args:
            window_size (tuple): A tuple (width, height) representing the size of the game window.
            time (int): duration of the order in seconds
        """
        super().__init__(window_size, config, time, recipe)
        self.product = None
    
    def _choose_container_asset(self):
        container = self.id_to_item[self.id_stack[0]]
        self.config["container"]["entities"][container]["assets"]
  

    def convert_recipe_to_list(self):
        super().convert_recipe_to_list()
        self.list_to_image()
    
    def add_ingredient(self, item, count, x_percent, y_percent):
        count = 2
        border = Image(
            self.screen,
            self.border, 
            x_percent=x_percent,
            y_percent=y_percent,
            scale_factor=self.scale_factor
        )
        self.recipe_images.append(border)

        image = Image(
            self.screen,
            self.get_image(item),
            x_percent + 6/CombinationOrder.WIDTH,
            y_percent + 7/CombinationOrder.HEIGHT,
            scale_factor=self.scale_factor/14,
        )
        self.recipe_images.append(image)  
        
        if count > 1:
            count = Button(
                self.screen,
                self.count, 
                x_percent=x_percent + 38/CombinationOrder.WIDTH,
                y_percent=y_percent + 33/CombinationOrder.HEIGHT,
                scale_factor=self.scale_factor,
                text=str(count),
                font_size=15
            )
            self.recipe_images.append(count)

    def list_to_image(self):
        """
        Draw circle and item
        """
        self.recipe_images = [] 
        offset_y = self.scale_factor * (59/CombinationOrder.WIDTH)
        offset_x = self.scale_factor * (53/CombinationOrder.HEIGHT)
        
        if len(self.items) <= 2:
            base_x = 51/CombinationOrder.WIDTH
            base_y = 62/CombinationOrder.HEIGHT
            i = 0
            for id, count in self.items.items(): 
                item = self.id_to_image.get(id, self.id_to_item[id])
                self.add_ingredient(item, count, base_x, base_y + (i * offset_y))
                i += 1
        else:
            base_x = 27/CombinationOrder.WIDTH
            base_y = 74/CombinationOrder.HEIGHT
            i = 0
            for id, count in self.items.items(): 
                item = self.id_to_image.get(id, self.id_to_item[id])
                self.add_ingredient(item, count, (base_x + ((i%2) * offset_x), base_y + ((i//2) * offset_y)))
                i += 1
        
        
    def draw(self):
        """
        Draw all components of the order onto the screen surface.
        """
        super().draw()
        for image in self.recipe_images:
            image.draw()
 
    
    def load_assets(self):
        """
        Load necessary assets (images) for the order, such as the background and profile images.
        """
        super().load_assets()
        self.border = LoadingScreen.ASSET[ASSETS_DIRECTORY]["border.png"]
        self.count = LoadingScreen.ASSET[ASSETS_DIRECTORY]["count.png"]
    