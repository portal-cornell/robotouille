import pygame
from frontend.constants import MAIN_MENU, FONT_PATH, GAME, MAX_PLAYERS, SHARED_DIRECTORY, BLACK, PROFILE, SETTINGS, WHITE, JOINLOBBY
from frontend.button import Button
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "ownlobby"))

class OwnLobby(ScreenInterface):
    def __init__(self, window_size, party_name="My Party", visibility="PUBLIC", players=None, lobby_id="#12345", offset_x=0, offset_y=0):
        """
        Initialize the Lobby Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size, mouse_offset_x=offset_x, mouse_offset_y=offset_y) 
        self.party_name = party_name
        self.visibility = visibility
        self.lobby_id = lobby_id
        self.players_data = players or ["HostPlayer"]
        self.load_assets()  
        
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.back_arrow = Button(self.screen, self.back_arrow_image, self.x_percent(64), self.y_percent(860), self.scale_factor, anchor="topleft")
        


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

        self.remove_buttons = []
        for _ in range(4):
            btn = Button(
                self.screen,
                self.remove_hover_img,
                0, 0,  # placeholder, will reposition dynamically
                self.scale_factor,
                anchor="center"
            )
            self.remove_buttons.append(btn)
        #lobby id image
        self.lobby_id_image = Image(self.screen, self.lobby_id_image, self.x_percent(521), self.y_percent(56), self.scale_factor, anchor="topleft")
        self.lobby_id_txt = Textbox(self.screen, self.lobby_id, self.x_percent(584), self.y_percent(58), 271, 95, WHITE, font_size=80, scale_factor=self.scale_factor, anchor="topleft")

        #start button
        self.start = Button(self.screen, self.start_button_image, self.x_percent(556), self.y_percent(686), self.scale_factor, 
                              hover_image_source= self.start_hover_button_image, pressed_image_source= self.start_pressed_button_image, 
                              text = "START", font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")

        self.lock_icon = Image(self.screen, self.locked_img if self.visibility == "PRIVATE" else self.unlocked_img,
                       self.x_percent(962), self.y_percent(38), self.scale_factor, anchor="topleft")

        self.player_count_icon = Image(self.screen, 
            [self.one_player_img, self.two_player_img, self.three_player_img, self.four_player_img][self.count - 1],
            self.x_percent(1060), self.y_percent(38), self.scale_factor, anchor="topleft")

    def load_assets(self):
        """Load necessary assets."""
        self.background_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["background.png"]
        self.back_arrow_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["back_arrow.png"]
        
        self.empty_profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["empty.png"]
        self.profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["profile.png"]
        
        self.lobby_id_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["number_box.png"]
        self.start_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b.png"]
        self.start_hover_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_h.png"]
        self.start_pressed_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_p.png"]

        self.remove_hover_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["remove_hover.png"]
        
        self.one_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["1.png"]
        self.two_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["2.png"]
        self.three_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["3.png"]
        self.four_player_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["4.png"]

        self.locked_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["locked.png"]
        self.unlocked_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["unlocked.png"]

    def set_lobby(self, lobby_data):
        self.party_name = lobby_data.get("name", "My Party")
        self.lobby_id = f"#{lobby_data.get('id', '00000')}"
        self.visibility = "PRIVATE" if lobby_data.get("locked", False) else "PUBLIC"
        self.players_data = [player[1] for player in lobby_data.get("players", [])]  # get player names

        self.count = len(self.players_data)

        for i in range(4):
            if i < self.count:
                self.players[i]["name"].set_text(self.players_data[i])
                self.players[i]["icon"].set_image(self.profile_image)
            else:
                self.players[i]["name"].set_text("")
                self.players[i]["icon"].set_image(self.empty_profile_image)
        
        self.lock_icon.set_image(self.locked_img if self.visibility == "PRIVATE" else self.unlocked_img)
        self.player_count_icon.set_image([
            self.one_player_img, self.two_player_img, self.three_player_img, self.four_player_img
        ][self.count - 1])  
        self.lobby_id_txt.set_text(self.lobby_id)

    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.back_arrow.draw()
        self.start.draw()
      
        self.lobby_id_image.draw()
        self.lobby_id_txt.draw()
        self.lock_icon.draw()
        self.player_count_icon.draw()

        for i, player in enumerate(self.players):
          player["icon"].draw()
          if player["name"].get_text():
              player["name"].draw()

              # Draw remove button if mouse hovers over the icon
              mouse_pos = pygame.mouse.get_pos()
              for i, player in enumerate(self.players):
                  player["icon"].draw()
                  if player["name"].get_text():
                      player["name"].draw()

                      if player["icon"].rect.collidepoint(mouse_pos):
                          # Dynamically position the remove button relative to the icon
                          icon_rect = player["icon"].rect
                          self.remove_buttons[i].x = player["icon"].x + self.x_percent(60)
                          self.remove_buttons[i].y = player["icon"].y - self.y_percent(60)
                          self.remove_buttons[i].draw()
        #self.kick_button.draw()


    def update(self):
        """Update the screen and handle events."""
        super().update()
        
        #Handle profile button
        clicked_anywhere = False
        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(JOINLOBBY)
            for i, btn in enumerate(self.remove_buttons):
              if btn.handle_event(event):
                  print(f"Removed {self.players[i]['name'].get_text()}")
                  self.players[i]["name"].set_text("")
                  self.players[i]["icon"].set_image(self.empty_profile_image)