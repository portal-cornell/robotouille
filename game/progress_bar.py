import pygame
import re
from frontend.constants import WHITE, SHARED_DIRECTORY, GAME, MAIN_MENU
from frontend.slider import Slider
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os
from backend.special_effects.repetitive_effect import RepetitiveEffect
from backend.special_effects.delayed_effect import DelayedEffect
from backend.special_effects.conditional_effect import ConditionalEffect



# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))

class ProgressBarScreen(ScreenInterface):
    # default width, height; used for finding pixel size
    WIDTH, HEIGHT = 512, 512

    def __init__(self, screen_size, env, renderer):
        """
        Initialize the Main Menu Screen.

        Args:
            window_size (tuple): (width, height) of the window
            effects
        """
        super().__init__(screen_size) 
        self.env = env
        self.effects = env.current_state.special_effects
        self.renderer = renderer

        # The PyGame screen
        self.progress_bars = {}
        self.item_to_object = {}
        self.draw_bar = {}

        self.layout = self.renderer.layout
        self.completed = set()
        self.rows, self.columns = len(self.layout), len(self.layout[0])
        self.asset_directory = LoadingScreen.ASSET

        self.width_scale = screen_size[0] / ProgressBarScreen.WIDTH
        self.height_scale = screen_size[1] / ProgressBarScreen.HEIGHT
        
        
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
            self.update_progress_bar(effect.arg, x, y, percentage=effect.current_repetitions/effect.goal_repetitions)
        elif isinstance(effect, DelayedEffect):
            # TODO: in the future this needs to be synchronized to the clock
            x, y = self.get_object_location(effect.arg)
            self.update_progress_bar(effect.arg, x, y, increment=1/effect.goal_time)
        elif isinstance(effect, ConditionalEffect):
            for subeffect in effect.special_effects:
                self.create_bar(subeffect)

    def load_assets(self):
        """
        Loads necessary assets.
        """
        pass
      

    def update_progress_bar(self, item, x, y, percentage = 0, increment = None):
        """
        Draws an image on the canvas.

        TODO: need to get the station at (x,y) store it when you initialize the image
        if the object is not on the same station, needs to hide the progress bar
        """
        
        if item in self.completed:
            return
    
        object = None
        if 0 <= y < self.rows and 0 <= x < self.columns:
            object = re.sub(r'\d+$', '', self.layout[int(y)][int(x)])

        fg_image = self.asset_directory[ASSETS_DIRECTORY]["progress_foreground.png"]
        bg_image = self.asset_directory[ASSETS_DIRECTORY]["progress_background.png"]
        
        if item not in self.progress_bars:
            self.progress_bars[item] = Slider(self.screen, bg_image, fg_image,
                                              self.width_scale * 80,  self.height_scale * 50, 
                                              self.width_scale * 80,  self.height_scale * 50, 
                                              x/self.rows, (y + 0.4)/self.columns, 
                                              filled_percent=percentage, anchor='topleft') 
            self.draw_bar[item] = True
            self.item_to_object[item] = object
        else:
            if self.item_to_object[item] != object: # if the item is not at the correct station 
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

    
    def draw(self):
        """
        Renders the active progress bars
        """
        self.screen.fill((0,0,0,0))
        for id, bar in self.progress_bars.items():
            if self.draw_bar[id]:
                bar.draw()
    

    def update(self):
        """
        iterates through special effects to update special effects
        """
        for effect in self.effects:
            self.create_bar(effect)
        