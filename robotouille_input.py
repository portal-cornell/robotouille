import pygame

def create_action_from_control(env, obs, action, renderer):
    """
    This function attempts to create a valid action from the provided action.

    This function takes a mouse click and key press and transforms it into a valid action. 
    The controls are as follows:
        - Click to move the robot to a station.
        - Click at a station to pick up or place down an item.
        - Click at a station to unstack or stack an item.
        - Press 'e' at a station to begin cooking or to cut an item.
    
    Args:
        env: The environment.
        obs: The current observation.
        action: The action to transform.
        renderer: The renderer.
    
    Returns:
        A valid action.
    """
    if len(action) == 0: return "noop"
    valid_actions = list(env.action_space.all_ground_literals(obs))
    str_valid_actions = list(map(str, valid_actions))
    action = action[0]
    if action.type == pygame.MOUSEBUTTONDOWN:
        pos_x, pos_y = action.pos
        grid_size = renderer.canvas.pix_square_size[0]
        layout_pos = int(pos_x / grid_size), int(pos_y / grid_size)
        clicked_station = renderer.canvas.layout[layout_pos[1]][layout_pos[0]]
        loc_tuples = [str_valid_action.split(",") for str_valid_action in str_valid_actions]
        locs = [loc_tuple[2].split(":")[0] if 'station' in loc_tuple[2] else loc_tuple[3].split(":")[0] for loc_tuple in loc_tuples]
        if clicked_station in locs:
            index = locs.index(clicked_station)
            while 'cook' in str_valid_actions[index] or 'cut' in str_valid_actions[index]:
                index = locs.index(clicked_station, index+1)
            return str_valid_actions[index]
    elif action.type == pygame.KEYDOWN:
        if action.key == pygame.K_e:
            literal_names = [str_valid_action.split("(")[0] for str_valid_action in str_valid_actions]
            if 'cook' in literal_names:
                index = literal_names.index('cook')
                return str_valid_actions[index]
            elif 'cut' in literal_names:
                index = literal_names.index('cut')
                return str_valid_actions[index]
    return "noop"