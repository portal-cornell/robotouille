# Robotouille Networking README

## Overview

Built into Robotouille is networking support for multiplayer. Robotouille uses an authoritative server, which clients can connect to. Servers record games played on them to collect data. 

## Available Modes

Several modes are offered, which can be chosen using the `--role` argument:

1. `server`
2. `client `
3. `single`
4. `replay`
5. `render`
6. `simulator`

## Simulator

This mode runs Robotouille without any networking overhead.

## Server

This mode sets up an Robotouille server. Clients that connect are automatically matchmaked and put together into lobbies. Use argument `display_server` to have the server render active games.

## Client

This mode runs the Robotouille client. Use argument `host` to choose which host to connect to. Defaults to local host.

## Single

This mode runs both the server and client for a single player experience. Server features, such as game recordings, remain available.

## Replay

This mode replays a recorded game through a window. The recording is specified with argument `recording`.

## Render

This mode renders a recording game into a video. The video is exported to the recordings folder. The recording is specified with argument `recording`.