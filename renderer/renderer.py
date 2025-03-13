import pygame
import numpy as np
import os
import json

from .canvas import RobotouilleCanvas

class RobotouilleRenderer:
    """
    Renderer for Robotouille.

    It is necessary to provide a render function to PDDLGym environments. This class
    provides that function but also setups up the pygame window to allow for rendering.
    """

    def __init__(self,  config_filename, layout=[], tiling=None, players=[], window_size=np.array([512,512]), render_fps=60):
        """
        Initializes the renderer.

        Args:
            layout (List[List[Optional[str]]]): 2D array of station names (or None)
            tiling (Dict): Dictionary with tiling data
            window_size (np.array): (width, height) of the window
            render_fps (int): Framerate of the renderer
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
        # The canvas is responsible for drawing the game state on a pygame surface.
        self.canvas = RobotouilleCanvas(self.config, self.layout, self.tiling, self.players, window_size)
        # The pygame window size.
        self.window_size = window_size
        # The framerate of the renderer.
        self.render_fps = render_fps
        # The pygame window
        self.window = None
        # The pygame clock
        self.clock = None
    
    def _init_setup(self):
        """
        This function initializes the pygame window and clock if not already initialized.
        """
        if os.getenv("DISPLAY") is None and os.getenv("SDL_VIDEODRIVER") is None:
            os.environ["SDL_VIDEODRIVER"] = "dummy" # For headless rendering
            print("Warning: Running in headless mode. No window will be displayed.")
        if self.window is None:
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(self.window_size)
            pygame.display.set_caption('Robotouille Simulator')
        if self.clock is None:
            self.clock = pygame.time.Clock()
    
    def _render_frame(self, state, render_mode):
        """
        This function renders a single frame of the game.

        The frame is drawn on the canvas before being copied to the pygame window if
        rendering in human mode or returned if rendering in rgb_array mode.

        Parameters:
            state (State):
                The current game state
            render_mode (str):
                Either "human" or "rgb_array"
        
        Returns:
            frame (np.array):
                The RGB array of the frame
        """
        self._init_setup()
        surface = pygame.Surface(self.window_size)
        self.canvas.draw_to_surface(surface, state)
        if render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(surface, surface.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.render_fps)
        return np.transpose(
            np.array(pygame.surfarray.pixels3d(surface)), axes=(1, 0, 2)
        )

    def render(self, state, mode='human', close=False):
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
        rendered_frame = self._render_frame(state, mode)
        if close and mode == "human":
            self.window = None
            self.clock = None
            pygame.display.set_mode(self.window_size, flags=pygame.HIDDEN) # Hide the window
            pygame.display.quit()
            pygame.quit()
        return rendered_frame
    
    def reset(self):
        """
        Resets the renderer.

        This function is called by PDDLGym environments when they are reset.
        """
        self.canvas = RobotouilleCanvas(self.config, self.layout, self.tiling, self.players, self.window_size)