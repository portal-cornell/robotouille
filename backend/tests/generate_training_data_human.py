"""
Collects imitation learning training data from human play.

For each seed, opens a pygame window. Complete the task to save the trajectory
and advance to the next seed. Press ESC to exit.

Usage:
    python backend/tests/generate_training_data_human.py
"""

import json
import os
import platform
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# On macOS, DISPLAY is unset, which tricks the renderer into headless mode.
# Pre-set SDL_VIDEODRIVER so the renderer's headless guard doesn't fire.
if platform.system() == "Darwin" and os.getenv("SDL_VIDEODRIVER") is None:
    os.environ["SDL_VIDEODRIVER"] = "cocoa"

from agents.human import Human
from robotouille.robotouille_env import create_robotouille_env

ENVIRONMENTS = [
    # "synchronous/0_cheese_sandwich",
    # "synchronous/1_lettuce_sandwich",
    "synchronous/2_lettuce_tomato_sandwich",
    # "synchronous/3_burger",
    # "synchronous/4_cheeseburger",
    # "synchronous/5_double_cheeseburger",
    # "synchronous/6_lettuce_tomato_cheeseburger",
    # "synchronous/7_two_lettuce_chicken_sandwich",
    # "synchronous/8_two_lettuce_tomatao_burger",
    # "synchronous/9_onion_cheese_burger_and_lettuce_tomato_chicken_sandwich"
]

SEEDS = [
    # 42, 
    # 84, 
    # 126, 
    # 168, 
    # 210, 
    # 252, 
    # 294, 
    # 336, 
    # 378, 

    420

    # added for the invalid map for 1_lettuce_sandwich when seed = 420. Also impossible for 2_lettuce_tomato_sandwich
    # 420 + 42
]

# 420 not possible with 1_lettuce_sandwich

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "training_data_human.jsonl"
)


def append_entry(path, entry):
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def run():
    for env_name in ENVIRONMENTS:
        for seed in SEEDS:
            env = create_robotouille_env(env_name, seed=seed, noisy_randomization=False)
            obs, _ = env.reset()
            agent = Human({})
            trajectory = []
            t0 = time.time()

            print(f"\n--- {env_name} | seed={seed} ---")
            print(f"Goal: {env.current_state.goal_description}")

            done = False
            while not done and not agent.is_done():
                env.render("human")
                proposed = agent.propose_actions(obs, env)

                if agent.is_retry(0):
                    obs, _ = env.reset()
                    agent = Human({})
                    trajectory = []
                    t0 = time.time()
                    print(f"Retrying seed={seed}...")
                    continue

                if not proposed:
                    continue

                action, params = proposed[0]
                trajectory.append(action.get_language_description(params))

                actions = []
                for player in env.current_state.get_players():
                    if player == env.current_state.current_player:
                        actions.append((action, params))
                    else:
                        actions.append((None, None))

                obs, _, done, _ = env.step(actions)

            env.render("human", close=True)

            if agent.is_done():
                print("Exiting.")
                return

            elapsed = round(time.time() - t0, 3)
            entry = {
                "environment": env_name,
                "seed": seed,
                "trajectory": trajectory,
                "length": len(trajectory),
                "elapsed_s": elapsed,
            }
            append_entry(OUTPUT_PATH, entry)
            print(f"Saved — {len(trajectory)} steps in {elapsed}s")

    print("\nAll seeds complete.")


if __name__ == "__main__":
    run()
