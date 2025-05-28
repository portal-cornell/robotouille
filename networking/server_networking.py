import asyncio
import json
import pickle
import base64
import websockets
import time
import traceback
from robotouille.robotouille_env import create_robotouille_env

UPDATE_INTERVAL = 1 / 60  # Game updates at 60 FPS
DEBUGGING = True
TIMEOUT = 5
# ========================
# Lobby Class
# ========================
class Lobby:
    """
    Represents a matchmaking lobby: collects players until full, then starts a GameSession.
    """

    def __init__(self, lobby_id: str, max_players: int, server_ref: "Server"):
        self.lobby_id = lobby_id
        self.max_players = max_players
        self.server_ref = server_ref
        self.waiting = {}  # websocket -> (queue, player_name)
        self.broadcast_task = None

    def add_player(self, websocket, queue: asyncio.Queue, player_name: str):
        """
        Registers a new player in the lobby and starts broadcast loop if needed.
        """
        if DEBUGGING:
            print(f"[Lobby {self.lobby_id}] Player {player_name} connected: {websocket.remote_address}")
        self.waiting[websocket] = (queue, player_name)

        if not self.broadcast_task:
            self.broadcast_task = asyncio.create_task(self.broadcast_waiting_players())

        asyncio.create_task(self._try_start())

    def remove_player(self, websocket):
        """
        Removes a player from the lobby and cancels broadcasting if empty.
        """
        print('removing websocket', websocket, "from lobby")
        if websocket in self.waiting:
            _, name = self.waiting.pop(websocket)
            if DEBUGGING:
                print(f"[Lobby {self.lobby_id}] Player {name} disconnected")

        if not self.waiting and self.broadcast_task:
            self.broadcast_task.cancel()
            self.broadcast_task = None

    def is_full(self) -> bool:
        return len(self.waiting) >= self.max_players

    async def broadcast_waiting_players(self):
        """
        Continuously sends the player list to all players in the lobby (60 FPS).
        """
        while True:
            try:
                player_list = [
                    {"playerID": idx, "name": name, "status": "waiting"}
                    for idx, (_, name) in enumerate(self.waiting.values())
                ]
                msg = json.dumps({"type": "Player_list", "payload": player_list})
                await asyncio.gather(*(ws.send(msg) for ws in self.waiting), return_exceptions=True)
                await asyncio.sleep(1 / 60)
            except asyncio.CancelledError:
                print(f"[Lobby {self.lobby_id}] Broadcast loop cancelled.")
                break
            except Exception as e:
                print(f"[Lobby {self.lobby_id}] Broadcast error: {e}")
   
    async def _try_start(self):
        """
        Starts a game session if the lobby is full.
        """
        if not self.is_full():
            return
        if DEBUGGING:
            print(f"[Lobby {self.lobby_id}] Full, starting game session.")

        if self.broadcast_task:
            self.broadcast_task.cancel()
            self.broadcast_task = None

        conns = {ws: q for ws, (q, _) in self.waiting.items()}
        names = [name for (_, name) in self.waiting.values()]
        self.waiting.clear()

        session = GameSession(
            session_id=self.lobby_id,
            connections=conns,
            player_names=names,
            environment=self.server_ref.create_environment(),
            server_ref=self.server_ref,
            update_interval=UPDATE_INTERVAL
        )
        self.server_ref.active_sessions[self.lobby_id] = session
        
        # Delay added to give players time to see lobby screen before game starts
        await session.send_opening()
        asyncio.create_task(session.run())


