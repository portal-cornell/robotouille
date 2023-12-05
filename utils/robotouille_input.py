import pygame


def get_station_move(loc_tuples, clicked_station, str_valid_actions):
    locs = [
        ""
        if "select" in loc_tuple[0]
        else loc_tuple[2].split(":")[0]
        if "station" in loc_tuple[2]
        else loc_tuple[3].split(":")[0]
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
            index = locs.index(clicked_station, index + 1)
        return str_valid_actions[index]


def get_select_player_move(players_pose, layout_pos, str_valid_actions):
    """
    Identifies if a user clicks on a robot to change selection
    """
    for str_valid_action in str_valid_actions:
        if "select" not in str_valid_action:
            continue

        player = str_valid_action.split(",")[1].split(":")[0]
        player_index = int(player[5:]) - 1
        if (
            players_pose[player_index]["position"][0] == layout_pos[0]
            and players_pose[player_index]["position"][1] == layout_pos[1]
        ):
            return str_valid_action

    return "noop"


def change_selected_player(env, obs, renderer):
    valid_actions = list(env.action_space.all_ground_literals(obs))
    str_valid_actions = list(map(str, valid_actions))

    current_selected_player = -1

    for literal in obs.literals:
        if literal.predicate == "selected":
            current_selected_player = int(literal.variables[0].name[5:])

    next_selected_player = (
        current_selected_player % len(renderer.canvas.players_pose) + 1
    )

    for str_valid_action in str_valid_actions:
        if "select" not in str_valid_action:
            continue

        if (
            str(next_selected_player) in str_valid_action
            and str(current_selected_player) in str_valid_action
        ):
            return str_valid_action


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
    valid_actions = list(env.action_space.all_ground_literals(obs))
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
        if clicked_station != None:
            return get_station_move(loc_tuples, clicked_station, str_valid_actions)
        else:
            return get_select_player_move(
                renderer.canvas.players_pose, layout_pos, str_valid_actions
            )

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
