from SocketClient import SocketClient
from threading import Thread

# ===== socket setup and thread-safe update function ====== #
WEBSOCKET = '192.168.169.145:8080'
client = SocketClient(f'ws://{WEBSOCKET}/web')


def test_response(data):
    print("Got response")
    print(data)

client.send("echo", "connected")

client.on("senseData", test_response)
client.on("echo", lambda x: print(x))

# Keep the script running to maintain the WebSocket connection
# This might need to be adapted based on how your SocketClient library handles connections.

print("test server started...")
# run client in a separate thread
Thread(target=client.start).start()

while True:
    _ = input("press Enter to get sensor data...")
    client.send("sense", {})