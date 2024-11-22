import pygame
from frontend.constants import *
from frontend.image import Image
from frontend.loading import LoadingScreen

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))

class Order:
    WIDTH, HEIGHT = 153, 165
    def __init__(self, window_size):
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
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        profile_path = os.path.join(ASSETS_DIRECTORY, "customer-profile.png")
        self.background_image = LoadingScreen.ASSET[background_path]
        self.profile_image = LoadingScreen.ASSET[profile_path]

    
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
  
    

   