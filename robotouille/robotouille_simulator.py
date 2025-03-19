import math
import pygame

from omegaconf import DictConfig
from typing import Dict, Any
import random

from agents import NAME_TO_AGENT

from utils.video_recorder import record_video
from utils.robotouille_input import create_action_from_event
from robotouille.robotouille_env import create_robotouille_env
from backend.movement.player import Player
from backend.movement.movement import Movement

# Deprecated - Use run_robotouille instead
def simulator(environment_name, seed = None, noisy_randomization = False, movement_mode = 'traverse'):
    env = create_robotouille_env(environment_name, movement_mode, seed, noisy_randomization)

<<<<<<< Updated upstream
    obs, info = env.reset()
    done = False
=======
class RobotouilleSimulator:
    def __init__(self, canvas, environment_name: str, seed: int = 42, noisy_randomization: bool = False, movement_mode: str = 'immediate', human = True, render_fps=60):
        """
        Initialize the Robotouille simulator.

        Args:
            canvas (pygame.Surface): The main display canvas.
            environment_name (str): The name of the environment to load.
            seed (int): Seed for randomization (default: 42).
            noisy_randomization (bool): Whether to introduce noise into randomization (default: False).
            movement_mode (str): The movement mode for the environment (default: 'traverse').
            human (bool): Whether a human player is controlling the game (default: True).
            render_fps (int): Frames per second for rendering (default: 60).
        """

        self.human = human
        self.canvas = canvas
        self.env, self.json, self.renderer = create_robotouille_env(environment_name, movement_mode, seed, noisy_randomization)
        self.obs, self.info = self.env.reset()
        self.done = False
        self.interactive = False  # Set to True to interact with the environment through terminal REPL (ignores input)
        screen_size = canvas.get_size()
        self.surface = pygame.Surface(screen_size)
        self.pause = PauseScreen(screen_size)
        self.clock = pygame.time.Clock()
        self.players = self.obs.get_players()
        self.actions = []
        self.render_fps = render_fps
        self.next_screen = None
>>>>>>> Stashed changes
    
    actions = []
    current_state = env.current_state
    players = current_state.get_players()
    while not done:
        env.render("human")

<<<<<<< Updated upstream
        # Construct action from input
        pygame_events = pygame.event.get()
