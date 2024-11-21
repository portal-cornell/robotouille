import pygame
import time
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env
from frontend.pause import PauseScreen
from frontend.constants import *
from backend.movement.player import Player
from backend.movement.movement import Movement, Mode


class RobotouilleSimulator:
    def __init__(self, canvas, environment_name: str, seed: int = 42, noisy_randomization: bool = False, movement_mode: str = 'traverse'):
        self.canvas = canvas
        self.env, self.json, self.renderer = create_robotouille_env(environment_name, movement_mode, seed, noisy_randomization)
        self.obs, self.info = self.env.reset()
        self.done = False
        self.interactive = False  # Set to True to interact with the environment through terminal REPL (ignores input)
        screen_size = canvas.get_size()
        self.surface = pygame.Surface(screen_size)
        self.pause = PauseScreen(screen_size)
        self.clock = pygame.time.Clock()
        self.players = self.obs.get_players()
        self.actions = []

    def draw(self):
        self.renderer.render(self.obs, mode='human')
        self.surface.blit(self.renderer.surface, (0, 0))
        self.surface.blit(self.pause.get_screen(), (0, 0))
        self.canvas.blit(self.surface, (0, 0))
        self.clock.tick(60)

    def update(self):
        if self.done:
            self.renderer.render(self.obs, close=True)
            return ENDGAME
        
        self.draw()
        pygame_events = pygame.event.get()
        for event in pygame_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.done = True
                if event.key == pygame.K_p:
                    self.pause.toggle()

        if self.pause.next_screen is not None:
            current_screen = self.pause.next_screen
            self.pause.set_next_screen(None)
            return current_screen

        self.pause.update(pygame_events)

        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        player_obj = Player.get_player(self.obs.current_player.name)
        no_action = True

        # If player is moving, do not allow any action; action will be None
        if Movement.is_player_moving(player_obj.name):
            action, args = None, None
            no_action = False
        # If player is not moving, allow action
        else:
            action, args = create_action_from_control(self.env, self.obs, self.obs.current_player, mousedown_events + keydown_events, self.renderer)
            if action is not None:
                no_action = False

        if not self.interactive and no_action:
            # Retry for keyboard input
            return

        # Construct actions for all players
        self.actions.append((action, args))
        self.obs.current_player = self.obs.next_player()

        # If all players have made an action, step the environment
        if len(self.actions) == len(self.players):
            self.obs, reward, self.done, self.info = self.env.step(self.actions, clock=self.clock, interactive=self.interactive)
            self.renderer.render(self.obs, mode='human')
            self.actions = []

        return 
