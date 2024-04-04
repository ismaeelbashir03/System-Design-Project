# ===== helper classes ====== #
from classification import WasteClassification

# ===== imports ====== #
from SocketClient import SocketClient
import json
import queue
import threading

# ===== global variables ====== #
user_queue = queue.Queue()

# ===== settings ====== #
MAX_QUEUE_SIZE = 100 # Credit: Daniel (The Lizzzard)

# ===== class instances ====== #
wc = WasteClassification()

# ===== socket setup ====== #
# server_url = os.environ['WEBSOCKET_SERVER_URL']
server_url = '192.168.170.118:8080'
websocket = SocketClient(f'ws://{server_url}/classification')

# ===== callbacks ====== #


"""
DETECT WASTE
"""
def detect_waste(data):

    print(f"recieved image, adding to queue...")
    if user_queue.qsize() < MAX_QUEUE_SIZE:
        user_queue.put([data["username"], data["image"]])
    else:
        websocket.send(
            "wasteDetectionResult", 
            json.dumps({"cup": False, "material": "Queue is full, please try again later"})
        )

# ===== worker function ====== #
def worker():
    while True:
        # Get an item from the queue
        username, data = user_queue.get()

        print("Received image...")

        # Process the item (this is your existing logic moved into the worker)
        image = wc.base64_to_image(data.split(",")[1])
        material_class, cup_class = wc.classify(image)

        print("Waste detected")
        print(f"Material class: {material_class}")
        print(f"Cup class: {cup_class}")

        websocket.send(
            "wasteDetectionResult", 
            json.dumps({"username": username, "cup": True if cup_class == "cups" else False, "material": material_class})
        )

        # Mark the processed task as done
        user_queue.task_done()

# ===== socket callbacks ====== #
websocket.on('detectWaste', detect_waste)

# # ===== run ====== #
print("Server started...")

# Initialize and start the worker thread
worker_thread = threading.Thread(target=worker)
worker_thread.daemon = True  # Daemon threads exit when the program does
worker_thread.start()

websocket.start()

# ===== tests ====== #

