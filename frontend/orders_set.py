from frontend.constants import *
from frontend.screen import ScreenInterface
from frontend.orders import Order

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "pause_screen"))

class OrdersCollection(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the OrdersCollection screen.  This class manage and display a collection of orders in the game.

        Args:
            window_size (tuple): A tuple (width, height) representing the size of the game window.
        """
        super().__init__(window_size)
        self.orders = {}
        self.addOrder(1, Order(window_size))
        self.addOrder(2, Order(window_size))
        self.addOrder(3, Order(window_size))


    def load_assets(self):
        """
        Load necessary assets for the orders collection screen.
        """
        pass


    def addOrder(self, customerid, order):
        """
        Add a new order to the collection.

        Args:
            customerid (int): The ID of the customer associated with the order.
            order (Order): The Order object to be added.
        """

        self.orders[customerid] = order


    def completeOrder(self, customerid):
        """
        Remove an order from the collection after it is completed.

        Args:
            customerid (int): The ID of the customer whose order is to be removed.
        """
        self.orders.pop(customerid, None)


    def draw(self):
        """
        Draw all orders on the screen.

        Side Effect:
            Blits each order onto the screen at appropriate positions.
        """
        count = 0
        for _, order in self.orders.items():
            order.draw()
            x_coord = 12 + (count * 161)
            self.screen.blit(order.get_screen(), (self.x_percent(x_coord) * self.screen_width, 0))
            count += 1
