# === Imports ===
from SocketServer import SocketServer
import json
import os
from time import sleep

# ====== Helpers ======
from maps import parsePgm

# === State ===
state = {
    "status": "home",
    "queue": [],
    "coordinates": [],
    "lid": [],
}


# === Utils ===
def formatMessage(event, data):
    return json.dumps({"event": event, "data": data})

# === Handlers ===
async def lid(boolean, type="general"):
    print("lid:", boolean)

    # HARD CODED SENSE DATA
    if not boolean:
        data = json.loads(open("sensor_data.json", "r").read())
        data[type] += 5
        open("sensor_data.json", "w").write(json.dumps(data))

    for ws in server.clients["peripherals"]:
        await ws.send(formatMessage("lid", {"boolean": boolean, "type": type}))


async def getMap(websocket, data):
    path = "maps/map.pgm"
    width, height, depth, data = parsePgm(path)
    data = json.dumps({"width": width, "height": height, "depth": depth, "data": data})

    await websocket.send(formatMessage("getMap", data))


async def summon(websocket, data):
    state["queue"].append(data["user"])
    state["coordinates"].append((data["x"], data["y"]))
    state["lid"].append(data["type"])
    await server.broadcast("web", "state", state)

    if len(state["queue"]) == 1:
        for ws in server.clients["ros"]:
            await ws.send(formatMessage("summon", data))


async def status(websocket, data):
    state["status"] = data["status"]

    animation_states = {
        "moving": "moving",
        "arrived": "happy",
        "home": "sleep",
        "done": "thankyou",
    }

    for ws in server.clients["face"]:
        await ws.send(
            formatMessage("changeEmotion", animation_states.get(data["status"]))
        )

    if data["status"] == "arrived":
        await lid(True, state["lid"][0])

    await server.broadcast("web", "state", state)
    for ws in server.clients["web"]:
        await ws.send(formatMessage("status", data))


async def exit(websocket, data):
    for ws in server.clients["ros"]:
        await ws.send(formatMessage("exit", data))
    for ws in server.clients["web"]:
        await ws.send(formatMessage("exit", data))


async def botPosition(websocket, data):
    for ws in server.clients["web"]:
        await ws.send(formatMessage("botPosition", data))


async def changeEmotion(websocket, data):
    for ws in server.clients["face"]:
        await ws.send(formatMessage("changeEmotion", data))


async def sense(websocket, data):
    for ws in server.clients["peripherals"]:
        await ws.send(formatMessage("sense", data))


async def onSense(websocket, data):
    data = json.loads(open("sensor_data.json", "r").read())
    for ws in server.clients["web"]:
        await ws.send(formatMessage("senseData", data))


async def done(websocket, data):
    print("done", state)

    state["queue"].pop(0)
    state["coordinates"].pop(0)
    state["status"] = "done"

    for ws in server.clients["web"]:
        await ws.send(formatMessage("state", state))

    for ws in server.clients["face"]:
        await ws.send(formatMessage("changeEmotion", "thankyou"))

    sleep(2)

    # close the lid
    await lid(False, state["lid"].pop(0))
    # send sense request to peripherals to send to web
    await sense(websocket, {"type": "fullness"})

    if len(state["coordinates"]) > 0:
        for ws in server.clients["ros"]:
            x, y = state["coordinates"][0]
            await ws.send(
                formatMessage("summon", {"user": state["queue"][0], "x": x, "y": y})
            )
    else:
        for ws in server.clients["ros"]:
            await ws.send(formatMessage("done", data))


async def detectWaste(websocket, data):
    print("detectWaste")
    for ws in server.clients["classification"]:
        await ws.send(formatMessage("detectWaste", data))


async def sendWasteDetectionResult(websocket, data):
    print("wasteDetectionResult", data)
    for ws in server.clients["web"]:
        await ws.send(formatMessage("wasteDetectionResult", data))


async def testLid(websocket, data):
    open = data.get("open", False)
    type = data.get("type", "general")
    await lid(open, type)


# === On Connect ===
async def on_connect(websocket, path):
    await websocket.send(formatMessage("state", state))


# === Run ===
server = SocketServer(os.environ["WEBSOCKET_PORT"], on_connect)

# ====== Events ======
server.on("echo", lambda ws, data: ws.send(formatMessage("echo", data)))
server.on("getMap", getMap)
server.on("summon", summon)
server.on("status", status)
server.on("exit", exit)
server.on("botPosition", botPosition)
server.on("changeEmotion", changeEmotion)
server.on("sense", sense)
server.on("fullnessSensor", onSense)
server.on("done", done)
server.on("detectWaste", detectWaste)
server.on("wasteDetectionResult", sendWasteDetectionResult)
server.on("testLid", testLid)

if __name__ == "__main__":
    server.start()
