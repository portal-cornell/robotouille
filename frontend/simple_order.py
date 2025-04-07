from frontend.image import Image
import os
from frontend.orders import Order

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))

class SimpleOrder(Order):
    COMPLETE, PENDING, DISCARDED = 0, 1, 2
    WIDTH, HEIGHT = 153, 165
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
        item = None
        for id, image in self.id_to_image.items():
            item = image
        
        #TODO fix the magic numbers: ypercent & scale factor. ALL THE IMAGES ARE NOT THE SAME SIZE!!!!
        self.product = Image(
                self.screen,
                self.get_image(item), 
                x_percent=0.5,
                y_percent=0.6,
                scale_factor=(self.scale_factor/5),
                anchor="center",
            )
        
    def draw(self):
        """
        Draw all components of the order onto the screen surface.
        """
        super().draw()
        self.product.draw()
    