import pygame
from frontend.constants import WHITE, SHARED_DIRECTORY, GAME, MAIN_MENU
from frontend.button import Button
from frontend.image import Image
from frontend.textbox import Textbox
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os, json

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "endgame"))

class EndScreen(ScreenInterface):
    def __init__(self, window_size, websocket):
        """Initialize the end screen with UI components.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size) 
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.level_complete = Textbox(self.screen, "LEVEL FINISHED", self.x_percent(720.5), self.y_percent(124.5), 615, 96, font_size=80, scale_factor=self.scale_factor, anchor="center")
        self.quit_button = Button(self.screen, self.blue_button_image, 
                                            self.x_percent(397), self.y_percent(868), self.scale_factor, 
                                            hover_image_source= self.blue_hover_button_image,
                                            pressed_image_source= self.blue_pressed_button_image, 
                                            font_size=40,
                                            text = "QUIT", text_color=WHITE, anchor="center")
        self.play_again_button = Button(self.screen, self.red_button_image, 
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
        self.coins_text = Textbox(self.screen, "0", self.x_percent(577), self.y_percent(431), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center")
        self.bells = Image(self.screen, self.bell_image, self.x_percent(881.5), self.y_percent(438.74), self.scale_factor, anchor="center")
        self.bells_text = Textbox(self.screen, "0", self.x_percent(984), self.y_percent(430), 188, 72, font_size=40, scale_factor=self.scale_factor, anchor="center")
        self.timer_started = False
        self.timer_start_time = 0
        self.websocket = websocket
        self.pending = True
        
    def create_profile(self, players): 
        """Create UI elements for each player.

        Args:
            players (list of tuples): A list containing one player tuple in the format (player_id, player_name, status). Max length is 4
        """
        offset = 313
        if len(players) == 1:
            x = 714
        elif len(players) == 2:
            x = 556.5
        elif len(players) == 3:
            x = 398.5 
        elif len(players) == 4:
            x = 239.5  
        else:
            raise Exception("To many players")

        for i in range(len(players)):
            image = None
            if players[i][2] == "no":
                image = self.no_image
            elif players[i][2] == "yes":
                image = self.yes_image
            else:
                iamge = self.pending_image

            pos = x + (offset) * i 
            self.profiles[players[i][0]] = {
            "profile": Image(self.screen, self.profile_image, self.x_percent(pos), self.y_percent(616.5), self.scale_factor, anchor="center"),
            "name": Textbox(self.screen, players[i][1], self.x_percent(pos), self.y_percent(697), 188, 72, font_size=40, scale_factor=self.scale_factor, text_color=WHITE, anchor="center"),
            "status": Image(self.screen, image, self.x_percent(pos + 98.5), self.y_percent(503), self.scale_factor, anchor="center")
            }

    def set_stars(self, count):
        """Set the number of stars to display as filled.

        Args:
            count (int): The number of stars to fill (must be between 0 and 3).

        """
        for i in range(3):
            if i < count:
                self.stars[i].set_image(self.star_full_image)
            else:
                self.stars[i].set_image(self.star_empty_image)

    def set_coin(self, value):
        """Update the displayed coin value.

        Args:
            value (int): The new coin value to display.
        """
        self.coins_text.set_text(str(value))
    
    def set_bell(self, value):
        """Update the displayed bell value.

        Args:
            value (int): The new bell value to display.
        """
        self.bells_text.set_text(str(value))
    
    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.level_complete.draw()
        self.quit_button.draw()
        self.play_again_button.draw()
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
        self.background_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["background.png"]
        self.profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["profile.png"]
        self.bell_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["bell.png"]
        self.coin_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["coin.png"]
        self.pending_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["pending.png"]
        self.yes_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["yes.png"]
        self.no_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["no.png"]
        self.star_full_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["star_full.png"]
        self.star_empty_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["star_empty.png"]

        self.blue_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b.png"]
        self.blue_hover_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_h.png"]
        self.blue_pressed_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_p.png"]
        self.red_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_r.png"]
        self.red_hover_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_r_h.png"]
        self.red_pressed_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_r_p.png"]

    def set_next_screen(self, next_screen):
        """
        Set the next screen for transition.

        Specifies the screen that should be displayed after the current screen.

        Args:
           next_screen (str): Identifier for the next screen (e.g., `MAIN_MENU`, `SETTINGS`).

        """
        super().set_next_screen(next_screen)
        self.pending = True

    async def update(self):
        """Update the screen and handle events."""
        super().update()

        # Handle events
        for event in pygame.event.get():
            if self.play_again_button.handle_event(event) and self.pending:
                self.pending = False
                if not self.timer_started:
                    self.timer_started = True
                    self.timer_start_time = pygame.time.get_ticks()
                # await self.websocket.send(json.dumps({"type": "play_again"}))
                # self.profiles[1]["status"].set_image(self.yes_image)

            if self.quit_button.handle_event(event):
                self.set_next_screen(MAIN_MENU)
                self.timer_started = False


        if self.timer_started:
            elapsed_time = (pygame.time.get_ticks() - self.timer_start_time) / 1000  # seconds
            print(f"Timer running: {elapsed_time:.2f} seconds")
            if elapsed_time >= 5:
                self.timer_start_time = 0
                self.timer_started = False
                self.set_next_screen(GAME)