import random
import itertools

from .object_enums import Item, Station
from copy import deepcopy

FORCE_ADD_TAG_NAME = "force_add"
FROZEN_TAG_NAME = "frozen"
STATION_WILDCARD = "station"
ITEM_WILDCARD = "item"
PLAYER_WILDCARD = "player"

def _generate_random_objects(width, height):
    """
    Generate and return a list of objects (stations, items and players) and
    their positions to add to the environment.

    As many as (width * height) stations may be generated while as many as 
    (number of stations generated) items can be generated.

    Args:
        width (int): The width of the environment.
        height (int): The height of the environment.

    Returns:
        stations (list): A list of stations to add to the environment.
        items (list): A list of items to add to the environment.
        containers (list): A list of containers to add to the environment.
        players (list): A list of players to add to the environment.
    """
    num_stations = random.randrange(0, width * height)    
    stations = [{"name": STATION_WILDCARD, "x": random.randrange(0, width), "y": random.randrange(0, height)} for _ in range(num_stations)]
    stations = _apply_lambdas(stations, [_update_station_name])
    
    num_items = random.randrange(0, num_stations+1)
    items = [{"name": ITEM_WILDCARD, "x": random.choice(stations)["x"], "y": random.choice(stations)["y"], "stack-level": 0} for _ in range(num_items)]
    items = _apply_lambdas(items, [_update_item_name])
    
    containers = [] # No new containers should be added to the environment to maximize items
    players = [] # Players count should be determined within the environment JSON

    return stations, items, containers, players

def _build_station_layout(grid_size, stations):
    """
    Returns a 2D layout of the environment's stations

    The layout is a 2D list of either booleans or visited dictionaries. If
    a cell has no station its value is False. Otherwise, the value is a
    dictonary with a "reachable" key.

    Args:
        grid_size (tuple): The size of the environment's grid.
        stations (list): A list of stations to add to the environment.
    
    Returns:
        layout (list): A 2D list of the environment.
    """
    width, height = grid_size
    layout = [[False for _ in range(width)] for _ in range(height)]
    for station in stations:
        x, y = station["x"], height - station["y"] - 1 # Origin is in the bottom left corner
        layout[y][x] = {"reachable": False}
    return layout

def _find_empty_cell(layout):
    """
    Returns the first empty cell's position found in the layout.

    Args:
        layout (list): A 2D list of the environment.
    
    Returns:
        position (tuple): The (x,y) position of the first empty cell found (or None if none)
    """
    for y in range(len(layout)):
        for x in range(len(layout[y])):
            if layout[y][x] == False:
                return (x, y)

def _reset_reachable_stations(layout):
    """
    Resets the "reachable" key of all stations in the layout to False.

    Args:
        layout (list): A 2D list of the environment.
    
    Side effects:
        - The layout is modified to reset the "reachable" key of all stations to False.
    """
    for row in layout:
        for cell in row:
            if type(cell) == dict:
                cell["reachable"] = False

def _get_reachable_station_count(layout, start_cell):
    """
    Returns the number of reachable stations from the start cell.
    
    Performs an iterative breadth-first search on the layout. If a cell is 
    visited, it is set from False to True. If one of the cells visited is a 
    station, the station's "reachable" key is set to True and the number of
    reachable stations is incremented.

    Args:
        layout (list): A 2D list of the environment.
        start_cell (tuple): The (x,y) cell to start the search from.
    
    Side effects:
        - The layout is modified to mark visited cells as True
    
    Returns:
        reachable_stations (int): The number of reachable stations.
    """
    width, height = len(layout[0]), len(layout)
    queue = [start_cell]
    reachable_stations = 0
    while queue:
        cell = queue.pop(0)
        x, y = cell
        if x < 0 or x >= width or y < 0 or y >= height:
            # Out of bounds!
            continue
        elif layout[y][x] == False:
            # Unvisited cell!
            layout[y][x] = True # Mark the cell as visited
            queue.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
        elif type(layout[y][x]) == dict and layout[y][x].get("reachable") == False:
            # Unvisited station!
            layout[y][x]["reachable"] = True
            reachable_stations += 1
    _reset_reachable_stations(layout) # Undo reachable flag side effects
    return reachable_stations

