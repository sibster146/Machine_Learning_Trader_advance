import bisect
import numpy as np
from queue import Queue
class OrderBook:
    def __init__(self):
        self.asks = []
        self.bids = []
        self.bids_asks_to_file = Queue()


    def get_size_by_value(self, buy_amount):

        i = 0
        curr_buy_amount = 0
        total_volume = 0
        while i < len(self.asks) and curr_buy_amount < buy_amount:
            curr_price, curr_volume = self.asks[i]
            curr_value = curr_price * curr_volume
            if curr_buy_amount + curr_value > buy_amount:
                needed_value = buy_amount - curr_buy_amount
                total_volume += (needed_value / curr_price)
                return total_volume
            else:
                curr_buy_amount += curr_value
                total_volume += curr_volume
                i+=1

        return total_volume
    
    def get_sell_value_of_volume(self, sell_volume):

        i = 0
        curr_sell_volume = 0
        total_value = 0
        while i < len(self.bids) and curr_sell_volume < sell_volume:
            curr_price, curr_volume = self.bids[i]
            curr_price *= -1
            curr_value = curr_price * curr_volume
            if curr_sell_volume + curr_volume > sell_volume:
                needed_volume = sell_volume - curr_sell_volume
                total_value += (needed_volume * curr_price)
                return total_value
            else:
                total_value += curr_value
                curr_sell_volume += curr_volume
                i+=1
        return total_value







            

    def get_n_level_bids_asks(self, n):

        asks = np.array(self.asks[:n])
        bids = np.array(self.bids[:n])
        bids[:,0] = -bids[:,0]

        return bids,asks


    def get_mid_price(self):
        return (self.asks[0][0] + (-self.bids[0][0])) / 2


    def process_updates(self, updates):
        for update in updates:
            self.update_level(update)


    def find_price_level_binary(self, data, target):
        l = 0
        r = len(data)-1

        while l <= r:
            m = (l+r)//2
            if data[m][0] == target:
                return m
            if data[m][0] > target:
                r = m-1
            else:
                l = m+1
        return -1


    def update_level(self, update):
        side = update["side"]
        new_price = float(update["price_level"])
        new_quantity = float(update["new_quantity"])
        if side == "offer":
            price_level_index = self.find_price_level_binary(self.asks, new_price)
            if new_quantity > 0.0:
                if price_level_index >= 0:
                    self.asks[price_level_index] = (new_price, new_quantity)
                else:
                    bisect.insort(self.asks, (new_price, new_quantity))
            else:
                if price_level_index >= 0:
                    self.asks.pop(price_level_index)
        else:
            new_price = new_price * -1
            price_level_index = self.find_price_level_binary(self.bids, new_price)
            if new_quantity > 0.0:
                if price_level_index >= 0:
                    self.bids[price_level_index] = (new_price,new_quantity)
                else:
                    bisect.insort(self.bids, (new_price, new_quantity))
            else:
                if price_level_index >= 0:
                    self.bids.pop(price_level_index)


    




