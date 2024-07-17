import hydra
from omegaconf import DictConfig, OmegaConf

from agents import NAME_TO_AGENT

from robotouille import simulator
from robotouille.robotouille_env import create_robotouille_env

from utils.robotouille_input import create_action_from_event
from utils.video_recorder import record_video

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg : DictConfig) -> None:
    llm_cfg = cfg.llm
    game_cfg = cfg.game
    if game_cfg.agent_name == "human":
        simulator(game_cfg.environment_name, game_cfg.seed, game_cfg.noisy_randomization, game_cfg)
    else:
        env, json, renderer = create_robotouille_env(game_cfg.environment_name, game_cfg.seed, game_cfg.noisy_randomization)
        obs, info = env.reset()
        done = False
        steps = 0
        render_mode = game_cfg.render_mode
        record = game_cfg.record

        agent = NAME_TO_AGENT[game_cfg.agent_name](llm_cfg)

        imgs = []
        while not done and not agent.is_done() and steps < game_cfg.max_steps:
            img = env.render(render_mode)
            if record:
                imgs.append(img)
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
            steps += 1
        img = env.render(render_mode, close=True)
        if record:
            imgs.append(img)
            filename = game_cfg.video_file
            fourcc_str = game_cfg.fourcc_str
            fps = game_cfg.video_fps
            record_video(imgs, filename, fourcc_str, fps)

if __name__ == "__main__":
    main()