import pickle
import time
from pathlib import Path
from robotouille.robotouille_env import create_robotouille_env

def run_replay(recording_name: str):
    replay(recording_name)

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
