from backend.object import Object
from backend.predicate import Predicate
from robotouille.env_utils import build_goal

class Customer(object):
    """
    The Customer class represents a customer in Robotouille.

    Customers are non-player characters that require a player to deliver some
    order to them. 
    """

    customers = {}
    id_counter = 0
    customer_queue = []

    def __init__(self, name, pos, direction, order, time_to_serve, enter_time):
        """
        Initializes the customer object.

        Args:
            name (str): The name of the customer.
            pos (tuple): The position of the customer in the form (x, y).
            direction (tuple): The unit vector of the customer's direction.
            order (List[Predicate]): The order the customer requires.
            time_to_serve (int): The time left that the player has to serve the 
                customer in milliseconds.
            enter_time (int): The time at which the customer enters the game
                in milliseconds.
        """
        self.id = Customer.id_counter
        self.name = name
        self.pos = pos
        self.direction = direction
        self.order = order
        self.time_to_serve = time_to_serve
        self.enter_time = enter_time
        self.has_been_served = False
        self.in_game = False
        self.has_left_queue = False
        self.sprite_value = 0
        self.action = None
        Customer.id_counter += 1
        Customer.customers[name] = self

    def build_order(order_name, environment_json, recipe_json):
        """
        Builds an order depending on the recipe json by creating a list of 
        predicates.

        Args:
            order_name (str): The name of the recipe
            environment_json (dict): The environment json.
            recipe_json (dict): The recipe json
        
        Returns:
            order (List[Predicate]): The order the customer requires.
        """
        return build_goal(environment_json, recipe_json["recipes"][order_name])[0]
    
    def build_customers(environment_json, recipe_json):
        """
        Builds the customers in the environment.

        Args:
            environment_json (dict): The environment json.
            recipe_json (dict): The recipe_json

        Returns:
            customers (list[Object]): A list of customer objects to be added to
                the state.

        Modifies:
            Adds customers to Customer.customers
        """
        customers = []
        if environment_json.get("customers"):
            for customer in environment_json["customers"]:
                name = customer["name"]
                pos = (customer["x"], customer["y"])
                direction = (customer["direction"][0], customer["direction"][1])
                order = Customer.build_order(customer["order"], environment_json, recipe_json)
                time_to_serve = customer["time_to_serve"]
                enter_time = customer["enter_time"]
                customer = Customer(name, pos, direction, order, time_to_serve, enter_time)
                customer_obj = Object(customer.name, "customer")
                customers.append(customer_obj)
        return customers

    def get_order(self):
        """
        Gets the order of the customer.

        Returns:
            order (List[Predicate]): The order the customer requires.
        """
        return self.order

    def order_is_satisfied(self, state):
        """
        Checks if the order is satisfied.

        Args:
            state (State): The state of the game.

        Returns:
            bool: True if the order is satisfied, False otherwise.
        """
        result = True
        for predicate in self.order:
            result &= state.get_predicate_value(predicate)
        return result
    
    def _get_empty_table(self, state):
        """
        Checks if a table is available for the customer.

        Args:
            state (State): The state of the game.

        Returns:
            table (Object): Returns the first empty table or None if no tables
                are available.
        """
        customer_tables = []

        for predicate, value in state.predicates.items():
            if predicate.name == "iscustomertable" and value:
                customer_tables.append(predicate.params[0])

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
            if predicate.name == "customer_loc" and predicate.params[0] == Object(self.name, "customer") and value:
                result = True
        return result

    def step(self, time, state):
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
            time (pygame.time): The time object.
            state (State): The game state.

        Returns:
            action (Tuple[Action, Dictionary[str, Object]]): The action performed
                by the customer.
        """
        table_to_move_to = None

        if self.action:
            return None

        if self._is_at_table(state):
            clock = time.Clock()
            self.time_to_serve -= clock.get_time()
            if self.order_is_satisfied(state):
                self.has_been_served = True
                
        elif not self.has_left_queue and self not in Customer.customer_queue \
            and time.get_ticks() >= self.enter_time:
            Customer.customer_queue.append(self)
            for action, param_arg_dict_list in state.npc_actions.items():
                if action.name == "customer_enter":
                    for param_arg_dict in param_arg_dict_list:
                        if param_arg_dict["c1"].name == self.name:
                            assert action.is_valid(state, param_arg_dict)
                            self.in_game = True
                            return (action, param_arg_dict)
        
        elif len(Customer.customer_queue) > 0:
            if Customer.customer_queue[0] == self:
                table_to_move_to = self._get_empty_table(state)
                if table_to_move_to:
                    Customer.customer_queue.pop()

        # Customer can either leave or move to a table, but not both
        assert not (self.has_been_served and table_to_move_to)

        for action, param_arg_dict_list in state.npc_actions.items():
            for param_arg_dict in param_arg_dict_list:
                if self.has_been_served and self.in_game and action.name == "customer_leave" and param_arg_dict["c1"].name == self.name and param_arg_dict["s2"].name == "customerspawn1":
                    assert action.is_valid(state, param_arg_dict)
                    self.in_game = False
                    return (action, param_arg_dict)
                if table_to_move_to and action.name == "customer_move" and param_arg_dict["c1"].name == self.name and param_arg_dict["s2"].name == table_to_move_to.name:
                    assert action.is_valid(state, param_arg_dict)
                    self.has_left_queue = True
                    return (action, param_arg_dict)
        return None