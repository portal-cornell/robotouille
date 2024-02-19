import pygame
from robotouille.build_domain import s1, s2

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
    action = action[0]
    for literal, is_true in obs.predicates.items():
        if literal.name == "loc" and is_true:
            player_loc = str(literal.params[1])
    if action.type == pygame.MOUSEBUTTONDOWN:
        pos_x, pos_y = action.pos
        grid_size = renderer.canvas.pix_square_size[0]
        layout_pos = int(pos_x / grid_size), int(pos_y / grid_size)
        clicked_station = renderer.canvas.layout[layout_pos[1]][layout_pos[0]]
        for args in valid_actions[action_dict['move']]:
            if args[s2].name == clicked_station:
                return action_dict['move'], args
        for args in valid_actions[action_dict['pick-up']]:
            if args[s1].name == clicked_station:
                return action_dict['pick-up'], args
        for args in valid_actions[action_dict['place']]:
            if args[s1].name == clicked_station:
                return action_dict['place'], args
        for args in valid_actions[action_dict['stack']]:
            if args[s1].name == clicked_station:
                return action_dict['stack'], args
        for args in valid_actions[action_dict['unstack']]:
            if args[s1].name == clicked_station:
                return action_dict['unstack'], args
        return None, None
    elif action.type == pygame.KEYDOWN:
        if action.key == pygame.K_e:
            for args in valid_actions[action_dict['cook']]:
                if args[s1].name == player_loc:
                    return action_dict['cook'], args
            for args in valid_actions[action_dict['cut']]:
                if args[s1].name == player_loc:
                    return action_dict['cut'], args  
            for args in valid_actions[action_dict['fry']]:
                if args[s1].name == player_loc:
                    return action_dict['fry'], args
        elif action.key == pygame.K_SPACE:
            for args in valid_actions[action_dict['wait']]:
                return action_dict['wait'], args
        return None, None
                