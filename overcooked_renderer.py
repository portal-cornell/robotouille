import pygame
import numpy as np

class OvercookedRenderer:

    def __init__(self, grid_size=5, window_size=512, render_fps=4):
        self._target_location = np.array([2, 2], dtype=int)
        self._agent_location = np.array([3, 3], dtype=int)
        self.grid_size = grid_size
        self.window_size = window_size
        self.render_fps = render_fps
        self.window = None
        self.clock = None
    
    def _init_setup(self, render_mode):
        if self.window is None and render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(
                (self.window_size, self.window_size)
            )
        if self.clock is None and render_mode == "human":
            self.clock = pygame.time.Clock()
    
    #def _draw_grid(self):

    def _render_frame(self, obs, render_mode):
        self._init_setup(render_mode)
        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        # The size of a single grid square in pixels
        pix_square_size = (self.window_size / self.grid_size)

        # First we draw the target
        pygame.draw.rect(
            canvas,
            (255, 0, 0),
            pygame.Rect(
                pix_square_size * self._target_location,
                (pix_square_size, pix_square_size),
            ),
        )
        # Now we draw the agent
        pygame.draw.circle(
            canvas,
            (0, 0, 255),
            (self._agent_location + 0.5) * pix_square_size,
            pix_square_size / 3,
        )

        # Finally, add some gridlines
        for x in range(self.grid_size + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
                width=3,
            )
            pygame.draw.line(
                canvas,
                0,
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
                width=3,
            )

        if render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()
            # if self._agent_location[1] == 3:
            #     self._agent_location = np.array([3, 2], dtype=int)
            # else:
            #     self._agent_location = np.array([3, 3], dtype=int)

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