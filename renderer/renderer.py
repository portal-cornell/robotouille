import pygame
import numpy as np

from .canvas import OvercookedCanvas

class OvercookedRenderer:
    """
    Renderer for Overcooked.

    It is necessary to provide a render function to PDDLGym environments. This class
    provides that function but also setups up the pygame window to allow for rendering.
    """

    def __init__(self, layout=[], window_size=np.array([512,512]), render_fps=4):
        """
        Initializes the renderer.

        Args:
            layout (List[List[Optional[str]]]): 2D array of station names (or None)
            window_size (np.array): (width, height) of the window
            render_fps (int): Framerate of the renderer
        """
        # The canvas is responsible for drawing the game state on a pygame surface.
        self.canvas = OvercookedCanvas(layout)
        # The pygame window size.
        self.window_size = window_size
        # The framerate of the renderer. This isn't too important since the renderer
        # displays static drawings.
        self.render_fps = render_fps
        # The pygame window
        self.window = None
        # The pygame clock
        self.clock = None
    
    def _init_setup(self, render_mode):
        """
        This function initializes the pygame window and clock if not already initialized.

        Args:
            render_mode (str): Either "human" or "rgb_array"
        """
        if self.window is None and render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(self.window_size)
            pygame.display.set_caption('Overcooked Simulator')
        if self.clock is None and render_mode == "human":
            self.clock = pygame.time.Clock()
    
    def _render_frame(self, obs, render_mode):
        """
        This function renders a single frame of the game.

        The frame is drawn on the canvas before being copied to the pygame window if
        rendering in human mode or returned if rendering in rgb_array mode.

        Args:
            obs (dict): The game state
            render_mode (str): Either "human" or "rgb_array"
        
        Returns:
            np.array: The RGB array of the frame (only if render_mode == "rgb_array")
        """
        self._init_setup(render_mode)
        surface = pygame.Surface(self.window_size)
        self.canvas.draw_to_surface(surface, obs)
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

    def render(self, obs, mode='human', close=False):
        """
        This function is called by PDDLGym environments to render the game state.

        Args:
            obs (dict): The game state
            mode (str): Either "human" or "rgb_array"
            close (bool): Whether to close the pygame window
        """
        if close:
            pygame.display.quit()
            pygame.quit()
        else:
            return self._render_frame(obs, mode)