import overcooked_env
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None, type=int)
args = parser.parse_args()

noisy_randomization = True
env, json = overcooked_env.create_overcooked_env(args.environment_name, args.seed, noisy_randomization)
obs, info = env.reset()
env.render(mode='human')
done = False
step = 0

while not done and step <= 1000:
    obs, reward, done, info = env.step(interactive=True)
    env.render(mode='human')
    step += 1