def _are_stations_reachable(environment_json):
    """
    Returns whether or not the stations are reachable from at least one empty space.

    This function generates a layout of the current environment which it uses to
    determine whether stations are reachable. If the environment_json contains any
    players, this function will return True if the player can reach all of the stations
    from their current cell. If the environment_json doesn't contain any players, then
    as long as there is at least one empty cell in the environment that can reach all
    of the stations, this function will return True.

    Args:
        environment_json (dict): The environment JSON to check.

    Returns:
        reachable (bool): Whether or not the stations are reachable.
    """
    width, height = environment_json["width"], environment_json["height"]
    stations = environment_json["stations"]
    layout = _build_station_layout((width, height), stations)
    players = environment_json["players"]
    if players:
        # Check if the player can reach all stations from their current cell
        player = players[0] # Assumption of one player
        player_pos = (player["x"], height - player["y"] - 1)
        num_reachable_stations = _get_reachable_station_count(layout, player_pos)
        if num_reachable_stations == len(stations):
            return True
    else:
        # No players found in environment
        empty_cell_pos = _find_empty_cell(layout)
        while empty_cell_pos is not None:
            num_reachable_stations = _get_reachable_station_count(layout, empty_cell_pos) # Side effects
            if num_reachable_stations == len(stations):
                return True
            empty_cell_pos = _find_empty_cell(layout)
    return False

def _randomly_add_stations(environment_json, stations, players):
    """
    Returns an environment JSON with randomly placed stations in the environment.

    This function will attempt to add stations into the environment until
    there are no more stations to add. An attempt may fail if the station's
    location conflicts with anothers or causes other stations to be unreachable.
    
    If a station has a FORCE_ADD tag, then it will eventually be added to the
    environment. If its location conflicts with another station, then it will
    replace the station. If it causes other stations to be unreachable, then
    a replaceable station will be chosen to be replaced with the FORCE_ADD
    station.

    If a station is being placed in the location of a player that has a FROZEN tag,
    then the location will be repicked.

    Args:
        environment_json (dict): The environment JSON to add stations to.
        stations (list): A list of stations to attempt adding to the environment.
        players (list): A list of players in the environment.
    
    Returns:
        updated_environment_json (dict): The updated environment JSON with the randomly added stations.
    """
    updated_environment_json = deepcopy(environment_json)
    player = list(filter(lambda player: player.get(FROZEN_TAG_NAME), players))
    for station in stations:
        position_conflict = lambda other: other["x"] == station["x"] and other["y"] == station["y"]
        conflicting_candidate = list(filter(position_conflict, updated_environment_json["stations"] + player)) # Empty or one element
        if station.get(FORCE_ADD_TAG_NAME):
            force_added = False # Flag to check if the station has been force added
            if conflicting_candidate and not conflicting_candidate[0].get(FORCE_ADD_TAG_NAME):
                # Replace conflicting station if not a FORCE_ADD station
                conflicting_station_index = updated_environment_json["stations"].index(conflicting_candidate[0])
                station["x"], station["y"] = conflicting_candidate[0]["x"], conflicting_candidate[0]["y"]
                updated_environment_json["stations"][conflicting_station_index] = station
                force_added = True
                # print(f"Replacement: {station['name']} at ({station['x']}, {station['y']})")
            elif not conflicting_candidate:
                environment_json_copy = deepcopy(updated_environment_json)
                environment_json_copy["stations"].append(station)
                reachable = _are_stations_reachable(environment_json_copy)
                if reachable:
                    # All stations are reachable
                    updated_environment_json["stations"].append(station)
                    force_added = True
                    # print(f"Added FORCE_ADD station {station['name']} at ({station['x']}, {station['y']})")
            
            if not force_added:
                # Force add failed, so try to replace a station
                replaceable_stations = list(filter(lambda s: s.get(FORCE_ADD_TAG_NAME) is None, updated_environment_json["stations"]))
                assert replaceable_stations, "No replaceable stations found"
                replaceable_station = random.choice(replaceable_stations)
                replaceable_station_idx = updated_environment_json["stations"].index(replaceable_station)
                station["x"], station["y"] = replaceable_station["x"], replaceable_station["y"]
                updated_environment_json["stations"][replaceable_station_idx] = station
                # print(f"Fail replacement: {station['name']} at ({station['x']}, {station['y']})")
        elif not conflicting_candidate:
            # Station does not occupy the same position as another station
            environment_json_copy = deepcopy(updated_environment_json)
            environment_json_copy["stations"].append(station)
            environment_json_copy['players'] = players # Consider frozen players' future positions
            reachable = _are_stations_reachable(environment_json_copy)
            if reachable:
                # All stations are reachable
                updated_environment_json["stations"].append(station)
                # print(f"Added station {station['name']} at ({station['x']}, {station['y']})")
    return updated_environment_json

