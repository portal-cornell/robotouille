import hydra
import os
import json

from omegaconf import DictConfig, OmegaConf

from robotouille.robotouille_simulator import run_robotouille

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
    for environment_name in cfg.evaluation.environment_names:
        for seed in cfg.evaluation.testing_seeds:
            log_subdir = os.path.join(log_dir_path, f"{environment_name}_{seed}")
            basefile_to_subdir_lambda = lambda file_path: os.path.join(log_subdir, os.path.basename(file_path)) if file_path is not None else None
            os.makedirs(log_subdir, exist_ok=True)
            kwargs = OmegaConf.to_container(cfg.game, resolve=True)
            kwargs['seed'] = seed
            kwargs['video_path'] = basefile_to_subdir_lambda(kwargs['video_path'])
            kwargs['llm_kwargs'] = OmegaConf.to_container(cfg.llm, resolve=True)
            kwargs['llm_kwargs']['log_path'] = basefile_to_subdir_lambda(kwargs['llm_kwargs']['log_path'])
            kwargs.pop('environment_name') # Unused for evaluation
            agent_name = kwargs.pop('agent_name')
            done, steps = run_robotouille(environment_name, agent_name, **kwargs)
            results[f"{environment_name}_{seed}"] = {'done': done, 'steps': steps}
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
    main()