# ===== helper classes & imports ====== #
from face import Face
from SocketClient import SocketClient
from threading import Thread
import queue
import os

# Set the DISPLAY environment variable (for ssh)
os.environ['DISPLAY'] = ':0'

# ===== settings ====== #
MAX_QUEUE_SIZE = 100 # Credit: Daniel (The Lizzzard)

# ===== class instances and initial setup ====== #
f = Face()
websocket_queue = queue.Queue()

# ===== socket setup and thread-safe update function ====== #
WEBSOCKET = os.environ.get('WEBSOCKET', 'localhost:8080')
WEBSOCKET = '192.168.214.145:8080'
websocket = SocketClient(F'ws://{WEBSOCKET}/face')

def update_face_from_websocket():
    """
    This function is called in a separate thread to update the face from the websocket
    (used this as tkinter was being a pain with threading and queues, so this was easier to implement)
    """

    while True:
        # blocks until a message is received
        message = websocket_queue.get()  
        f.change_emotion(message)

# ===== websocket callback modification ====== #
def on_change_emotion(message):
    """
    This function is called when the websocket receives a message
    """

    # queue the message for processing by the main thread
    websocket_queue.put(message)  

websocket.on('changeEmotion', on_change_emotion)

# ===== run websocket in a separate thread ====== #
Thread(target=websocket.start).start()

# ===== Tkinter main loop modification for polling the queue ====== #
def check_websocket_queue():
    try:
        for x in range(MAX_QUEUE_SIZE):  
            # do all messages currently in the queue
            message = websocket_queue.get_nowait()
            print('got message:', message)
            f.change_emotion(message)

    except queue.Empty:
        pass

    # after 100ms, check again
    finally:
        f.after(100, check_websocket_queue)  # Check again after 100ms

websocket.send("echo", {"connected": "true"})
f.after(100, check_websocket_queue)  # Start polling the queue
f.mainloop()
