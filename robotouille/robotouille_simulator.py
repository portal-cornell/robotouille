import pygame
from omegaconf import DictConfig
from typing import Dict, Any

from agents import NAME_TO_AGENT

from utils.video_recorder import record_video
from robotouille.robotouille_env import create_robotouille_env

# Deprecated - Use run_robotouille instead
def simulator(environment_name: str, seed: int=42, noisy_randomization: bool=False):
    env, json, renderer = create_robotouille_env(environment_name, seed, noisy_randomization)
    obs, info = env.reset()
    done = False
    
    while not done:
        env.render("human")
        current_state = env.current_state
        # Construct action from input
        pygame_events = pygame.event.get()
        # Mouse clicks for movement and pick/place stack/unstack
        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        # Keyboard events ('e' button) for cut/cook ('space' button) for noop
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        actions = []
        action, param_arg_dict = create_action_from_event(current_state, mousedown_events+keydown_events, env.input_json, renderer)
        for player in current_state.get_players():
            if player == current_state.current_player:
                actions.append((action, param_arg_dict))
            else:
                actions.append((None, None))
        if action is None:
            # Retry for keyboard input
            continue
        obs, reward, done, info = env.step(actions)
    env.render("human", close=True)

def run_robotouille(environment_name: str, agent_name: str, **kwargs: Dict[str, Any]):
    """Runs the provided Robotouille environment with the given agent.

    Parameters:
        environment_name (str):
            The name of the environment to run.
            Find environment names under environments/env_generator/examples
        agent_name (str):
            The name of the agent to run. Use "human" for Pygame human input.
            Find agent names under agents/__init__.py
        kwargs (Dict[str, Any]):
            Optional parameters to run Robotouille with including:
                - seed (int):
                    The seed for the environment.
                - max_steps (int):
                    The maximum number of steps to run the environment.
                - noisy_randomization (bool):
                    Whether to use noisy randomization.
                    See environments/env_generator/README.md for more information.
                - render_mode (str):
                    The render mode to use. Can be "human" or "rgb_array".
                - record (bool):
                    Whether to record a video of the run.
                - fourcc_str (str):
                    The fourcc string to use for the video codec.
                - video_path (str):
                    The filename for the file to save the video to.
                - video_fps (int):
                    The frames per second for the video.
                - llm_kwargs (Dict[str, Any]):
                    The kwargs for the LLM agent.
    
    Returns:
        done (bool):
            Whether the environment is done.
        steps (int):
            The number of steps taken in the environment.
    """
    # Initialize environment
    seed = kwargs.get('seed', None)
    noisy_randomization = kwargs.get('noisy_randomization', False)
    env = create_robotouille_env(environment_name, seed, noisy_randomization)
    renderer = env.renderer
    # Initialize agent
    llm_kwargs = kwargs.get('llm_kwargs', {})
    agent = NAME_TO_AGENT[agent_name](llm_kwargs)
    agent_done_cond = lambda a: a.is_done() if a is not None else False

    render_mode = kwargs.get('render_mode', 'human')
    record = kwargs.get('record', False)

    obs, info = env.reset()
    done = False
    steps = 0
    max_steps = kwargs.get('max_steps', 100)
    imgs = []
    while not done and not agent_done_cond(agent) and steps < max_steps:
        
        img = env.render(render_mode)
        if record:
            imgs.append(img)
        
        # Retrieve action from agent output
        proposed_actions = agent.propose_actions(obs, env)
        if len(proposed_actions) == 0:
            # Reprompt agent for action
            continue
        action, param_arg_dict = proposed_actions[0]
        
        # Assign action to players
        actions = []
        current_state = env.current_state
        for player in current_state.get_players():
            if player == current_state.current_player:
                actions.append((action, param_arg_dict))
            else:
                actions.append((None, None))
        
        # Step environment
        obs, reward, done, info = env.step(actions)
        steps += 1
    
    img = env.render(render_mode, close=True)
    if record:
        imgs.append(img)
        filename = kwargs.get('video_path', 'recorded_video.mp4')
        fourcc_str = kwargs.get('fourcc_str', 'mp4v')
        fps = kwargs.get('video_fps', 3) # Videos with FPS < 3 on MP4 will appear corrupted (all green)
        record_video(imgs, filename, fourcc_str, fps)
    
    return done, steps