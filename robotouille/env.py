import copy
import gym
import json
import random
import pygame
import re
import string

from backend.predicate import Predicate
from backend.object import Object
from backend.state import State
from backend.movement.movement import Movement
from backend.gamemodes.classic import Classic
from domain.domain_builder import build_domain
from utils.robotouille_utils import trim_item_ID
from .env_utils import build_identity_predicates, build_location_predicates, build_stacking_predicates, build_goal

def build_state(domain_json, environment_json, layout, animate):
    """
    This function is a temporary solution to building the state.

    Args:
        domain_json (dict): Dictionary containing the domain name, object types, predicate definitions, and action definitions.
        environment_json (dict): Dictionary containing the initial stations, items, and player location.
        layout (list): A 2D list of station names representing where stations are in the environment.
        animate (bool): Whether or not to animate the movement of the players.

    Returns:
        state (State): The state.
    """
    domain = build_domain(domain_json)

    entity_fields = domain.get_entity_fields()

    objects = []

    for field in entity_fields:
        if environment_json.get(field) is None: continue
        for entity in environment_json[field]:
            objects.append(Object(entity["name"], field[:-1]))

    true_predicates = []
    true_predicates += build_identity_predicates(domain_json, environment_json, entity_fields)
    true_predicates += build_location_predicates(domain_json, environment_json)
    true_predicates += build_stacking_predicates(domain_json, environment_json)
    goal = build_goal(domain_json, environment_json, environment_json["goal"])
    goal_description = environment_json["goal_description"]

    state = State().initialize(domain, objects, true_predicates, goal, goal_description)

    return state

def build_input_json(domain_json):
    """
    This function builds the input JSON from the domain JSON.

    Args:
        domain_json (dict): Dictionary containing the domain name, object types, predicate definitions, and action definitions.

    Returns:
        input_json (dict): The input JSON.
    """
    input_json_name = domain_json["input_json"]

    with open(input_json_name, "r") as input_json_file:
        input_json = json.load(input_json_file)

    return input_json

def build_gamemode(environment_json, domain_json, state, layout, animate):
    """
    This function builds the gamemode of the environment. 
    Args:
        environment_json (dict): The environment dictionary
        domain_json (dict): The domain dictionary
        state (State): The state of the environment
        layout (list): A 2D list of station names representing where stations are in the environment.
        animate (bool): Whether or not to animate the movement of the players.
    Returns:
        gamemode (GameMode): The gamemode of the environment
    """
    name = environment_json["gamemode"]["name"]

    recipe_json_name = domain_json["recipe_json"]
    with open(recipe_json_name, "r") as recipe_json_file:
        recipe_json = json.load(recipe_json_file)
    if name == "classic":
        gamemode = Classic(state, domain_json, environment_json, recipe_json)
        gamemode.movement = Movement(layout, animate, environment_json, gamemode)
        return gamemode
    return None

class LanguageSpace(gym.spaces.Text):
    
    @staticmethod
    def state_to_language_description(state):
        """
        Converts a state to a language description.

        Parameters:
            state (State):
                The state to convert to a language description.
        
        Returns:
            language_description (str):
                The language description of the state.
        """
        predicates = [pred for pred, is_true in state.predicates.items() if is_true]
        language_description = ""
        # TODO(chalo2000): Separate Predicate and Action into PredicateDef and ActionDef
        #                  to remove param_arg_dict and simplify retrieving the language 
        #                  description of the action.
        # Object descriptions
        object_descriptions = []
        pred_parser = lambda x: [s.strip() for s in re.findall(r'\(([^()]+)\)', str(x))[0].split(',')]
        for obj in state.objects:
            description_header = f"{obj.object_type.capitalize()} {obj.name}:"
            relevant_preds = [pred for pred in predicates if obj.name in pred_parser(pred)]
            language_descriptions = [pred.get_language_description(obj) for pred in relevant_preds]
            predicate_descriptions = "\n".join(language_descriptions)
            object_descriptions.append(f"{description_header}\n{predicate_descriptions}")
        language_description += "\n\n".join(object_descriptions)
        # Valid Actions
        language_description += "\n\nValid Actions:\n"
        _, str_valid_actions = state.get_valid_actions_and_str()
        language_description += "\n".join(str_valid_actions)
        # Goal
        language_description += f"\n\nGoal: {state.goal_description}"
        return language_description
    
    def __init__(self, initial_state, min_length=1, max_length=32768):
        """
        Initializes the Language space.

        Parameters:
            initial_state (State):
                The initial state of the language environment.
            min_length (int):
                The minimum length of the string. At least one character by default.
            max_length (int):
                The maximum length of the string. At most 8192 * 4 characters by default
                to match most LLM's max context lengths. 
        """
        charset = string.ascii_letters + string.digits + string.punctuation + string.whitespace
        super().__init__(min_length=min_length, max_length=max_length, charset=charset)
        self.initial_state = initial_state
    
    def sample(self):
        """
        Samples a random language description from the state space.

        Note, while this function returns valid language descriptions,
        it is likely to return illegal state descriptions. This function
        should only be used for testing purposes (e.g. generate example
        formats for the initial state).

        Returns:
            language (str): The random language description.
        """
        # TODO(chalo2000): Reimplement this to generate valid language actions ()
        state_copy = copy.deepcopy(self.initial_state)
        for pred in state_copy.predicates:
            state_copy.predicates[pred] = random.choice([True, False])
        return LanguageSpace.state_to_language_description(state_copy)

class RobotouilleEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(self, domain_json, environment_json, renderer, layout, movement_mode, render_fps=60, time=pygame.time):        
        self.environment_json = environment_json
        self.initial_state = build_state(domain_json, environment_json, layout, movement_mode)
        self.current_state = copy.deepcopy(self.initial_state)

        self.gamemode = build_gamemode(environment_json, domain_json, self.initial_state, layout, movement_mode)

        language_space = LanguageSpace(initial_state=self.initial_state)
        self.observation_space = language_space
        self.action_space = language_space

        self.input_json = build_input_json(domain_json)

        self.renderer = renderer
        self.render_fps = render_fps
        self.clock = pygame.time.Clock()
        self.time = time

    def get_state(self):
        return self.observation_space
    
    def set_state(self, state):
        self.observation_space = state

    def step(self, actions):
        _, done = self.gamemode.step(actions, self.time, self.clock)
        self.current_state = copy.deepcopy(self.gamemode.state)
        obs = LanguageSpace.state_to_language_description(self.current_state)
        return obs, 0, done, {}

    def reset(self, seed=None, options=None):
        obs = LanguageSpace.state_to_language_description(self.initial_state)
        self.current_state = copy.deepcopy(self.initial_state)
        self.renderer.reset()
        return obs, {}
    
    def render(self, render_mode, close=False):
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        img = self.renderer.render(self.gamemode)
        if render_mode == "human":
            pygame.display.update()
            if close:
                self.renderer.reset()
                self.clock = None
                pygame.display.set_mode(size=(1,1), flags=pygame.HIDDEN) # Hide the window
            else:
                pygame.event.pump()
                self.clock.tick(self.render_fps)
        return img

        

