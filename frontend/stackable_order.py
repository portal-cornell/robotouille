import pygame
from frontend.image import Image
import os
from frontend.orders import Order

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))

class StackableOrder(Order):
    COMPLETE, PENDING, DISCARDED = 0, 1, 2
    WIDTH, HEIGHT = 153, 165
    ITEM = 17
    SPACE = 9
    X, Y = 42, 43  #represents the topleft corner
    EY = 25 # Y coordinate of the topleft expanded corner
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
        self.stack_offset = StackableOrder.SPACE * self.scale_factor/self.height
        self.collapsed_y = (StackableOrder.Y + ((len(self.recipe) - 1) * StackableOrder.SPACE)) * self.scale_factor/self.height
        self.expanded_y =  (StackableOrder.EY + ((len(self.recipe) - 1) * StackableOrder.ITEM)) * self.scale_factor/self.height
        self.list_to_image()
    
    def create_screen(self):
        """
        Create a surface representing the order's screen.

        This screen will have a size scaled based on the scale factor and the default width/height.
        """

        self.width, self.height = StackableOrder.WIDTH * self.scale_factor, (StackableOrder.HEIGHT + (StackableOrder.ITEM * len(self.items))) * self.scale_factor 
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
            self.background.scale_to_size(StackableOrder.WIDTH, StackableOrder.HEIGHT)
            self.collapsed_location()


    def expanded_location(self):
        """
        Relocate all ingredients, expanding the space between the ingredients.
        """
        for i, item in enumerate(self.recipe_images):
            y_percent = self.expanded_y - (i * self.stack_offset * 3)  
            item.set_percentage(StackableOrder.Y * self.scale_factor/self.width, y_percent)


    def collapsed_location(self):
        """
        Relocate all ingredients to default location.
        """
        for i, item in enumerate(self.recipe_images):
            y_percent = self.collapsed_y - (i * self.stack_offset)  
            item.set_percentage(StackableOrder.Y * self.scale_factor/self.width, y_percent)
    
    def list_to_image(self):
        """
        Draw the stack in the correct order based on `self.recipe_images`.
        Each item is rendered centered on the screen, with incremental upward stacking.
        """
        self.recipe_images = [] 
        for i, id in enumerate(self.id_stack): 
            item = self.id_to_image.get(id, self.id_to_item[id])
            y_percent = self.collapsed_y - (i * self.stack_offset)  
            image = Image(
                self.screen,
                self.get_image(item), 
                x_percent=StackableOrder.Y * self.scale_factor/self.width,
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
    