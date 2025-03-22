import hydra
import os
import json
import pygame

parser = argparse.ArgumentParser()

# Robotouille game parameters
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None)
parser.add_argument("--noisy_randomization", action="store_true", help="Whether to use 'noisy randomization' for procedural generation")
parser.add_argument("--movement_mode", help="The movement mode to use for the environment.", default="traverse")

# Network parameters (see README under networking folder)
parser.add_argument("--role", help="\"local\" for vanilla simulator, \"client\" if client, \"server\" if server, \"single\" if single-player, \"replay\" if replaying, \"render\" if rendering video", default="local")
parser.add_argument("--display_server", action="store_true", help="Whether to show the game window as server (ignored for other roles)")
parser.add_argument("--host", help="Host to connect to", default="ws://localhost:8765")
parser.add_argument("--recording", help="Recording to replay", default="")
args = parser.parse_args()

simulator(args.environment_name, args.seed, args.noisy_randomization, args.movement_mode, args.role, args.display_server, args.host, args.recording)



from robotouille.robotouille_simulator import run_robotouille

from omegaconf import DictConfig, OmegaConf

def play(cfg: DictConfig) -> None:
    """Play the game with the given configuration.
    
    Use this function for either
    1. Playing an environment as a human
    2. Running an agent in an environment

    Parameters:
        cfg (DictConfig):
            The Hydra configuration for Robotouille.
    """
    kwargs = OmegaConf.to_container(cfg.game, resolve=True)
    kwargs['llm_kwargs'] = OmegaConf.to_container(cfg.llm, resolve=True)
    environment_name = kwargs.pop('environment_name')
    agent_name = kwargs.pop('agent_name')
    run_robotouille(environment_name, agent_name, **kwargs)

def evaluate(cfg: DictConfig) -> None:
    """Play the game with the given configuration.
    
    Use this function for evaluating an agent on various environments
    and seeds.
    
    Parameters:
        cfg (DictConfig):
            The Hydra configuration for Robotouille.
    """
    log_dir_path = cfg.evaluation.log_dir_path
    os.makedirs(log_dir_path, exist_ok=True)
    results = {}
    environment_names = cfg.evaluation.environment_names
    optimal_steps = cfg.evaluation.optimal_steps
    for environment_name, max_steps in zip(environment_names, optimal_steps):
        for seed in cfg.evaluation.testing_seeds:
            log_subdir = os.path.join(log_dir_path, f"{environment_name}_{seed}")
            basefile_to_subdir_lambda = lambda file_path: os.path.join(log_subdir, os.path.basename(file_path)) if file_path is not None else None
            os.makedirs(log_subdir, exist_ok=True)
            kwargs = OmegaConf.to_container(cfg.game, resolve=True)
            kwargs['max_steps'] = max_steps if kwargs.get('max_steps') is None else kwargs['max_steps']
            kwargs['max_steps'] *= kwargs.get('max_step_multiplier', 1)
            kwargs['seed'] = seed
            kwargs['video_path'] = basefile_to_subdir_lambda(kwargs['video_path'])
            kwargs['llm_kwargs'] = OmegaConf.to_container(cfg.llm, resolve=True)
            kwargs['llm_kwargs']['log_path'] = basefile_to_subdir_lambda(kwargs['llm_kwargs']['log_path'])
            kwargs.pop('environment_name') # Unused for evaluation
            agent_name = kwargs.pop('agent_name')
            done, steps = run_robotouille(environment_name, agent_name, **kwargs)
            results[f"{environment_name}_{seed}"] = {'done': done, 'steps': steps, 'max_steps': kwargs['max_steps']}
    accuracy = sum([result['done'] for result in results.values()]) / len(results)
    average_steps = sum([result['steps'] for result in results.values()]) / len(results)
    results["accuracy"] = accuracy
    results["average_steps"] = average_steps
    results_path = os.path.join(log_dir_path, os.path.basename(cfg.evaluation.results_path))
    with open(results_path, 'w') as f:
        f.write(json.dumps(results, indent=4))

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    if not cfg.evaluation.evaluate:
        play(cfg)
    else:
        evaluate(cfg)

if __name__ == "__main__":
    # TODO(chalo2000): Hide this in RobotouilleApp
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption('Robotouille Simulator')
    pygame.display.set_mode((512,512))
    from frontend.loading import LoadingScreen
    LoadingScreen((512,512)).load_all_assets()

    main()
    
    pygame.display.quit()
    pygame.quit()