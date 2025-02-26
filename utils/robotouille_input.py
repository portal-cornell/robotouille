import pygame

def create_mousebutton_action(pygame_event, renderer, input_json, action_name_to_param_arg_dict):
    """This function attempts to create a valid action from the provided mouse click Pygame event.

    This function takes a mouse click and maps it to a valid action.

    Parameters:
        pygame_event (pygame.event.Event):
            The pygame mouse click event.
        renderer (RobotouilleRenderer):
            The renderer to extract the clicked station from.
        input_json (dict):
            The input JSON containing the mouse click actions.
        action_name_to_param_arg_dict (dict):
            The dictionary containing a mapping of action names to parameters and arguments.
    
    Returns:
        action_name (str):
            The name of the parametrized action to perform.
            Example: 'cook'
        param_arg_dict (dict):
            The dictionary containing a mapping of parameters to arguments for the action.
            Example: {'i1': patty1, 'p1': robot1, 's1': stove1}
    """
    # Get the station that was clicked
    pos_x, pos_y = pygame_event.pos
    grid_size = renderer.canvas.pix_square_size[0]
    layout_pos = int(pos_x / grid_size), int(pos_y / grid_size)
    clicked_station = renderer.canvas.layout[layout_pos[1]][layout_pos[0]]
    # Search for the action that corresponds to the clicked station
    for action_input in input_json["mouse_click_actions"]:
        action_name = action_input["name"]
        input_instructions = action_input["input_instructions"]
        param = input_instructions["click_on"]
        for args in action_name_to_param_arg_dict[action_name]:
            if args[param].name == clicked_station:
                return action_name, args
    return None, None

def create_keypress_action(pygame_event, player_loc, input_json, action_name_to_param_arg_dict):
    """This function attempts to create a valid action from the provided key press Pygame event.

    This function takes a key press and maps it to a valid action.

    Parameters:
        pygame_event (pygame.event.Event):
            The pygame key press event.
        player_loc (str):
            The location of the player.
        input_json (dict):
            The input JSON containing the key press actions.
        action_name_to_param_arg_dict (dict):
            The dictionary containing a mapping of action names to parameters and arguments.
    
    Returns:
        action_name (str):
            The name of the parametrized action to perform.
            Example: 'cook'
        param_arg_dict (dict):
            The dictionary containing a mapping of parameters to arguments for the action.
            Example: {'i1': patty1, 'p1': robot1, 's1': stove1}
    """
    key_pressed = pygame.key.name(pygame_event.key)
    for action_input in input_json["keyboard_actions"]:
        action_name = action_input["name"]
        input_instructions = action_input["input_instructions"]
        if key_pressed == input_instructions["key"]:
            # Return the only param_arg dict for actions like 'noop' where location is irrelevant
            if input_instructions["at"] is None:
                return action_name, action_name_to_param_arg_dict[action_name][0]
            # Return the param arg dict with the correct player location
            for param_arg_dict in action_name_to_param_arg_dict[action_name]:
                param = input_instructions["at"]
                if param_arg_dict[param].name == player_loc:
                    return action_name, param_arg_dict
    return None, None

def create_action_from_event(current_state, pygame_events, input_json, renderer):
    """This function attempts to create a valid action from the provided Pygame event.

    This function takes a combination of mouse clicks and key presses and maps it to a valid action.
    The controls are as follows:
        - Click to move the robot to a station.
        - Click at a station to pick up or place down an item.
        - Click at a station to unstack or stack an item.
        - Press 'e' at a station for interactions like cooking, frying, cutting, etc.

    Parameters:
        current_state (State):
            The current environment state.
        pygame_events (pygame.event.Event):
            The pygame keypress / mouse click events.
        input_json (dict):
            The input JSON containing the key press and mouse click actions.
        renderer (RobotouilleRenderer):
            The renderer to extract coordinates from.
    
    Returns:
        action: The parametrized action to perform.
        param_arg_dict: The dictionary containing a mapping of parameters to
            arguments for the action.
    
    Raises:
        AssertionError: If the Pygame event type is not supported.
    """
    if len(pygame_events) == 0: return None, None
    player = current_state.current_player
    action_to_param_arg_dict = current_state.get_valid_actions_for_player(player)
    # Convert actions to strings for easier comparison
    action_name_to_param_arg_dict = {str(action): action_to_param_arg_dict[action] for action in action_to_param_arg_dict}
    # Locate the player's current location loc(player, loc)
    for literal, is_true in current_state.predicates.items():
        if literal.name == "loc" and is_true and literal.params[0].name == player.name:
            player_loc = str(literal.params[1])
            break
    
    pygame_event = pygame_events[0] # Only consider the first event
    if pygame_event.type == pygame.MOUSEBUTTONDOWN:
        action_name, param_arg_dict = create_mousebutton_action(pygame_event, renderer, input_json, action_name_to_param_arg_dict)
    elif pygame_event.type == pygame.KEYDOWN:
        action_name, param_arg_dict = create_keypress_action(pygame_event, player_loc, input_json, action_name_to_param_arg_dict)
    else:
        assert False, f"create_action_from_event does not support {pygame_event.type} events."
    
    if action_name is None or param_arg_dict is None:
        return None, None
    
    # Convert the action name back to an Action object
    action = [action for action in action_to_param_arg_dict if str(action) == action_name][0]
    return action, param_arg_dict

                