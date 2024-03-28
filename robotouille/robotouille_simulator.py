import pygame
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env
import asyncio
import json
import pickle
import base64
import websockets
import time


def simulator(environment_name: str, seed: int=42, role="client", host="ws://localhost:8765", noisy_randomization: bool=False):
    if role == "server":
        server_loop(environment_name, seed, noisy_randomization)
    else:
        client_loop(environment_name, seed, host, noisy_randomization)

def server_loop(environment_name: str, seed: int=42, noisy_randomization: bool=False):
    print("I am server")
    async def simulator(websocket):
        print("Hello client", websocket)
        env, json_data, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
        obs, info = env.reset()
        renderer.render(obs, mode='human')
        done = False
        interactive = False  # Adjust based on client commands later if needed
        try:
            while not done:
                action_message = await websocket.recv()
                encoded_action, encoded_args = json.loads(action_message)
                action = pickle.loads(base64.b64decode(encoded_action))
                args = pickle.loads(base64.b64decode(encoded_args))
                #print((action, args))
                #time.sleep(0.25)

                obs, reward, done, info = env.step(action=action, args=args, interactive=interactive)
                # Convert obs to a suitable format to send over the network
                obs_data = pickle.dumps(obs)
                encoded_obs_data = base64.b64encode(obs_data).decode('utf-8')
                #time.sleep(0.25)
                await websocket.send(json.dumps({"obs": encoded_obs_data, "reward": reward, "done": done, "info": info}))
                renderer.render(obs, mode='human')
        except e:
            pass
        finally:
            renderer.render(obs, close=True)
            print("GG")

    start_server = websockets.serve(simulator, "localhost", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

def client_loop(environment_name: str, seed: int=42, host="ws://localhost:8765", noisy_randomization: bool=False):
    uri = host

    async def interact_with_server():
        async with websockets.connect(uri) as websocket:
            env, _, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
            obs, info = env.reset()
            renderer.render(obs, mode='human')
            done = False
            interactive = False # Set to True to interact with the environment through terminal REPL (ignores input)

            while True:
                pygame_events = pygame.event.get()
                # Mouse clicks for movement and pick/place stack/unstack
                mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
                # Keyboard events ('e' button) for cut/cook ('space' button) for noop
                keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
                # Assume the action can be created despite not updating environment
                action, args = create_action_from_control(env, obs, mousedown_events + keydown_events, renderer)
                
                if action is None:
                    continue

                #print((action, args))
                encoded_action = base64.b64encode(pickle.dumps(action)).decode('utf-8')
                encoded_args = base64.b64encode(pickle.dumps(args)).decode('utf-8')
                await websocket.send(json.dumps((encoded_action, encoded_args)))

                response = await websocket.recv()
                data = json.loads(response)
                encoded_obs_data, reward, done, info = data["obs"], data["reward"], data["done"], data["info"]
                obs = pickle.loads(base64.b64decode(encoded_obs_data))
                renderer.render(obs, mode='human')
                if done:
                    break
            renderer.render(obs, close=True)

    asyncio.get_event_loop().run_until_complete(interact_with_server())
