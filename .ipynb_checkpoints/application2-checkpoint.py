from websocket import WebSocket
from queue import Queue
import threading
from orderbook import OrderBook
from collections import deque
import traceback

class Simulator:
    def __init__(self, symbol, binary_regression_model):
        self.pnl = 0
        self.symbol = symbol
        self.binary_regression_model = binary_regression_model
        self.orderbook = OrderBook()
        self.websocket_updates_queue = Queue() # updates from exchange
        self.exposure = deque() # (sell_sequence_num, price_bought)
        self.websocket = WebSocket(self.websocket_updates_queue)
        self.process_websocket_updates_queue_thread = threading.Thread(target=self.process_update_queue)

    def start(self):
        print("starting application")
        self.process_websocket_updates_queue_thread.start()
        self.websocket.open_socket(self.symbol)

    def stop(self):
        print("closing application")
        self.websocket.close_socket()
        self.websocket_updates_queue.put(None)
        self.process_websocket_updates_queue_thread.join()

    def process_msg(self, msg_json):
        try:

            if "updates" in msg_json["events"][0]:

                sequence_number = msg_json["sequence_num"]
                updates = msg_json["events"][0]["updates"]
                self.orderbook.process_updates(updates)

                while self.exposure and self.exposure[0][0] <= sequence_number:
                    _, buy_price = self.exposure.popleft()
                    sell_price = self.orderbook.get_mid_price()
                    self.pnl += (sell_price - buy_price)
                    print(self.pnl)

                bids, asks = self.orderbook.get_n_level_bids_asks(self.model.price_level_num)
                timestamp_str = msg_json["timestamp"]
                up = self.binary_regression_model.create_inference_vector(bids, asks, timestamp_str)
                if up:
                    update_lag = self.binary_regression_model.update_lag
                    sell_sequence_num = sequence_number + update_lag
                    buy_price = self.orderbook.get_mid_price()
                    self.exposure.append((sell_sequence_num, buy_price))

                

        except Exception as e:
            print(" Error in processing update ", e, "\n")
            # print(msg_json)
            traceback.print_exc()

    def process_websocket_updates_queue_thread(self):
        while True:
            msg_json = self.websocket_updates_queue.get()
            if msg_json == None:
                return
            
            self.process_msg(msg_json)

    

    






