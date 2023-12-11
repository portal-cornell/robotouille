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
        self.max_steps = 20

    def _wrap_env(self):
        expanded_truths, expanded_states = pddlgym_utils.expand_state(
            self.pddl_env.prev_step[0].literals, self.pddl_env.prev_step[0].objects
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

    def step(self, action=None, interactive=False, print_action=False):
        action = self.env.unwrap_move(action)
        if print_action:
            print(action)
        obs, reward, done, info = self.pddl_env.step(action, interactive)
        self._wrap_env()
        return (
            self.env.state,
            reward,
            done,
            self.pddl_env.timesteps > self.max_steps,
            info,
        )

    def reset(self, seed=42, options=None):
        obs, info = self.pddl_env.reset()
        self._wrap_env()
        return self.env.state, info

    def render(self, *args, **kwargs):
        self.pddl_env.render()
