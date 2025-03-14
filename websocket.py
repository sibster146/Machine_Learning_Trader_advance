from dotenv import load_dotenv
import os
import sys
import json
from coinbase.websocket import WSClient
from queue import Queue

class WebSocket:
    def __init__(self, updates_queue):

        load_dotenv()
        api_key = os.getenv("COINBASE_API_NAME")
        secret_key = os.getenv("COINBASE_PRIVATE_KEY")
        if secret_key:
            secret_key = secret_key.replace("\\n", "\n")

        self.ws_client = WSClient(api_key=api_key, api_secret=secret_key, on_message=self.on_message, verbose=False)
        self.ws_updates_queue = updates_queue
        self.sequence_num = 0
        self.on = False

    def on_message(self, msg):
        msg_json = json.loads(msg)
        update_seq_num = msg_json["sequence_num"]
        if self.sequence_num != update_seq_num:
            print("Sequence Number is Wrong")
            return
        self.sequence_num += 1
        self.ws_updates_queue.put(msg_json)

    def close_socket(self):
        self.on = False
        self.ws_client.close()

    def open_socket(self, symbol):
        self.on = True
        self.sequence_num = 0
        self.ws_client.open()
        self.ws_client.subscribe([symbol], ["level2"])
        while self.on:
            self.ws_client.run_forever_with_exception_check()


