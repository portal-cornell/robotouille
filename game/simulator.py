import pygame

from frontend.pause import PauseScreen
from frontend.constants import ENDGAME

from utils.robotouille_input import create_action_from_event
from robotouille.robotouille_env import create_robotouille_env
from backend.movement.player import Player
from backend.movement.movement import Movement
from game.renderer import RobotouilleGameRenderer

class RobotouilleSimulator:
    def __init__(self, canvas, environment_name: str, seed: int = 42, noisy_randomization: bool = False, movement_mode: str = 'traverse', human = True, render_fps=60):
        """
        Initialize the Robotouille application for gameplay.

        Args:
            canvas (pygame.Surface): The main display canvas.
            environment_name (str): The name of the environment to load.
            seed (int): Seed for randomization (default: 42).
            noisy_randomization (bool): Whether to introduce noise into randomization (default: False).
            movement_mode (str): The movement mode for the environment (default: 'traverse').
            human (bool): Whether a human player is controlling the game (default: True).
            render_fps (int): Frames per second for rendering (default: 60).
        """
        self.human = human
        self.canvas = canvas
        self.env = create_robotouille_env(environment_name, movement_mode, seed, noisy_randomization, renderer_cls=RobotouilleGameRenderer)
        self.renderer = self.env.renderer
        self.obs, self.info = self.env.reset()
        self.done = False
        self.interactive = False  # Set to True to interact with the environment through terminal REPL (ignores input)
        screen_size = canvas.get_size()
        self.surface = pygame.Surface(screen_size)
        self.pause = PauseScreen(screen_size)
        self.clock = pygame.time.Clock()
        self.players = self.env.current_state.get_players()
        self.actions = []
        self.render_fps = render_fps
        self.next_screen = None
    
    def set_next_screen(self, next_screen):
        """
        Set the next screen for transition.

        Specifies the screen that should be displayed after the current screen.

        Args:
           next_screen (str): Identifier for the next screen (e.g., `MAIN_MENU`, `SETTINGS`).

        """
        self.next_screen = next_screen

    def draw(self):
        """
        Renders the current state of the game environment and pause screen onto the canvas.
        """
        self.renderer.render(self.env.current_state, mode='human')
        self.surface.blit(self.renderer.surface, (0, 0))
        self.canvas.blit(self.surface, (0, 0))
        self.surface.blit(self.pause.get_screen(), (0, 0))
        self.canvas.blit(self.surface, (0, 0))
        # The framerate of the renderer. This isn't too important since the renderer
        self.clock.tick(self.render_fps)


    def handle_pause(self, pygame_events):
        """
        Handles pause functionality, including toggling the pause screen and switching game states.

        Args:
            pygame_events (list): List of pygame events to handle.
        """

        if not self.human:
            return
        for event in pygame_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.done = True
                if event.key == pygame.K_p:
                    self.pause.toggle()
                    print("pause toggled")

        if self.pause.next_screen is not None:
            current_screen = self.pause.next_screen
            self.pause.set_next_screen(None)
            print("returning pause")
            return current_screen

        self.pause.update(pygame_events)


    def update(self):
        """
        Main update loop for the simulation. Handles rendering, input, and game logic.

        """
        
        if self.done:
            self.renderer.render(self.env.current_state, close=False)
            self.next_screen = ENDGAME
            return
        
        if self.pause.next_screen is not None:
            self.next_screen = self.pause.next_screen
            self.pause.set_next_screen(None)
            self.pause.toggle()
            return
        
        pygame_events = pygame.event.get()
            
        self.draw()
        self.handle_pause(pygame_events)

        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        player_obj = Player.get_player(self.env.current_state.current_player.name)
        no_action = True

        # If player is moving, do not allow any action; action will be None
        if Movement.is_player_moving(player_obj.name):
            action, args = None, None
            no_action = False
        # If player is not moving, allow action
        else:
            action, args = create_action_from_event(self.env.current_state, mousedown_events + keydown_events, self.env.input_json, self.renderer)
            if action is not None:
                no_action = False

        if not self.interactive and no_action:
            # Retry for keyboard input
            return

        # Construct actions for all players
        self.actions.append((action, args))
        self.env.current_state.current_player = self.env.current_state.next_player()

        # If all players have made an action, step the environment
        if len(self.actions) == len(self.players):
            self.obs, reward, self.done, self.info = self.env.step(self.actions, clock=self.clock)#, interactive=self.interactive)
            self.renderer.render(self.env.current_state, mode='human')
            self.actions = []

        return 