import pickle
import time
from pathlib import Path
from robotouille.robotouille_env import create_robotouille_env

def run_replay(recording_name: str):
    replay(recording_name)

def replay(recording_name: str):
    """
    Replays a recorded game session by stepping through saved actions and states.

    Loads a `.pkl` recording file from the `recordings/` directory, reconstructs the original
    environment, and plays back the session in real-time using time deltas from the recording.

    Args:
        recording_name (str): The filename (without extension) of the recording to replay.

    Raises:
        ValueError: If an empty `recording_name` is provided.
        FileNotFoundError: If the specified recording does not exist.
    """
    if not recording_name:
        raise ValueError("Empty recording_name supplied")

    p = Path('recordings')
    with open(p / (recording_name + '.pkl'), 'rb') as f:
        recording = pickle.load(f)
    
    env = create_robotouille_env(recording["environment_name"], recording["movement_mode"], recording["seed"], recording["noisy_randomization"])
    obs, _ = env.reset()
    env.render(render_mode='human')

    previous_time = 0
    for actions, state, t in recording["actions"]:
        time.sleep(t - previous_time)
        previous_time = t
        obs, reward, done, info = env.step(actions)
        env.render(render_mode='human')
    env.render(render_mode='human', close=True)
