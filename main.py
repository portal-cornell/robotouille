import overcooked_utils
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
# optional argument

args = parser.parse_args()

env = overcooked_utils.create_overcooked_env(args.environment_name)
obs, info = env.reset()
env.render(mode='human')
done = False
step = 0

while not done and step <= 1000:
    obs, reward, done, info = env.step(interactive=True)
    env.render(mode='human')
    step += 1