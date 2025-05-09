# Robotouille Networking README

## Overview

Built into Robotouille is networking support for multiplayer. Robotouille uses an authoritative server, which clients can connect to. Servers record games played on them to collect data. 

## Available Modes

Several modes are offered, which can be chosen using the `++game.role` argument:

1. `local`
2. `server`
3. `client`
4. `replay`
5. `render`

## Local

This mode runs Robotouille without any networking overhead.

E.g.
```sh
python main.py ++game.environment_name=original
```

## Server

This mode sets up an Robotouille server. Clients that connect are automatically matchmaked and put together into lobbies. Use argument `display_server` to have the server render active games.

E.g.
```sh
python main.py ++game.role=server
```

To render active games:
```sh
python main.py ++game.role=server ++game.display_server=true
```

## Client

This mode runs the Robotouille client. Use argument `host` to choose which host to connect to. Defaults to local host. Note that the URL should be a websocket at port 8765.

Connect to local host:
```sh
python main.py ++game.role=client
```

Connect to another host:
```sh
python main.py ++game.role=client ++game.host=ws://example.com:8765
```

## Replay

This mode replays a recorded game through a window. The recording is specified with argument `recording` in base_game.yaml. 

E.g.
```sh
python main.py ++game.role=replay
```

## Render

This mode renders a recording game into a video. The video is exported to the recordings folder. The recording is specified with argument `recording` in base_game.yaml. 

E.g.
```sh
python main.py ++game.role=render
```