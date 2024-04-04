# === Imports ===
import time
from SocketClient import SocketClient
import json
import os

# ====== Helpers ======
from Remap import Remap
rm = Remap()

from go_to_point import GoToPose
gtp = GoToPose()


# ====== Global variables ======

# get hub location on startup
global hub_trans, hub_rot	
hub_trans, hub_rot = gtp.listen_to_transform_once()

# === Handlers ===

"""
MISC
"""
def exitFunc(data):
	quit()

"""
MAPPING
"""
def get_map(data):
    path = "maps/map.pgm"
    width, height, depth, data = rm.parsePgm(path)

    websocket.send("receivedMap", {"width": width, "height": height, "depth": depth, "data": data})

"""
MOVEMENT
"""
def go_to_point(data):
	# go to user location
	websocket.send(formatMessage("NavStarting", ""))
	success = gtp.goto(data['x'], data['y'], 0, 0, 0, 1)
	websocket.send("status", {"status": "arrived"})

    
def get_bot_pos(data):
    # get hub location
	x, y = gtp.listen_to_transform_once()
	
	# give success
	websocket.send("BotPosition", {"x": x, "y": y})

def summon(data):

	# decide on bin TODO:
	
	# retrieve bin if needed TODO:
	
	# notify user of bin retrieval
	websocket.send("status", {"status": "moving"})
    
   	# go to user location
	result = gtp.goto(data['x'], data['y'], 0, 0, 0,1)

	# notify user of bin arrival
	websocket.send("status", {"status": "arrived"})
	
	
		
def goHome(data):
	
	global hub_trans, hub_rot
	
	websocket.send("status", {"status": "moving"})
	
	# return to hub
	result = gtp.goto(hub_trans[0], hub_trans[1], hub_rot[0], hub_rot[1], hub_rot[2], 1)
	
	# give success
	if result:
		websocket.send("status", {"status": "home"})
	else:
		websocket.send("status", {"status": "failed"}) 


# === Run ===
websocket = SocketClient(os.environ['WEBSOCKET_SERVER_URL']+'/ros')

# echo
websocket.on('echo', lambda data: print(data))
websocket.send('echo', 'Connected!')

# ====== Events ======
websocket.on("getMap", get_map)
websocket.on("goToPoint", go_to_point)
websocket.on("summon", summon)
websocket.on("exit", exitFunc)
websocket.on("done", goHome)

#websocket.on("getBotPosition", get_bot_pos)

# ====== main ======
websocket.start()
