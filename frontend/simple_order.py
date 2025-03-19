import pygame
from frontend.image import Image
from frontend.loading import LoadingScreen
from renderer.canvas import RobotouilleCanvas
import os
from collections import defaultdict
from frontend.orders import Order

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))

class SimpleOrder(Order):
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
        item = None
        for id, image in self.id_image.items():
            item = image
        
        self.product = Image(
                self.screen,
                self.get_image(item), 
                x_percent=0.5,
                y_percent=0.6,
                scale_factor=self.scale_factor/5,
                anchor="center",
            )
        
    def draw(self):
        """
        Draw all components of the order onto the screen surface.
        """
        super().draw()
        self.product.draw()
    