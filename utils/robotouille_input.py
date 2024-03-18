import pygame

from utils.robotouille_utils import get_valid_moves


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
    if len(action) == 0:
        return

    valid_actions = get_valid_moves(env, obs, renderer)
    str_valid_actions = list(map(str, valid_actions))
    action = action[0]
    if action.type == pygame.MOUSEBUTTONDOWN:
        pos_x, pos_y = action.pos
        grid_size = renderer.canvas.pix_square_size[0]
        layout_pos = int(pos_x / grid_size), int(pos_y / grid_size)
        clicked_station = renderer.canvas.layout[layout_pos[1]][layout_pos[0]]
        loc_tuples = [
            str_valid_action.split(",") for str_valid_action in str_valid_actions
        ]

        locs = [
            (
                []
                if len(loc_tuple) == 2
                else (
                    loc_tuple[2].split(":")[0]
                    if "station" in loc_tuple[2]
                    else loc_tuple[3].split(":")[0]
                )
            )
            for loc_tuple in loc_tuples
        ]
        if clicked_station in locs:
            index = locs.index(clicked_station)
            while (
                "cook(" in str_valid_actions[index]
                or "cut(" in str_valid_actions[index]
                or "fry(" in str_valid_actions[index]
                or "fry_cut_item(" in str_valid_actions[index]
            ):
                # We look for fry( instead which should be guaranteed to only match the fry action, and not the fryer
                try:
                    index = locs.index(clicked_station, index + 1)
                except ValueError:
                    return None
            return str_valid_actions[index]
    elif action.type == pygame.KEYDOWN:
        if action.key == pygame.K_e:
            literal_names = [
                str_valid_action.split("(")[0] for str_valid_action in str_valid_actions
            ]
            if "cook" in literal_names:
                index = literal_names.index("cook")
                return str_valid_actions[index]
            elif "cut" in literal_names:
                index = literal_names.index("cut")
                return str_valid_actions[index]
            elif "fry" in literal_names:
                index = literal_names.index("fry")
                return str_valid_actions[index]
            elif "fry_cut_item" in literal_names:
                index = literal_names.index("fry_cut_item")
                return str_valid_actions[index]
        elif action.key == pygame.K_SPACE:
            return "noop"
