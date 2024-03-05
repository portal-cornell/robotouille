import pygame

def create_action_from_control(env, obs, action, renderer):
    """
    This function attempts to create a valid action from the provided action.

    This function takes a mouse click and key press and transforms it into a valid action. 
    The controls are as follows:
        - Click to move the robot to a station.
        - Click at a station to pick up or place down an item.
        - Click at a station to unstack or stack an item.
        - Press 'e' at a station to begin cooking, frying, or cutting an item.
    
    Args:
        env: The environment.
        obs: The current observation.
        action: The action to transform.
        renderer: The renderer.
    
    Returns:
        action: The action to perform.
        params_args_dict: The dictionary containing the mapping of parameters to
            arguments for the action.
    """
    if len(action) == 0: return None, None
    valid_actions = obs.get_valid_actions()
    action_dict = {str(action): action for action in env.action_space}
    input_json = env.input_json
    param_objs = env.observation_space.param_objs
    action = action[0]
    for literal, is_true in obs.predicates.items():
        if literal.name == "loc" and is_true:
            player_loc = str(literal.params[1])
    if action.type == pygame.MOUSEBUTTONDOWN:
        pos_x, pos_y = action.pos
        grid_size = renderer.canvas.pix_square_size[0]
        layout_pos = int(pos_x / grid_size), int(pos_y / grid_size)
        clicked_station = renderer.canvas.layout[layout_pos[1]][layout_pos[0]]
        for action_input in input_json["mouse_click_actions"]:
            action_name = action_input["name"]
            input_instructions = action_input["input_instructions"]
            param_obj = param_objs[input_instructions["click_on"]]
            for args in valid_actions[action_dict[action_name]]:
                if args[param_obj].name == clicked_station:
                    return action_dict[action_name], args
        return None, None
    elif action.type == pygame.KEYDOWN:
        key_pressed = pygame.key.name(action.key)
        for action_input in input_json["keyboard_actions"]:
            action_name = action_input["name"]
            input_instructions = action_input["input_instructions"]
            if key_pressed == input_instructions["key"]:
                if not input_instructions["at"]:
                    for args in valid_actions[action_dict[action_name]]:
                        return action_dict[action_name], args
                for args in valid_actions[action_dict[action_name]]:
                    param_obj = param_objs[input_instructions["at"]]
                    if args[param_obj].name == player_loc:
                        return action_dict[action_name], args
        return None, None
                