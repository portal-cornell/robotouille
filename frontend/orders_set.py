from frontend.constants import *
from frontend.screen import ScreenInterface
from frontend.orders import Order

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "pause_screen"))

class OrdersCollection(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the Order Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size)
        self.orders = {}
        self.addOrder(1, Order(window_size))
        self.addOrder(2, Order(window_size))
        self.addOrder(3, Order(window_size))
        
       
    def load_assets(self):
        pass
      
    
    def addOrder(self, customerid, order):
        self.orders[customerid] = order
        self.update()

    def completeOrder(self, customerid):
        self.orders.pop(customerid)
        self.update()
        
    
    def draw(self):
        """Draws all the screen components."""
        count = 0
        for _, order in self.orders.items():
            order.draw()
            x_coord = 12 + (count * 161)
            self.screen.blit(order.get_screen(), (self.x_percent(x_coord) * self.screen_width, 0))
            count += 1
        
        
