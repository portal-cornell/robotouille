import pygame
from frontend.constants import *
from frontend.button import Button
from frontend.image import Image
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
            {"name": None, "icon": Image(screen, self.empty_profile_image, self.x_percent(290.5), self.y_percent(421.5), self.scale_factor)},
            {"name": None, "icon": Image(screen, self.empty_profile_image, self.x_percent(290.5), self.y_percent(575.5), self.scale_factor)},
            {"name": None, "icon": Image(screen, self.empty_profile_image, self.x_percent(290.5), self.y_percent(861.5), self.scale_factor)},
            {"name": None, "icon": Image(screen, self.empty_profile_image, self.x_percent(290.5), self.y_percent(1147.5), self.scale_factor)},
            ] 
        self.max_players = 4 
        self.numPlayer = 0
        

    def load_assets(self):
        """Load necessary assets."""
        background_path = os.path.join(SHARED_DIRECTORY, "background.png")
        empty_path = os.path.join(ASSETS_DIRECTORY, "empty.png")
        profile_path = os.path.join(ASSETS_DIRECTORY, "profile.png")

        self.background_image = pygame.image.load(background_path).convert_alpha()
        self.empty_profile_image = pygame.image.load(empty_path).convert_alpha()
        self.profile_image = pygame.image.load(profile_path).convert_alpha()


    def create_room(self, host_name):
        """
        Creates a room with the host player.

        Args:
            host_name (str): The name of the host player.
        """
        self.players[0] = {"name": host_name, "icon": self.profile_image}
        self.numPlayer = 1

    def add_player(self, player_name):
        """
        Adds a new player to the room.

        Args:
            player_name (str): The name of the player to add.
        """

        if self.numPlayer >= (self.max_players - 1):
            raise Exception("To many players")

        self.players[self.numPlayer] = {"name": player_name, "icon": self.profile_image}
        self.numPlayer += 1

    def join_room(self, existing_players):
        """
        Joins a room with existing players.

        Args:
            existing_players (list of dict): List of players to add, each with 'name' and 'icon'.
        """

        if len(existing_players) >= self.max_players :
            raise Exception("To many players")
        self.players = existing_players

    def remove_player(self, player_name):
        """
        Removes a player from the room by name.

        Args:
            player_name (str): The name of the player to remove.
        """
        for player in self.players:
            if player["name"] == player_name:
                player["name"] = None
                player["icon"] = self.empty_profile_image
                break
        self._remove_gaps() 

    def _remove_gaps(self):
        """Shift players to the left to remove gaps between them."""
        self.players = [player for player in self.players if player["name"] is not None]
        while len(self.players) < self.max_players:
            self.players.append({"name": None, "icon": self.empty_profile_image})

    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        # for i, player in enumerate(self.players):
        #     icon = player["icon"]
        #     name = player["name"]
        #     player_icon = Image(self.screen, icon, self.x_percent(20 + i * 20), self.y_percent(40), self.scale_factor)
        #     player_icon.draw()
        #     if name is not None:
        #         name_text = self.font.render(name, True, (0, 0, 0))
        #         self.screen.blit(name_text, (self.x_percent(20 + i * 20), self.y_percent(55))) 

    def update(self):
        """Update the screen and handle events."""
        super().update()
