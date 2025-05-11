import pygame
import asyncio
from frontend.constants import MAIN_MENU, GAME, MAX_PLAYERS, SHARED_DIRECTORY
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os


# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "matchmaking"))

class MatchMakingScreen(ScreenInterface):
    def __init__(self, window_size, offset_x=0, offset_y=0):
        """
        Initialize the Lobby Screen.

        Args:
            window_size (tuple): (width, height) of the window
            offset_x (int): Represents the number of pixels vertically this nodes is offseted from the top level parent screen
            offset_y (int): Represents the number of pixels horizonally this nodes is offseted from the top level parent screen
        """
        super().__init__(window_size, mouse_offset_x=offset_x, mouse_offset_y=offset_y) 
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
        self.networking_manager= None

    def set_networking_manager(self, manager):
        self.networking_manager = manager
        
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
                    # TODO this should disconnect client from server
                # Transitions to the Game when key G is pressed.
                elif event.key == pygame.K_g:
                    # self.set_next_screen(GAME)
                    if self.networking_manager:
                        asyncio.run(self.networking_manager.send_message("start game"))
                    # TODO remove this functionality? Game start should now be based on server
