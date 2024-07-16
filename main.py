import argparse
import hydra
from omegaconf import DictConfig, OmegaConf

from robotouille import simulator
from agents import NAME_TO_AGENT
from utils.robotouille_input import create_action_from_event
from robotouille.robotouille_env import create_robotouille_env

# parser = argparse.ArgumentParser()
# parser.add_argument("--agent", help="The agent to use for the environment.", default="human")
# parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
# parser.add_argument("--seed", help="The seed to use for the environment.", default=None)
# parser.add_argument("--noisy_randomization", action="store_true", help="Whether to use 'noisy randomization' for procedural generation")
# args = parser.parse_args()

# if args.agent == "human":
#     simulator(args.environment_name, args.seed, args.noisy_randomization)
# else:
#     env, json, renderer = create_robotouille_env(args.environment_name, args.seed, args.noisy_randomization)
#     obs, info = env.reset()
#     env.render()
#     done = False

#     agent = 0 #get_agent(args.agent)
    
#     while not done:
#         current_state = env.current_state
#         text_action = agent.get_action(obs)
#         action, param_arg_dict = 0#create_action_from_text(text_action, current_state)
#         actions = []
#         for player in current_state.get_players():
#             if player == current_state.current_player:
#                 actions.append((action, param_arg_dict))
#             else:
#                 actions.append((None, None))
#         if action is None:
#             # Retry for keyboard input
#             continue
#         obs, reward, done, info = env.step(actions)
#         env.render()
#         print(obs)
#     env.render(close=True)

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

        agent = NAME_TO_AGENT[game_cfg.agent_name](llm_cfg)
        assert False, 'TODO(chalo2000): Make observation contain valid actions'

        while not done:
            current_state = env.current_state
            text_action = agent.get_action(obs)
            action, param_arg_dict = 0#create_action_from_text(text_action, current_state)
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
            print(obs)
        env.render(close=True)

if __name__ == "__main__":
    main()