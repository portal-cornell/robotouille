import pygame
from frontend.image import Image
from frontend.button import Button
from frontend.loading import LoadingScreen
import os
from frontend.orders import Order

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))

class CombinationOrder(Order):
    COMPLETE, PENDING, DISCARDED = 0, 1, 2
    WIDTH, HEIGHT = 153, 165
    ITEM = 34
    def __init__(self, window_size, config, time, recipe, offset_x, offset_y):
        """
        Initialize an Order object.

        Args:
             window_size (tuple): A tuple (width, height) representing the size of the game window.
            config (dict): Configuration details for the game.
            time (int): duration of the order in seconds.
            recipe (list): List of steps or actions required for this order.
            offset_x (int): Represents the number of pixels vertically this nodes is offseted from the parent screen
            offset_y (int): Represents the number of pixels horizonally this nodes is offseted from the parent screen
        """
        super().__init__(window_size, config, time, recipe, offset_x, offset_y)
        self.list_to_image() # generate recipe assets
        self.choose_container_asset() # generate complete order asset
        self.product = Image(
            self.screen,
            self.get_image(self.product_image), 
            x_percent=(self.scale_factor * 32)/self.width,
            y_percent=(self.scale_factor * 51)/self.height,
            scale_factor=(self.scale_factor/5),
        )
        self.check_hover()
    
    def create_screen(self):
        """
        Create a surface representing the order's screen.

        This screen will have a size scaled based on the scale factor and the default width/height.
        """
        if len(self.items) == 2:
             self.width, self.height = CombinationOrder.WIDTH * self.scale_factor, (CombinationOrder.ITEM + CombinationOrder.HEIGHT) * self.scale_factor
        else:
            self.width, self.height = CombinationOrder.WIDTH * self.scale_factor, CombinationOrder.HEIGHT * self.scale_factor + (CombinationOrder.ITEM * ((len(self.items) - 1)//2))
        self.screen = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def choose_container_asset(self):
        """
        Generates the complete order asset
        """
        container = self.id_to_item[self.id_stack[0]]
        container_assets = self.config["container"]["entities"][container]["assets"]
        meal_name = None
        item_predicates = []
        for pred in self.recipe:
            item_predicates.append({"name": pred["predicate"], "params": pred["args"]})
            if pred["predicate"] == "in" and pred["args"][1] == container:
                meal_name = pred["args"][0]
                break
        if not meal_name:
            return container_assets.get("default", None)
        self.product_image = self.find_best_asset(container_assets, item_predicates)
        
    def _predicate_match(self, p1, p2):
        """
        Compares two predicates to determine if they match, treating '' as wildcard.

        Args:
            p1 (dict): A predicate with name and params key.
            p2 (dict): Another predicate with name and params key.

        Returns:
            bool: True if predicates match (empty strings count as wildcards), otherwise False.
        """
        if p1["name"] != p2["name"]:
            return False
        if len(p1["params"]) != len(p2["params"]):
            return False
        for a, b in zip(p1["params"], p2["params"]):
            if a != "" and b != "" and a != b:
                return False
        return True

    def _count_predicate_matches(self, target_predicates, item_predicates):
        """
        Counts how many predicates in item_predicates match those in target_predicates.

        Args:
            target_predicates (list): List of predicates from roboutouille_config for the specific asset.
            item_predicates (list): Predicates derived from the recipe.

        Returns:
            int: Number of matches.
        """
        count = 0
        for target_p in target_predicates:
            for item_p in item_predicates:
                if self._predicate_match(target_p, item_p):
                    count += 1
                    break  
        return count

    def find_best_asset(self, asset, item_predicate):
        """
        Recursively searches through asset dictionary to find 
        the asset that best matches the item predicates.
        
        Args:
            asset (dict): A nested dictionary from robotouille_config["container"]["entities"][<container>]["assets"].
            item_predicate (list): The predicates to match against.

        Returns:
            str: iamge of the best-matching asset.
        """
        best_match = asset["default"]
        max_matches = 0

        def dfs(subtree):
            nonlocal best_match, max_matches
            if isinstance(subtree, dict):
                if "asset" in subtree and "predicates" in subtree:
                    matches = self._count_predicate_matches(subtree["predicates"], item_predicate)
                    if matches > max_matches:
                        max_matches = matches
                        best_match = subtree["asset"]
                else:                
                    for v in subtree.values():
                        dfs(v)
        
        dfs(asset)
        return best_match
    
    def add_ingredient(self, item, count, x_percent, y_percent):
        """
        Creates a border, image of the ingredient, and a counter
        for the specific item (if the item count is greater than 0)
        at the specified x_percent, y_percent
       
        Args:
            item (str): The ingredient name or ID.
            count (int): Quantity of the ingredient.
            x_percent (float): X position relative to width of the surface.
            y_percent (float): Y position relative to height of the surface.
        """
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
            x_percent + (self.scale_factor * 6)/self.width,
            y_percent + (self.scale_factor * 7)/self.height,
            scale_factor=self.scale_factor,
        )
        image.scale_to_size(37,37)
        self.recipe_images.append(image)  
        
        if count >= 2:
            count = Button(
                self.screen,
                self.count, 
                x_percent=x_percent + (self.scale_factor * 38)/self.width,
                y_percent=y_percent + (self.scale_factor * 33)/self.height,
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
        offset_y = (self.scale_factor * 59)/self.height
        offset_x = (self.scale_factor * 53)/self.width
        
        if len(self.items) <= 2:
            base_x = (self.scale_factor * 51)/self.width
            base_y = (self.scale_factor * 62)/self.height
            i = 0
            for item, count in self.items.items(): 
                # item = self.id_to_image.get(id, self.id_to_item[id])
                self.add_ingredient(item, count, base_x, base_y + (i * offset_y))
                i += 1
        else:
            base_x = (self.scale_factor * 27)/self.width
            base_y = (self.scale_factor * 74)/self.height
            i = 0
            for item, count in self.items.items(): 
                self.add_ingredient(item, count, base_x + ((i%2) * offset_x), base_y + ((i//2) * offset_y))
                i += 1

    def check_hover(self): 
        """
        Check whether mouse is over the recipe and modifies recipe if hovering
        """
        self.hover = self._in_bound(pygame.mouse.get_pos())
        if self.hover:
            self.background.scale_to_size(CombinationOrder.WIDTH, self.height/self.scale_factor)
        else:
            self.background.scale_to_size(CombinationOrder.WIDTH, CombinationOrder.HEIGHT)


    def draw(self):
        """
        Draw all components of the order onto the screen surface.
        """
        super().draw()
        if self.hover:
            for image in self.recipe_images:
                image.draw()
        else:
            self.product.draw()
    
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
                self.id_stack.append(top_id)
                self.id_stack.append(bottom_id)
                self._add_item(top, top_id)
                self._add_item(bottom, bottom_id)

        self.items = self.items
        self.id_stack = list(reversed(self.id_stack)) # id stack 
        
    def load_assets(self):
        """
        Load necessary assets (images) for the order, such as the background and profile images.
        """
        super().load_assets()
        self.border = LoadingScreen.ASSET[ASSETS_DIRECTORY]["border.png"]
        self.count = LoadingScreen.ASSET[ASSETS_DIRECTORY]["count.png"]
    