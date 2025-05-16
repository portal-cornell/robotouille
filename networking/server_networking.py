import asyncio
import json
import pickle
import base64
import websockets
import time
import traceback
from collections import defaultdict
from robotouille.robotouille_env import create_robotouille_env

UPDATE_INTERVAL = 1/60  # 60 FPS


class Lobby:
    """
    Represents a matchmaking lobby: collects players until full, then starts a GameSession.
    """
    def __init__(self, lobby_id: str, max_players: int, server_ref: "Server"):
        self.lobby_id = lobby_id
        self.max_players = 1
        self.server_ref = server_ref
        self.waiting = {}

    def add_player(self, websocket, queue: asyncio.Queue, player_name: str):
        print(f"[Lobby {self.lobby_id}] Player {player_name} connected: {websocket.remote_address}")
        self.waiting[websocket] = (queue, player_name)
        asyncio.create_task(self._try_start())

    def remove_player(self, websocket):
        if websocket in self.waiting:
            _, name = self.waiting.pop(websocket)
            print(f"[Lobby {self.lobby_id}] Player {name} disconnected")

    def is_full(self) -> bool:
        return len(self.waiting) >= self.max_players

    async def _try_start(self):
        if not self.is_full():
            return
        print(f"[Lobby {self.lobby_id}] Full, starting game session.")
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
        asyncio.create_task(session.run())


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
        self.connections = connections
        self.player_names = player_names
        self.env = environment
        self.server_ref = server_ref
        self.update_interval = update_interval
        self.sockets = list(connections.keys())
        self.num_players = len(self.sockets)
        self.sockets_to_id = {ws: idx for idx, ws in enumerate(self.sockets)}
        self.scores = [0] * self.num_players
        self._send_opening()

    def _send_opening(self):
        # Player_list
        player_list = [
            {"playerID": idx, "name": name, "status": "waiting"}
            for idx, name in enumerate(self.player_names)
        ]
        pl_msg = json.dumps({"type": "Player_list", "payload": player_list})
        
        # Start_game
        sg_msg = json.dumps({"type": "Start_game"})
        for ws in self.sockets:
            asyncio.create_task(ws.send(pl_msg))
            asyncio.create_task(ws.send(sg_msg))

    async def run(self):
        """
        Main loop: collect, step, broadcast, until done.
        """
        obs, info = self.env.reset()
        done = False
        last_time = time.monotonic()

        while not done:
            now = time.monotonic()
            delay = self.update_interval - (now - last_time)
            if delay > 0:
                actions = await self._collect_actions(timeout=delay)
            else:
                actions = [None] * self.num_players

            # step env
            obs, rewards, done, info = self.env.step(actions)
            for i, r in enumerate(rewards or []):
                self.scores[i] += r

            # broadcast state
            state_payload = {
                "env": base64.b64encode(pickle.dumps(self.env.current_state)).decode(),
                "scores": list(enumerate(self.scores))
            }
            state_msg = json.dumps({"type": "Game_state", "payload": state_payload})
            for ws in self.sockets:
                asyncio.create_task(ws.send(state_msg))

            last_time = now

        # Game ended
        end_msg = json.dumps({"type": "Game_ended"})
        results = [
            {"playerID": i, "stars": self.env.get_stars(i), "points": self.scores[i]}
            for i in range(self.num_players)
        ]
        res_msg = json.dumps({"type": "Results", "payload": results})
        for ws in self.sockets:
            asyncio.create_task(ws.send(end_msg))
            asyncio.create_task(ws.send(res_msg))

        # cleanup
        for ws in self.sockets:
            await ws.close()
        del self.server_ref.active_sessions[self.session_id]

    async def _collect_actions(self, timeout: float) -> list:
        tasks = {asyncio.create_task(q.get()): ws for ws, q in self.connections.items()}
        done, pending = await asyncio.wait(
            tasks.keys(), timeout=timeout, return_when=asyncio.FIRST_COMPLETED
        )
        for p in pending:
            p.cancel()
        actions = [None] * self.num_players
        for task in done:
            ws = tasks[task]
            raw = task.result()
            try:
                msg = json.loads(raw)
                t = msg.get("type")
                if t == "Disconnect":
                    await self._handle_disconnect(ws)
                    return [None] * self.num_players
                if t == "Action":
                    act = pickle.loads(base64.b64decode(msg.get("payload")))
                    pid = self.sockets_to_id[ws]
                    actions[pid] = act
            except Exception:
                continue
        return actions

    async def _handle_disconnect(self, ws):
        # notify and cleanup
        end_msg = json.dumps({"type": "Game_ended"})
        for c in self.sockets:
            if c != ws:
                asyncio.create_task(c.send(end_msg))
        for c in self.sockets:
            await c.close()
        del self.server_ref.active_sessions[self.session_id]


class Server:
    """
    Main server: manages lobbies and active sessions.
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
        self.lobbies = {}
        self.active_sessions = {}

    def create_environment(self):
        return create_robotouille_env(
            self.environment_name,
            self.movement_mode,
            seed=self.seed,
            noisy_randomization=self.noisy_randomization,
        )

    async def handler(self, websocket):
        """
        Handle each new client connection. 
        """
        q = asyncio.Queue()
        lobby = None
        try:
            raw = await websocket.recv()
            msg = json.loads(raw)
            if msg.get("type") != "Connect":
                await websocket.close()
                return
            lobby_id = msg.get("lobby_id")
            player_name = msg.get("player_name") or str(websocket.remote_address)
            lobby = self.lobbies.get(lobby_id)
            if not lobby:
                lobby = Lobby(lobby_id, self.max_players, self)
                self.lobbies[lobby_id] = lobby
            lobby.add_player(websocket, q, player_name)
            async for message in websocket:
                await q.put(message)
        except websockets.ConnectionClosed:
            if lobby:
                lobby.remove_player(websocket)
        except Exception:
            traceback.print_exc()

    async def run(self):
        print(f"Server listening on {self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()