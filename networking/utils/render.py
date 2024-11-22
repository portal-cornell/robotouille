import pickle
import imageio
from pathlib import Path
from robotouille.robotouille_env import create_robotouille_env

def run_render(recording_name: str):
    render(recording_name)

def render(recording_name: str):
    p = Path('recordings')
    with open(p / (recording_name + '.pkl'), 'rb') as f:
        recording = pickle.load(f)
    
    env, _, renderer = create_robotouille_env(recording["environment_name"], recording["movement_mode"], recording["seed"], recording["noisy_randomization"])
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
