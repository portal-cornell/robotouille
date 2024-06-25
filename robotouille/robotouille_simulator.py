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
import traceback

SIMULATE_LATENCY = False
SIMULATED_LATENCY_DURATION = 0.25

def simulator(environment_name: str, seed: int=42, role: str="client", display_server: bool=False, host: str="ws://localhost:8765", recording: str="", noisy_randomization: bool=False):
    if recording != "" and role != "replay" and role != "render":
        role = "replay"
    if role == "server":
        asyncio.run(server_loop(environment_name, seed, noisy_randomization, display_server))
    elif role == "client":
        asyncio.run(client_loop(environment_name, seed, host, noisy_randomization))
    elif role == "single":
        asyncio.run(single_player(environment_name, seed, noisy_randomization))
    elif role == "replay":
        replay(recording)
    elif role == "render":
        render(recording)
    else:
        print("Invalid role:", role)

async def single_player(environment_name: str, seed: int=42, noisy_randomization: bool=False):
    event = asyncio.Event()
    server = asyncio.create_task(server_loop(environment_name=environment_name, seed=seed, noisy_randomization=noisy_randomization, event=event))
    await asyncio.sleep(0.5)  # wait for server to initialize
    client = asyncio.create_task(client_loop(environment_name=environment_name, seed=seed, noisy_randomization=noisy_randomization))
    await client
    event.set()
    await server


