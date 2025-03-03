import pygame
import numpy as np
import os
import json

from renderer.canvas import RobotouilleCanvas

class RobotouilleGameRenderer:
    """
    Renderer for Robotouille.

    It is necessary to provide a render function to PDDLGym environments. This class
    provides that function but also setups up the pygame window to allow for rendering.
    """

    def __init__(self, config_filename, layout=[], tiling=None, players=[], window_size=np.array([512,512])):
        """
        Initializes the renderer.

        Args:
            layout (List[List[Optional[str]]]): 2D array of station names (or None)
            tiling (Dict): Dictionary with tiling data
            window_size (np.array): (width, height) of the window
        """
        self.surface = pygame.Surface(window_size)
        # Opens the configuration file to be used in the canvas.
        CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../renderer/configuration"))
        with open(os.path.join(CONFIG_DIR, config_filename), "r") as f:
            self.config = json.load(f)
        # The layout of the game.
        self.layout = layout
        # The players in the game.
        self.players = players
        # Empty tiling if not provided
        self.tiling = tiling
        # The canvas is responsible for drawing the game state on a pygame surface.
        self.canvas = RobotouilleCanvas(self.config, layout, tiling, players, window_size)
        # The pygame window size.
        self.window_size = window_size
        # displays static drawings.
        # TODO Remove; make screen as large as can fit in the screen (should be fixed in main).
        pygame.display.set_mode(self.window_size)
    
    def _render_frame(self, obs, render_mode):
        """
        This function renders a single frame of the game.

        The frame is drawn on the canvas before being copied to the pygame window if
        rendering in human mode or returned if rendering in rgb_array mode.

        Args:
            obs (State): The game state
            render_mode (str): Either "human" or "rgb_array"
        
        Returns:
            np.array: The RGB array of the frame (only if render_mode == "rgb_array")
        """
        self.canvas.draw_to_surface(self.surface, obs)
        if not render_mode == "human":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.surface)), axes=(1, 0, 2)
            )

    def render(self, obs, mode='human', close=False):
        """
        This function is called by PDDLGym environments to render the game state.

        If close is True, the window and clock are uninitialized as well as pygame
        and the display. Since pygame doesn't close the window until the script
        ends, we also hide the window.

        Args:
            obs (State): The game state
            mode (str): Either "human" or "rgb_array"
            close (bool): Whether to close the pygame window
        """
        if not close:
            return self._render_frame(obs, mode)
    
    def reset(self):
        """
        Resets the renderer.

        This function is called by PDDLGym environments when they are reset.
        """
        self.canvas = RobotouilleCanvas(self.config, self.layout, self.tiling, self.players, self.window_size)