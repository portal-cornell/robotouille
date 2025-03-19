import pygame
from frontend.image import Image
from frontend.loading import LoadingScreen
from renderer.canvas import RobotouilleCanvas
import os
from collections import defaultdict
from frontend.orders import Order

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))

class StackableOrder(Order):
    COMPLETE, PENDING, DISCARDED = 0, 1, 2
    WIDTH, HEIGHT = 153, 165
    def __init__(self, window_size, config, time, recipe):
        """
        Initialize an Order object.

        Args:
            window_size (tuple): A tuple (width, height) representing the size of the game window.
            time (int): duration of the order in seconds
        """
        super().__init__(window_size, config, time, recipe)
        self.convert_stack_recipe()


    def create_screen(self):
        #TODO override so that screen size changes
        return super().create_screen()

    
    def convert_stack_recipe(self):
        """
        Render the recipe, stacking items nicely on top of each other.
        """
        id_stack = []
        for step in self.recipe:
            pred, arg, ids = step["predicate"], step["args"], step["ids"]
            if pred == "atop":
                top_id, bottom_id = ids
                if len(id_stack) == 0:
                    id_stack.append(top_id)
                    id_stack.append(bottom_id)
                else:
                    if top_id != id_stack[-1]:
                        raise Exception("RECIPE NOT IN ORDER")
                    id_stack.append(bottom_id)
        self.draw_stack(id_stack)


    def draw_stack(self, stack):
        """
        Draw the stack in the correct order based on `self.recipe_images`.
        Each item is rendered centered on the screen, with incremental upward stacking.
        """
        self.recipe_images = [] 
        base_x = 0.5  
        base_y = 0.7 
        stack_offset = self.config["item"]["constants"]["STATION_ITEM_OFFSET"] * (self.scale_factor/4)

        for i, id in enumerate(reversed(stack)): 
            item = self.id_image.get(id, self.default_item[id])
            y_percent = base_y - (i * stack_offset)  
            image = Image(
                self.screen,
                self.get_image(item), 
                x_percent=base_x,
                y_percent=y_percent,
                scale_factor=self.scale_factor/2,
                anchor="center",
            )
            self.recipe_images.append(image)  


    def draw(self):
        """
        Draw all components of the order onto the screen surface.
        """
        super().draw()
        for item in self.recipe_images:
            item.draw()
    