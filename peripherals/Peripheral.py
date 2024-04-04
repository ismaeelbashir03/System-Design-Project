# ===== helper classes ====== #
from Lid import Lid
from infrared import Sensor

# ===== imports ====== #
from SocketClient import SocketClient
import threading
import time

# ===== global variables ====== #
SENSOR_DELAY = 0.25

# ===== class instances ====== #
l = Lid(motor_id_left = 2, left_button_close = 18, left_button_open = 5, motor_id_right = 0, right_button_close = 24, right_button_open = 22, speed = 87, close_buff = 3)
s = Sensor()

# ===== socket setup ====== #
# server_url = os.environ['WEBSOCKET_SERVER_URL']
server_url = '192.168.170.145:8080'
websocket = SocketClient(f'ws://{server_url}/peripherals')

# ===== workers ====== #
def sense_worker():
    print("starting sensor worker...")
    while True:
        # readding sensor data
        reading_1, reading_2 = s.sense_once()
        websocket.send("fullnessSensor", {"reading1": reading_1, "reading2": reading_2})
        print("Data Sent:", reading_1, reading_2)
        time.sleep(SENSOR_DELAY)


"""
SENSOR WORKER
"""
# Initialize and start the worker thread
worker_thread = threading.Thread(target=sense_worker)
worker_thread.daemon = True  # Daemon threads exit when the program does
worker_thread.start()

"""
LID
"""
def lidHandler(data):

    if data["type"] == "both":
        if data["boolean"]:
            l.open()
            l.open()
    
websocket.on('openLid', lambda x: l.open())
websocket.on('closeLid', lambda x: l.close())


# ===== run ====== #
print("Server started...")
websocket.start()
