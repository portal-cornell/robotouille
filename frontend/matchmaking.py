import pygame
from frontend.constants import *
from frontend.button import Button
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.screen import ScreenInterface

# Set up the assets directory
ASSETS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "matchmaking")

class MatchMakingScreen(ScreenInterface):
    def __init__(self, screen):
        """
        Initialize the Lobby Screen.

        Args:
            screen (pygame.Surface): The display surface where the lobby screen components will be drawn.
        """
        super().__init__(screen)
        self.background = Image(screen, self.background_image, 0.5, 0.5, self.scale_factor)
        self.players = [
            {"name": Textbox(self.screen,"", self.x_percent(291), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor),
              "icon": Image(self.screen, self.empty_profile_image, self.x_percent(291), self.y_percent(426), self.scale_factor)},
            {"name": Textbox(self.screen,"", self.x_percent(576), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor), 
             "icon": Image(self.screen, self.empty_profile_image, self.x_percent(576), self.y_percent(426), self.scale_factor)},
            {"name": Textbox(self.screen,"", self.x_percent(862), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor), 
             "icon": Image(self.screen, self.empty_profile_image, self.x_percent(862), self.y_percent(426), self.scale_factor)},
            {"name": Textbox(self.screen,"", self.x_percent(1148), self.y_percent(577), 188, 72, font_size=40, scale_factor=self.scale_factor), 
             "icon": Image(self.screen, self.empty_profile_image, self.x_percent(1148), self.y_percent(426), self.scale_factor)},
            ] 
        self.host = False
        self.count = 0

    def load_assets(self):
        """Load necessary assets."""
        background_path = os.path.join(SHARED_DIRECTORY, "background.png")
        empty_path = os.path.join(ASSETS_DIRECTORY, "empty.png")
        profile_path = os.path.join(ASSETS_DIRECTORY, "profile.png")

        self.background_image = pygame.image.load(background_path).convert_alpha()
        self.empty_profile_image = pygame.image.load(empty_path).convert_alpha()
        self.profile_image = pygame.image.load(profile_path).convert_alpha()


    def setPlayers(self, existing_players):
        """
        Set existing players.

        Args:
            existing_players (list of dict): List of players to add, each with 'name' and 'icon'.
        """

        if len(existing_players) >= MAX_PLAYERS :
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
            
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.set_next_screen(MAIN_MENU)
                elif event.key == pygame.K_g:
                    self.set_next_screen(GAME)
