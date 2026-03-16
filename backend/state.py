from backend.predicate import Predicate
from backend.object import Object
from utils.robotouille_utils import trim_item_ID
import itertools
import copy

class State(object):
    '''
    This class represents a state in the Robotouille game.

    States are created by the game, and are updated by the game when actions are
    performed.
    '''

    def __init__(self):
        """
        Creates a state object with default values.
        """
        self.domain = None
        self.objects = []
        self.predicates = {}
        self.actions = {}
        self.goal = []
        self.special_effects = []

    def _build_object_dictionary(self, domain, objects):
        """
        Builds a dictionary of objects.

        The keys of the dictionary are the types of objects in the domain, and
        the values are lists of objects of that type.

        Args:
            domain (Domain): The domain of the game.
            objects (List[Object]): The objects in the state.

        Returns:
            object_dict (Dictionary[str, List[Object]]): A dictionary of objects
                in the state.

        Raises:
            ValueError: If an object type is not defined in the domain.
        """
        object_dict = {k: [] for k in domain.object_types}
        for obj in objects:
            if obj.object_type not in object_dict:
                raise ValueError(f"Type {obj.object_type} is not defined in the domain.")
            object_dict[obj.object_type].append(obj)

        return object_dict

    def _build_predicates(self, domain, objects, true_predicates):
        """
        Builds a dictionary of predicates.

        The dictionary is populated with all possible predicates in the state 
        using the predicates in the domain and the objects in the problem file. 
        All predicates are set to False, except for the predicates that are true 
        in the problem file, which are passed in as the argument 
        [true_predicates].

        Args:
            domain (Domain): The domain of the game.
            objects (List[Object]): The objects in the state.
            true_predicates (Set[Predicate]): The predicates that are true in
                the state, as defined by the problem file. 

        Returns:
            predicates (Dictionary[Predicate, bool]): A dictionary of predicates
                in the state. The keys are the predicates, and the values are
                boolean, where True means that the predicate is true in the state,
                and False means that the predicate is false in the state.
        """
        object_dict = self._build_object_dictionary(domain, objects)
            
        # Loop through the predicates in the domain
        predicates = {}
        for predicate in domain.predicates:
            # Check the types of the parameters in the domain. For each type, 
            # get the objects of that type in the problem file. Then create a 
            # list of all possible combinations of objects for the parameters.
            param_objects = [object_dict[object_type] for object_type in predicate.types]
            param_combinations = list(itertools.product(*param_objects))
            # For each combination of objects, create a predicate and add it to
            # the list of predicates.
            for combination in param_combinations:
                # If combination repeats an object, skip it
                if len(set(combination)) != len(combination):
                    continue
                pred = Predicate().initialize(predicate.name, predicate.types, combination, language_descriptors=predicate.language_descriptors)
                predicates[pred] = pred in true_predicates
        return predicates
    
    def _build_actions(self, domain, objects):
        """
        Builds a dictionary of all actions for the state.

        This helper method first builds a dictionary of objects in the state. 
        It then loops through the actions in the domain. For each action, it
        creates every possible combination of objects for the parameters of the
        action.

        Args:
            domain (Domain): The domain of the game.
            objects (List[Object]): The objects in the state.

        Returns:
            actions (Dictionary[Action, Dictionary[str, Object]]): A 
                dictionary of valid actions for the state. The keys are the 
                actions, and the values are dictionaries whose key are
                a parameter name and values with Object arguments.
        """
        object_dict = self._build_object_dictionary(domain, objects)
        actions = {}
        
        for action in self.domain.actions:
            params = action.get_all_params()
            param_objects = [object_dict[param.object_type] for param in params]
            param_combinations = list(itertools.product(*param_objects))
            actions[action] = []
            for combination in param_combinations:
                # If combination repeats an object, skip it
                if len(set(combination)) != len(combination):
                    continue
                args = {param.name:combination[params.index(param)] for param in params}
                actions[action].append(args)
        return actions
    
    def get_players(self):
        """
        Returns the player objects in the state.

        Returns:
            players (List[Object]): The player objects in the state.
        """
        return [obj for obj in self.objects if obj.object_type == "player"]

    def initialize(self, domain, objects, true_predicates, all_goals, goal_description, special_effects=[]):
        """
        Initializes a state object.

        Predicates are stored in a dictionary with the predicate as the key, and
        the value as the value. The value is a boolean, where True means that 
        the predicate is true in the state, and False means that the predicate 
        is false in the state.

        The initializer also checks the types of the objects in the state and
        the goal predicates to ensure that they are defined in the domain.

        Parameters:
            domain (Domain):
                The domain of the game.
            objects (List[Object]):
                The objects in the state.
            true_predicates (Set[Predicate]):
                The predicates that are true in the state, as defined by the problem file. 
            all_goals (List[List[Predicate]]):
                The goal predicates of the game.
            goal_description (str):
                The natural language description of the goal.
            special_effects (List[Special_effects]):
                The special effects that are active in the state.

        Returns:
            state (State): The initialized state.

        Raises:
            ValueError:
                If the type of an object is not defined in the domain, or if a 
                goal predicate is not defined in the domain.
        """
        predicates = self._build_predicates(domain, objects, true_predicates)
        # Check if objects have types defined in domain
        for object in objects:
            if object.object_type not in domain.object_types:
                raise ValueError(f"Type {object.object_type} is not defined in the domain.")
        predicate_names = list(map(lambda x: x.name, domain.predicates))
        # Check if goal predicates are defined in domain
        for goal_set in all_goals:
            for goal in goal_set:
                if goal.name not in predicate_names:
                    raise ValueError(f"Predicate {goal.name} is not defined in the domain.")
                if not domain.are_valid_object_types(goal.types):
                    raise ValueError(f"Types {goal.types} are not defined in the domain.")
        
        self.domain = domain
        self.objects = objects
        self.current_player = self.get_players()[0]
        self.predicates = predicates
        self.actions = self._build_actions(domain, objects)
        self.goal = all_goals
        self.goal_description = goal_description
        self.special_effects = special_effects

        return self
        
    def __eq__(self, other):
        """
        Checks if two states are equal.

        Args:
            other (State): The state to compare to.

        Returns:
            bool: True if the states are equal, False otherwise.
        """
        return self.domain == other.domain and self.objects == other.objects \
            and self.predicates == other.predicates and self.goal == other.goal \
            and self.special_effects == other.special_effects

    def get_predicate_value(self, predicate):
        """
        Returns the value of a predicate in the state.

        If a predicate is not yet in the state, then the function returns False.
        For example, for goal predicates involving objects not yet created, the
        predicate would not be defined in the state. Then the function returns 
        False.

        Args:
            predicate (Predicate): The predicate to check.
            value (bool): The value of the predicate to check for.

        Returns:
            bool: True if the predicate is True in the state, False if the 
                predicate is False in the state or if the predicate is not in 
                the state. 
        """
        return self.predicates[predicate] if predicate in self.predicates else False
        
    def update_predicate(self, predicate, value):
        """
        Updates a predicate in the state with a new value.

        Args:
            predicate (Predicate): The predicate to update.
            value (bool): The new value of the predicate.

        Raises:
            AssertionError: If the predicate is not in the state.
        """
        assert predicate in self.predicates
        self.predicates[predicate] = value
    
    def update_special_effect(self, special_effect, arg, param_arg_dict):
        """
        Updates a special effect in the state.

        If the special effect is not in the state, it is added.
        Otherwise, the special effect is sent an active update.

        Args:
            special_effect (SpecialEffect): The special effect to update.
            arg (Object): The object to update the special effect for.
            param_arg_dict (Dictionary[Str, Object]): The arguments for the 
                special effect.
        """
        replaced_effect = special_effect.apply_sfx_on_arg(arg, param_arg_dict)
        if replaced_effect not in self.special_effects:
            self.special_effects.append(replaced_effect)
        current = self.special_effects[self.special_effects.index(replaced_effect)]
        current.update(self, active=True)

    def _get_next_ID_for_object(self, obj):
        """
        This helper function finds the next available ID for an object.
        
        IDs are still not reused even if objects have been deleted, because the 
        function always finds the greatest current ID and increments it by 1.

        Args:
            obj (Object): The object to get the next available ID for.

        Returns:
            int: The next available ID for the object.
        """
        max_id = 0
        for object in self.objects:
            name, id = trim_item_ID(object.name)
            if name == obj.name:
                max_id = max(max_id, int(id))
        return max_id + 1

    def add_object(self, obj):
        """
        Adds an object to the state.

        Args:
            obj (Object): The object to add to the state. 

        Side effects:
            - The objects, predicates, and actions in the state are modified and 
              updated to account for the new object.

        Returns:
            created_obj (Object): The object that was created.
        """
        num = self._get_next_ID_for_object(obj)
        name = f"{obj.name}{num}"
        new_obj = Object(name, obj.object_type)
        # TODO(lsuyean): create field to store ID instead of modifying name
        self.objects.append(new_obj)
        # TODO(lsuyean): optimize creating predicates and actions; only add
        # necessary predicates and actions instead of building from scratch
        true_predicates = {predicate for predicate, value in self.predicates.items() if value}
        self.predicates = self._build_predicates(self.domain, self.objects, true_predicates)
        self.actions = self._build_actions(self.domain, self.objects)
        return new_obj

    def delete_object(self, obj):
        """
        Deletes an object from the state.

        Args:
            obj (Object): The object to delete from the state.

        Side effects:
            - The objects, predicates, and actions in the state are modified and 
              updated to account for the deleted object.
        """
        self.objects.remove(obj)
        # TODO(lsuyean): optimize creating predicates and actions; only delete
        # necessary predicates and actions instead of building from scratch
        true_predicates = {predicate for predicate, value in self.predicates.items() if value}
        self.predicates = self._build_predicates(self.domain, self.objects, true_predicates)
        self.actions = self._build_actions(self.domain, self.objects)

    def is_goal_reached(self):
        """
        Returns whether the goal is satisfied in the current state.
        
        self.goal is a list of lists of predicates. Each list of predicates is a
        goal set, which represents a possible goal state. The state satisfies
        the goal if it satisfies any of the goal sets.

        Returns:
            bool: True if the state satisfies the goal, False otherwise.
        """
        for goal_set in self.goal:
            if all(self.get_predicate_value(goal) for goal in goal_set):
                return True
        return False
    
    def _get_player_location(self, player):
        """Get the current location (station) of a player."""
        for predicate, is_true in self.predicates.items():
            if (is_true and predicate.name == 'loc' and 
                len(predicate.params) == 2 and predicate.params[0] == player):
                return predicate.params[1]  # Return the station
        return None
    
    def _get_items_at_location(self, station):
        """Get all items at a specific station."""
        items = set()  # Use set to avoid duplicates
        for predicate, is_true in self.predicates.items():
            if (is_true and predicate.name in ['item_at', 'item_on'] and 
                len(predicate.params) == 2 and predicate.params[1] == station):
                items.add(predicate.params[0])  # Add the item
        return list(items)  # Convert back to list
    
    def _get_player_held_items(self, player):
        """Get all items/containers held by a player."""
        held_items = set()  # Use set to avoid duplicates
        for predicate, is_true in self.predicates.items():
            if (is_true and predicate.name in ['has_item', 'has_container'] and 
                len(predicate.params) == 2 and predicate.params[0] == player):
                held_items.add(predicate.params[1])  # Add the held item
        return list(held_items)  # Convert back to list
    
    def _is_player_holding_nothing(self, player):
        """Check if player is holding nothing."""
        for predicate, is_true in self.predicates.items():
            if (is_true and predicate.name == 'nothing' and 
                len(predicate.params) == 1 and predicate.params[0] == player):
                return True
        return False
    
    def _prune_actions_by_spatial_constraints(self):
        """Prune action space based on spatial constraints to reduce validity checks."""
        pruned_actions = {}
        current_player = self.current_player
        player_location = self._get_player_location(current_player)
        items_at_player_location = self._get_items_at_location(player_location) if player_location else []
        held_items = self._get_player_held_items(current_player)
        holding_nothing = self._is_player_holding_nothing(current_player)
        
        # print(f"DEBUG PRUNING: Player {current_player.name} at location {player_location.name if player_location else None}")
        # print(f"DEBUG PRUNING: Items at location: {[item.name for item in items_at_player_location]}")
        # print(f"DEBUG PRUNING: Held items: {[item.name for item in held_items]}")
        # print(f"DEBUG PRUNING: Holding nothing: {holding_nothing}")
        
        total_original_actions = sum(len(args_list) for args_list in self.actions.values())
        total_pruned_actions = 0
        
        for action, args_list in self.actions.items():
            action_name = action.name.lower()
            pruned_args = []
            
            # print(f"\nDEBUG PRUNING: Processing action '{action.name}' with {len(args_list)} combinations")
            
            for args in args_list:
                # Get player parameter from args (usually first parameter)
                action_player = None
                for param_name, obj in args.items():
                    if obj.object_type == 'player':
                        action_player = obj
                        break
                
                # Only consider actions for the current player (skip if no player found)
                if action_player is None or action_player != current_player:
                    continue
                
                # Apply action-specific spatial constraints
                kept = False
                if 'move' in action_name:
                    # Move: player must start from current location
                    # In move(p1=robot1, s1=source, s2=dest), s1 is source station
                    source_station = args.get('s1')  # source station parameter
                    if source_station == player_location:
                        pruned_args.append(args)
                        kept = True
                        
                elif 'pick' in action_name or 'pickup' in action_name:
                    # Pickup: item must be at player location, player must be holding nothing
                    if holding_nothing:
                        item_to_pickup = args.get('i1')  # item parameter
                        pickup_station = args.get('s1')  # station parameter
                        # Item must be at the pickup station, and robot must be at that station
                        if (pickup_station == player_location and 
                            item_to_pickup in items_at_player_location):
                            pruned_args.append(args)
                            kept = True
                            
                elif ('drop' in action_name or 'place' in action_name or 
                      'stack' in action_name or 'put' in action_name):
                    # Drop/Place/Stack: player must be holding something
                    if held_items:
                        # Check if the item being dropped/placed is actually held
                        item_to_drop = args.get('i1')  # item parameter  
                        if item_to_drop in held_items:
                            pruned_args.append(args)
                            kept = True
                            
                elif ('use' in action_name or 'cut' in action_name or 'cook' in action_name or
                      'wash' in action_name or 'fry' in action_name):
                    # Tool/appliance actions: player must be at the appliance location
                    appliance_station = args.get('s1')  # station parameter
                    if appliance_station == player_location:
                        pruned_args.append(args)
                        kept = True
                        
                else:
                    # For unknown action types, keep all args (conservative approach)
                    pruned_args.append(args)
                    kept = True
                
                # if not kept:
                #     arg_str = ", ".join([f"{k}={v.name}" for k, v in args.items()])
                #     print(f"  FILTERED OUT: {action.name}({arg_str})")
            
            # print(f"  KEPT: {len(pruned_args)}/{len(args_list)} combinations")
            total_pruned_actions += len(pruned_args)
            
            if pruned_args:
                pruned_actions[action] = pruned_args
            else:
                # Even if no args pass spatial filter, keep empty list to maintain action structure
                pruned_actions[action] = []
        
        # print(f"\nDEBUG PRUNING SUMMARY: {total_pruned_actions}/{total_original_actions} actions kept ({100*total_pruned_actions/total_original_actions:.1f}%)")
        return pruned_actions
    
    def get_valid_actions(self):
        """
        Gets all valid actions for the state.

        An empty list is initially assigned to each action. For every possible 
        set of arguments for each action, the arguments that are currently 
        valid for each action are appended to the lists for the relevant action.

        Returns:
            valid_actions (Dictionary[Action, List[Dictionary[Str, Object]]]): A
                dictionary of valid actions for the state. The keys are the
                actions, and the values are the parameter-argument dictionaries
                for the actions.
        """
        valid_actions = {action:[] for action in self.actions}

        for action, args in self.actions.items():
            for arg in args:
                if action.is_valid(self, arg):
                    valid_actions[action].append(arg)

        return valid_actions
    
    def get_valid_actions_and_str(self):
        """
        Gets all valid actions for the state as dictionaries and strings.

        TODO(chalo2000): Temp until Action class split into definition and instance class.

        This is a temporary function until the Action class is split into a definition
        and instance class (which would allow get_valid_actions() to be easily converted
        to a string representation).

        Both lists are returned in the same order for easily converting between the two.

        Returns:
            valid_actions (List[(Action, Dictionary[Str, Object]])): A list of valid action
                + param_arg dicts tuples for the current state.
            str_valid_actions (List[str]): A string list of valid actions for the state.
        """
        # Use spatial constraint pruning to reduce action space before validity checks
        pruned_actions = self._prune_actions_by_spatial_constraints()
        valid_actions_dict = {action:[] for action in pruned_actions}

        for action, args in pruned_actions.items():
            for arg in args:
                if action.is_valid(self, arg):
                    valid_actions_dict[action].append(arg)

        valid_actions = []
        str_valid_actions = []
        for action, param_arg_dicts in valid_actions_dict.items():
            for param_arg_dict in param_arg_dicts:
                valid_action = (action, param_arg_dict)
                valid_actions.append(valid_action)
                str_valid_actions.append(action.get_language_description(param_arg_dict))
        
        return valid_actions, str_valid_actions
    
    def get_valid_actions_for_player(self, player):
        """
        Gets all valid actions for a player in the state.

        Args:
            player (Object): The player to get the valid actions for.

        Returns:
            valid_actions (Dictionary[Action, Dictionary[Str, Object]]): A
                dictionary of valid actions for the player. The keys are the
                actions, and the values are the parameter-argument dictionaries
                for the actions.
        """
        valid_actions = self.get_valid_actions()

        player_actions = {action:[] for action in self.actions}

        for action, args in valid_actions.items():
            for arg in args:
                if player in arg.values() or arg == {}:
                    player_actions[action].append(arg)

        return player_actions
                    
    def next_player(self):
        """
        Returns the next player in the state.

        Returns:
            player (Object): The next player in the state.
        """
        players = self.get_players()
        current_index = players.index(self.current_player)
        next_index = (current_index + 1) % len(players)
        return players[next_index]

    def step(self, actions):
        """
        Steps the state forward by applying the effects of the action.

        Args:
            actions (List[Tuple[Action, Dictionary[str, Object]]): A list of
                tuples where the first element is the action to perform, and the
                second element is a dictionary of arguments for the action. The 
                length of the list is the number of players, where actions[i] is
                the action for player i. If player i is not performing an action,
                actions[i] is None.
        
        Side Effects:
            - The current state is stepped to the next state with the provided actions
        
        Returns:
            done (bool): True if the goal is reached, False otherwise.

        Raises:
            AssertionError: If the action is invalid with the given arguments in
            the given state.
        """
        for action, param_arg_dict in actions:
            if action is None:
                continue
            assert action.is_valid(self, param_arg_dict)
            self = action.perform_action(self, param_arg_dict)
        
        for special_effect in self.special_effects:
            special_effect.update(self)
            if special_effect.completed:
                self.special_effects.remove(special_effect)
        
        if self.is_goal_reached():
            return True
        
        self.current_player = self.next_player()

        return False
    
    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new

        new.domain = self.domain
        new.goal = self.goal
        new.goal_description = self.goal_description
        new.objects = list(self.objects)
        new.current_player = self.current_player

        new.predicates = dict(self.predicates)

        new.actions = {act: [arg.copy() for arg in args] for act, args in self.actions.items()}

        new.special_effects = copy.deepcopy(self.special_effects, memo)

        return new
    
    def signature(self, include_player=True, include_sfx=True):
        """
        Returns a hashable, comparable fingerprint of the current state.
        Used by search algorithms to detect revisits.

        Args:
            include_player (bool): include current player's turn in the key.
            include_sfx (bool): include a lightweight fingerprint of special effects.

        Returns:
            tuple: hashable key
        """
        true_facts = tuple(
            sorted(
                (p.name, tuple(o.name for o in p.params))
                for p, v in self.predicates.items() if v
            )
        )
        parts = [true_facts]
        if include_player:
            parts.append(self.current_player.name)
        if include_sfx:
            parts.append(tuple(sorted(map(repr, self.special_effects))))
        return tuple(parts)