def _randomly_add_items(environment_json, items):
    """
    Returns an environment JSON with randomly placed items in the environment.

    This function will attempt to add items into the environment until
    there are no more items to add. An attempt may fail if the item's
    location conflicts with anothers. It'll also fail if the item's location
    is not on a station or player.

    If a item has a FORCE_ADD tag, then it will eventually be added to the
    environment. If its location conflicts with another item, then it will
    replace the item. If its location is not on a station, then another
    attempt will be made to add it.

    Args:
        environment_json (dict): The environment JSON to add items to.
        items (list): A list of items to attempt adding to the environment.
    
    Returns:
        updated_environment_json (dict): The updated environment JSON with the randomly added items.
    """
    updated_environment_json = deepcopy(environment_json)
    item_loc_candidates = updated_environment_json["stations"] + updated_environment_json["players"]
    for item in items:
        position_match = lambda other: other["x"] == item["x"] and other["y"] == item["y"]
        matched_candidate = list(filter(position_match, item_loc_candidates)) # Empty or one element
        conflicting_item = list(filter(position_match, updated_environment_json["items"])) # Empty or one element
        if matched_candidate and not conflicting_item and (item.get(FROZEN_TAG_NAME) or matched_candidate[0].get(FROZEN_TAG_NAME) is None):
            # Directly add item to environment
            updated_environment_json["items"].append(item)
            #print("Added item {} at ({}, {})".format(item["name"], item["x"], item["y"]))
        elif item.get(FORCE_ADD_TAG_NAME):
            if item.get(FROZEN_TAG_NAME):
                # Add item to environment immediately if it is frozen
                updated_environment_json["items"].append(item)
                #print("Added frozen item {} at ({}, {})".format(item["name"], item["x"], item["y"]))
            elif matched_candidate and conflicting_item and not conflicting_item[0].get(FORCE_ADD_TAG_NAME):
                # Replace conflicting items with FORCE_ADD items which are necessary to add. Exclude conflicting items that were forced added.
                conflicting_item_index = updated_environment_json["items"].index(conflicting_item[0])
                item["x"], item["y"] = conflicting_item[0]["x"], conflicting_item[0]["y"]
                updated_environment_json["items"][conflicting_item_index] = item
                #print("Replacement: {} at ({}, {})".format(item["name"], item["x"], item["y"]))
            else:
                # Replace an item from a candidate (or place on an empty station)
                added = False
                for candidate in item_loc_candidates:
                    occupied_item_lambd = lambda item: item["x"] == candidate["x"] and item["y"] == candidate["y"]
                    occupied_item = list(filter(occupied_item_lambd, updated_environment_json["items"]))
                    if len(occupied_item) == 0 and candidate.get(FROZEN_TAG_NAME) is None:
                        # Place the item on the candidate
                        item["x"], item["y"] = candidate["x"], candidate["y"]
                        updated_environment_json["items"].append(item)
                        added = True
                        break
                    elif occupied_item[0].get(FORCE_ADD_TAG_NAME) is None:
                        # Replace the item with the FORCE_ADD item
                        occupied_item_index = updated_environment_json["items"].index(occupied_item[0])
                        item["x"], item["y"] = occupied_item[0]["x"], occupied_item[0]["y"]
                        updated_environment_json["items"][occupied_item_index] = item
                        added = True
                        break
                assert added, "Item force add failed"
                #print("Fail item add: {} at ({}, {}) {}".format(item["name"], item["x"], item["y"], "[FORCE]" if item.get(FORCE_ADD_TAG_NAME) else ""))
    # TODO: Add and option to allow for randomizing stacked items. For now, ensure no stacks (unless frozen)
    set_stacklevel = lambda obj: not obj.get(FROZEN_TAG_NAME) and obj.update({"stack-level": 0})
    updated_environment_json["items"] = _apply_lambdas(updated_environment_json["items"], [set_stacklevel])
    return updated_environment_json

