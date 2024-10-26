import asyncio
import json
import pickle
import base64
import websockets
import time
import traceback
from pathlib import Path
from datetime import datetime
from robotouille.robotouille_env import create_robotouille_env

SIMULATE_LATENCY = False
SIMULATED_LATENCY_DURATION = 0.25

def run_server(environment_name: str, seed: int=42, noisy_randomization: bool=False, display_server: bool=False, event: asyncio.Event=None):
    asyncio.run(server_loop(environment_name, seed, noisy_randomization, display_server))

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
                # TODO(aac77): #41
                # currently cannot handle disconnected clients
                # cannot handle invalid messages
                # pickle needs to removed for security
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
                    encoded_action = json.loads(message)
                    action = pickle.loads(base64.b64decode(encoded_action))

                    actions[sockets_to_playerID[client]] = action

                
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
        # TODO(aac77): #41
        # cannot handle disconnections
        print("Hello client", websocket)
        q = asyncio.Queue()
        waiting_queue[websocket] = q
        if len(waiting_queue) == num_players:
            connections = waiting_queue.copy()
            waiting_queue.clear()
            asyncio.create_task(simulator(connections))
        async for message in websocket:
            await q.put(message)

    if event == None:
        event = asyncio.Event()

    async with websockets.serve(handle_connection, "0.0.0.0", 8765):
        print("I am server")
        await event.wait()