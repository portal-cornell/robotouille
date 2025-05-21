import pygame
from frontend.constants import JOINLOBBY, FONT_PATH, GAME, SHARED_DIRECTORY, GREY, PROFILE, SETTINGS, WHITE
from frontend.button import Button
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os

# Assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "guestlobby"))

class GuestLobby(ScreenInterface):
    def __init__(self, window_size, offset_x=0, offset_y=0):
        super().__init__(window_size, mouse_offset_x=offset_x, mouse_offset_y=offset_y) 

        self.load_assets()

        # Background & back button
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.back_arrow = Button(self.screen, self.back_arrow_image, self.x_percent(64), self.y_percent(860), self.scale_factor, anchor="topleft")

        # Players (4 slots)
        self.players = [
            {"name": Textbox(self.screen, "", self.x_percent(291), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center"),
             "icon": Image(self.screen, self.empty_profile_image, self.x_percent(291), self.y_percent(426), self.scale_factor, anchor="center")},
            {"name": Textbox(self.screen, "", self.x_percent(576), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center"),
             "icon": Image(self.screen, self.empty_profile_image, self.x_percent(576), self.y_percent(426), self.scale_factor, anchor="center")},
            {"name": Textbox(self.screen, "", self.x_percent(862), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center"),
             "icon": Image(self.screen, self.empty_profile_image, self.x_percent(862), self.y_percent(426), self.scale_factor, anchor="center")},
            {"name": Textbox(self.screen, "", self.x_percent(1148), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center"),
             "icon": Image(self.screen, self.empty_profile_image, self.x_percent(1148), self.y_percent(426), self.scale_factor, anchor="center")}
        ]

        # Hardcoded guest players
        self.players[0]["name"].set_text("Player 1")
        self.players[0]["icon"].set_image(self.profile_image)

        self.players[1]["name"].set_text("Player 2")
        self.players[1]["icon"].set_image(self.profile_image)

        self.count = 2
        self.visibility = "PRIVATE"

        # Lobby ID and info icons
        self.lobby_id_image = Image(self.screen, self.lobby_id_bg, self.x_percent(521), self.y_percent(56), self.scale_factor, anchor="topleft")
        self.lobby_id_txt = Textbox(self.screen, "40956", self.x_percent(584), self.y_percent(58), 271, 95, WHITE, font_size=80, scale_factor=self.scale_factor, anchor="topleft")

        self.lock_icon = Image(self.screen, self.locked_img if self.visibility == "PRIVATE" else self.unlocked_img, self.x_percent(962), self.y_percent(38), self.scale_factor, anchor="topleft")
        self.player_count_icon = Image(self.screen, [self.one_player_img, self.two_player_img, self.three_player_img, self.four_player_img][self.count - 1], self.x_percent(1060), self.y_percent(38), self.scale_factor, anchor="topleft")

        #waiting
        self.waiting = Textbox(self.screen, "WAITING...", self.x_percent(599), self.y_percent(760), 303, 88, GREY, font_size=60, scale_factor=self.scale_factor, anchor="topleft")
    
    def load_assets(self):
        """Load assets for the guest lobby screen."""
        self.background_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["background.png"]
        self.back_arrow_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["back_arrow.png"]

        self.empty_profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["empty.png"]
        self.profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["profile.png"]
        self.lobby_id_bg = LoadingScreen.ASSET[ASSETS_DIRECTORY]["lobbyid.png"]

        self.one_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["1.png"]
        self.two_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["2.png"]
        self.three_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["3.png"]
        self.four_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["4.png"]

        self.locked_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["locked.png"]
        self.unlocked_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["unlocked.png"]

    def draw(self):
        self.background.draw()
        self.back_arrow.draw()
        self.lobby_id_image.draw()
        self.lobby_id_txt.draw()
        self.lock_icon.draw()
        self.player_count_icon.draw()
        self.waiting.draw()

        for player in self.players:
            player["icon"].draw()
            if player["name"].get_text():
                player["name"].draw()

    def update(self):
        super().update()
        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(JOINLOBBY)