def _randomly_add_players(environment_json, players):
    """
    Returns an environment JSON with randomly placed players in the environment.

    This function currently only adds one player to the environment. It will
    attempt to add a player to be adjacent to a station. It is assumed that
    there is at least one station. Since there is always a need to add a player,
    this function will continue to retry until the player is added to the environment.

    TODO: Add multiplayer functionality

    Args:
        environment_json (dict): The environment JSON to add players to.
        players (list): A list of players to attempt adding to the environment.
    
    Returns:
        updated_environment_json (dict): The updated environment JSON with the randomly added players.
    """
    # Assuming one player for now
    player = players[0].copy()
    updated_environment_json = deepcopy(environment_json)

    width, height = updated_environment_json["width"], updated_environment_json["height"]
    added_player = False
    for station in updated_environment_json["stations"]:
        if added_player:
            break
        # print(f"Trying to add player to station {station['name']} at ({station['x']}, {station['y']})")
        x, y = station["x"], station["y"]
        other_station_pos = [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        for pos in other_station_pos:
            # Check within bounds
            if pos[0] >= 0 and pos[0] < width and pos[1] >= 0 and pos[1] < height:
                # Check if position is not on a station
                station_matcher = lambda s: s["x"] == pos[0] and s["y"] == pos[1]
                has_station = len(list(filter(station_matcher, updated_environment_json["stations"]))) > 0
                if not has_station:
                    # Check if player can reach all other stations
                    environment_json_copy = deepcopy(updated_environment_json)
                    player["x"], player["y"] = pos[0], pos[1]
                    player["direction"] = [x - pos[0], y - pos[1]]
                    environment_json_copy["players"].append(player)
                    reachable = _are_stations_reachable(environment_json_copy)
                    if reachable:
                        updated_environment_json["players"].append(player)
                        added_player = True
                        break
    return updated_environment_json

def _randomly_add_containers(environment_json, containers):
    """
    Returns an environment JSON with randomly placed containers in the environment.

    This function will attempt to add containers into the environment until
    there are no more containers to add. An attempt may fail if the container's
    location conflicts with anothers. It'll also fail if the container's location
    is not on a station or player. Finally, a container cannot occupy an item's
    position.

    If a container has a FORCE_ADD tag, then it will eventually be added to the
    environment. If its location conflicts with another container, then it will
    replace the container. If its location is not on a station, then another
    attempt will be made to add it.

    Args:
        environment_json (dict): The environment JSON to add items to.
        containers (list): A list of containers to attempt adding to the environment.
    
    Returns:
        updated_environment_json (dict): The updated environment JSON with the randomly added containers.
    """
    updated_environment_json = deepcopy(environment_json)
    container_loc_candidates = updated_environment_json["stations"] + updated_environment_json["players"]
    for container in containers:
        position_match = lambda other: other["x"] == container["x"] and other["y"] == container["y"]
        matched_candidate = list(filter(position_match, container_loc_candidates)) # Empty or one element
        conflicting_item = list(filter(position_match, updated_environment_json["items"])) # Empty or one element
        conflicting_container = list(filter(position_match, updated_environment_json["containers"])) # Empty or one element
        conflicting_object = conflicting_item + conflicting_container
        if matched_candidate and not conflicting_object and (container.get(FROZEN_TAG_NAME) or matched_candidate[0].get(FROZEN_TAG_NAME) is None):
            # Directly add container to environment
            updated_environment_json["containers"].append(container)
            # print("Added container {} at ({}, {})".format(container["name"], container["x"], container["y"]))
        elif container.get(FORCE_ADD_TAG_NAME):
            if container.get(FROZEN_TAG_NAME):
                # Add item to environment immediately if it is frozen
                updated_environment_json["containers"].append(container)
                # print("Added frozen container {} at ({}, {})".format(container["name"], container["x"], container["y"]))
            elif matched_candidate and conflicting_item and not conflicting_item[0].get(FORCE_ADD_TAG_NAME):
                # Replace conflicting items with FORCE_ADD containers which are necessary to add. Exclude conflicting items that were forced added.
                conflicting_item_index = updated_environment_json["items"].index(conflicting_item[0])
                item = updated_environment_json["items"].pop(conflicting_item_index)
                container["x"], container["y"] = item[0]["x"], item[0]["y"]
                updated_environment_json["containers"].append(container)
                # print("Item replacement: {} at ({}, {})".format(container["name"], container["x"], container["y"]))
            elif matched_candidate and conflicting_container and not conflicting_container[0].get(FORCE_ADD_TAG_NAME):
                # Replace conflicting containers with FORCE_ADD containers which are necessary to add. Exclude conflicting containers that were forced added.
                conflicting_container_index = updated_environment_json["containers"].index(conflicting_container[0])
                container["x"], container["y"] = conflicting_container[0]["x"], conflicting_container[0]["y"]
                updated_environment_json["containers"][conflicting_container_index] = container
                # print("Container replacement: {} at ({}, {})".format(container["name"], container["x"], container["y"]))
            else:
                # Replace a container from a candidate (or place on an empty station)
                added = False
                for candidate in container_loc_candidates:
                    occupied_container_lambd = lambda container: container["x"] == candidate["x"] and container["y"] == candidate["y"]
                    occupied_container = list(filter(occupied_container_lambd, updated_environment_json["containers"]))
                    occupied_item = list(filter(occupied_container_lambd, updated_environment_json["items"]))
                    occupied_object = occupied_container + occupied_item
                    if len(occupied_object) == 0 and candidate.get(FROZEN_TAG_NAME) is None:
                        # Place the container on the candidate
                        container["x"], container["y"] = candidate["x"], candidate["y"]
                        updated_environment_json["containers"].append(container)
                        added = True
                        break
                    elif occupied_container and occupied_container[0].get(FORCE_ADD_TAG_NAME) is None:
                        # Replace the container with the FORCE_ADD container
                        occupied_container_index = updated_environment_json["containers"].index(occupied_container[0])
                        container["x"], container["y"] = occupied_container[0]["x"], occupied_container[0]["y"]
                        updated_environment_json["containers"][occupied_container_index] = container
                        added = True
                        break
                    elif occupied_item and occupied_item[0].get(FORCE_ADD_TAG_NAME) is None:
                        # Replace the item with the FORCE_ADD container
                        updated_environment_json["items"].remove(occupied_item[0])
                        container["x"], container["y"] = occupied_item[0]["x"], occupied_item[0]["y"]
                        updated_environment_json["containers"].append(container)
                        added = True
                        break
                assert added, "Container force add failed"
                #print("Fail container add: {} at ({}, {}) {}".format(container["name"], container["x"], container["y"], "[FORCE]" if container.get(FORCE_ADD_TAG_NAME) else ""))
    return updated_environment_json

def _randomly_add_objects(environment_json, stations, items, containers, players):
    """
    Returns an environment JSON with randomly placed objects in the environment.

    This function takes in an environment and attempts to add the provided stations,
    items, and players to the environment. If an attempt to add an object fails, the
    object isn't added to the environment; however, if the object has a FORCE_ADD_TAG
    then it will eventually be added to the environment.
    
    Args:
        environment_json (dict): The environment JSON to place objects in.
        stations (list): A list of stations to add.
        items (list): A list of items to add.
        containers (list): A list of containers to add.
        players (list): A list of players to add.

    Returns:
        new_environment_json (dict): The environment JSON with the randomly added objects.
    """
    new_environment_json = deepcopy(environment_json)
    new_environment_json = _randomly_add_stations(new_environment_json, stations, players)
    # print("Added stations")
    # print(new_environment_json["stations"])
    new_environment_json = _randomly_add_players(new_environment_json, players)
    # print("Added players")
    # print(new_environment_json["players"])
    new_environment_json = _randomly_add_items(new_environment_json, items)
    # print("Added items")
    # print(new_environment_json["items"])
    new_environment_json = _randomly_add_containers(new_environment_json, containers)
    # print("Added containers")
    # print(new_environment_json["containers"])
    return new_environment_json

def _apply_lambdas(iterables, lambdas):
    """
    Applies the provided lambdas to the provided iterables. 
    
    Does not modify the original iterables.

    Args:
        iterables (list): A list of iterables.
        lambdas (list): A list of lambdas to apply to the iterables.

    Returns:
        iterables (list): A list of iterables with the lambdas applied.
    """
    iterables_copy = deepcopy(iterables)
    for iterable in iterables_copy:
        for lambd in lambdas:
            lambd(iterable)
    return iterables_copy

def _group_objects(environment_json):
    """
    Returns a list of grouped objects in the current environment.

    This function groups objects in the environment JSON by their starting position in the environment_json. The possible
    groups include
        - Station ["station"]
        - Station with item(s) on it ["station", "station_items"]
        - Station with a player by it ["station", "player"]
        - Station with a player by it holding an item ["station", "player", "player_item"]
        - Station with item(s) on it with a player by it ["station", "station_items", "player"]
        - Station with item(s) on it with a player by it holding another item ["station", "station_items", "player", "player_item"]
    where the dictionary will use the keys in the lists above.

    Args:
        environment_json (dict): The environment JSON with objects to group.
    
    Returns:
        grouped_objects (list): A list of grouped objects.
    """
    grouped_objects = []
    position_checks = lambda positions, obj: any([obj["x"] == pos[0] and obj["y"] == pos[1] for pos in positions])
    for station in environment_json["stations"]:
        group = {"station": station}
        x, y = station["x"], station["y"]
        station_positions = [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        station_positions_check = lambda obj: position_checks(station_positions, obj)
        adjacent_players = list(filter(station_positions_check, environment_json["players"]))
        group["player"] = adjacent_players[0] if len(adjacent_players) != 0 else None
        station_items = list(filter(lambda obj: position_checks([(x, y)], obj), environment_json["items"]))
        group["station_items"] = station_items if len(station_items) != 0 else None
        if group.get("player"):
            player_pos = (group["player"]["x"], group["player"]["y"])
            player_item = list(filter(lambda obj: position_checks([player_pos], obj), environment_json["items"]))
            group["player_item"] = player_item[0] if len(player_item) != 0 else None
        grouped_objects.append(group)
    return grouped_objects

def _update_station_name(station):
    """
    Updates a wilcard station to be one of the station types.

    Args:
        station (dict): The station to update.
    
    Side Effects:
        station["name"] is updated to be one of the station types.
    """
    if station["name"] != STATION_WILDCARD: return
    station["name"] = random.choice(list(Station)).value

def _update_item_name(item):
    """
    Updates the wildcard item to be one of the item types.

    Args:
        item (dict): The item to update.
    
    Side Effects:
        item["name"] is updated to be one of the item types.
    """
    if item["name"] != ITEM_WILDCARD: return
    item_enum = random.choice(list(Item))
    item["name"] = item_enum.value
    if item_enum in [Item.PATTY, Item.CHICKEN]:
        item["predicates"] = ["iscookable"] # + random.choice([[], ["iscooked"]])
    elif item_enum in [Item.LETTUCE, Item.ONION, Item.TOMATO]:
        item["predicates"] = ["iscuttable"] # + random.choice([[], ["iscut"]])

def _randomize_and_freeze_objects(environment_json):
    """
    Returns stations, items, and players in the current environment with random locations and a frozen tag.

    This function randomizes the positions of grouped objects (see _group_objects) in the environment JSON 
    (and direction for player).

    As objects' positions are determined, frozen tags are added to them. This prevents the objects from being modified when
    adding other objects later (for example, a station that was empty before will remain empty).

    WARNING: This function is not guaranteed to halt. This function assumes that the environment provided is a JSON example
    which contains small enough items such that this function is likely to eventually terminate.

    Args:
        environment_json (dict): The environment JSON with objects to group, randomize and add FROZEN tag.
    
    Returns:
        stations (list): A list of stations with random positions and FROZEN tags.
        items (list): A list of items with random positions and FROZEN tags.
        players (list): A list of players with random positions and directions and FROZEN tags.
    """
    new_environment_json = deepcopy(environment_json)
    groups = _group_objects(new_environment_json)
    width, height = environment_json["width"], environment_json["height"]
    bounds_check = lambda pos: pos[0] >= 0 and pos[0] < width and pos[1] >= 0 and pos[1] < height
    reachable_state, filled_positions = False, False
    while not reachable_state or not filled_positions:
        new_environment_json["stations"], new_environment_json["items"], new_environment_json["players"] = [], [], []
        possible_positions = list(itertools.product(range(width), range(height)))
        random.shuffle(possible_positions)
        for group in groups:
            station = group["station"] # Each group MUST have a station
            x, y = possible_positions.pop() # This is safe because there are always more positions than groups
            station_positions = [(x, y)]
            if group.get("player"):
                # Check for adjacent spots too
                station_positions += [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
            valid_station_positions = list(filter(bounds_check, station_positions))
            stations, players = new_environment_json["stations"], new_environment_json["players"]
            conflict_check = lambda pos: not any([pos[0] == obj["x"] and pos[1] == obj["y"] for obj in stations + players])
            valid_station_positions = list(filter(conflict_check, valid_station_positions))
            if len(valid_station_positions) == 0 or (x, y) not in valid_station_positions:
                # No valid positions for station, so we need to try again
                break
            if group.get("player") and len(valid_station_positions) == 1:
                # No adjacent spots available for player, so we need to try again
                break

            # Add the group to the environment (and freeze them)
            if station["name"] == "station":
                _update_station_name(station)
            station["x"], station["y"] = x, y
            station[FROZEN_TAG_NAME] = True
            station[FORCE_ADD_TAG_NAME] = True
            new_environment_json["stations"].append(station)
            if group.get("station_items"):
                items = group["station_items"]
                for item in items:
                    if item["name"] == "item":
                        _update_item_name(item)
                    item["x"], item["y"] = x, y
                    item[FROZEN_TAG_NAME] = True
                    item[FORCE_ADD_TAG_NAME] = True
                    new_environment_json["items"].append(item)
            if group.get("player"):
                player = group["player"]
                player["x"], player["y"] = random.choice(valid_station_positions[1:]) # Choose a random adjacent spot
                player["direction"] = [x - player["x"], y - player["y"]]
                player[FROZEN_TAG_NAME] = True
                player[FORCE_ADD_TAG_NAME] = True
                new_environment_json["players"].append(player)
                if group.get("player_item"):
                    item = group["player_item"]
                    if item["name"] == "item":
                        _update_item_name(item)
                    item["x"], item["y"] = player["x"], player["y"]
                    item[FROZEN_TAG_NAME] = True
                    item[FORCE_ADD_TAG_NAME] = True
                    new_environment_json["items"].append(item)
        filled_positions = len(new_environment_json["stations"]) == len(groups)
        reachable_state = _are_stations_reachable(new_environment_json)
    return new_environment_json["stations"], new_environment_json["items"], new_environment_json["players"]

def _randomize_and_tag_objects(environment_json):
    """
    Returns stations, items, and players in the current environment with random locations and tags.

    This function randomizes the positions of current objects in the environment JSON (and direction
    for player). It also adds a FORCE_ADD tag to each object so that the object is eventually added
    into the environment.

    Args:
        environment_json (dict): The environment JSON with objects to randomize and add FORCE_ADD tags to.
    
    Returns:
        stations (list): A list of stations with random positions and FORCE_ADD tags.
        items (list): A list of items with random positions and FORCE_ADD tags.
        containers (list): A list of containers with random positions and FORCE_ADD tags.
        players (list): A list of players with random positions and directions and FORCE_ADD tags.
    """
    width, height = environment_json["width"], environment_json["height"]
    randomize_position = lambda obj: obj.update({"x": random.randrange(0, width), "y": random.randrange(0, height)})
    set_mustadd = lambda obj: obj.update({FORCE_ADD_TAG_NAME: True})
    stations = _apply_lambdas(environment_json.get("stations", []), [randomize_position, set_mustadd, _update_station_name])
    items = _apply_lambdas(environment_json.get("items", []), [randomize_position, set_mustadd, _update_item_name])
    containers = _apply_lambdas(environment_json.get("containers", []), [randomize_position, set_mustadd])
    randomize_direction = lambda obj: obj.update({"direction": random.choice([[0,1], [1,0], [0,-1], [-1,0]])})
    players = _apply_lambdas(environment_json.get("players", []), [randomize_position, randomize_direction, set_mustadd])
    return stations, items, containers, players

def randomize_environment(environment_json, seed, noisy_randomization=False):
    """
    Returns an environment JSON with a random layout based on the provided environment.

    This function requires an environment JSON that has the minimum required objects to
    complete the intended task. The layout of the environment will be randomized based
    on the provided seed either by 
        1) adding new objects or
        2) changing the location of existing objects.

    There are two types of randomization. In all forms of randomization, any kind of objects
    can be added meaning that they can be placed on tables (currently, items cannot be stacked
    upon each other randomly). By default, can be moved with no restrictions including stations,
    items (and stacks), and players. If noisy_randomization is True, then objects that are
    required to complete the intended task are grouped (e.g. a task where the player starts at 
    a station with an item on it that needs to be moved to an empty station will always have the
    station, item, and player moved together and the empty station will remain empty).

    Args:
        environment_json (dict): An environment JSON with minimum objects necessary
            for the intended task.
        seed (int): The seed for the random layout generator.

    Returns:
        new_environment_json (dict): An environment JSON with a random layout.
    """
    random.seed(seed)
    new_environment_json = deepcopy(environment_json)
    new_environment_json["stations"] = []
    new_environment_json["items"] = []
    new_environment_json["containers"] = []
    new_environment_json["players"] = []
    width, height = new_environment_json["width"], new_environment_json["height"]
    stations, items, containers, players = _generate_random_objects(width, height)
    if noisy_randomization:
        # Move existing objects in groups
        existing_stations, existing_items, existing_players = _randomize_and_freeze_objects(environment_json) # TODO(chalo2000): Support containers
        # Add frozen objects first to avoid conflicts
        stations = existing_stations + stations
        items = existing_items + items
        players = existing_players + players
    else:
        # Prepare existing objects (from environment_json) to be randomly moved
        existing_stations, existing_items, existing_containers, existing_players = _randomize_and_tag_objects(environment_json)
        stations += existing_stations
        items += existing_items
        containers += existing_containers
        players += existing_players
    new_environment_json = _randomly_add_objects(new_environment_json, stations, items, containers, players)
    return new_environment_json