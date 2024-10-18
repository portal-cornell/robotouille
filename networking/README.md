# Robotouille Networking README

## Overview

Built into Robotouille is networking support for multiplayer. Robotouille uses an authoritative server, which clients can connect to. Servers record games played on them to collect data. 

## Available Modes

Several modes are offered, which can be chosen using the `--role` argument:

1. `local`
2. `server`
3. `client`
4. `single`
5. `replay`
6. `render`

## Local

This mode runs Robotouille without any networking overhead.

E.g.
```python main.py --environment_name original```

## Server

This mode sets up an Robotouille server. Clients that connect are automatically matchmaked and put together into lobbies. Use argument `display_server` to have the server render active games.

E.g.
```python main.py --role server```

To render active games:
```python main.py --role server --server_display```

## Client

This mode runs the Robotouille client. Use argument `host` to choose which host to connect to. Defaults to local host. Note that the URL should be a websocket at port 8765.

Connect to local host:
```python main.py --role client```

Connect to another host:
```python main.py --role client --host ws://example.com:8765```

## Single

This mode runs both the server and client for a single player experience. Server features, such as game recordings, remain available.

E.g.
```python main.py --role single```

## Replay

This mode replays a recorded game through a window. The recording is specified with argument `recording` (exclude file extension).

E.g.
```python main.py --role replay --recording 20241018_164547_745081```

## Render

This mode renders a recording game into a video. The video is exported to the recordings folder. The recording is specified with argument `recording` (exclude file extension).

E.g.
```python main.py --role render --recording 20241018_164547_745081```