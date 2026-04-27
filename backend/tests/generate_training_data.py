"""
Generates imitation learning training data by running A* on synchronous environments
across multiple seeds and saving the optimal trajectory (action sequence) to JSON.

Writes results incrementally — one entry per seed — so progress is preserved on failure.

Usage:
    python backend/tests/generate_training_data.py
"""

import json
import os
import sys
import time

# Resolve imports from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.astar_agent import AStarAgent
from robotouille.robotouille_env import create_robotouille_env

ENVIRONMENTS = [
    "synchronous/0_cheese_sandwich",
]

SEEDS = [42, 84, 126, 168, 210, 252, 294, 336, 378, 420]

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "training_data.json"
)


def load_existing(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def collect(env_name, seed):
    env = create_robotouille_env(env_name, seed=seed, noisy_randomization=False)
    obs, _ = env.reset()
    agent = AStarAgent({})

    t0 = time.time()
    plan = agent.propose_actions(obs, env)
    elapsed = time.time() - t0

    trajectory = [
        action.get_language_description(params)
        for action, params in plan
    ]

    return {
        "environment": env_name,
        "seed": seed,
        "trajectory": trajectory,
        "length": len(trajectory),
        "elapsed_s": round(elapsed, 3),
    }


def run():
    results = load_existing(OUTPUT_PATH)
    done_keys = {(r["environment"], r["seed"]) for r in results}

    for env_name in ENVIRONMENTS:
        for seed in SEEDS:
            if (env_name, seed) in done_keys:
                print(f"Skipping {env_name} seed={seed} (already collected)")
                continue

            print(f"Running {env_name} seed={seed} ...")
            try:
                entry = collect(env_name, seed)
                results.append(entry)
                save(OUTPUT_PATH, results)
                print(f"  Done — {entry['length']} steps in {entry['elapsed_s']}s")
            except Exception as e:
                print(f"  ERROR: {e}")


if __name__ == "__main__":
    run()
