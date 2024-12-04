import pygame
from frontend.constants import MAIN_MENU, GAME, MAX_PLAYERS, SHARED_DIRECTORY
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "matchmaking"))

class MatchMakingScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the Lobby Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size) 
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.players = [
            {"name": Textbox(self.screen,"", self.x_percent(291), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center"),
              "icon": Image(self.screen, self.empty_profile_image, self.x_percent(291), self.y_percent(426), self.scale_factor, anchor="center")},
            {"name": Textbox(self.screen,"", self.x_percent(576), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center"), 
             "icon": Image(self.screen, self.empty_profile_image, self.x_percent(576), self.y_percent(426), self.scale_factor, anchor="center")},
            {"name": Textbox(self.screen,"", self.x_percent(862), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center"), 
             "icon": Image(self.screen, self.empty_profile_image, self.x_percent(862), self.y_percent(426), self.scale_factor, anchor="center")},
            {"name": Textbox(self.screen,"", self.x_percent(1148), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center"), 
             "icon": Image(self.screen, self.empty_profile_image, self.x_percent(1148), self.y_percent(426), self.scale_factor, anchor="center")},
            ] 
        self.host = False
        self.count = 0

    def load_assets(self):
        """Load necessary assets."""
        self.background_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["background.png"]
        self.empty_profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["empty.png"]
        self.profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["profile.png"]

    def set_players(self, existing_players):
        """
        Set existing players.

        Args:
            existing_players (list of dict): List of players to add, each with 'name' and 'icon'.
        """

        if len(existing_players) >= MAX_PLAYERS:
            raise Exception("To many players")
        
        self.count = len(existing_players)

        for i in range(4):
            if i < len(existing_players):
                self.players[i]["name"].set_text(existing_players[i])
                self.players[i]["icon"].set_image(self.profile_image)
            else:
                self.players[i]["name"].set_text("")
                self.players[i]["icon"].set_image(self.empty_profile_image)  

    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        for player in self.players:
            player["icon"].draw()
            if player["name"].get_text(): player["name"].draw()

        # draw play button if player is host

    def update(self):
        """Update the screen and handle events."""
        super().update()
        
        if self.count == MAX_PLAYERS:
            self.set_next_screen(GAME)
        
        # TODO: Temprorary behavior. Q used to switch to leave match making and G used to start game
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # Transitions to Main Menu when key Q is pressed.
                if event.key == pygame.K_q:
                    self.set_next_screen(MAIN_MENU)
                 # Transitions to the Game when key G is pressed.
                elif event.key == pygame.K_g:
                    self.set_next_screen(GAME)
