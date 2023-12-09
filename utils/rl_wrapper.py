from typing import List, Optional, Union
import gym
import pddlgym
import utils.robotouille_utils as robotouille_utils
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_wrapper as robotouille_wrapper
from utils.rl_env import RLEnv


class RLWrapper(robotouille_wrapper.RobotouilleWrapper):
    def __init__(self, env, config):
        super().__init__(env, config)

        self.pddl_env = env
        self.env = None

    def _wrap_env(self):
        expanded_truths, expanded_states = pddlgym_utils.expand_state(
            self.prev_step[0].literals, self.prev_step[0].objects
        )

        valid_actions = list(
            self.pddl_env.action_space.all_ground_literals(self.pddl_env.prev_step[0])
        )

        all_actions = list(
            self.pddl_env.action_space.all_ground_literals(
                self.pddl_env.prev_step[0], valid_only=False
            )
        )

        self.env = RLEnv(expanded_truths, valid_actions, all_actions)

    def step(self, action=None, interactive=False):
        action = str(self.env.unwrap_move(action))
        obs, reward, done, info = self.pddl_env.step(action, interactive)
        self._wrap_env()
        return self.env.state, reward, done, False, info

    def reset(self, seed=42, options=None):
        obs, _ = self.pddl_env.reset()
        info = {
            "timesteps": self.timesteps,
            "expanded_truths": None,
            "expanded_states": None,
            "toggle_array": None,
            "state": {},
        }
        self.prev_step = (obs, 0, False, info)
        self.timesteps = 0
        self.state = {}

        self._wrap_env()
        return self.env.state, info

    def render(self, *args, **kwargs):
        self.pddl_env.render()
