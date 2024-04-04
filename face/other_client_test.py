from SocketClient import SocketClient
import json

# ===== socket setup and thread-safe update function ====== #
WEBSOCKET = '192.168.214.145:8080'
client = SocketClient(F'ws://{WEBSOCKET}/face')

client.send("echo", "connected")

# Keep the script running to maintain the WebSocket connection
# This might need to be adapted based on how your SocketClient library handles connections.
try:
    while True:
        emotion = input("Press enter to send a message: ")
        client.send("changeEmotion", emotion)
except KeyboardInterrupt:
    quit()
finally:
    client.close()
    print("Connection closed")
