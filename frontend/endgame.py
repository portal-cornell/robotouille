import pygame
from frontend.constants import *
from frontend.button import Button
from frontend.image import Image
from frontend.slider import Slider
from frontend.textbox import Textbox
from frontend.editable_textbox import EditableTextbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "endgame"))

class EndScreen(ScreenInterface):
    def __init__(self, window_size):
        """Initialize the end screen with UI components.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size) 
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.level_complete = Textbox(self.screen, "LEVEL FINISHED", self.x_percent(720.5), self.y_percent(124.5), 615, 96, font_size=80, scale_factor=self.scale_factor, anchor="center")
        self.quit = Button(self.screen, self.blue_button_image, 
                                            self.x_percent(397), self.y_percent(868), self.scale_factor, 
                                            hover_image_source= self.blue_hover_button_image,
                                            pressed_image_source= self.blue_pressed_button_image, 
                                            font_size=40,
                                            text = "QUIT", text_color=WHITE, anchor="center")
        self.play_again = Button(self.screen, self.red_button_image, 
                                            self.x_percent(1044), self.y_percent(868), self.scale_factor, 
                                            hover_image_source= self.red_hover_button_image,
                                            pressed_image_source= self.red_pressed_button_image, 
                                            font_size=40,
                                            text = "PLAY AGAIN", text_color=WHITE, anchor="center")
        self.profiles = {}
        self.stars = [
            Image(self.screen, self.star_empty_image, self.x_percent(459.26), self.y_percent(263.26), self.scale_factor, anchor="center"),
            Image(self.screen, self.star_empty_image, self.x_percent(720.5), self.y_percent(263.26), self.scale_factor, anchor="center"),
            Image(self.screen, self.star_empty_image, self.x_percent(981.74), self.y_percent(263.26), self.scale_factor, anchor="center"),
        ]
        self.coins = Image(self.screen, self.coin_image, self.x_percent(479), self.y_percent(431), self.scale_factor, anchor="center")
        self.coins_text = Textbox(self.screen, "213", self.x_percent(577), self.y_percent(431), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center")
        self.bells = Image(self.screen, self.bell_image, self.x_percent(881.5), self.y_percent(438.74), self.scale_factor, anchor="center")
        self.bells_text = Textbox(self.screen, "214", self.x_percent(984), self.y_percent(430), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center")

    def createOneProfile(self, players):
        """Create UI elements for a single player profile.

        Args:
            players (list of tuples):
                A list containing one player tuple in the format (player_id, player_name).
        """
        self.profiles[players[0][0]] = {
            "profile":Image(self.screen, self.profile_image, 0.5, self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen,players[0][1], 0.5, self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status":Image(self.screen, self.pending_image, 0.5 + self.x_percent(107.5), self.y_percent(503), self.scale_factor, anchor="center")
            }

    def createTwoProfile(self, players):
        """Create UI elements for a two player profile.

        Args:
            players (list of tuples): A list containing one player tuple in the format (player_id, player_name).
        """
        self.profiles[players[0][0]] = {
            "profile":Image(self.screen, self.profile_image, self.x_percent(556.5), self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen,players[0][1], self.x_percent(556.5), self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status":Image(self.screen, self.pending_image, self.x_percent(664), self.y_percent(503), self.scale_factor, anchor="center")
            }
        self.profiles[players[1][0]] = {
            "profile":Image(self.screen, self.profile_image, self.x_percent(869.5), self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen,players[0][1], self.x_percent(869.5), self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status":Image(self.screen, self.pending_image, self.x_percent(976.5), self.y_percent(503), self.scale_factor, anchor="center")
            }

    def createThreeProfile(self, players):
        """Create UI elements for a Three player profile.

        Args:
            players (list of tuples): A list containing one player tuple in the format (player_id, player_name).
        """
        self.profiles[players[0][0]] = {
            "profile": Image(self.screen, self.profile_image, self.x_percent(398.5), self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen, players[0][1], self.x_percent(398.5), self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status": Image(self.screen, self.pending_image, self.x_percent(506), self.y_percent(503), self.scale_factor, anchor="center")
        }
        self.profiles[players[1][0]] = {
            "profile": Image(self.screen, self.profile_image, self.x_percent(711.5), self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen, players[1][1], self.x_percent(711.5), self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status": Image(self.screen, self.pending_image, self.x_percent(818.5), self.y_percent(503), self.scale_factor, anchor="center")
        }
        self.profiles[players[2][0]] = {
            "profile": Image(self.screen, self.profile_image, self.x_percent(1026.5), self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen, players[2][1], self.x_percent(1026.5), self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status": Image(self.screen, self.pending_image, self.x_percent(1133.5), self.y_percent(503), self.scale_factor, anchor="center")
        }

    def createFourProfile(self, players):
        """Create UI elements for a Four player profile.

        Args:
            players (list of tuples): A list containing one player tuple in the format (player_id, player_name).
        """
        self.profiles[players[0][0]] = {
            "profile": Image(self.screen, self.profile_image, self.x_percent(239.5), self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen, players[0][1], self.x_percent(239.5), self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status": Image(self.screen, self.pending_image, self.x_percent(347), self.y_percent(503), self.scale_factor, anchor="center")
        }
        self.profiles[players[1][0]] = {
            "profile": Image(self.screen, self.profile_image, self.x_percent(552.5), self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen, players[1][1], self.x_percent(552.5), self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status": Image(self.screen, self.pending_image, self.x_percent(660), self.y_percent(503), self.scale_factor, anchor="center")
        }
        self.profiles[players[2][0]] = {
            "profile": Image(self.screen, self.profile_image, self.x_percent(865.5), self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen,players[2][1], self.x_percent(865.5), self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status": Image(self.screen, self.pending_image, self.x_percent(973), self.y_percent(503), self.scale_factor, anchor="center")
        }
        self.profiles[players[3][0]] = {
            "profile": Image(self.screen, self.profile_image, self.x_percent(1178.5), self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen, players[3][1], self.x_percent(1178.5), self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status": Image(self.screen, self.pending_image, self.x_percent(1286), self.y_percent(503), self.scale_factor, anchor="center")
        }

    def createProfile(self, players):
        """Create UI elements for each player.

        Args:
            players (list of tuples): A list containing one player tuple in the format (player_id, player_name). Max length is 4
        """
        if len(players) == 1:
            self.createOneProfile(players)
        elif len(players) == 2:
            self.createTwoProfile(players)
        elif len(players) == 3:
            self.createThreeProfile(players)
        else:
            self.createFourProfile(players)

    def setStars(self, count):
        """Set the number of stars to display as filled.

        Args:
            count (int): The number of stars to fill (must be between 0 and 3).

        """
        for i in range(3):
            if i < count:
                self.stars[i].set_image(self.star_full_image)
            else:
                self.stars[i].set_image(self.star_empty_image)

    def setCoin(self, value):
        """Update the displayed coin value.

        Args:
            value (int): The new coin value to display.
        """
        self.coins_text.set_text(str(value))
    
    def setBell(self, value):
        """Update the displayed bell value.

        Args:
            value (int): The new bell value to display.
        """
        self.bells_text.set_text(str(value))
    
    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.level_complete.draw()
        self.quit.draw()
        self.play_again.draw()
        for star in self.stars:
            star.draw()
        for id in self.profiles:
            self.profiles[id]["profile"].draw()
            self.profiles[id]["status"].draw()
            self.profiles[id]["name"].draw()
        self.bells.draw()
        self.coins.draw()
        self.coins_text.draw()
        self.bells_text.draw()

    def load_assets(self):
        """Load necessary assets."""
        background_path = os.path.join(SHARED_DIRECTORY, "background.png")
        profile_path = os.path.join(ASSETS_DIRECTORY, "profile.png")
        bell_path = os.path.join(ASSETS_DIRECTORY, "bell.png")
        coin_path = os.path.join(ASSETS_DIRECTORY, "coin.png")
        pending_path = os.path.join(ASSETS_DIRECTORY, "pending.png")
        yes_path = os.path.join(ASSETS_DIRECTORY, "yes.png")
        no_path = os.path.join(ASSETS_DIRECTORY, "no.png")
        star_full_path = os.path.join(ASSETS_DIRECTORY, "star_full.png")
        star_empty_path = os.path.join(ASSETS_DIRECTORY, "star_empty.png")
        blue_button_path = os.path.join(SHARED_DIRECTORY, "button_b.png")
        blue_hover_button_path = os.path.join(SHARED_DIRECTORY, "button_b_h.png")
        blue_pressed_button_path = os.path.join(SHARED_DIRECTORY, "button_b_p.png")
        red_button_path = os.path.join(SHARED_DIRECTORY, "button_r.png")
        red_hover_button_path = os.path.join(SHARED_DIRECTORY, "button_r_h.png")
        red_pressed_button_path = os.path.join(SHARED_DIRECTORY, "button_r_p.png")

        self.background_image = LoadingScreen.ASSET[background_path]
        self.profile_image = LoadingScreen.ASSET[profile_path]
        self.bell_image = LoadingScreen.ASSET[bell_path]
        self.coin_image = LoadingScreen.ASSET[coin_path]
        self.pending_image = LoadingScreen.ASSET[pending_path]
        self.yes_image = LoadingScreen.ASSET[yes_path]
        self.no_image = LoadingScreen.ASSET[no_path]
        self.star_full_image = LoadingScreen.ASSET[star_full_path]
        self.star_empty_image = LoadingScreen.ASSET[star_empty_path]

        self.blue_button_image = LoadingScreen.ASSET[blue_button_path]
        self.blue_hover_button_image = LoadingScreen.ASSET[blue_hover_button_path]
        self.blue_pressed_button_image = LoadingScreen.ASSET[blue_pressed_button_path]
        self.red_button_image = LoadingScreen.ASSET[red_button_path]
        self.red_hover_button_image = LoadingScreen.ASSET[red_hover_button_path]
        self.red_pressed_button_image = LoadingScreen.ASSET[red_pressed_button_path]
    

    def update(self):
        """Update the screen and handle events."""
        super().update() 

        # Handle events
        for event in pygame.event.get():
            if self.play_again.handle_event(event):
                self.set_next_screen(GAME)
            if self.quit.handle_event(event):
                self.set_next_screen(MAIN_MENU)
            
