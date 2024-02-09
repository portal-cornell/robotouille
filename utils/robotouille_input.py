import pygame
from robotouille.env import ACTIONS
from pddlgym.backend.object import Object

i1 = Object("i1", "item")
i2 = Object("i2", "item")
s1 = Object("s1", "station")
s2 = Object("s2", "station")
p1 = Object("p1", "player")

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
        A valid action.
    """
    if len(action) == 0: return None, None
    valid_actions = (obs.get_valid_actions())
    action = action[0]
    # print(valid_actions)
    for predicate, value in obs.predicates.items():
        if predicate.name == "loc" and value:
            player_loc = str(predicate.params[1])
    if action.type == pygame.MOUSEBUTTONDOWN:
        pos_x, pos_y = action.pos
        grid_size = renderer.canvas.pix_square_size[0]
        layout_pos = int(pos_x / grid_size), int(pos_y / grid_size)
        clicked_station = renderer.canvas.layout[layout_pos[1]][layout_pos[0]]
        for args in valid_actions[ACTIONS[0]]:
            if args[s2].name == clicked_station:
                return ACTIONS[0], args
        for args in valid_actions[ACTIONS[1]]:
            if args[s1].name == clicked_station:
                return ACTIONS[1], args
        for args in valid_actions[ACTIONS[2]]:
            if args[s1].name == clicked_station:
                return ACTIONS[2], args
        for args in valid_actions[ACTIONS[6]]:
            if args[s1].name == clicked_station:
                return ACTIONS[6], args
        for args in valid_actions[ACTIONS[7]]:
            if args[s1].name == clicked_station:
                return ACTIONS[7], args
        return None, None
    elif action.type == pygame.KEYDOWN:
        if action.key == pygame.K_e:
            for args in valid_actions[ACTIONS[3]]:
                if args[s1].name == player_loc:
                    return ACTIONS[3], args
            for args in valid_actions[ACTIONS[4]]:
                if args[s1].name == player_loc:
                    return ACTIONS[4], args  
            for args in valid_actions[ACTIONS[5]]:
                if args[s1].name == player_loc:
                    return ACTIONS[5], args
        return None, None
                