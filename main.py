from robotouille import simulator
import argparse

parser = argparse.ArgumentParser()

# Robotuille game parameters
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None)
parser.add_argument("--noisy_randomization", action="store_true", help="Whether to use 'noisy randomization' for procedural generation")

# Network parameters (see README under networking folder)
parser.add_argument("--role", help="\"local\" for vanilla simulator, \"client\" if client, \"server\" if server, \"single\" if single-player, \"replay\" if replaying, \"render\" if rendering video", default="local")
parser.add_argument("--server_display", action="store_true", help="Whether to show the game window as server (ignored for other roles)")
parser.add_argument("--host", help="Host to connect to", default="ws://localhost:8765")
parser.add_argument("--recording", help="Recording to replay", default="")
args = parser.parse_args()

simulator(args.environment_name, args.seed, args.noisy_randomization, args.role, args.server_display, args.host, args.recording)
