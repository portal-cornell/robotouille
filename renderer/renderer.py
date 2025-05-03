import pygame
import numpy as np
import os
import re
import json
from frontend.slider import Slider
from frontend.loading import LoadingScreen
from frontend.orders_set import OrdersCollection
from .canvas import RobotouilleCanvas

class RobotouilleRenderer:
    """
    Renderer for Robotouille.

    It is necessary to provide a render function to PDDLGym environments. This class
    provides that function but also setups up the pygame window to allow for rendering.
    """

    def __init__(self,  config_filename, layout=[], tiling=None, players=[], screen_size=np.array([512,512]), render_fps=60, screen=None):
        """
        Initializes the renderer.

        Args:
            config_filename (str): Name of the configuration file
            layout (List[List[Optional[str]]]): 2D array of station names (or None)
            tiling (Dict): Dictionary with tiling data
            players (List[Dict]): List of player dictionaries
            screen_size (np.array): (width, height) of the screen
            render_fps (int): Framerate of the renderer
            screen (pygame.Surface): Pre-existing screen to render to, if any
        """
        # Opens the configuration file to be used in the canvas.
        CONFIG_DIR = os.path.join(os.path.dirname(__file__), "configuration")
        with open(os.path.join(CONFIG_DIR, config_filename), "r") as f:
            self.config = json.load(f)
        # The layout of the game.
        self.layout = layout
        # The players in the game.
        self.players = players
        # Empty tiling if not provided
        self.tiling = tiling
        # The size of the screen
        self.screen_size = screen_size
        # The canvas is responsible for drawing the game state on a pygame surface.
        self.canvas = RobotouilleCanvas(self.config, layout, self.tiling, players, self.screen_size)
        # The framerate of the renderer.
        self.render_fps = render_fps
        if os.getenv("DISPLAY") is None and os.getenv("SDL_VIDEODRIVER") is None:
            os.environ["SDL_VIDEODRIVER"] = "dummy" # For headless rendering
            print("Warning: Running in headless mode. No window will be displayed.")
        # The PyGame screen
        self.screen = pygame.display.set_mode(screen_size) if screen is None else screen
        self.progress_bars = {}
        self.item_to_object = {}
        self.draw_bar = {}

        self.completed = set()
        self.length, self.width = len(self.layout), len(self.layout[0])
        self.asset_directory = LoadingScreen.ASSET

        width = 512
        height = 512
        self.width_scale = screen_size[0] / width
        self.height_scale = screen_size[1] / height
        
        # TODO Remove; renderer should not own the ORDERS
        self.orders = OrdersCollection(screen_size, self.config)
        self.next_screen = None

    def update_next_screen(self):
        """
        TODO move this to order's controller/parent
        """
        if self.orders.next_screen:
            self.next_screen = self.orders.next_screen


    def update_progress_bar(self, item, x, y, percentage = 0, increment = None):
        """
        Draws an image on the canvas.

        TODO: need to get the station at (x,y) store it when you initialize the image
        if the object is not on the same station, needs to hide the progress bar
        """

        object = None
        if 0 <= y < len(self.layout) and 0 <= x < len(self.layout[0]):
            object = self.layout[int(y)][int(x)]
        if object: 
            object = re.sub(r'\d+$', '', object)

        fg_image = self.asset_directory[RobotouilleCanvas.ASSETS_DIRECTORY]["progress_foreground.png"]
        bg_image = self.asset_directory[RobotouilleCanvas.ASSETS_DIRECTORY]["progress_background.png"]

        if item in self.completed:
            return
        
        if item not in self.progress_bars:
            self.progress_bars[item] = Slider(self.screen, bg_image, fg_image,
                                              self.width_scale * 80,  self.height_scale * 50, 
                                              self.width_scale * 80,  self.height_scale * 50, 
                                              x/self.length, (y + 0.4)/self.width, 
                                              filled_percent=percentage, anchor='topleft') 
            self.draw_bar[item] = True
            self.item_to_object[item] = object
        else:
            if self.item_to_object[item] != object:
                self.draw_bar[item] = False
                return

            self.draw_bar[item] = True
            slider = self.progress_bars[item]
            value = slider.get_value()

            # update the value 
            if percentage:
                slider.set_value(percentage)
            
            if increment:
                slider.set_value(value + increment)

            value = slider.get_value()

            if value >= 1:
                self.completed.add(item)
                self.progress_bars.pop(item)
                self.item_to_object.pop(item)
                self.draw_bar.pop(item)

    
    def draw_progress_bar(self):
        for id, bar in self.progress_bars.items():
            if self.draw_bar[id]:
                bar.draw()

    def render(self, state):
        """
        This function is called by PDDLGym environments to render the game state.

        If close is True, the window and clock are uninitialized as well as pygame
        and the display. Since pygame doesn't close the window until the script
        ends, we also hide the window.

        Parameters:
            state (State):
                The current game state
            mode (str):
                Either "human" or "rgb_array"
            close (bool):
                Whether to close the pygame window
        """
        self.screen.fill((0,0,0,0))
        self.canvas.draw_to_surface(self.screen, state)
        self.draw_progress_bar()
        self.orders.draw()
        self.update_next_screen() # TODO remove to order owner
        self.screen.blit(self.orders.get_screen(), (0,0))
        return np.transpose(
            np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
        )
    
    def reset(self):
        """
        Resets the renderer.

        This function is called by PDDLGym environments when they are reset.
        """
        self.canvas = RobotouilleCanvas(self.config, self.layout, self.tiling, self.players, self.screen_size)