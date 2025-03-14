class Trade:
    def __init__(self, buy_amount, volume, buy_sequence_number, sell_sequence_number):
        self.buy_amount = buy_amount
        self.volume = volume
        self.sell_amount = None
        self.gain = None

        self.buy_sequence_number = buy_sequence_number
        self.sell_sequence_number = sell_sequence_number
        self.pnl = None


    def update(self, sell_amount, pnl):
        self.sell_amount = sell_amount
        self.gain = sell_amount > self.buy_amount
        self.pnl = pnl
