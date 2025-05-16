import asyncio
import json
import pickle
import base64
import websockets
import pygame
from robotouille.robotouille_env import create_robotouille_env
from utils.robotouille_input import create_action_from_event
from backend.movement.player import Player

from frontend.constants import GAME, ENDGAME, MATCHMAKING, MAIN_MENU
from frontend.endgame import EndScreen
from frontend.matchmaking import MatchMakingScreen
from game.simulator import RobotouilleSimulator

class NetworkManager:
    def __init__(self, environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str, host: str = "ws://localhost:8765", args = None, screen = None, fps = None, clock = None, screen_size = (1440, 1024), simulator_screen_size = (512, 512)):
        self.websocket = None
        self.shared_state = {}
        self.environment_name = environment_name
        self.seed = seed
        self.noisy_randomization = noisy_randomization
        self.movement_mode = movement_mode
        self.host = host
        self.message_handlers = {}
        self.simulator_screen_size = simulator_screen_size
        self.current_screen = MATCHMAKING
        self.need_update = True
        self.screen = screen
        self.running = True
        self.simulator_instance = None
        self.args = args
        self.fps = fps
        self.clock = clock
        self.screen_size = screen_size

    def update_screen(self):
        if self.current_screen in self.screens:
            screen_obj = self.screens[self.current_screen]
            screen_obj.update()
            self.screen.blit(screen_obj.get_screen(), (0, 0))
            if screen_obj.next_screen is not None:
                self.current_screen = screen_obj.next_screen
                screen_obj.set_next_screen(None)
                self.need_update = True
        if self.current_screen == MAIN_MENU:
            self.running = False

    async def game_loop(self):
        while self.running:
            current_screen = self.current_screen
            self.screen.fill((0,0,0))
            if self.current_screen == GAME:
                if self.simulator_instance is None:
                    screen = pygame.display.set_mode(self.simulator_screen_size) # TODO: Remove when screen size can scale properly
                    self.simulator_instance = RobotouilleSimulator(
                            screen=screen,
                            environment_name=self.args.environment_name,
                            seed=self.args.seed,
                            noisy_randomization=self.args.noisy_randomization,
                            movement_mode=self.args.movement_mode,
                            clock=self.clock,
                            screen_size=self.simulator_screen_size,
                            render_fps=self.fps
                        )
                    
                self.simulator_instance.update()
                screen.blit(self.simulator_instance.get_screen(), (0, 0))
                if self.simulator_instance.next_screen is not None:
                    self.current_screen = self.simulator_instance.next_screen
                    self.simulator_instance.set_next_screen(None)
                    self.simulator_instance = None 
                    screen = pygame.display.set_mode(self.screen_size)
            else:
                if self.current_screen == MATCHMAKING and self.need_update:
                    # TODO should be a packet that sends player data over network
                    self.screens[current_screen].set_players(["Player1", "Player2"]) # list of dictionary of profile + names [{name: ----, profile_image: ----.png, id: ___}]
                    self.need_update = False
                if self.current_screen == ENDGAME and self.need_update:
                    # TODO should be a packet that sends player data over network
                    self.screens[current_screen].create_profile([(1,  "Player 1", "profile"), (2, "Player 2", "profile")]) # [{id, name, profile, status}]
                    self.screens[current_screen].set_stars(2) # 
                    self.screens[current_screen].set_coin(12)
                    self.screens[current_screen].set_bell(121)
                    self.need_update = False
            self.update_screen()
            pygame.display.flip()
            self.clock.tick(self.fps)


    def register_handler(self, message_type: str, handler_fn):
        """Register a handler function for a specific message type."""
        self.message_handlers[message_type] = handler_fn
        
    async def background_listener(self):
        """
        Continuously listens for messages from the server in the background.
        NEED TO DEBUG DOES NOT WORK 
        """
        print("[Listener] Started")
        try:
            while self.running:
                message = await self.websocket.recv()
                print("[Listener] Raw message:", message)
        except websockets.ConnectionClosed:
            print("[Listener] Connection closed")


    async def handle_message(self, message):
        """
        Handle incoming messages from the server.

        You can parse JSON, dispatch to handlers, etc.
        """
        try:
            data = json.loads(message)
            print("[Handler] Decoded:", data)
        except Exception as e:
            print("[Handler] Failed to decode:", e)

    async def connect(self):
        """
        Runs the client by starting the asynchronous client loop.

        Args:
            environment_name (str): The name of the environment to run.
            seed (int):The seed for the environment.
            noisy_randomization (bool): Whether to use noisy randomization.
            movement_mode (str): The movement mode to use.
            host (str): The host to connect to.
        """
        async with websockets.connect(self.host) as websocket:
            print("[Client] Connected!")
            self.websocket = websocket
            self.screens = {
                ENDGAME : EndScreen(self.screen_size, websocket),
                MATCHMAKING : MatchMakingScreen(self.screen_size, websocket)
            }

            receiver = asyncio.create_task(self.background_listener())
            await self.game_loop()
            await receiver
            print('close connection')