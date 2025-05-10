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


    def __init__(self,  config_filename, layout=[], tiling=None, players=[], customers=[], screen_size=np.array([512,512]), render_fps=60, screen=None):
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
        # The customers in the game.
        self.customers = customers
        # Empty tiling if not provided
        self.tiling = tiling
        # The size of the screen
        self.screen_size = screen_size
        # The canvas is responsible for drawing the game state on a pygame surface.
        self.canvas = RobotouilleCanvas(self.config, layout, self.tiling, players, customers, self.screen_size)
        # The framerate of the renderer.
        self.render_fps = render_fps
        if os.getenv("DISPLAY") is None and os.getenv("SDL_VIDEODRIVER") is None:
            os.environ["SDL_VIDEODRIVER"] = "dummy" # For headless rendering
            print("Warning: Running in headless mode. No window will be displayed.")
        # The PyGame screen
        self.screen = pygame.display.set_mode(screen_size) if screen is None else screen
        
        # TODO (lsuyean): Remove; renderer should not own the ORDERS. Should be own by customer controller/ GameMode class
        self.orders = OrdersCollection(screen_size, self.config)


    
    def _render_frame(self, gamemode, render_mode):
        """
        This function renders a single frame of the game.

        The frame is drawn on the canvas before being copied to the pygame window if
        rendering in human mode or returned if rendering in rgb_array mode.

        Args:
            gamemode (GameMode): The game mode object
            render_mode (str): Either "human" or "rgb_array"
        
        Returns:
            np.array: The RGB array of the frame (only if render_mode == "rgb_array")
        """
        self._init_setup(render_mode)
        surface = pygame.Surface(self.window_size)
        self.canvas.draw_to_surface(surface, gamemode)
        if render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(surface, surface.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.render_fps)
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(surface)), axes=(1, 0, 2)
            )

    def render(self, gamemode):
        """
        This function is called by PDDLGym environments to render the game state.

        If close is True, the window and clock are uninitialized as well as pygame
        and the display. Since pygame doesn't close the window until the script
        ends, we also hide the window.

        Parameters:
            state (Gamemode): 
                The game mode object
            mode (str):
                Either "human" or "rgb_array"
            close (bool):
                Whether to close the pygame window
        """
        self.screen.fill((0,0,0,0))
        self.canvas.draw_to_surface(self.screen, gamemode)
        self.orders.draw()
        self.screen.blit(self.orders.get_screen(), (0,0))
        return np.transpose(
            np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
        )
    
    def reset(self):
        """
        Resets the renderer.

        This function is called by PDDLGym environments when they are reset.
        """
        self.canvas = RobotouilleCanvas(self.config, self.layout, self.tiling, self.players, self.customers, self.screen_size)
