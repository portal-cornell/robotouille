import pygame
from utils.robotouille_input import create_action_from_control
from robotouille.robotouille_env import create_robotouille_env
import asyncio
import json
import pickle
import base64
import websockets
import time
from pathlib import Path
from datetime import datetime
import imageio

SIMULATE_LATENCY = False
SIMULATED_LATENCY_DURATION = 0.25

def simulator(environment_name: str, seed: int=42, role: str="client", display_server: bool=False, host: str="ws://localhost:8765", recording: str="", noisy_randomization: bool=False):
    if recording != "" and role != "replay" and role != "render":
        role = "replay"
    if role == "server":
        server_loop(environment_name, seed, noisy_randomization, display_server)
    elif role == "client":
        client_loop(environment_name, seed, host, noisy_randomization)
    elif role == "replay":
        replay(recording)
    elif role == "render":
        render(recording)

def server_loop(environment_name: str, seed: int=42, noisy_randomization: bool=False, display_server: bool=False):
    print("I am server")
    async def simulator(websocket):
        print("Hello client", websocket)
        recording = {}
        recording["start_time"] = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        recording["environment_name"] = environment_name
        recording["seed"] = seed
        recording["noisy_randomization"] = noisy_randomization
        recording["actions"] = []
        recording["violations"] = []
        start_time = time.monotonic()

        env, json_data, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
        obs, info = env.reset()
        if display_server:
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
                if SIMULATE_LATENCY:
                    time.sleep(SIMULATED_LATENCY_DURATION)

                reply = None

                try:
                    obs, reward, done, info = env.step(action=action, args=args, interactive=interactive)
                    recording["actions"].append((action, args, env.get_state(), time.monotonic() - start_time))
                    reply = json.dumps({"valid": True, "done": done})
                    if display_server:
                        renderer.render(obs, mode='human')
                except AssertionError:
                    recording["violations"].append((action, time.monotonic() - start_time))
                    env_data = pickle.dumps(env.get_state())
                    encoded_env_data = base64.b64encode(env_data).decode('utf-8')
                    obs_data = pickle.dumps(obs)
                    encoded_obs_data = base64.b64encode(obs_data).decode('utf-8')
                    reply = json.dumps({"valid": False, "env": encoded_env_data, "obs": encoded_obs_data, "done": False})
                
                if SIMULATE_LATENCY:
                    time.sleep(SIMULATED_LATENCY_DURATION)
                await websocket.send(reply)
            recording["result"] = "done"
        except BaseException as e:
            print(e)
            recording["result"] = e
        finally:
            if display_server:
                renderer.render(obs, close=True)
            print("GG")
            recording["end_time"] = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

            p = Path('recordings')
            p.mkdir(exist_ok=True)
            with open(p / (recording["start_time"] + '.pkl'), 'wb') as f:
                pickle.dump(recording, f)

    start_server = websockets.serve(simulator, "0.0.0.0", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

def client_loop(environment_name: str, seed: int = 42, host: str="ws://localhost:8765", noisy_randomization: bool = False):
    uri = host

    async def send_actions(websocket, shared_state):
        env = shared_state["env"]
        renderer = shared_state["renderer"]
        renderer.render(shared_state["obs"], mode='human')
        online = True
        while not shared_state["done"]:
            pygame_events = pygame.event.get()
            mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
            keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
            action, args = create_action_from_control(env, shared_state["obs"], mousedown_events + keydown_events, renderer)

            online = not (pygame.key.get_mods() & pygame.KMOD_CAPS)

            if action is not None:
                if online:
                    encoded_action = base64.b64encode(pickle.dumps(action)).decode('utf-8')
                    encoded_args = base64.b64encode(pickle.dumps(args)).decode('utf-8')
                    await websocket.send(json.dumps((encoded_action, encoded_args)))
                shared_state["obs"], reward, done, info = env.step(action=action, args=args, interactive=True)
            renderer.render(env.get_state(), mode='human')

            await asyncio.sleep(0)  # Yield control to allow other tasks to run

    async def receive_responses(websocket, shared_state):
        while not shared_state["done"]:
            response = await websocket.recv()
            data = json.loads(response)
            shared_state["done"] = data["done"]

            if(not data["valid"]):
                shared_state["env"].set_state(pickle.loads(base64.b64decode(data["env"])))
                shared_state["obs"] = pickle.loads(base64.b64decode(data["obs"]))

    async def interact_with_server():
        async with websockets.connect(uri) as websocket:
            env, _, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
            obs, info = env.reset()
            shared_state = {"done": False, "env": env, "renderer": renderer, "obs": obs}
            sender = asyncio.create_task(send_actions(websocket, shared_state))
            receiver = asyncio.create_task(receive_responses(websocket, shared_state))
            await asyncio.gather(sender, receiver)
            # Additional cleanup if necessary

    asyncio.get_event_loop().run_until_complete(interact_with_server())

def replay(recording_name: str):
    if not recording_name:
        raise ValueError("Empty recording_name supplied")

    p = Path('recordings')
    with open(p / (recording_name + '.pkl'), 'rb') as f:
        recording = pickle.load(f)
    
    env, _, renderer = create_robotouille_env(recording["environment_name"], recording["seed"], recording["noisy_randomization"])
    obs, _ = env.reset()
    renderer.render(obs, mode='human')

    previous_time = 0
    for action, args, state, t in recording["actions"]:
        time.sleep(t - previous_time)
        previous_time = t
        obs, reward, done, info = env.step(action=action, args=args, interactive=False)
        renderer.render(obs, mode='human')
    renderer.render(obs, close=True)

def render(recording_name: str):
    p = Path('recordings')
    with open(p / (recording_name + '.pkl'), 'rb') as f:
        recording = pickle.load(f)
    
    env, _, renderer = create_robotouille_env(recording["environment_name"], recording["seed"], recording["noisy_randomization"])
    obs, _ = env.reset()
    frame = renderer.render(obs, mode='rgb_array')

    vp = Path('recordings')
    vp.mkdir(exist_ok=True)
    fps = 20
    video_writer = imageio.get_writer(vp / (recording_name + '.mp4'), fps=fps)

    i = 0
    t = 0
    while i < len(recording["actions"]):
        action, args, state, time_stamp = recording["actions"][i]
        while t > time_stamp:
            obs, reward, done, info = env.step(action=action, args=args, interactive=False)
            frame = renderer.render(obs, mode='rgb_array')
            i += 1
            if i >= len(recording["actions"]):
                break
            action, args, state, time_stamp = recording["actions"][i]
        t += 1 / fps
        video_writer.append_data(frame)
    renderer.render(obs, close=True)
    video_writer.close()