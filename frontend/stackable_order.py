import pygame
from frontend.image import Image
import os
from frontend.orders import Order
from collections import defaultdict, deque

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))

class StackableOrder(Order):
    COMPLETE, PENDING, DISCARDED = 0, 1, 2
    WIDTH, HEIGHT = 153, 165
    ITEM = 17
    SPACE = 9
    X, Y = 42, 44  #represents the topleft corner
    EY = 38 # Y coordinate of the topleft expanded corner
    def __init__(self, window_size, config, time, recipe, offset_x, offset_y):
        """
        Initialize an Order object.

        Args:
            window_size (tuple): A tuple (width, height) representing the size of the game window.
            config (dict): Configuration details for the game.
            time (int): duration of the order in seconds.
            recipe (list): List of steps or actions required for this order.
            offset_x (int): Represents the number of pixels vertically this nodes is offseted from the top level parent screen
            offset_y (int): Represents the number of pixels horizonally this nodes is offseted from the top level parent screen
        """
        super().__init__(window_size, config, time, recipe, offset_x, offset_y)
        self.stack_collapse_offset = (StackableOrder.SPACE * self.scale_factor)/self.height
        self.stack_expanded_offset = (StackableOrder.ITEM * self.scale_factor)/self.height
        self.collapsed_y = (StackableOrder.Y  * self.scale_factor)/self.height # represents the last image, the y coordinate of the bottom image in the stack
        self.expanded_y = (StackableOrder.EY  * self.scale_factor)/self.height
        self.list_to_image()
        self.background.scale_to_size(StackableOrder.WIDTH, self.compressed_height/self.scale_factor)
    
    def create_screen(self):
        """
        Create a surface representing the order's screen.

        This screen will have a size scaled based on the scale factor and the default width/height.
        """
        self.compressed_height = (StackableOrder.HEIGHT + (StackableOrder.SPACE * (len(self.id_stack)-4))) * self.scale_factor 
        self.width, self.height = StackableOrder.WIDTH * self.scale_factor, (StackableOrder.HEIGHT + (StackableOrder.ITEM * (len(self.id_stack)-2))) * self.scale_factor 
        self.screen = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def check_hover(self): 
        """
        Check whether mouse is over the recipe and modifies recipe if hovering
        """
        self.hover = self._in_bound(pygame.mouse.get_pos())
        if self.hover:
            self.background.scale_to_size(StackableOrder.WIDTH, self.height/self.scale_factor)
            self.expanded_location()
        else:
            self.background.scale_to_size(StackableOrder.WIDTH, self.compressed_height/self.scale_factor)
            self.collapsed_location()


    def expanded_location(self):
        """
        Relocate all ingredients, expanding the space between the ingredients.
        """
        for i, item in enumerate(self.recipe_images):
            y_percent = self.expanded_y + ((len(self.recipe_images) - i) * self.stack_expanded_offset)  
            item.set_percentage(StackableOrder.X * self.scale_factor/self.width, y_percent)


    def collapsed_location(self):
        """
        Relocate all ingredients to default location.
        """
        for i, item in enumerate(self.recipe_images):
            y_percent = self.collapsed_y + ((len(self.recipe_images) - i) * self.stack_collapse_offset)  
            item.set_percentage(StackableOrder.X * self.scale_factor/self.width, y_percent)
    
    def list_to_image(self):
        """
        Draw the stack in the correct order based on `self.recipe_images`.
        Each item is rendered centered on the screen, with incremental upward stacking.
        """
        self.recipe_images = [] 
        for i, id in enumerate(self.id_stack): 
            item = self.id_to_image.get(id, self.id_to_item[id])
            y_percent = self.collapsed_y + ((len(self.recipe_images) - i) * self.stack_collapse_offset)   
            image = Image(
                self.screen,
                self.get_image(item), 
                x_percent=StackableOrder.X * self.scale_factor/self.width,
                y_percent=y_percent,
                scale_factor=self.scale_factor,
            )
            image.scale_to_size(68,68)
            self.recipe_images.append(image)  

    def draw(self):
        """
        Draw all components of the order onto the screen surface.
        """
        super().draw()
        for item in self.recipe_images:
            item.draw()

    def convert_recipe_to_list(self):
        """
        Converts the recipe into a ordered list. For stackable orders, the 
        list is from bottom to top. For combination order, the list in order
        of how it's cooked: (i.e bowl-water-tomato)
        """
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        all_id = set()
        for step in self.recipe:
            pred, arg, ids = step["predicate"], step["args"], step["ids"]
            if pred in Order.PREDICATES:
                top, bottom = arg
                top_id, bottom_id = ids
                all_id.update(ids)
                graph[top_id].append(bottom_id)
                in_degree[bottom_id] += 1
                self._add_item(top, top_id)
                self._add_item(bottom, bottom_id)

        queue = deque([id for id in all_id if in_degree[id] == 0])
        self.id_stack = []

        while queue:
            current = queue.popleft()
            self.id_stack.append(current)
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        self.id_stack = list(reversed(self.id_stack))