async def server_loop(environment_name: str, seed: int=42, noisy_randomization: bool=False, display_server: bool=False, event: asyncio.Event=None):
    waiting_queue = {}
    reference_env = create_robotouille_env(environment_name, seed, noisy_randomization)[0]
    num_players = len(reference_env.get_state().get_players())

    async def simulator(connections):
        try:
            print("Start game", connections.keys())
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

            assert len(connections) == num_players
            sockets_to_playerID = {}
            for i, socket in enumerate(connections.keys()):
                sockets_to_playerID[socket] = i
                player_data = base64.b64encode(pickle.dumps(i)).decode('utf-8')
                opening_message = json.dumps({"player": player_data})
                await socket.send(opening_message)

            while not done:
                # Wait for messages from any client
                # lol this is causing a memory leak
                receive_tasks = {asyncio.create_task(q.get()): client for client, q in connections.items()}
                finished_tasks, pending_tasks = await asyncio.wait(receive_tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
                
                # Cancel pending tasks, otherwise we leak
                for task in pending_tasks:
                    task.cancel()
                
                # Retrieve the message from the completed task
                actions = [(None, None)] * num_players
                for task in finished_tasks:
                    message = task.result()
                    client = receive_tasks[task]
                    #print(f"Received: {message} from {client.remote_address}")
                    encoded_action = json.loads(message)
                    action = pickle.loads(base64.b64decode(encoded_action))

                    actions[sockets_to_playerID[client]] = action

                
                #print((action, args))
                if SIMULATE_LATENCY:
                    time.sleep(SIMULATED_LATENCY_DURATION)

                reply = None

                try:
                    obs, reward, done, info = env.step(actions, interactive=interactive)
                    recording["actions"].append((actions, env.get_state(), time.monotonic() - start_time))
                    if display_server:
                        renderer.render(obs, mode='human')
                except AssertionError:
                    print("violation")
                    recording["violations"].append((actions, time.monotonic() - start_time))
                
                env_data = pickle.dumps(env.get_state())
                encoded_env_data = base64.b64encode(env_data).decode('utf-8')
                obs_data = pickle.dumps(obs)
                encoded_obs_data = base64.b64encode(obs_data).decode('utf-8')
                reply = json.dumps({"env": encoded_env_data, "obs": encoded_obs_data, "done": done})
                
                if SIMULATE_LATENCY:
                    time.sleep(SIMULATED_LATENCY_DURATION)
                websockets.broadcast(connections.keys(), reply)
            recording["result"] = "done"
        except BaseException as e:
            traceback.print_exc(e)
            recording["result"] = traceback.format_exc(e)
        finally:
            for websocket in connections.keys():
                await websocket.close()

            if display_server:
                renderer.render(obs, close=True)
            print("GG")
            recording["end_time"] = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

            p = Path('recordings')
            p.mkdir(exist_ok=True)
            with open(p / (recording["start_time"] + '.pkl'), 'wb') as f:
                pickle.dump(recording, f)
    
    async def handle_connection(websocket):
        # simple lobby code; will break if anyone disconnects, probably has race conditions lol, etc.
        print("Hello client", websocket)
        q = asyncio.Queue()
        waiting_queue[websocket] = q
        if len(waiting_queue) == num_players:
            connections = waiting_queue.copy()
            waiting_queue.clear()
            asyncio.create_task(simulator(connections))
        async for message in websocket:
            await q.put(message)

    #start_server = websockets.serve(handle_connection, "0.0.0.0", 8765)

    #asyncio.get_event_loop().run_until_complete(start_server)
    #asyncio.get_event_loop().run_forever()

    if event == None:
        event = asyncio.Event()

    async with websockets.serve(handle_connection, "0.0.0.0", 8765):
        print("I am server")
        await event.wait()

async def client_loop(environment_name: str, seed: int = 42, host: str="ws://localhost:8765", noisy_randomization: bool = False):
    uri = host

    async def send_actions(websocket, shared_state):
        env = shared_state["env"]
        renderer = shared_state["renderer"]
        renderer.render(shared_state["obs"], mode='human')
        player = shared_state["player"]
        online = True
        while not shared_state["done"]:
            pygame_events = pygame.event.get()
            mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
            keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
            action, args = create_action_from_control(env, shared_state["obs"], player, mousedown_events + keydown_events, renderer)

            online = not (pygame.key.get_mods() & pygame.KMOD_CAPS)

            if action is not None:
                if online:
                    encoded_action = base64.b64encode(pickle.dumps((action, args))).decode('utf-8')
                    await websocket.send(json.dumps(encoded_action))
                #shared_state["obs"], reward, done, info = env.step(action=action, interactive=True)
            renderer.render(env.get_state(), mode='human')

            await asyncio.sleep(0)  # Yield control to allow other tasks to run

    async def receive_responses(websocket, shared_state):
        while not shared_state["done"]:
            response = await websocket.recv()
            data = json.loads(response)
            shared_state["done"] = data["done"]
            
            shared_state["env"].set_state(pickle.loads(base64.b64decode(data["env"])))
            shared_state["obs"] = pickle.loads(base64.b64decode(data["obs"]))

    async with websockets.connect(uri) as websocket:
        env, _, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
        obs, info = env.reset()
        shared_state = {"done": False, "env": env, "renderer": renderer, "obs": obs, "player": None}
        print("In lobby")

        opening_message = await websocket.recv()
        print("In game")
        opening_data = json.loads(opening_message)
        player_index = pickle.loads(base64.b64decode(opening_data["player"]))
        player = env.get_state().get_players()[player_index]
        shared_state["player"] = player
        

        sender = asyncio.create_task(send_actions(websocket, shared_state))
        receiver = asyncio.create_task(receive_responses(websocket, shared_state))
        await asyncio.gather(sender, receiver)
        # Additional cleanup if necessary

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
    for actions, state, t in recording["actions"]:
        time.sleep(t - previous_time)
        previous_time = t
        obs, reward, done, info = env.step(actions=actions, interactive=False)
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
        actions, state, time_stamp = recording["actions"][i]
        while t > time_stamp:
            obs, reward, done, info = env.step(actions=actions, interactive=False)
            frame = renderer.render(obs, mode='rgb_array')
            i += 1
            if i >= len(recording["actions"]):
                break
            action, state, time_stamp = recording["actions"][i]
        t += 1 / fps
        video_writer.append_data(frame)
    renderer.render(obs, close=True)
    video_writer.close()