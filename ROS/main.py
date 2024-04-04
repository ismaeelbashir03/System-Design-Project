from SocketClient import SocketClient
import json
import os

websocket = SocketClient(os.environ['WEBSOCKET_SERVER_URL'])

websocket.on('test', lambda x: print(x))

websocket.start()