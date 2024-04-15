import pygame

def create_action_from_control(env, obs, player, action, renderer):
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
        player: The player to control.
        action: The action to transform.
        renderer: The renderer.
    
    Returns:
        action: The action to perform.
        param_arg_dict: The dictionary containing the mapping of parameters to
            arguments for the action.
    """
    if len(action) == 0: return None, None
    valid_actions = obs.get_valid_actions_for_player(player)
    action_dict = {str(action): action for action in env.action_space}
    input_json = env.input_json
    action = action[0]
    for literal, is_true in obs.predicates.items():
        if literal.name == "loc" and is_true and literal.params[0].name == player.name:
            player_loc = str(literal.params[1])
    if action.type == pygame.MOUSEBUTTONDOWN:
        pos_x, pos_y = action.pos
        grid_size = renderer.canvas.pix_square_size[0]
        layout_pos = int(pos_x / grid_size), int(pos_y / grid_size)
        clicked_station = renderer.canvas.layout[layout_pos[1]][layout_pos[0]]
        for action_input in input_json["mouse_click_actions"]:
            action_name = action_input["name"]
            input_instructions = action_input["input_instructions"]
            param = input_instructions["click_on"]
            for args in valid_actions[action_dict[action_name]]:
                if args[param].name == clicked_station:
                    return action_dict[action_name], args
        return None, None
    elif action.type == pygame.KEYDOWN:
        key_pressed = pygame.key.name(action.key)
        for action_input in input_json["keyboard_actions"]:
            action_name = action_input["name"]
            input_instructions = action_input["input_instructions"]
            if key_pressed == input_instructions["key"]:
                if not input_instructions["at"]:
                    return action_dict[action_name], valid_actions[action_dict[action_name]][0]
                for args in valid_actions[action_dict[action_name]]:
                    param = input_instructions["at"]
                    if args[param].name == player_loc:
                        return action_dict[action_name], args
        return None, None
                