=======
        Specifies the screen that should be displayed after the current screen.

        Args:
           next_screen (str): Identifier for the next screen (e.g., `MAIN_MENU`, `SETTINGS`).

        """
        self.next_screen = next_screen

    def draw(self):
        """
        Renders the current state of the game environment and pause screen onto the canvas.
        """

        self.renderer.render(self.obs, mode='human')
        self.surface.blit(self.renderer.surface, (0, 0))
        self.surface.blit(self.pause.get_screen(), (0, 0))
        self.canvas.blit(self.surface, (0, 0))
        # The framerate of the renderer. This isn't too important since the renderer
        # self.clock.tick(self.render_fps)


    def handle_pause(self, pygame_events):
        """
        Handles pause functionality, including toggling the pause screen and switching game states.

        Args:
            pygame_events (list): List of pygame events to handle.
        """

        if not self.human:
            return
        for event in pygame_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.done = True
                if event.key == pygame.K_p:
                    self.pause.toggle()

        if self.pause.next_screen is not None:
            current_screen = self.pause.next_screen
            self.pause.set_next_screen(None)
            return current_screen

        self.pause.update(pygame_events)


    def update(self):
        """
        Main update loop for the simulation. Handles rendering, input, and game logic.

        """
        
        if self.done:
            self.renderer.render(self.obs, close=True)
            self.next_screen = ENDGAME
            return
        
        if self.pause.next_screen is not None:
            self.next_screen = self.pause.next_screen
            self.pause.set_next_screen(None)
            self.pause.toggle()
            return
        
        pygame_events = pygame.event.get()
            
        self.draw()
        self.handle_pause(pygame_events)

>>>>>>> Stashed changes
        mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
        keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
        player_obj = Player.get_player(current_state.current_player.name)
        no_action = True
        
        # If player is moving, do not allow any action; action will be None
        if Movement.is_player_moving(player_obj.name):
            action, param_arg_dict = None, None
            no_action = False
        # If player is not moving, allow action
        else:
            action, param_arg_dict = create_action_from_event(current_state, mousedown_events+keydown_events, env.input_json, env.renderer)
            no_action = action is None

        if no_action:
            # Retry for keyboard input
            continue
        
        # Construct actions for all players
        actions.append((action, param_arg_dict))
        current_state.current_player = current_state.next_player()

        # If all players have made an action, step the environments
        if len(actions) == len(players):
            obs, reward, done, info = env.step(actions)
            env.render('human')
            actions = []

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
                    - log_path (str):
                        The path to the log file to write to.
    
    Returns:
        done (bool):
            Whether the environment is done.
        steps (int):
            The number of steps taken in the environment.
    """
    # Initialize environment
    movement_mode = kwargs.get('movement_mode', 'immediate')
    assert movement_mode != 'traverse' or agent_name == "human", "Traverse movement mode only supported for human agent"
    seed = kwargs.get('seed', None)
    noisy_randomization = kwargs.get('noisy_randomization', False)
    env = create_robotouille_env(environment_name, movement_mode, seed, noisy_randomization)

    # Initialize agent
    llm_kwargs = kwargs.get('llm_kwargs', {})
    agent = NAME_TO_AGENT[agent_name](llm_kwargs)
    agent_done_cond = lambda a: a.is_done() if a is not None else False
    agent_retry_cond = lambda a, steps_left: a.is_retry(steps_left) if a is not None else False

    render_mode = kwargs.get('render_mode', 'human')
    record = kwargs.get('record', False)

    obs, info = env.reset()
    done = False
    steps = 0
    if kwargs.get('max_steps'):
        max_steps = kwargs.get('max_steps')
    elif kwargs.get('max_steps_multiplier'):
        agent = NAME_TO_AGENT['bfs'](None)
        optimal_plan = agent.propose_actions(obs, env)
        max_steps = math.ceil(len(optimal_plan) * kwargs.get('max_steps_multiplier'))
    else:
        assert False, "Must provide either max_steps or max_steps_multiplier in kwargs"
    imgs = []
    queued_actions = []
    stochastic_done = False
    while not done and not agent_done_cond(agent) and steps < max_steps:
        img = env.render(render_mode)
        if record:
            imgs.append(img)
        
        if len(queued_actions) == 0:
            # Retrieve action(s) from agent output
            proposed_actions = agent.propose_actions(obs, env)
            if len(proposed_actions) == 0:
                # Reprompt agent for action(s)
                continue
            action, param_arg_dict = proposed_actions[0]
            queued_actions = proposed_actions[1:]
        else:
            action, param_arg_dict = queued_actions.pop(0)
        
        actions = [(action, param_arg_dict)]
        
        # Step environment
        obs, reward, done, info = env.step(actions)

        if kwargs.get("stochastic") and not stochastic_done and random.random() < 0.1:
            # Randomly set one cut ingredient to be uncut
            cut_predicates = [p for p in env.current_state.predicates if p.name == 'iscut']
            for predicate in cut_predicates:
                if env.current_state.predicates[predicate]:
                    env.current_state.predicates[predicate] = False
                    stochastic_done = True
                    break
        
        steps += action is not None # Only increment steps if an action was taken

        if agent_retry_cond(agent, math.floor(max_steps - steps)):
            steps = 0
            obs, info = env.reset()
            queued_actions = []
    
    img = env.render(render_mode, close=True)
    if record:
        imgs.append(img)
        filename = kwargs.get('video_path', 'recorded_video.mp4')
        fourcc_str = kwargs.get('fourcc_str', 'avc1')
        fps = kwargs.get('video_fps', 3) # Videos with FPS < 3 on MP4 will appear corrupted (all green)
        record_video(imgs, filename, fourcc_str, fps)
    
    return done, steps