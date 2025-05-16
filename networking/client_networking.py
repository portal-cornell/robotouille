import asyncio
import json
import pickle
import base64
import websockets
import pygame
from robotouille.robotouille_env import create_robotouille_env
from utils.robotouille_input import create_action_from_event
from backend.movement.player import Player

class NetworkManager:
    def __init__(self, environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str, host: str = "ws://localhost:8765"):
        self.websocket = None
        self.shared_state = {}
        self.environment_name = environment_name
        self.seed = seed
        self.noisy_randomization = noisy_randomization
        self.movement_mode = movement_mode
        self.host = host
        self.message_handlers = {}

    def register_handler(self, message_type: str, handler_fn):
        """Register a handler function for a specific message type."""
        self.message_handlers[message_type] = handler_fn

    def try_decode_message(self, message):
        try:
            parsed = json.loads(message)
            if isinstance(parsed, str):
                return parsed
            elif isinstance(parsed, dict):
                return parsed.get("type")  # optional support
        except:
            return None
        
    async def background_listener(self):
        """
        Continuously listens for messages from the server in the background.
        NEED TO DEBUG DOES NOT WORK 
        """
        print("[Listener] Started")
        try:
            while True:
                message = await self.websocket.recv()
                print("[Listener] Raw message:", message)
                decoded = self.try_decode_message(message)
                print("[Listener] Received:", decoded)

                # Dispatch by message type
                if isinstance(decoded, str):
                    if decoded in self.message_handlers:
                        await self.message_handlers[decoded]()
                        del self.message_handlers[decoded]
                    else:
                        print(f"[Listener] No handler for message: {decoded}")
                else:
                    print(f"[Listener] Ignored unrecognized message: {message}")

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
        print('run client')
        await self.create_websocket()
        print('[Client] Connected to server')

    async def create_websocket(self):
        """
        Establish Websocket connection
        """
        self.websocket = await websockets.connect(self.host)
        asyncio.create_task(self.background_listener())  # Run listener in background


    async def send_message(self, payload):
        """
        Encodes and sends a message to the server.

        Args:
            payload (dict): dictionary
        """
        await self.websocket.send(json.dumps(payload))
