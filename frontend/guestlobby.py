import pygame
from frontend.constants import JOINLOBBY, FONT_PATH, GAME, SHARED_DIRECTORY, BLACK, PROFILE, SETTINGS, WHITE
from frontend.button import Button
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "guestlobby"))

class GuestLobby(ScreenInterface):
    def __init__(self, window_size, offset_x=0, offset_y=0):
        """
        Initialize the Lobby Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size, mouse_offset_x=offset_x, mouse_offset_y=offset_y) 
        #self.lobby = lobby_data
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.back_arrow = Button(self.screen, self.back_arrow_image, self.x_percent(64), self.y_percent(860), self.scale_factor, anchor="topleft")
        
        
        # # Player slots
        # self.players = []
        # x_coords = [291, 576, 862, 1148]
        # for x in x_coords:
        #     self.players.append({
        #         "name": Textbox(self.screen, "", self.x_percent(x), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center"),
        #         "icon": Image(self.screen, self.empty_profile_image, self.x_percent(x), self.y_percent(426), self.scale_factor, anchor="center")
        #     })
          
        # #lobby id
        # self.lobby_id_image_box = Image(self.screen, self.lobby_id_image, self.x_percent(521), self.y_percent(56), self.scale_factor, anchor="topleft")
        # self.lobby_id_txt = Textbox(
        #     self.screen,
        #     f"#{self.lobby['id']}",
        #     self.x_percent(584), self.y_percent(58),
        #     271, 95,
        #     WHITE, font_size=80, scale_factor=self.scale_factor, anchor="topleft"
        # )

        # count_img_map = {
        #     1: self.one_player_img,
        #     2: self.two_player_img,
        #     3: self.three_player_img,
        #     4: self.four_player_img
        # }
        # count = len(self.lobby["players"])
        # self.count_img = Image(self.screen, count_img_map.get(count, self.four_player_img), self.x_percent(1060), self.y_percent(38), self.scale_factor, anchor="topleft")

        # # Lock status
        # lock_img = self.locked_img if self.lobby.get("locked", False) else self.unlocked_img
        # self.lock_icon = Image(self.screen, lock_img, self.x_percent(962), self.y_percent(38), self.scale_factor, anchor="topleft")



    def load_assets(self):
        """Load necessary assets."""
        self.background_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["background.png"]
        self.back_arrow_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["back_arrow.png"]
        self.empty_profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["empty_profile.png"]
        self.profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["profile.png"]
        self.lobby_id_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["lobbyid.png"]

        self.one_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["1.png"]
        self.two_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["2.png"]
        self.three_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["3.png"]
        self.four_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["4.png"]

        self.locked_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["locked.png"]
        self.unlocked_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["unlocked.png"]

    def draw(self):
      self.background.draw()
      self.back_arrow.draw()
      # self.lobby_id_image_box.draw()
      # self.lobby_id_txt.draw()
      # self.count_img.draw()
      # self.lock_icon.draw()

      # for player in self.players:
      #     player["icon"].draw()
      #     if player["name"].get_text():
      #         player["name"].draw()



    def update(self):
        """Update the screen and handle events."""
        super().update()
        
        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(JOINLOBBY)