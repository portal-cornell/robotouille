from backend.object import Object
from backend.predicate import Predicate
from robotouille.env_utils import build_goal

class Customer(object):
    """
    The Customer class represents a customer in Robotouille.

    Customers are non-player characters that require a player to deliver some
    order to them. 
    """

    def __init__(self, name, pos, direction, order_name, order, time_to_serve, enter_time, gamemode):
        """
        Initializes the customer object.

        Args:
            name (str): The name of the customer.
            pos (tuple): The position of the customer in the form (x, y).
            direction (tuple): The unit vector of the customer's direction.
            order_name (str): The name of the order the customer wants.
            order (list): The list of predicates that make up the order.
            time_to_serve (int): The time left that the player has to serve the 
                customer in milliseconds.
            enter_time (int): The time at which the customer enters the game
                in milliseconds.
            gamemode (GameMode): The game mode object.
        """
        self.id = gamemode.customer_id_counter
        self.name = name
        self.pos = pos
        self.direction = direction
        self.order_name = order_name
        self.order = order
        self.time_to_serve = time_to_serve
        self.enter_time = enter_time
        self.time_passed = 0
        self.has_been_served = False
        self.has_eaten = False
        self.in_game = False
        self.has_left_queue = False
        self.sprite_value = 0
        self.action = None
        self.assigned_table = None
        gamemode.customer_id_counter += 1
        gamemode.customers[name] = self
    
    def build_customers(domain_json, environment_json, recipe_json, gamemode):
        """
        Builds the customers in the environment.

        Args:
            domain_json (dict): The domain json.
            environment_json (dict): The environment json.
            recipe_json (dict): The recipe_json
            gamemode (GameMode): The game mode object.

        Returns:
            customers (list[Object]): A list of customer objects to be added to
                the state.

        Modifies:
            Adds customers to gamemode.customers
        """
        Customer.environment_json = environment_json
        Customer.recipe_json = recipe_json
        customers = []
        if environment_json.get("customers"):
            for customer in environment_json["customers"]:
                name = customer["name"]
                pos = (customer["x"], customer["y"])
                direction = (customer["direction"][0], customer["direction"][1])
                order_name = customer["order"]
                order = build_goal(domain_json, environment_json, recipe_json["recipes"][order_name])
                time_to_serve = customer["time_to_serve"]
                enter_time = customer["enter_time"]
                customer = Customer(name, pos, direction, order_name, order, time_to_serve, enter_time, gamemode)
                customer_obj = Object(customer.name, "customer")
                customers.append(customer_obj)
        return customers

    def order_is_satisfied(self, state, gamemode):
        """
        Checks if the order is satisfied.

        Args:
            state (State): The state of the game.
            order_name (str): The name of the order.
            environment_json (dict): The environment json.
            recipe_json (dict): The recipe json.
            gamemode (GameMode): The game mode object.

        Returns:
            bool: True if the order is satisfied, False otherwise.
        """        
        for order in self.order:
            result = True
            for predicate in order:
                result &= state.get_predicate_value(predicate)
            if result:
                return True
        return False
    
    def _get_empty_table(self, gamemode):
        """
        Checks if a table is available for the customer.

        Args:
            state (State): The state of the game.

        Returns:
            table (Object): Returns the first empty table or None if no tables
                are available.
        """
        state = gamemode.get_state()
        customer_tables = []

        for predicate, value in state.predicates.items():
            if predicate.name == "iscustomertable" and value:
                customer_tables.append(predicate.params[0])

        for customer in gamemode.customers.values():
            if customer.assigned_table:
                customer_tables.remove(customer.assigned_table)
        
        for predicate, value in state.predicates.items():
            if predicate.name == "table_occupied" and not value and predicate.params[0] in customer_tables:
                return predicate.params[0]
        return None

    def _is_at_table(self, state):
        """
        Checks if the customer is at a table.

        Args:
            state (State): The state of the game.

        Returns:
            bool: True if the customer is at a table, False otherwise.
        """
        result = False
        for predicate, value in state.predicates.items():
            if predicate.name == "customer_loc" and predicate.params[0].name == self.name and value:
                result = True
        return result

    def step(self, dt, gamemode):
        """
        Steps the customer.

        If the customer has not entered the game, checks if the customer should
        enter the game and into a queue.

        Checks if there are any available tables for the customer to sit at. If
        there are, the customer moves to the table.
        
        If the customer has sat down at a table, decrements the
        time left to serve the customer. Checks if the customer has been served,
        and if the time to serve the customer has expired.

        Updates GameMode class according to whether the customer has been served,
        if they have been served the right order, and if the time to serve the
        customer has expired.

        Args:
            dt (int): The time delta in milliseconds.
            gamemode (GameMode): The game mode object.

        Returns:
            action (Tuple[Action, Dictionary[str, Object]]): The action performed
                by the customer.
        """
        state = gamemode.get_state()

        self.time_passed += dt

        # If the customer is not performing an action, do nothing
        if self.action:
            return None
        
        # If the customer is at a table, decrement the time to serve
        # and check if the customer has been served
        if self._is_at_table(state) and not self.has_been_served:
            self.time_to_serve -= dt
            if self.order_is_satisfied(state, gamemode):
                self.has_been_served = True
        
        # If the customer needs to enter the game, perform the customer_enter action
        # and add the customer to the queue
        elif not self.has_left_queue and self not in gamemode.customer_queue \
            and self.time_passed >= self.enter_time:
            gamemode.customer_queue.append(self)
            for action, param_arg_dict_list in state.npc_actions.items():
                if action.name == "customer_enter":
                    for param_arg_dict in param_arg_dict_list:
                        if param_arg_dict["npc1"].name == self.name:
                            assert action.is_valid(state, param_arg_dict)
                            self.in_game = True
                            return (action, param_arg_dict)
        
        # If the customer is in the queue, check if the customer is at the front of the queue
        # and if there are any available tables
        elif len(gamemode.customer_queue) > 0:
            if gamemode.customer_queue[0] == self:
                self.assigned_table = self._get_empty_table(gamemode)
                if self.assigned_table:
                    gamemode.customer_queue.pop()
        
        # Check if the customer has eaten
        if not self.has_eaten:
            for predicate, value in state.predicates.items():
                if predicate.name == "customer_has_eaten" and value and predicate.params[0].name == self.name:
                    self.has_eaten = True

        # Based on the information above, return the appropriate action
        for action, param_arg_dict_list in state.npc_actions.items():
            for param_arg_dict in param_arg_dict_list:
                # Customer should eat if they have been served and have not eaten
                if not self.has_eaten and self.has_been_served and self.in_game \
                    and action.name == "customer_eat" and param_arg_dict["npc1"].name == self.name:
                    assert action.is_valid(state, param_arg_dict)
                    return (action, param_arg_dict)
                
                # Customer should leave if they have eaten and have been served
                elif self.has_eaten and self.has_been_served and self.in_game and \
                    action.name == "customer_leave" and param_arg_dict["npc1"].name == self.name \
                        and param_arg_dict["s2"].name == "customerspawn1" and param_arg_dict["s1"].name == self.assigned_table.name:
                    assert action.is_valid(state, param_arg_dict)
                    self.in_game = False
                    self.assigned_table = None
                    return (action, param_arg_dict)
                
                # Customer should move to the table if they have been assigned a table
                elif not self.has_left_queue and self.assigned_table and action.name == "customer_move" \
                    and param_arg_dict["npc1"].name == self.name and param_arg_dict["s2"].name == self.assigned_table.name:
                    assert action.is_valid(state, param_arg_dict)
                    self.has_left_queue = True
                    return (action, param_arg_dict)
        return None