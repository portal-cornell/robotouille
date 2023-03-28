import pygame
import numpy as np

from .canvas import make_canvas

class OvercookedRenderer:

    def __init__(self, grid_size=np.array([5,5]), window_size=np.array([512,512]), render_fps=4):
        self.grid_size = grid_size
        self.window_size = window_size
        self.render_fps = render_fps
        self.window = None
        self.clock = None
    
    def _init_setup(self, render_mode):
        if self.window is None and render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(self.window_size)
            pygame.display.set_caption('Overcooked Simulator')
        if self.clock is None and render_mode == "human":
            self.clock = pygame.time.Clock()
    
    def _render_frame(self, obs, render_mode):
        self._init_setup(render_mode)
        canvas = make_canvas(self.grid_size, self.window_size, obs)
        if render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.render_fps)
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def render(self, obs, mode='human', close=False):
        if close:
            pygame.display.quit()
            pygame.quit()
        else:
            return self._render_frame(obs, mode)