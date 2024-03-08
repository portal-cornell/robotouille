def _handle_moving_reward(self, action, obs):
    """
    This function handles the reward for the moving action. It currently rewards the agent for moving to the correct location with the correct item (patty to grill, lettuce to board)
    """

    # Check if an item is being held
    reward = 0
    holding = False
    literals = obs.literals
    for literal in literals:
        if "has" in literal.predicate.name:
            item_name = literal.variables[1].name
            holding = True

    if not holding:
        return 0

    destination = action.variables[2]

    item_status = self.state.get(destination.name)

    # See if lettuce is going to board or patty is going to stove. If it is, return 10 reward
    if ("lettuce" in item_name and "board" in destination.name) or (
        "patty" in item_name and "stove" in destination.name
    ):
        if item_status is None:
            self.state[destination.name] = {"visited": True}
            return 10
        elif item_status.get("visited") is None:
            item_status["visited"] = True
            return 10
        elif item_status.get("visited") is False:
            item_status["visited"] = True
            return 10

    return 0


def _handle_stacking_reward(self, action):
    # Check that no incorrect stacking occured
    items = ["patty1", "lettuce1", "topbun1"]
    correct_order = [
        "atop(patty1:item,bottombun1:item)",
        "atop(lettuce1:item,patty1:item)",
        "atop(topbun1:item,lettuce1:item)",
    ]

    expanded_truths = self.prev_step[3]["expanded_truths"]
    expanded_states = self.prev_step[3]["expanded_states"]
    reward = 0

    # Penalize for anyt stacking that is not in the correct order
    for truth, state in zip(expanded_truths, expanded_states):
        if (
            truth == 1
            and "atop" == state.predicate
            and action.variables[1].name == state.variables[0].name
            and str(state) not in correct_order
        ):
            reward -= 0

    state_truth_map = self.map_state_to_truth(expanded_truths, expanded_states)

    valid_stacking = True
    # Go through every item and check if it is stacked correctly
    for stack, item in zip(correct_order, items):
        if state_truth_map[stack]:
            if action.variables[1].name == item:
                item_status = self.state.get(item)
                if item_status is None:
                    self.state[item.name] = {"stacked": False}
                elif item_status.get("stacked") is None:
                    item_status["stacked"] = False

                if not item_status["stacked"]:
                    # Check if patty is cooked or lettuce is cut if stacking is correct
                    if valid_stacking:
                        if (
                            item == "patty1"
                            and not state_truth_map[f"iscooked({item}:item)"]
                        ) or (
                            item == "lettuce1"
                            and not state_truth_map[f"iscut({item}:item)"]
                        ):
                            reward -= 0
                        else:
                            reward += 10
                            item_status["stacked"] = True
                    else:
                        reward -= 0

        else:
            valid_stacking = False

    return reward


def _top_bun_left(self):
    """
    Return True if only the top bun is left, False otherwise.
    """
    correct_order = [
        "atop(patty1:item,bottombun1:item)",
        "atop(lettuce1:item,patty1:item)",
    ]

    expanded_truths = self.prev_step[3]["expanded_truths"]
    expanded_states = self.prev_step[3]["expanded_states"]
    state_truth_map = self.map_state_to_truth(expanded_truths, expanded_states)

    return all([state_truth_map[stack] for stack in correct_order])


def _handle_reward(self, action, obs):
    reward = 0
    action_name = action.predicate.name

    # Reward/Penalty for cutting
    if action_name == "move":
        reward += self._handle_moving_reward(action, obs)
    if action_name == "cut":
        item = next(
            filter(
                lambda typed_entity: typed_entity.var_type == "item",
                action.variables,
            ),
            None,
        )
        if item:
            item_name, _ = robotouille_utils.trim_item_ID(item.name)
            num_cuts = self.config["num_cuts"]
            max_num_cuts = num_cuts.get(item_name, num_cuts["default"])

            item_status = self.state.get(item.name, {})
            num_cuts = item_status.get("cut", 0)

            reward += 10 if num_cuts <= max_num_cuts else 0
    # Reward/Penalty for cooking and frying
    elif action_name in ["cook", "fry"]:
        item = next(
            filter(
                lambda typed_entity: typed_entity.var_type == "item",
                action.variables,
            ),
            None,
        )
        if item:
            item_status = self.state.get(item.name, {})
            if action_name == "fry":
                num_fries = item_status.get("fry", {}).get("fry_time", 0)
                reward += 10 if num_fries < 1 else 0
            elif action_name == "cook":
                cook_time = item_status.get("cook", {}).get("cook_time", 0)
                reward += 10 if cook_time < 1 else 0
    elif action_name == "pick-up":
        item = next(
            filter(
                lambda typed_entity: typed_entity.var_type == "item",
                action.variables,
            ),
            None,
        )
        item_status = self.state.get(item.name, {})
        # Check if the picked up item was a cooking patty.
        if item_status is not None and item_status.get("cook") is not None:
            if (
                item_status["cook"]["cook_time"] > 0
                and "iscooked(" + item.name not in self.prev_step[0]
            ):
                literals = obs.literals

                cooked = False
                for literal in literals:
                    if "iscooked" == literal.predicate.name:
                        cooked = True

                if not cooked:
                    reward -= 10

        # Give a reward for picking up items other than the bottombun in hopes of it learning to stack better
        if not "bottombun" in item.name:
            item_status = self.state.get(item.name)
            if item_status is None:
                self.state[item.name] = {"picked-up": False}
                item_status = self.state.get(item.name)
            elif item_status.get("picked-up") is None:
                item_status["picked-up"] = False

            if item_status.get("picked-up") is False:
                if "topbun" in item.name:
                    if self._top_bun_left():
                        reward += 10
                        item_status["picked-up"] = True
                else:
                    reward += 10
                    item_status["picked-up"] = True
    elif action_name == "place":
        item = action.variables[1].name
        destination = action.variables[2].name
        literals = obs.literals

        item_status = self.state.get(item)

        # Initialize item status if it doesn't exist
        if item_status is None:
            self.state[item] = {"placed": False}
        elif item_status.get("placed") is None:
            item_status["placed"] = False

        # Give a reward for placing a lettuce on the board or a patty on the stove
        if "lettuce" in item and "board" in destination and not item_status["placed"]:
            cut = False
            for literal in literals:
                if "iscut" == literal.predicate.name:
                    cut = True
            if not cut:
                item_status["placed"] = True
                reward += 10
        elif "patty" in item and "stove" in destination and not item_status["placed"]:
            cooked = False
            for literal in literals:
                if "iscooked" == literal.predicate.name:
                    cooked = True
            if not cooked:
                item_status["placed"] = True
                reward += 10
        else:
            reward -= 20
    elif action_name == "stack":
        reward += self._handle_stacking_reward(action)

    # Reward for continuous cooking
    for item, status_dict in self.state.items():
        for status, state in status_dict.items():
            if status == "cook":
                item_name, _ = robotouille_utils.trim_item_ID(item)
                cook_time = self.config["cook_time"]
                max_cook_time = cook_time.get(item_name, cook_time["default"])
                if state["cooking"] and state["cook_time"] <= max_cook_time:
                    reward += 1
                elif state["cooking"] and state["cook_time"] > max_cook_time:
                    reward -= 0

    return reward


def map_state_to_truth(self, expanded_truths, expanded_states):
    if expanded_truths is None or len(expanded_truths) != len(expanded_states):
        print("Error: Mismatch in lengths or None input")  # Debugging
        return {}
    return {str(expanded_states[i]): truth for i, truth in enumerate(expanded_truths)}
