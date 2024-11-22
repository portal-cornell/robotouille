import pygame
from frontend.constants import *
from frontend.image import Image
from frontend.slider import Slider
from frontend.screen import ScreenInterface

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "loading"))

class LoadingScreen(ScreenInterface):
    ASSET = {}
    def __init__(self, window_size):
        """
        Initialize the Loading Screen.

        Args:
           window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size) 
        self.count = 0
        self.total = 0
        self.directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
        for _, _, files in os.walk(self.directory):
            for file in files:
                if file.lower().endswith((".png")):
                    self.total += 1


        self.percent = 0
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.loading_bar = Slider(self.screen, self.progress_border_image, self.progress_bar_image,
                                         573 * self.scale_factor, 93 * self.scale_factor, 539 * self.scale_factor, 61 * self.scale_factor,
                                         0.5, 0.75, filled_percent= self.percent, anchor="center", foreground_padding=(0,0,0,0))
    
    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.loading_bar.draw()
    
    def load_assets(self):
        """Load immediate necessary assets."""
        background_path = os.path.join(ASSETS_DIRECTORY, "background.png")
        progress_bar_path = os.path.join(ASSETS_DIRECTORY, "progress_bar.png")
        progress_border_path = os.path.join(ASSETS_DIRECTORY, "progress_border.png")

        self.background_image =  pygame.image.load(background_path).convert_alpha()
        self.progress_bar_image =  pygame.image.load(progress_bar_path).convert_alpha()
        self.progress_border_image =  pygame.image.load(progress_border_path).convert_alpha()


    def load_all_assets(self):
        """
        Recursively load all assets from the asset directory.
        """

        if self.count >= self.total:
            return 
        
        self.count = 0
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.abspath(os.path.join(root, file))
                self.count += 1
                self.set_loading_percent((self.count/self.total)/2)
                if file.lower().endswith(".png"):
                    LoadingScreen.ASSET[file_path] = pygame.image.load(file_path).convert_alpha()


    def set_loading_percent(self, value):
        """
        Set the loading percentage for the loading bar.

        Args:
           value (float): The new percentage value to set on the loading bar (between 0 and 1).

        Side Effects:
        - Sets the new value on the loading bar slider.
        """
        self.percent = value
        self.loading_bar.set_value(self.percent)

    def update(self):
        """Update the screen and handle events."""
        super().update() 

        self.load_all_assets()

        if self.percent >= 1:
            self.set_next_screen(MAIN_MENU)
        
        self.set_loading_percent(self.percent + 0.01)

        
