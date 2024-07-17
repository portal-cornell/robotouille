import hydra
from omegaconf import DictConfig, OmegaConf

from robotouille import simulator
from agents import NAME_TO_AGENT
from utils.robotouille_input import create_action_from_event
from robotouille.robotouille_env import create_robotouille_env

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg : DictConfig) -> None:
    llm_cfg = cfg.llm
    game_cfg = cfg.game
    if game_cfg.agent_name == "human":
        simulator(game_cfg.environment_name, game_cfg.seed, game_cfg.noisy_randomization)
    else:
        env, json, renderer = create_robotouille_env(game_cfg.environment_name, game_cfg.seed, game_cfg.noisy_randomization)
        obs, info = env.reset()
        env.render()
        done = False
        steps = 0

        agent = NAME_TO_AGENT[game_cfg.agent_name](llm_cfg)

        while not done or not agent.is_done() or steps < game_cfg.max_steps:
            current_state = env.current_state
            proposed_actions = agent.propose_actions(obs, current_state)
            if len(proposed_actions) == 0:
                steps += 1
                continue
            action, param_arg_dict = proposed_actions[0]
            actions = []
            for player in current_state.get_players():
                if player == current_state.current_player:
                    actions.append((action, param_arg_dict))
                else:
                    actions.append((None, None))
            if action is None:
                # Retry for keyboard input
                continue
            obs, reward, done, info = env.step(actions)
            env.render()
            steps += 1
        env.render(close=True)

if __name__ == "__main__":
    main()