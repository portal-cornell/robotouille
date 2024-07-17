from backend.predicate import Predicate

# TODO: Draft out predicates for customer. Customer tables are also stations 
# since players need to be able to move to them and place items down. 

class Customer(object):
    """
    The Customer class represents a customer in Robotouille.

    Customers are non-player characters that require a player to deliver some
    order to them. 
    """

    customers = {}
    id_counter = 0

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
        pass
    
    def build_customers(environment_json):
        """
        Builds the customers in the environment.

        Args:
            environment_json (dict): The environment json.
        """
        pass

    def get_order(self):
        """
        Gets the order of the customer.

        Returns:
            order (List[Predicate]): The order the customer requires.
        """
        pass

    def order_is_satisfied(self, order, state):
        """
        Checks if the order is satisfied.

        Args:
            order (List[Predicate]): The order to check.
            state (State): The state of the game.

        Returns:
            bool: True if the order is satisfied, False otherwise.
        """
        pass

    def _table_is_available(self, state):
        """
        Checks if a table is available for the customer.

        Args:
            state (State): The state of the game.

        Returns:
            bool: True if the table is available, False otherwise.
        """
        pass

    def _move_to_table(self, state):
        """
        Moves the customer to a table.

        Args:
            state (State): The state of the game.
        """
        pass

    def step(self):
        """
        Steps the customer.

        TODO: For now, all customers enter from the bottom left tile. The 
        bottom row of tiles acts as a queue. In the future, find a way to make
        this customisable through the environment json.

        If the customer has not entered the game, checks if the customer should
        enter the game and into a queue.

        If there is already a customer in the queue, the queue shifts left by one,
        and the customer enters the game.

        Checks if there are any available tables for the customer to sit at. If
        there are, the customer moves to the table.
        
        If the customer has entered the game, decrements the
        time left to serve the customer. Checks if the customer has been served,
        and if the time to serve the customer has expired.

        Updates GameMode class according to whether the customer has been served,
        if they have been served the right order, and if the time to serve the
        customer has expired.
        """
        pass