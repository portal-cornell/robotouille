from robotouille import simulator
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None)
parser.add_argument("--role", help="\"client\" if client, \"server\" if server, \"replay\" if replaying, \"render\" if rendering video", default="client")
parser.add_argument("--server_display", action="store_true", help="Whether to show the game window as server (ignored for other roles)")
parser.add_argument("--host", help="Host to connect to", default="ws://localhost:8765")
parser.add_argument("--replay", help="Recording to replay", default="")
parser.add_argument("--noisy_randomization", action="store_true", help="Whether to use 'noisy randomization' for procedural generation")
args = parser.parse_args()

simulator(args.environment_name, args.seed, args.role, args.server_display, args.host, args.replay, args.noisy_randomization)
