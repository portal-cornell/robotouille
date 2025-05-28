import asyncio
import json
import websockets
import pygame

from frontend.constants import GAME, ENDGAME, MATCHMAKING, MAIN_MENU
from frontend.endgame import EndScreen
from frontend.matchmaking import MatchMakingScreen
from game.simulator import RobotouilleSimulator
from networking.server_networking import DEBUGGING

class NetworkManager:
    """
    NetworkManager handles all WebSocket communication and screen transitions
    on the client side for the Robotouille game.

    Responsibilities:
    - Connect to the server and send initial connection info
    - Listen for server messages (e.g., Start_game, Player_list, Results, etc.)
    - Route messages to appropriate frontend components
    - Coordinate screen updates via `game_loop()`
    - Launch and update the RobotouilleSimulator when in-game

    Attributes:
        websocket (WebSocketClientProtocol): Current active connection.
        shared_state (dict): Future-proofing for client state sharing across modules.
        current_screen (int): Active screen identifier (from constants like MATCHMAKING, GAME).
        simulator_instance (RobotouilleSimulator): Only active when in-game.
        screen (pygame.Surface): Main display surface.
        fps (int): Frame rate for UI rendering.

    TODO: Suyean, should update game/simulator to match the states given by the server
    """
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
        self.screen = screen
        self.running = True
        self.simulator_instance = None
        self.args = args
        self.fps = fps
        self.clock = clock
        self.screen_size = screen_size

    async def update_screen(self):
        """
        Transitions between in game screens
        """
        if self.current_screen in self.screens:
            screen_obj = self.screens[self.current_screen]
            await screen_obj.update()
            self.screen.blit(screen_obj.get_screen(), (0, 0))
            if screen_obj.next_screen is not None:
                self.current_screen = screen_obj.next_screen
                screen_obj.set_next_screen(None)
        if self.current_screen == MAIN_MENU:
            if DEBUGGING: print("[Client] Returning to main menu — exiting game loop")
            self.running = False
            await self.websocket.close()

    async def game_loop(self):
        """
        Runs game loop
        """
        while self.running:
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
            await self.update_screen()
            pygame.display.flip()
            await asyncio.sleep(1 / self.fps)


    async def background_listener(self):
        """
        Continuously listens for messages from the server in the background.
        """
        if DEBUGGING: print("[Listener] Started")
        try:
            while self.running:
                message = await self.websocket.recv()
                if DEBUGGING: print("[Listener] Raw message:", message)
                parsed = json.loads(message)
                if isinstance(parsed, dict): 
                    if parsed.get("type") == "Start_game" or parsed.get("type") == "Restart":
                        self.screens[self.current_screen].set_next_screen(None)
                        self.current_screen = GAME
                    elif parsed.get("type") == "Player_list":
                        payload = parsed.get("payload")
                        self.screens[MATCHMAKING].set_players(payload)  
                    elif parsed.get("type") == "Player_status":
                        payload = parsed.get("payload")
                        self.screens[ENDGAME].create_profile(payload) 
                    elif parsed.get("type") == "Game_state":
                        # TODO Su Yean
                        pass
                    elif parsed.get("type") == "Game_ended":
                        # TODO Su Yean
                        pass
                    elif parsed.get("type") == "Result":
                        payload = parsed.get("payload")
                        stars, coins, bells = payload.get("stars"), payload.get("coins"), payload.get("bells")
                        self.screens[ENDGAME].set_stars(stars) 
                        self.screens[ENDGAME].set_coin(coins)
                        self.screens[ENDGAME].set_bell(bells)
                    elif parsed.get("type") == "Auto_matchmaking":
                        self.screens[self.current_screen].set_next_screen(None)
                        self.current_screen = MATCHMAKING
                    elif parsed.get("type") == "Quit":
                        self.screens[self.current_screen].set_next_screen(None)
                        self.current_screen = MAIN_MENU
        except websockets.ConnectionClosed:
            print("[Listener] Connection closed")
        except Exception as e:
            print(f"[Listener] ERROR: {e}")


    async def connect(self):
        """
        Connects to the WebSocket server, rusn the game loop, and creates 
        the background listens to hear server messages
        """
        try:
            async with websockets.connect(self.host) as websocket:
                if DEBUGGING: print("[Client] Connected!")
                self.websocket = websocket
                # TODO change this to be personalized
                await websocket.send(json.dumps({
                    "type": "Connect",
                    "lobby_id": "default",       
                    "player_name": "Alice"  
                }))
                # await websocket.send(json.dumps({"type": "Connect to server"}))
                if DEBUGGING: print("[Client] Sent Connect message")

                self.screens = {
                    ENDGAME : EndScreen(self.screen_size, websocket),
                    MATCHMAKING : MatchMakingScreen(self.screen_size, websocket)
                }

                await asyncio.gather(
                            self.background_listener(),
                            self.game_loop()
                        )
        except Exception as e:
            print(f"[Client] Failed to connect: {e}")