import asyncio
import json
import pickle
import base64
import websockets
import pygame
from robotouille.robotouille_env import create_robotouille_env
from utils.robotouille_input import create_action_from_event
from backend.movement.player import Player

def run_client(environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str, host: str="ws://localhost:8765"):
    asyncio.run(client_loop(environment_name, seed, noisy_randomization, movement_mode, host))

async def client_loop(environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str, host: str="ws://localhost:8765"):
    uri = host

    async def send_actions(websocket, shared_state):
        env = shared_state["env"]
        env.render(render_mode = 'human')
        player = shared_state["player"]
        online = True
        while not shared_state["done"]:
            state = env.current_state
            pygame_events = pygame.event.get()
            mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
            keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
            action, args = create_action_from_event(state, mousedown_events + keydown_events, env.input_json, env.renderer, player)
            # Use this to simulate disconnect
            online = not (pygame.key.get_mods() & pygame.KMOD_CAPS)

            if action is not None:
                if online:
                    encoded_action = base64.b64encode(pickle.dumps((action, args))).decode('utf-8')
                    await websocket.send(json.dumps(encoded_action))
            # env.render(render_mode = 'human')

            await asyncio.sleep(0)  # Yield control to allow other tasks to run

    async def receive_responses(websocket, shared_state):
        while not shared_state["done"]:
            response = await websocket.recv()
            data = json.loads(response)
            shared_state["done"] = data["done"]
            
            shared_state["env"].set_current_state(pickle.loads(base64.b64decode(data["env"])))
            shared_state["obs"] = pickle.loads(base64.b64decode(data["obs"]))
            Player.players = pickle.loads(base64.b64decode(data["players"]))

            shared_state["env"].render(render_mode='human')

    async with websockets.connect(uri) as websocket:
        env = create_robotouille_env(environment_name, movement_mode, seed, noisy_randomization)
        obs, info = env.reset()
        shared_state = {"done": False, "env": env, "renderer": env.renderer, "obs": obs, "player": None}
        print("In lobby")

        opening_message = await websocket.recv()
        print("In game")
        opening_data = json.loads(opening_message)
        player_index = pickle.loads(base64.b64decode(opening_data["player"]))
        player = env.initial_state.get_players()[player_index]
        shared_state["player"] = player

        receiver = asyncio.create_task(receive_responses(websocket, shared_state))
        await send_actions(websocket, shared_state)
        await receiver
        # Additional cleanup if necessary