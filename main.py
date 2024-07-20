import hydra
import os

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
    log_dir = cfg.evaluation.log_dir
    os.makedirs(log_dir, exist_ok=True)
    for environment_name in cfg.evaluation.environment_names:
        for seed in cfg.evaluation.testing_seeds:
            log_subdir = os.path.join(log_dir, f"{environment_name}_{seed}")
            basefile_to_subdir_lambda = lambda file_path: os.path.join(log_subdir, os.path.basename(file_path))
            os.makedirs(log_subdir, exist_ok=True)
            kwargs = OmegaConf.to_container(cfg.game, resolve=True)
            kwargs['seed'] = seed
            kwargs['video_file'] = basefile_to_subdir_lambda(kwargs['video_file'])
            kwargs['llm_kwargs'] = OmegaConf.to_container(cfg.llm, resolve=True)
            kwargs['llm_kwargs']['log_file'] = basefile_to_subdir_lambda(kwargs['llm_kwargs']['log_file'])
            kwargs.pop('environment_name') # Unused for evaluation
            agent_name = kwargs.pop('agent_name')
            run_robotouille(environment_name, agent_name, **kwargs)

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    if not cfg.evaluation.evaluate:
        play(cfg)
    evaluate(cfg)

if __name__ == "__main__":
    main()