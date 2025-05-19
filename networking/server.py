import asyncio
import json
import pickle
import base64
import websockets
import time
import traceback
import pygame
from pathlib import Path
from datetime import datetime
from robotouille.robotouille_env import create_robotouille_env
from backend.movement.player import Player
from backend.movement.movement import Movement

# currently unimplemented
SIMULATE_LATENCY = False
SIMULATED_LATENCY_DURATION = 0.25

UPDATE_INTERVAL = 1/60

def run_server(environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str, display_server: bool=False, event: asyncio.Event=None):
    """
    Runs the server by starting the asynchronous server loop.

    Args:
        environment_name (str): The name of the environment to run.
        seed (int):The seed for the environment.
        noisy_randomization (bool): Whether to use noisy randomization.
        movement_mode (str): The movement mode to use.
        display_server (bool): Whether to display the server.
        event (asyncio.Event): An event to signal when the server is ready.
    """
    asyncio.run(server_loop(environment_name, seed, noisy_randomization, movement_mode, display_server, event))

async def server_loop(environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str, display_server: bool, event: asyncio.Event):
    """
    Main asynchronous loop for the server. Manages communication with the server and user inputs.

    Args:
        environment_name (str): Name of the environment to connect to.
        seed (int): Random seed for environment initialization.
        noisy_randomization (bool): Whether to use noisy randomization.
        movement_mode (str): Mode of movement for the environment agent.
        display_server (bool): Whether to display the server.
        event (asyncio.Event): An event to signal when the server is ready.
    """
    waiting_queue = {}
    start_game_event = asyncio.Event()
    reference_env = create_robotouille_env(environment_name, movement_mode, seed, noisy_randomization)
    num_players = len(reference_env.initial_state.get_players())


    async def simulator(connections):
        """
        Runs the main simulation loop for a single game session.

        Steps the environment at a fixed rate, handles incoming player actions,
        and broadcasts updated environment states to all connected clients.

        It uses base64 and pickle to encode/decode game states and actions. 
        It also logs the entire session including actions, state snapshots, and violations.
        This method assumes all expected players are already connected when called.

        Args:
            connections (dict): Mapping from WebSocket client connections to asyncio queues
                                where incoming messages are stored.
        """
        try:
            print("Start game", connections.keys())
            recording = {}
            recording["start_time"] = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            recording["environment_name"] = environment_name
            recording["seed"] = seed
            recording["noisy_randomization"] = noisy_randomization
            recording["movement_mode"] = movement_mode
            recording["actions"] = []
            recording["violations"] = []
            start_time = time.monotonic()

            env = create_robotouille_env(environment_name, movement_mode, seed, noisy_randomization)
            obs, info = env.reset()
            if display_server:
                env.render(render_mode='human')
            done = False
            interactive = False  # Adjust based on client commands later if needed

            assert len(connections) == num_players
            sockets_to_playerID = {}
            for i, socket in enumerate(connections.keys()):
                sockets_to_playerID[socket] = i
                player_data = base64.b64encode(pickle.dumps(i)).decode('utf-8')
                opening_message = json.dumps({"player": player_data})
                print(f"[Server] Assigned player ID {i} to {socket.remote_address}")
                await socket.send(opening_message)
                print(f"[Server] opening message: {opening_message}")

            last_update_time = time.monotonic()

            clock = pygame.time.Clock()

            while not done:
                # Wait for messages from any client
                # TODO(aac77): #41
                # currently cannot handle disconnected clients
                # cannot handle invalid messages
                # pickle needs to removed for security
                # will not function correctly if there are parallel instances due to global game state
                current_time = time.monotonic()
                time_until_next_update = UPDATE_INTERVAL - (current_time - last_update_time)
                
                if time_until_next_update > 0:
                    receive_tasks = {asyncio.create_task(q.get()): client 
                                   for client, q in connections.items()}
                    try:
                        finished_tasks, pending_tasks = await asyncio.wait(
                            receive_tasks.keys(),
                            timeout=time_until_next_update,
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        
                        for task in pending_tasks:
                            task.cancel()
                        
                        actions = [(None, None)] * num_players
                        for task in finished_tasks:
                            message = task.result()
                            print("message", message)
                            client = receive_tasks[task]
                            player_id = sockets_to_playerID[client]
                            player_obj = Player.get_player(env.current_state.get_players()[player_id].name)
                            
                            try:
                                parsed = json.loads(message)
                                print(f"[Server] 'start_game' received {parsed} from player {player_id}")
                                if isinstance(parsed, dict) and parsed.get("type") == "start_game":
                                    for ws in connections.keys():
                                        await ws.send(json.dumps({"type": "game"}))
                                        print(f"[Server] Sent 'game' to {ws.remote_address}")
                                    continue 
                            except Exception as e:
                                print("[Server] Failed to decode message:", e)



                            # Only process action if player is not moving
                            if not Movement.is_player_moving(player_obj.name):
                                encoded_action = json.loads(message)
                                action = pickle.loads(base64.b64decode(encoded_action))
                                actions[player_id] = action
                            # If player is moving, their action remains (None, None)
                            
                    except asyncio.TimeoutError:
                        # No inputs, self update
                        actions = [(None, None)] * num_players

                else:
                    # Must update immediately, use no-op inputs
                    actions = [(None, None)] * num_players

                try:
                    clock.tick()
                    obs, reward, done, info = env.step(actions)
                    recording["actions"].append((actions, env.current_state, time.monotonic() - start_time))
                    if display_server:
                        env.render(render_mode='human')
                    else:
                        env.clock.tick(env.render_fps)
                except AssertionError:
                    print("violation")
                    recording["violations"].append((actions, time.monotonic() - start_time))
                
                env_data = base64.b64encode(pickle.dumps(env.current_state)).decode('utf-8')
                obs_data = base64.b64encode(pickle.dumps(env.get_state())).decode('utf-8')
                player_data = base64.b64encode(pickle.dumps(Player.players)).decode('utf-8')
                reply = json.dumps({"env": env_data, "obs": obs_data, "players": player_data, "done": done})
                
                await asyncio.gather(*(websocket.send(reply) for websocket in connections.keys()))
                
                last_update_time = time.monotonic()

            recording["result"] = "done"
        except BaseException as e:
            traceback.print_exc(e)
            recording["result"] = traceback.format_exc(e)
        finally:
            for websocket in connections.keys():
                await websocket.send(json.dumps({"type": "game_over"}))
                await websocket.close()

            if display_server:
                env.render(render_mode='human', close=True)
            print("GG")
            recording["end_time"] = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

            p = Path('recordings')
            p.mkdir(exist_ok=True)
            with open(p / (recording["start_time"] + '.pkl'), 'wb') as f:
                pickle.dump(recording, f)
    
    async def handle_connection(websocket):
        print("Hello client", websocket)
        await websocket.send(json.dumps({"type": "connected to server"}))

        q = asyncio.Queue()
        waiting_queue[websocket] = q

        if len(waiting_queue) == num_players:
            print(f"[Server] All {num_players} players connected. Waiting for 'start_game'...")
            asyncio.create_task(wait_for_start_and_begin_game())

        async for message in websocket:
            print(f"[Server] Raw message: {message}")
            try:
                parsed = json.loads(message)
                print(f"[Server] Received 'start_game' from {websocket.remote_address}")
                if isinstance(parsed, dict) and parsed.get("type") == "connect":
                    await websocket.send(json.dumps({"type": "start_game"}))
                await q.put(message)
            except Exception as e:
                print("[Server] Message handling error:", e)

    async def wait_for_start_and_begin_game():
        await start_game_event.wait()
        print("[Server] 'start_game' signal received. Starting simulator.")
        connections = waiting_queue.copy()
        waiting_queue.clear()
        asyncio.create_task(simulator(connections))

    if event is None:
        event = asyncio.Event()

    async with websockets.serve(handle_connection, "0.0.0.0", 8765):
        if event:
            event.set()
        while True:
            await asyncio.sleep(1)