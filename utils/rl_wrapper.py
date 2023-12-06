import gym
import pddlgym
import utils.robotouille_utils as robotouille_utils
import utils.pddlgym_utils as pddlgym_utils
import utils.robotouille_wrapper as robotouille_wrapper


class RLWrapper(robotouille_wrapper.RobotouilleWrapper):
    def __init__(self, env, config):
        super().__init__(env, config)

        self.pddl_env = env

        expanded_truths, expanded_states = pddlgym_utils.expand_state(
            self.pddl_env.prev_step[0].literals, self.prev_step[0].objects
        )

        self.env = expanded_truths

    def _state_update(self):
        return super()._state_update()

    def _handle_action(self, action):
        return super()._handle_action(action)

    def step(self, action=None, interactive=False):
        # TODO: step given action
        pass
