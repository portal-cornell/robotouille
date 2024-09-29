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
import networking.server as robotouille_server
import networking.client as robotouille_client

def simulator(environment_name: str, seed: int=42, role: str="simulator", display_server: bool=False, host: str="ws://localhost:8765", recording: str="", noisy_randomization: bool=False):
    if recording != "" and role != "replay" and role != "render":
        role = "replay"
    if role == "server":
        robotouille_server.run_server(environment_name, seed, noisy_randomization, display_server)
    elif role == "client":
        robotouille_client.run_client(environment_name, seed, host, noisy_randomization)
    elif role == "single":
        asyncio.run(single_player(environment_name, seed, noisy_randomization))
    elif role == "replay":
        replay(recording)
    elif role == "render":
        render(recording)
    elif role == "simulator":
        simulate(environment_name, seed, noisy_randomization)
    else:
        print("Invalid role:", role)

async def single_player(environment_name: str, seed: int=42, noisy_randomization: bool=False):
    event = asyncio.Event()
    server = asyncio.create_task(robotouille_server.server_loop(environment_name=environment_name, seed=seed, noisy_randomization=noisy_randomization, event=event))
    await asyncio.sleep(0.5)  # wait for server to initialize
    client = asyncio.create_task(robotouille_client.client_loop(environment_name=environment_name, seed=seed, noisy_randomization=noisy_randomization))
    await client
    event.set()
    await server

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

def simulate(environment_name, seed, noisy_randomization):
    # Your code for robotouille goes here
    env, json, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
    obs, info = env.reset()
    renderer.render(obs, mode='human')
    done = False
    interactive = False # Set to True to interact with the environment through terminal REPL (ignores input)
    
    while not done:
        # Construct action from input
        pygame_events = pygame.event.get()
        # Mouse clicks for movement and pick/place stack/unstack
        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        # Keyboard events ('e' button) for cut/cook ('space' button) for noop
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        actions = []
        action, args = create_action_from_control(env, obs, obs.current_player, mousedown_events+keydown_events, renderer)
        for player in obs.get_players():
            if player == obs.current_player:
                actions.append((action, args))
            else:
                actions.append((None, None))
        if not interactive and action is None:
            # Retry for keyboard input
            continue
        obs, reward, done, info = env.step(actions, interactive=interactive)
        renderer.render(obs, mode='human')
    renderer.render(obs, close=True)