# ========================
# GameSession Class
# ========================
class GameSession:
    """
    Handles a running game:
      - steps environment
      - gathers actions
      - broadcasts state and results
      - cleans up
    """

    def __init__(
        self,
        session_id: str,
        connections: dict,
        player_names: list,
        environment,
        server_ref: "Server",
        update_interval: float = UPDATE_INTERVAL,
    ):
        self.session_id = session_id
        self.connections = connections  # websocket -> queue
        self.player_names = player_names
        self.env = environment
        self.server_ref = server_ref
        self.update_interval = update_interval

        self.sockets = list(connections.keys())
        self.num_players = len(self.sockets)
        self.sockets_to_id = {ws: idx for idx, ws in enumerate(self.sockets)}
        self.scores = [0] * self.num_players
        self.post_status = {}  
        if DEBUGGING:
            print(f"[Session {self.session_id}] Game started with players: {self.player_names}")

    async def send_opening(self):
        """
        Sends 'Player_list' immediately and 'Start_game' after 1s delay.
        """
        player_list = [
            {"playerID": idx, "name": name, "status": "waiting"}
            for idx, name in enumerate(self.player_names)
        ]
        pl_msg = json.dumps({"type": "Player_list", "payload": player_list})
        await asyncio.gather(*(ws.send(pl_msg) for ws in self.sockets))

        await asyncio.sleep(1)  # Delay to show lobby briefly

        sg_msg = json.dumps({"type": "Start_game"})
        await asyncio.gather(*(ws.send(sg_msg) for ws in self.sockets))

    async def run(self):
        """
        Main game loop: collects actions, steps environment, sends state.
        After game ends, waits for 'Post_status' messages to determine replay.
        """
        try:
            # Game initialization
            obs, info = self.env.reset()
            done = False
            last_time = time.monotonic()

            # Game loop
            while not done:
                now = time.monotonic()
                delay = self.update_interval - (now - last_time)
                actions = await self._collect_actions(timeout=delay) if delay > 0 else [None] * self.num_players

                if actions is None:
                    actions = [None] * self.num_players

                try:
                    obs, rewards, done, info = self.env.step(actions)
                except Exception as e:
                    print(f"[Session {self.session_id}] env.step() failed: {e}")
                    break

                for i, r in enumerate(rewards or []):
                    self.scores[i] += r

                state_payload = {
                    "env": base64.b64encode(pickle.dumps(self.env.current_state)).decode(),
                    "scores": list(enumerate(self.scores))
                }
                state_msg = json.dumps({"type": "Game_state", "payload": state_payload})
                await asyncio.gather(*(ws.send(state_msg) for ws in self.sockets))

                last_time = now

            # Send Game results
            end_msg = json.dumps({"type": "Game_ended"})
            # results = [
            #     {"playerID": i, "stars": self.env.get_stars(i), "points": self.scores[i]}
            #     for i in range(self.num_players)
            # ]

            results = [
                {"playerID": i, "stars": 0, "points": 0}
                for i in range(self.num_players)
            ]
            res_msg = json.dumps({"type": "Results", "payload": results})
            await asyncio.gather(*(ws.send(end_msg) for ws in self.sockets))
            await asyncio.gather(*(ws.send(res_msg) for ws in self.sockets))

            # Post-game status  
            should_restart = await self._await_post_game_responses()
            if should_restart:
                # Re-initialize for replay
                self.env = self.server_ref.create_environment()
                self.scores = [0] * self.num_players
                self.post_status.clear()
                await self.run()

        except Exception as e:
            print(f"[Session {self.session_id}] Fatal error: {e}")
            traceback.print_exc()
        finally:
            del self.server_ref.active_sessions[self.session_id]


    async def _collect_actions(self, timeout: float):
        """
        Waits for any player actions or disconnects, applies them to the environment.
        This is only utilized while players are in game.
        """
        tasks = {asyncio.create_task(q.get()): ws for ws, q in self.connections.items()}
        done, pending = await asyncio.wait(tasks.keys(), timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
        for p in pending:
            p.cancel()

        actions = [None] * self.num_players
        for task in done:
            ws = tasks[task]
            try:
                raw = task.result()
                msg = json.loads(raw)
                if msg.get("type") == "Disconnect":
                    await self._handle_disconnect(ws)
                    return None
                if msg.get("type") == "Action":
                    act = pickle.loads(base64.b64decode(msg.get("payload")))
                    pid = self.sockets_to_id[ws]
                    actions[pid] = act
            except Exception as e:
                print(f"Error parsing client message: {e}")
                await self._handle_disconnect(ws)
                continue

        return actions

    async def _await_post_game_responses(self) -> bool:
        """
        Collects 'Post_status' responses for up to 5 seconds after the first one arrives.
        Returns True if everyone said 'again' (Restart), otherwise handles Auto-matchmaking and Quit.
        """
        self.post_status = {}
        start_time = None

        while True:
            # Break if all players responded
            if len(self.post_status) == self.num_players:
                break

            # If the timeout has started, check if it expired
            if start_time is not None:
                elapsed = time.monotonic() - start_time
                if elapsed >= TIMEOUT:
                    if DEBUGGING:
                        print(f"[Post_status] Timeout expired after {TIMEOUT} seconds.")
                    break

            timeout = TIMEOUT if start_time is None else max(0.0, TIMEOUT - (time.monotonic() - start_time))
            tasks = {
                asyncio.create_task(self.connections[ws].get()): ws
                for ws in self.sockets if ws not in self.post_status
            }
            if not tasks:
                break  
            done, _ = await asyncio.wait(tasks.keys(), timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
            if not done:
                if DEBUGGING:
                    print("[Post_status] No further responses before timeout.")
                break

            for task in done:
                ws = tasks[task]
                try:
                    msg = json.loads(task.result())
                    if msg.get("type") == "Post_status":
                        _, name, decision = msg["payload"]
                        self.post_status[ws] = decision
                        if not start_time:
                            start_time = time.monotonic()
                        if DEBUGGING:
                            print(f"[Post_status] {name} chose: {decision}")
                except Exception as e:
                    print(f"[Post_status] Error handling response: {e}")

        for ws in self.sockets:
            if ws not in self.post_status:
                self.post_status[ws] = "quit"
                if DEBUGGING:
                    print(f"[Post_status] No response from {ws.remote_address}, defaulted to 'quit'.")

        if all(status == "again" for status in self.post_status.values()):
            if DEBUGGING:
                print("[Post_status] All players chose again. Restarting.")
            reply = json.dumps({"type": "Restart", "payload": None})
            await asyncio.gather(*(ws.send(reply) for ws in self.sockets))
            return True
        else:
            if DEBUGGING:
                print("[Post_status] Not all players chose again. Returning to matchmaking.")
            auto_msg = json.dumps({"type": "Auto_matchmaking", "payload": None})
            quit_msg = json.dumps({"type": "Quit", "payload": None})
            again_ws = [ws for ws, status in self.post_status.items() if status == "again"]
            quit_ws = [ws for ws in self.sockets if ws not in again_ws]

 
            del self.server_ref.lobbies[self.session_id]

            if again_ws:
                for ws in again_ws:
                    queue = self.connections[ws]
                    player_name = self.player_names[self.sockets_to_id[ws]]

                    # Create a new lobby if needed
                    lobby = self.server_ref.lobbies.get(self.session_id)
                    if not lobby:
                        lobby = Lobby(self.session_id, self.server_ref.max_players, self.server_ref)
                        self.server_ref.lobbies[self.session_id] = lobby

                    lobby.add_player(ws, queue, player_name)

                await asyncio.gather(*(ws.send(auto_msg) for ws in again_ws))

            # Handle players who quit
            if quit_ws:
                await asyncio.gather(*(ws.send(quit_msg) for ws in quit_ws))
                await asyncio.gather(*(ws.close() for ws in quit_ws))

            # Clean up session
            return False

                
    async def _handle_disconnect(self, ws):
        """
        Ends the game if any player disconnects.
        """
        if DEBUGGING:
            print(f"[Session {self.session_id}] Player disconnected: {ws.remote_address}")
        end_msg = json.dumps({"type": "Game_ended"})
        await asyncio.gather(*(c.send(end_msg) for c in self.sockets if c != ws))
        await asyncio.gather(*(c.close() for c in self.sockets))
        del self.server_ref.active_sessions[self.session_id]


# ========================
# Server Class
# ========================
class Server:
    """
    Manages all lobbies and incoming websocket connections.
    """

    def __init__(
        self,
        environment_name: str,
        seed: int,
        noisy_randomization: bool,
        movement_mode: str,
        host: str = "0.0.0.0",
        port: int = 8765,
        max_players: int = 2,
        display_server: bool = False,
    ):
        self.environment_name = environment_name
        self.seed = seed
        self.noisy_randomization = noisy_randomization
        self.movement_mode = movement_mode
        self.host = host
        self.port = port
        self.max_players = max_players
        self.display_server = display_server

        self.lobbies = {}  # lobby_id -> Lobby
        self.active_sessions = {}  # session_id -> GameSession

    def create_environment(self):
        """
        Creates a new instance of the game environment for each session.
        """
        return create_robotouille_env(
            self.environment_name,
            self.movement_mode,
            seed=self.seed,
            noisy_randomization=self.noisy_randomization,
        )

    async def handler(self, websocket):
        """
        Handles an individual websocket connection, forwarding its messages to its queue.
        """
        q = asyncio.Queue()
        lobby = None
        try:
            if DEBUGGING:
                print("[Server] New connection received")
            raw = await websocket.recv()
            if DEBUGGING:
                print(f"[Server] Received message: {raw}")
            msg = json.loads(raw)

            if msg.get("type") != "Connect":
                if DEBUGGING:
                    print("[Server] Invalid first message. Closing.")
                await websocket.send(json.dumps({"type": "Error", "payload": "Expected Connect"}))
                await websocket.close()
                return

            # TODO change this part, the server should assign the lobby, the client should not need to know anything about lobby
            lobby_id = msg.get("lobby_id")
            player_name = msg.get("player_name") or str(websocket.remote_address)

            if DEBUGGING: print(f"[Server] Connecting player {player_name} to lobby {lobby_id}")
            lobby = self.lobbies.get(lobby_id)
            if not lobby:
                lobby = Lobby(lobby_id, self.max_players, self)
                self.lobbies[lobby_id] = lobby

            lobby.add_player(websocket, q, player_name)

            async for message in websocket:
                if DEBUGGING: print(f"[Server] Forwarding message to queue: {message}")
                await q.put(message)

        except websockets.ConnectionClosed:
            print("[Server] Client disconnected")
            if lobby:
                lobby.remove_player(websocket)
        except Exception:
            traceback.print_exc()

    async def run(self):
        """
        Launches the server and listens for new websocket connections.
        """
        if DEBUGGING: print(f"Server listening on {self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()
