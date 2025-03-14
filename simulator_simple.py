from websocket import WebSocket
from queue import Queue
import threading
from orderbook import OrderBook
from collections import deque
import traceback
from trade import Trade
from datetime import datetime
import os
import csv
import time
import pickle
from model import BinaryRegressor

class Simulator:
    def __init__(self, symbol, binary_regression_model):
        self.symbol = symbol
        self.binary_regression_model = binary_regression_model
        self.orderbook = OrderBook()
        self.websocket_updates_queue = Queue() # updates from exchange
        self.completed_trades_queue = Queue() 
        self.exposure = deque() 
        self.websocket = WebSocket(self.websocket_updates_queue)
        self.process_websocket_updates_queue_thread = threading.Thread(target=self.process_websocket_updates_queue)
        self.process_completed_trades_queue_thread = threading.Thread(target = self.process_completed_trades_queue)
        self.completed_trades_filename = f"simple_simulations/{symbol}_{datetime.now()}_{self.binary_regression_model.name}.csv"

    def start(self):
        print("starting application")
        self.process_websocket_updates_queue_thread.start()
        self.process_completed_trades_queue_thread.start()
        self.websocket.open_socket(self.symbol)

    def stop(self):
        print("closing application")
        self.websocket.close_socket()
        self.websocket_updates_queue.put(None)
        self.completed_trades_queue.put(None,None,None)
        self.process_websocket_updates_queue_thread.join()
        self.process_completed_trades_queue_thread.join()

    def process_completed_trades_queue(self):

        # mid price, buy price, sell price
        while True:
            trade_seq_num, trade_type, trade_price = self.completed_trades_queue.get()
            if trade_seq_num == None:
                return
            
            if not os.path.exists(self.completed_trades_filename):
                column_names = ["sequence_number","type","price"]
                with open(self.completed_trades_filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(column_names)

            values = [trade_seq_num, trade_type, trade_price]
            with open(self.completed_trades_filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(values)

            self.completed_trades_queue.task_done()

        



    def process_msg(self, msg_json):
        try:

            if "updates" in msg_json["events"][0]:

                sequence_number = msg_json["sequence_num"]
                updates = msg_json["events"][0]["updates"]
                self.orderbook.process_updates(updates)
                curr_mid_price = self.orderbook.get_mid_price()
                self.completed_trades_queue.put((sequence_number, 0, curr_mid_price))
                bids, asks = self.orderbook.get_n_level_bids_asks(self.binary_regression_model.price_level_num)
                timestamp_str = msg_json["timestamp"]
                up, predicted_sell_price, back_lag_price = self.binary_regression_model.create_inference_vector(bids, asks, timestamp_str)
                
                if predicted_sell_price !=-1:
                    self.completed_trades_queue.put((sequence_number+self.binary_regression_model.update_lag, 1, predicted_sell_price ))
  
        except Exception as e:
            print(" Error in processing update ", e, "\n")
            traceback.print_exc()

    def process_websocket_updates_queue(self):
        while True:
            msg_json = self.websocket_updates_queue.get()
            if msg_json == None:
                return
            
            self.process_msg(msg_json)
            self.websocket_updates_queue.task_done()

    

    



filename = "50_new_update_linear_regressor.pkl"
with open(filename, 'rb') as file:
    loaded_model = pickle.load(file)

price_level_num = 10
historical_inference_max_length = 5000000
update_lag = 50
percent_gain = 0.0001
binary_regressor = BinaryRegressor(binary_regressor_model=loaded_model, price_level_num=price_level_num, historical_inference_max_length=historical_inference_max_length, update_lag = update_lag, percent_gain = percent_gain, filename = filename, simple = True)

simulator = Simulator(symbol ="BTC-USD", binary_regression_model=binary_regressor)

simulator.start()
time.sleep(1000)
simulator.stop()





