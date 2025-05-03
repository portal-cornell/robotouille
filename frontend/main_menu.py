import pygame
from frontend.constants import WHITE, SHARED_DIRECTORY, MATCHMAKING, SETTINGS, BLACK, PROFILE, JOINLOBBY
from frontend.button import Button
from frontend.image import Image
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen
import os

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "main_menu"))

class MenuScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the Main Menu Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size) 
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")

        self.start_button = Button(self.screen, self.start_button_image, 
                                    self.x_percent(556), self.y_percent(342), self.scale_factor, 
                                    hover_image_source= self.start_hover_button_image,
                                    pressed_image_source= self.start_pressed_button_image, 
                                    text = "START", text_color=WHITE)
        self.setting_button = Button(self.screen, self.start_button_image, 
                                    self.x_percent(720), self.y_percent(524), self.scale_factor,
                                    hover_image_source= self.start_hover_button_image, 
                                    pressed_image_source= self.start_pressed_button_image, 
                                    text = "SETTINGS", text_color=WHITE, anchor="center")

        self.profile_button = Button(self.screen, self.profile_image, self.x_percent(1289), self.y_percent(33), 
                                      self.scale_factor, anchor="topleft")
        self.edit_profile_button = Button(self.screen, self.edit_profile_button_image, self.x_percent(956),
                                          self.y_percent(158),  self.scale_factor, text="   edit profile", 
                                          font_size = 40, text_color=BLACK, anchor="topleft", align_text = "left")
        self.setting_logo_button = Button(self.screen, self.settings_button_image, self.x_percent(956), 
                                          self.y_percent(230),  self.scale_factor,  text="   settings", font_size = 40, 
                                          text_color=BLACK, anchor="topleft", align_text = "left")
        self.dropdown_visible = False


    def load_assets(self):
        """
        Loads necessary assets.
        """
        self.background_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["background.png"]
        self.start_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b.png"]
        self.start_hover_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_h.png"]
        self.start_pressed_button_image = LoadingScreen.ASSET[SHARED_DIRECTORY]["button_b_p.png"]
        self.profile_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["menu_profile.png"]
        self.edit_profile_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["edit_profile_button.png"]
        self.settings_button_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["settings_button.png"]

    
    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self.start_button.draw()
        self.setting_button.draw()
        self.profile_button.draw()
        if self.dropdown_visible:
            self.edit_profile_button.draw()
            self.setting_logo_button.draw()


    def update(self):
        """Update the screen and handle events."""
        super().update() 
        clicked_anywhere = False
        # Handle events
        for event in pygame.event.get():
            # Check if the mouse is clicked anywhere on screen.
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_anywhere=True

            # Transitions to JoinLobby when start_button is pressed.
            if self.start_button.handle_event(event):
                self.set_next_screen(JOINLOBBY)
                #self.set_next_screen(MATCHMAKING)


            # Transitions to Settings when setting_button is pressed.
            if self.setting_button.handle_event(event):
                self.set_next_screen(SETTINGS)
            
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