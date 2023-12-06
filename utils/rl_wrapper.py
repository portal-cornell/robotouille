from typing import List, Optional, Union
import gym
import pddlgym
import utils.robotouille_utils as robotouille_utils
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_wrapper as robotouille_wrapper


class RLWrapper(robotouille_wrapper.RobotouilleWrapper):
    def __init__(self, env, config):
        super().__init__(env, config)

        self.pddl_env = env
        self.env = None

    def _state_update(self):
        return super()._state_update()

    def _handle_action(self, action):
        return super()._handle_action(action)

    def _wrap_env(self):
        expanded_truths, expanded_states = pddlgym_utils.expand_state(
            self.prev_step[0].literals, self.prev_step[0].objects
        )
        # Box(low=0.0, high=1.0, shape=expanded_truths.shape)
        self.env = expanded_truths

    def step(self, action=None, interactive=False):
        return super().step(action, interactive)

    def reset(self):
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
        return obs, info

    def render(self, *args, **kwargs):
        self.pddl_env.render()
