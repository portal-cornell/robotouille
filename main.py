from robotouille import simulator
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None)
parser.add_argument("--noisy_randomization", action="store_true", help="Whether to use 'noisy randomization' for procedural generation")
args = parser.parse_args()

simulator(args.environment_name, args.seed, args.noisy_randomization)
