import gym
import pddlgym
import overcooked_utils
import pddlgym_utils

class OvercookedWrapper(gym.Wrapper):
    def __init__(self, env):
        super(OvercookedWrapper, self).__init__(env)
        self.env = env
        self.prev_step = None
        self.timesteps = 0
        self.state = {}

    def _interactive_starter_prints(self, expanded_truths):
        print('\n' * 10)
        if self.timesteps % 10 == 0:
            print(f"You have made {self.timesteps} steps.")
        overcooked_utils.print_states(self.prev_step[0])
        print('\n')
        overcooked_utils.print_actions(self.env, self.prev_step[0])
        print(f"True Predicates: {expanded_truths.sum()}")
    
    def _state_update(self):
        state_updates = []
        for item, status_dict in self.state.items():
            for status, state in status_dict.items():
                if status == "cut":
                    if state >= 3:
                        literal = pddlgym_utils.str_to_literal(f"iscut({item}:item)")
                        state_updates.append(literal)
                elif status == "cook":
                    if state["cooking"]:
                        state["cook_time"] += 1
                    if state["cook_time"] >= 3:
                        literal = pddlgym_utils.str_to_literal(f"iscooked({item}:item)")
                        state_updates.append(literal)
        env_state = self.env.get_state()
        new_literals = env_state.literals.union(state_updates)
        new_env_state = pddlgym.structs.State(new_literals, env_state.objects, env_state.goal)
        self.env.set_state(new_env_state)
        return new_env_state

    def _handle_action(self, action):
        if action == "noop": return self.prev_step
        action_name = action.predicate.name
        if action_name == "cut":
            item = next(filter(lambda typed_entity: typed_entity.var_type == "item", action.variables))
            item_status = self.state.get(item.name)
            if item_status is None:
                self.state[item.name] = {"cut": 1}
            elif item_status.get("cut") is None:
                item_status["cut"] = 1
            else:
                item_status["cut"] += 1
            return self.prev_step
        elif action_name == "cook":
            item = next(filter(lambda typed_entity: typed_entity.var_type == "item", action.variables))
            item_status = self.state.get(item.name)
            if item_status is None:
                self.state[item.name] = {"cook": {"cook_time": -1, "cooking": True}}
            elif item_status.get("cook") is None:
                item_status["cook"] = {"cook_time": -1, "cooking": True}
            else:
                item_status["cook"]["cooking"] = True
            return self.prev_step
        elif action_name == "pick-up":
            item = next(filter(lambda typed_entity: typed_entity.var_type == "item", action.variables))
            item_status = self.state.get(item.name)
            if item_status is not None and item_status.get("cook") is not None:
                item_status["cook"]["cooking"] = False
        # TODO: Probably stop cooking if something is stacked on top of meat
        return self.env.step(action)
        
    def step(self, action=None, interactive=False):
        expanded_truths, expanded_states = pddlgym_utils.expand_state(self.prev_step[0].literals, self.prev_step[0].objects)
        if interactive:
            self._interactive_starter_prints(expanded_truths)
            action = overcooked_utils.create_action_repl(self.env, self.prev_step[0])
        else:
            action = overcooked_utils.create_action(self.env, self.prev_step[0], action)
        obs, reward, done, _ = self._handle_action(action)
        obs = self._state_update()
        toggle_array = pddlgym_utils.create_toggle_array(expanded_truths, expanded_states, obs.literals)
        if interactive:
            print(f"Predicates Changed: {toggle_array.sum()}")
        info = {
            'timesteps': self.timesteps, 
            "expanded_truths": expanded_truths, 
            "expanded_states": expanded_states, 
            "toggle_array": toggle_array,
            "state": self.state
        }
        self.prev_step = (obs, reward, done, info)
        self.timesteps += 1
        return obs, reward, done, info
        
    def reset(self):
        obs, _ = self.env.reset()
        info = {
            'timesteps': self.timesteps, 
            "expanded_truths": None, 
            "expanded_states": None, 
            "toggle_array": None,
            "state": {}
        }
        self.prev_step = (obs, 0, False, info)
        self.timesteps = 0
        self.state = {}
        return obs, info