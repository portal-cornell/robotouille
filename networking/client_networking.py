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

    async def background_listener(self):
        """
        Continuously listens for messages from the server in the background.
        """
        print("[Listener] Started")
        # while True:
        try:
            message = await self.websocket.recv()
            print("[Listener] Received:", message)
            await self.handle_message(message)
        except websockets.ConnectionClosed:
            print("[Listener] WebSocket connection closed")
            # break

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

    def connect(self):
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
        asyncio.run(self.create_websocket())

    async def create_websocket(self):
        """
        Establish Websocket + Game loop
        """
        uri = self.host

        async with websockets.connect(uri) as websocket:
            self.websocket = websocket

            print("In lobby")
            opening_message = await websocket.recv()
            print("In game")
            opening_data = json.loads(opening_message)

            print(opening_data)
            await self.background_listener()


    async def send_message(self, payload):
        """
        Encodes and sends a message to the server.

        Args:
            payload (Any): A serializable Python object (e.g., action tuple)
        """
        if self.websocket is None or self.websocket.close:
            print("[Warning] Tried to send on a closed WebSocket.")
            return

        encoded = base64.b64encode(pickle.dumps(payload)).decode('utf-8')
        await self.websocket.send(json.dumps(encoded))
