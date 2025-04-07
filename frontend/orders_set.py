from frontend.screen import ScreenInterface
from frontend.orders import Order
from frontend.stackable_order import StackableOrder
from frontend.simple_order import SimpleOrder
from frontend.combination_order import CombinationOrder
from frontend.textbox import Textbox
from frontend.image import Image
from frontend.constants import ENDGAME
from frontend.loading import LoadingScreen
import os
import pygame

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "orders"))
TOMATO_SOUP = [
       {
            "predicate": "addedto",
            "args": ["lettuce", "water"],
            "ids": ["x", "b"]
        },
           {
            "predicate": "addedto",
            "args": ["tomato", "water"],
            "ids": ["y", "b"]
        },
           {
            "predicate": "addedto",
            "args": ["tomato", "water"],
            "ids": ["z", "b"]
        },
        {
            "predicate": "addedto",
            "args": ["tomato", "water"],
            "ids": ["a", "b"]
        },
        {
            "predicate": "in",
            "args": ["water", "bowl"],
            "ids": ["b", "d"]
        }
]

HAMBURGER = [
            {
                "predicate": "iscut",
                "args": ["lettuce"],
                "ids": [1]
            },
            {
                "predicate": "iscooked",
                "args": ["patty"],
                "ids": [2]
            },
            {
                "predicate": "atop",
                "args": ["topbun", "lettuce"],
                "ids": [3, 1]
            },
            {
                "predicate": "atop",
                "args": ["lettuce", "patty"],
                "ids": [1, 2]
            },
            {
                "predicate": "atop",
                "args": ["patty", "bottombun"],
                "ids": [2, 4]
            },
            {
                "predicate": "atop_container",
                "args": ["bottombun", "bowl"],
                "ids": [4, 5]
            },
            {
                "predicate": "container_at",
                "args": ["bowl", "customertable"],
                "ids": [5, 6]
            }
        ]

FRIED_CHICKEN = [{
            "predicate": "isfried",
            "args": ["chicken"],
            "ids": [1]
        }]
class OrdersCollection(ScreenInterface):
    def __init__(self, window_size, config):
        """
        Initialize the OrdersCollection screen.  This class manage and display a collection of orders in the game.

        Args:
            window_size (tuple): A tuple (width, height) representing the size of the game window.
        """
        super().__init__(window_size)
        self.score = 0
        self.time = 300
        self.orders = {}

        for count in range(3):
            x_coord = 12 + (count * 161)
            if count == 0: self.add_order(count, CombinationOrder(window_size, config, 50, TOMATO_SOUP, self.x_percent(x_coord) * self.screen_width, 0))
            if count == 1: self.add_order(2, StackableOrder(window_size, config, 8, HAMBURGER, self.x_percent(x_coord) * self.screen_width, 0))
            if count == 2: self.add_order(3, SimpleOrder(window_size, config, 10, FRIED_CHICKEN, self.x_percent(x_coord) * self.screen_width, 0))
        self.score_box = Textbox(self.screen, str(self.score), self.x_percent(1007), self.y_percent(71), 70, 45, font_size=40, scale_factor=self.scale_factor)
        self.time_box = Textbox(self.screen, self.convert_seconds_to_time(self.time) , self.x_percent(1162), self.y_percent(71), 108, 45, font_size=38, scale_factor=self.scale_factor)
        self.score_background = Image(self.screen, self.background_image, self.x_percent(944), self.y_percent(40), self.scale_factor)
        self.last_update_time = pygame.time.get_ticks() 


    def x_percent(self, value):
        """
        Convert a horizontal position value to a scaled screen coordinate, adjusted for the offset.

        Args:
           value (float): Horizontal position value in pixels.

        Returns:
           (float): Adjusted x-coordinate as a percentage of the screen width.
        """
        return (self.scale_factor * value/ self.screen_width)
    
    def y_percent(self, value):
        """
        Convert a vertical position value to a scaled screen coordinate, adjusted for the offset.

        Args:
           value (float): Vertical position value in pixels.

        Returns:
           (float): Adjusted x-coordinate as a percentage of the screen width.
        """
        return (self.scale_factor * value/ self.screen_height)

    def convert_seconds_to_time(self, seconds):
        """
        Converts a given number of seconds into a "MM:SS" formatted string.

        Args:
            seconds (int): The total number of seconds to convert. Must be a non-negative integer.

        Returns:
            str: A string representing the time in "MM:SS" format.

        Raises:
            TypeError: If `seconds` is not an integer.
            ValueError: If `seconds` is negative.
        """
        
        if not isinstance(seconds, int):
            raise TypeError("seconds must be an integer")
        if seconds < 0:
            raise ValueError("seconds cannot be negative")

        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02}:{remaining_seconds:02}"
    
    def update_time(self):
        """
        Update the remaining time by decrementing it based on the elapsed time.
        """
        # updates the game clock
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.last_update_time
        seconds_passed = 0
        if elapsed_time >= 1000:
            seconds_passed = elapsed_time // 1000
            self.time -= seconds_passed
            self.last_update_time += seconds_passed * 1000

            self.time = max(self.time, 0)

            self.time_box.text = self.convert_seconds_to_time(self.time)

            if self.time == 0:
                self.next_screen = ENDGAME

        self.time_box.set_text(self.convert_seconds_to_time(self.time))
        
        # discard expire orders 
        discarded_order = False
        for id, order in list(self.orders.items()):
            order.update(seconds_passed)  
            if order.status == Order.DISCARDED:
                self.complete_order(id)
                discarded_order = True

        # if order is discard, let children know position have been shifted 
        if discarded_order:
            count = 0
            for _, order in self.orders.items():
                x_coord = 12 + (count * 161)
                order.set_offset(self.x_percent(x_coord) * self.screen_width, 0)
                count += 1


    def load_assets(self):
        """
        Load necessary assets for the orders collection screen.
        """
        self.background_image = LoadingScreen.ASSET[ASSETS_DIRECTORY]["score_background.png"]


    def add_order(self, customerid, order):
        """
        Add a new order to the collection.

        Args:
            customerid (int): The ID of the customer associated with the order.
            order (Order): The Order object to be added.
        """
        self.orders[customerid] = order


    def complete_order(self, customerid):
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
        self.screen.fill((0,0,0,0))
        self.score_background.draw()
        self.update_time()
        self.score_box.draw()
        self.time_box.draw()

        count = 0
        for _, order in self.orders.items():
            order.check_hover()
            order.draw()
            x_coord = 12 + (count * 161)
            self.screen.blit(order.get_screen(), (self.x_percent(x_coord) * self.screen_width, 0))
            count += 1
