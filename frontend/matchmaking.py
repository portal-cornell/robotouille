import pygame
from frontend.constants import MAIN_MENU, FONT_PATH, GAME, MAX_PLAYERS, SHARED_DIRECTORY, BLACK, PROFILE, SETTINGS, WHITE
from frontend.button import Button
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os

"""
TODO BACKEND INTEGRATION

BACKEND NEEDS 
- Tell every player the names of player currently in the lobby
screens[current_screen].set_players(["Player1", "Player2"])

TODO HENRY
- ADD PROFILES 
"""
# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "matchmaking"))

class MatchMakingScreen(ScreenInterface):
    def __init__(self, window_size, offset_x=0, offset_y=0):
        """
        Initialize the Lobby Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size, mouse_offset_x=offset_x, mouse_offset_y=offset_y) 
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

        #profile button 
        self.profile_button = Button(self.screen, self.userprofile_image, self.x_percent(1289), self.y_percent(33), 
                                      self.scale_factor, anchor="topleft")
        self.edit_profile_button = Button(self.screen, self.edit_profile_button_image, self.x_percent(956),
                                          self.y_percent(158),  self.scale_factor, text="   edit profile", 
                                          font_size = 40, text_color=BLACK, anchor="topleft", align_text = "left")
        self.setting_logo_button = Button(self.screen, self.settings_button_image, self.x_percent(956), 
                                          self.y_percent(230),  self.scale_factor,  text="   settings", font_size = 40, 
                                          text_color=BLACK, anchor="topleft", align_text = "left")
        self.dropdown_visible = False

        #lobby id image
        self.lobby_id_image = Image(self.screen, self.lobby_id_image, self.x_percent(521), self.y_percent(56), self.scale_factor, anchor="topleft")
        self.lobby_id_txt = Textbox(self.screen, '#12345', self.x_percent(584), self.y_percent(58), 271, 95, WHITE, font_size=80, scale_factor=self.scale_factor, anchor="topleft")

        #kick button
        #self.kick_button = Button(self.screen, self.kick_button_image, self.x_percent(968), self.y_percent(55),
        #                          self.scale_factor, hover_image_source= self.kick_button_hover_image, text = "KICK", font_path = FONT_PATH,
        #                          font_size = 60, text_color = WHITE, anchor="topleft")
        #start button
        self.start = Button(self.screen, self.start_button_image, self.x_percent(556), self.y_percent(686), self.scale_factor, 
                              hover_image_source= self.start_hover_button_image, pressed_image_source= self.start_pressed_button_image, 
                              text = "START", font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")


    def load_assets(self):
        """Load necessary assets."""
        self.background_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["background.png"]
        self.back_arrow_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["back_arrow.png"]
        self.empty_profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["empty.png"]
        self.profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["profile.png"]
        
        self.userprofile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["userprofile.png"]
        self.edit_profile_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["edit_profile_button.png"]
        self.settings_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["settings_button.png"]

        self.lobby_id_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["number_box.png"]

        #self.kick_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["kick_button.png"]
        #self.kick_button_hover_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["kick_button_hover.png"]
        self.start_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b.png"]
        self.start_hover_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_h.png"]
        self.start_pressed_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_p.png"]

    def set_players(self, existing_players):
        """
        Set existing players.

        Args:
            existing_players (list of dict): List of players to add, each with 'name' and 'icon'.
        """

        if len(existing_players) >= MAX_PLAYERS:
            raise Exception("Too many players")
        
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
        self.back_arrow.draw()
        self.start.draw()
        for player in self.players:
            player["icon"].draw()
            if player["name"].get_text(): player["name"].draw()

        # draw play button if player is host

        #draw top right profile button
        self.profile_button.draw()
        if self.dropdown_visible:
            self.edit_profile_button.draw()
            self.setting_logo_button.draw()

        self.lobby_id_image.draw()
        self.lobby_id_txt.draw()

        #self.kick_button.draw()


    def update(self):
        """Update the screen and handle events."""
        super().update()
        
        if self.count == MAX_PLAYERS:
            self.set_next_screen(GAME)
        
        #Handle profile button
        clicked_anywhere = False

        # TODO: Temprorary behavior. Q used to switch to leave match making and G used to start game
        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.set_next_screen(MAIN_MENU)

            if event.type == pygame.KEYDOWN:
                # Transitions to Main Menu when key Q is pressed.
                if event.key == pygame.K_q:
                    self.set_next_screen(MAIN_MENU)
                 # Transitions to the Game when key G is pressed.
                elif event.key == pygame.K_g:
                    self.set_next_screen(GAME)
        
       
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_anywhere=True

            # Transitions for profile button.
            if self.profile_button.handle_event(event):
                self.dropdown_visible = not self.dropdown_visible

            if self.dropdown_visible:
                if self.edit_profile_button.handle_event(event):
                    self.set_next_screen(PROFILE)
                if self.setting_logo_button.handle_event(event):
                    self.set_next_screen(SETTINGS)
        
        # Close dropdown if mouse is clicked outside of the dropdown area.
        if clicked_anywhere and self.dropdown_visible:
            if not (self.edit_profile_button.in_bound() or self.setting_logo_button.in_bound() or
                     self.profile_button.in_bound()):
                self.dropdown_visible = False
