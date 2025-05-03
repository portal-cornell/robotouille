import pygame
from frontend.constants import WHITE, SHARED_DIRECTORY, GAME, MAIN_MENU
from frontend.button import Button
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os
from backend.special_effects.repetitive_effect import RepetitiveEffect
from backend.special_effects.delayed_effect import DelayedEffect
from backend.special_effects.conditional_effect import ConditionalEffect



# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "main_menu"))

class ProgressBarScreen(ScreenInterface):
    def __init__(self, window_size, env, renderer):
        """
        Initialize the Main Menu Screen.

        Args:
            window_size (tuple): (width, height) of the window
            effects
        """
        super().__init__(window_size) 
        self.env = env
        self.effects = env.current_state.special_effects
        self.renderer = renderer
        
    def get_object_location(self, name):
        """
        Retrieves the (x, y) position of the object if found; otherwise, returns (-999, -999).

        Args:
            name (Backend.Object): The game object to locate.

        Returns:
            tuple: A tuple (x, y) representing the object's position, or (-999, -999) if not found.
        """
        ans = None
        for k,v in self.env.current_state.predicates.items():
            if ans is not None:
                break
            if not v or len(k.params) < 2:
                continue
            f, s = k.params
            if s == name:
                ans = self.renderer.canvas._get_station_position(f.name)
            if f == name:
                ans = self.renderer.canvas._get_station_position(s.name)
        if ans is None: 
            return -999, -999
        return ans


    def create_bar(self, effect):
        """
        Recursively goes through all nested effects and create/updates the progress bar
        """
        if isinstance(effect, RepetitiveEffect):
            x, y = self.get_object_location(effect.arg)
            self.renderer.update_progress_bar(effect.arg, x, y, percentage=effect.current_repetitions/effect.goal_repetitions)
        elif isinstance(effect, DelayedEffect):
            # TODO: in the future this needs to be synchronized to the clock
            x, y = self.get_object_location(effect.arg)
            self.renderer.update_progress_bar(effect.arg, x, y, increment=1/effect.goal_time)
        elif isinstance(effect, ConditionalEffect):
            for subeffect in effect.special_effects:
                self.create_bar(subeffect)

    def load_assets(self):
        """
        Loads necessary assets.
        """
        pass
      
    def draw(self):
        """Draws all the screen components."""
        pass

    def update(self):
        """
        iterates through special effects to update special effects
        """
        for effect in self.effects:
            self.create_bar(effect)
        