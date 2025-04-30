import time

class OrderController:
    def __init__(self, config):
        self.active_orders = {}      # customer_id -> Order
        self.completed_orders = []   # (customer_id, timestamp)
        self.failed_orders = []      # (customer_id, timestamp)
        self.start_time = time.time()
        self.config = config         # Comes from GameMode

    def add_order(self, customer):
        self.active_orders[customer.id] = {
            "customer": customer,
            "start_time": time.time(),
            "deadline": time.time() + (customer.time_to_serve / 1000)
        }

    def mark_order_completed(self, customer_id):
        if customer_id in self.active_orders:
            self.completed_orders.append((customer_id, time.time()))
            del self.active_orders[customer_id]

    def mark_order_failed(self, customer_id):
        if customer_id in self.active_orders:
            self.failed_orders.append((customer_id, time.time()))
            del self.active_orders[customer_id]

    def get_global_time(self):
        return int(time.time() - self.start_time)

    def get_completed_order_ids(self):
        return [cid for cid, _ in self.completed_orders]

    def get_remaining_time(self, customer_id):
        if customer_id in self.active_orders:
            return max(0, self.active_orders[customer_id]["deadline"] - time.time())
        return None

    def get_score(self):
        return {
            "stars": len(self.completed_orders),
            "bells": 0,
            "coins": len(self.completed_orders) * 10,
            "timer": 30  # placeholder for play-again countdown
        }
