from websockets.sync.client import connect
import json

class SocketClient:
    def __init__(self, url) -> None:
        self.socket = connect(url)
        self.events = {}

    def on(self, event, callback):
        self.events[event] = callback

    def send(self, event, data):
        message = json.dumps({"event": event, "data": data})
        self.socket.send(message)

    def start(self):
        while True:
            message = json.loads(self.socket.recv())
            event = message["event"]
            data = message["data"]
            print('Received:', event, data)
            if event in self.events:
                self.events[event](data)
