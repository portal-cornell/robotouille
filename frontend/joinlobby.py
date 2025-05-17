import pygame
from frontend.constants import SHARED_DIRECTORY, MAIN_MENU, BLACK, FONT_PATH, WHITE, SETTINGS, BLUE, GUESTLOBBY, OWNLOBBY
from frontend.button import Button
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.editable_textbox import EditableTextbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
from frontend.guestlobby import GuestLobby 
from frontend.ownlobby import OwnLobby
import os
import random
lobby_id = f"#{random.randint(10000, 99999)}"



# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "joinlobby"))

class LobbyButton:
    def __init__(self, screen, x, y, x_name, x_lobby, y_button, lobby, scale_factor, 
                 font_path, button_img, profile_img,  empty_profile_img, player_icon_positions, on_click, x_percent, y_percent):
        self.screen = screen
        self.lobby = lobby  # dict with 'name', 'id', 'players'
        self.scale = scale_factor
        self.x = x
        self.y = y
        self.x_name = x_name
        self.x_lobby = x_lobby
        self.y_button = y_button
        self.player_icon_positions = player_icon_positions
        self.empty_profile_img = empty_profile_img    
        self.on_click = on_click
        
        # Lobby background (this spans the full row)
        self.background = Button(
            screen, 
            button_img,  
            x, y, 
            scale_factor, 
            anchor="topleft"
        )
        
        self.rect = pygame.Rect(x, y, 600, 50)
             
        # PARTY NAME — aligned to left padding
        self.name_text = Textbox(
            screen, lobby["name"],x_name, y_button,
            338, 71,
            text_color=WHITE, scale_factor=scale_factor, anchor="topleft"
        )

        # LOBBY ID — aligned toward center-right
        self.id_text = Textbox(
            screen, lobby["id"],
            x_lobby, y_button,
            338, 71,
            text_color=WHITE, font_path=font_path, 
            scale_factor=scale_factor, anchor="topleft"
        )

        # Player icons — aligned at the far right side
        self.player_icons = []
        num_players = len(lobby["players"])
        for i, (x_percent, y_percent) in enumerate(player_icon_positions):
            img = profile_img if i < num_players else empty_profile_img
            icon = Image(screen, img, x_percent, y_percent, scale_factor, anchor="topleft")
            self.player_icons.append(icon)

    def draw(self):
        
        self.background.draw()
        self.name_text.draw()
        self.id_text.draw()
        for icon in self.player_icons:
            icon.draw()
        #pygame.draw.rect(self.screen, (255, 0, 0), self.rect, 2)  # red outline


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                print(f"Clicked lobby: {self.lobby['id']}")
                self.on_click()

class JoinLobbyScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the Profile Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size) 
        self.window_size = window_size
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.back_arrow = Button(self.screen, self.back_arrow_image, self.x_percent(64), self.y_percent(860), self.scale_factor, anchor="topleft")
        self.open_lobbies = Image(self.screen, self.open_lobbies_img, self.x_percent(77), self.y_percent(188), self.scale_factor, anchor="topleft")
        self.enterid_bg = Image(self.screen, self.enterid_button_image, self.x_percent(505), self.y_percent(64), self.scale_factor, anchor="topleft")
        self.enterid = EditableTextbox(self.screen, "   ENTER ID", self.x_percent(554), self.y_percent(83) , 331, 62, align_text="LEFT",text_color = BLUE, scale_factor= self.scale_factor)

        self.create = Button(self.screen, self.create_button_image,
                                            self.x_percent(956), self.y_percent(64), self.scale_factor, 
                                            hover_image_source= self.create_button_hover_image, 
                                            pressed_image_source= self.create_button_pressed_image, 
                                            text = "(+) create", font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")

        self.reload = Button(self.screen, self.reload_button_image,
                                            self.x_percent(1317), self.y_percent(64), self.scale_factor, 
                                            hover_image_source= self.reload_button_image_hover, 
                                            pressed_image_source= self.reload_button_pressed_image, 
                                            font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")

        self.create_lobby_background = Image(self.screen, self.create_lobby_background_img, self.x_percent(230), self.y_percent(244), self.scale_factor, anchor="topleft")        
        self.party_name_img = Image(self.screen, self.party_name_img, self.x_percent(299), self.y_percent(402), self.scale_factor, anchor="topleft")
        self.party_name = EditableTextbox(self.screen, "PARTY NAME", self.x_percent(336), self.y_percent(421) , 338, 71, align_text="LEFT",text_color = BLUE, scale_factor= self.scale_factor)
        self.create_lobby = Button(self.screen, self.create_lobby_img,
                                            self.x_percent(391), self.y_percent(702), self.scale_factor, 
                                            hover_image_source= self.create_lobby_hover_img, 
                                            pressed_image_source= self.create_lobby_hover_img, 
                                            text = "CREATE", font_path=FONT_PATH, font_size=60, text_color=BLACK, anchor="topleft")

        self.cancel = Button(self.screen, self.cancel_img,
                                            self.x_percent(757), self.y_percent(702), self.scale_factor, 
                                            hover_image_source= self.cancel_hover_img, 
                                            pressed_image_source= self.cancel_hover_img,  text = "CANCEL", 
                                            font_path=FONT_PATH, font_size=60, text_color=BLACK, anchor="topleft")

        self.show_create_lobby = False
        self.lobby_visibility = "PUBLIC"  

        self.public_pressed = Button(self.screen, self.public_pressed_img,
                                            self.x_percent(299), self.y_percent(552), self.scale_factor, 
                                            hover_image_source= self.public_pressed_img, 
                                            pressed_image_source= self.public_pressed_img,  text = "PUBLIC", 
                                            font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")
        self.public_unpressed = Button(self.screen, self.public_unpressed_img,
                                            self.x_percent(299), self.y_percent(552), self.scale_factor, 
                                            hover_image_source= self.public_unpressed_img, 
                                            pressed_image_source= self.public_unpressed_img,  text = "PUBLIC", 
                                            font_path=FONT_PATH, font_size=60, text_color=BLACK, anchor="topleft")
        
        self.private_pressed = Button(self.screen, self.private_pressed_img,
                                            self.x_percent(706), self.y_percent(552), self.scale_factor, 
                                            hover_image_source= self.private_pressed_img, 
                                            pressed_image_source= self.private_pressed_img,  text = "PUBLIC", 
                                            font_path=FONT_PATH, font_size=60, text_color=WHITE, anchor="topleft")
        self.private_unpressed = Button(self.screen, self.private_unpressed_img,
                                            self.x_percent(706), self.y_percent(552), self.scale_factor, 
                                            hover_image_source= self.private_unpressed_img, 
                                            pressed_image_source= self.private_unpressed_img,  text = "PRIVATE", 
                                            font_path=FONT_PATH, font_size=60, text_color=BLACK, anchor="topleft")


    def load_assets(self):
        """
        Loads necessary assets.
        """
        self.background_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["background.png"]
        self.start_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b.png"]
        self.start_hover_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_h.png"]
        self.start_pressed_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_p.png"]
        self.back_arrow_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["back_arrow.png"]
        self.open_lobbies_img =  LoadingScreen.ASSET[ASSETS_DIRECTORY]["open_lobbies.png"]

        self.create_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["create.png"]
        self.create_button_hover_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["createhover.png"]
        self.create_button_pressed_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["createpressed.png"]
        self.reload_button_image =  LoadingScreen.ASSET[ASSETS_DIRECTORY]["reload.png"]
        self.reload_button_image_hover = LoadingScreen.ASSET[ASSETS_DIRECTORY]["reloadhover.png"]
        self.reload_button_pressed_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["reloadpressed.png"]
        self.enterid_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["enterid.png"]

        self.create_lobby_background_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["createlobby_background.png"]
        self.party_name_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["partyname.png"]
        self.create_lobby_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["createlobby.png"]
        self.create_lobby_hover_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["createlobbyhover.png"]
        self.cancel_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["cancel.png"]
        self.cancel_hover_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["cancelhover.png"]

        self.public_pressed_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["public_pressed.png"]
        self.public_unpressed_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["public_unpressed.png"]

        self.private_pressed_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["private_pressed.png"]
        self.private_unpressed_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["private_unpressed.png"]
        
        self.lobby_button_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["lobbybutton.png"]
        self.empty_profile_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["empty_profile.png"]
        self.profile_img = LoadingScreen.ASSET[ASSETS_DIRECTORY]["profile_img.png"]


    def set_lobbies(self, lobbies_data):
        self.lobby_buttons = []
        for i, lobby in enumerate(lobbies_data):
            x = self.x_percent(174)
            y = self.y_percent(352 + i * 86)
            x_name = self.x_percent(190) 
            y_button = self.y_percent(352 + i * 86 + 6)
            x_lobby = self.x_percent(566)
            
            player_icon_positions = []
            for j in range(4):
                x_icon = 942 + j * 84  # pixel X position
                x_icon_percent = self.x_percent(x_icon)
                player_icon_positions.append((x_icon_percent, y_button))  
            
            btn = LobbyButton(
                screen=self.screen,
                x=x,
                y=y,
                x_name = x_name,
                x_lobby = x_lobby,
                y_button = y_button,
                lobby=lobby,
                scale_factor=self.scale_factor,
                font_path=FONT_PATH,
                button_img=self.lobby_button_img,
                profile_img=self.profile_img,
                empty_profile_img=self.empty_profile_img,
                player_icon_positions=player_icon_positions,
                on_click=lambda: self.set_next_screen(GUESTLOBBY),
                x_percent=self.x_percent,
                y_percent=self.y_percent
             )
            self.lobby_buttons.append(btn)
           

    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.back_arrow.draw()
        self.enterid_bg.draw()
        self.enterid.draw()
        self.create.draw()
        self.reload.draw()
        self.open_lobbies.draw()
        for btn in getattr(self, 'lobby_buttons', []):
            btn.draw()

        if self.show_create_lobby:
          self.create_lobby_background.draw()
          self.party_name_img.draw()
          self.party_name.draw()
          self.create_lobby.draw()
          self.cancel.draw()

          if self.lobby_visibility == "PUBLIC":
            self.public_pressed.draw()
            self.private_unpressed.draw()
          else:
              self.public_unpressed.draw()
              self.private_pressed.draw() 
        
            

    def update(self):
        """Update the screen and handle events."""
        super().update() 
       
        # Handle events
        for event in pygame.event.get():
            if self.back_arrow.handle_event(event):
                self.show_create_lobby = False
                self.set_next_screen(MAIN_MENU)
            self.enterid.handle_event(event)

            if self.show_create_lobby:
                # First handle modal elements (before handling create)
                self.party_name.handle_event(event)
                if self.cancel.handle_event(event):
                    self.show_create_lobby = False
                if self.public_pressed.handle_event(event):
                    self.lobby_visibility = "PUBLIC"
                if self.private_pressed.handle_event(event):
                    self.lobby_visibility = "PRIVATE"
                if self.create_lobby.handle_event(event):
                    # Handle the creation of the lobby here
                    self.show_create_lobby = False
                    print("Creating lobby with name:", self.party_name.get_text())
                    print("Lobby visibility:", self.lobby_visibility)  
                    self.set_next_screen(OWNLOBBY)
            else:
                # Only handle "create" button if modal isn't open
                if self.create.handle_event(event):
                    self.show_create_lobby = True

            for btn in getattr(self, 'lobby_buttons', []):
                btn.handle_event(event)