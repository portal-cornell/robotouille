import pygame
from frontend.constants import *
from frontend.image import Image
from frontend.loading import LoadingScreen

# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders")

class Order:
    width, height= 153, 165
    def __init__(self, window_size):
        """
        Initialize a Order object.

        Args:
            window_size (tuple): (width, height) of the window/canvas
        """
        self.load_assets()
        self.scale_factor = min(window_size[0]/1440, window_size[1]/1024)
        self.width, self.height = Order.width * self.scale_factor, Order.height * self.scale_factor
        self.screen = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.background = Image(self.screen, self.background_image, self.x_percent(0), self.y_percent(0), self.scale_factor, anchor="topleft")
        self.profile = Image(self.screen, self.profile_image, self.x_percent(6), self.y_percent(6), self.scale_factor, anchor="topleft")
        
    def x_percent(self,value):
        return value/self.width
    
    def y_percent(self,value):
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
        """Draws all the screen components."""
        self.background.draw()
        self.profile.draw()
    
    def get_screen(self):
        return self.screen
  
    

   