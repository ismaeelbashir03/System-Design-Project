import asyncio
import websockets
import json
import ssl
import pathlib


class SocketServer:
    def __init__(self, port, on_connect=None):
        self.port = port
        self.clients = {
            "web": [],
            "ros": [],
            "peripherals": [],
            "face": [],
            "classification": [],
        }
        self.events = {}
        self.on_connect = on_connect

    def on(self, event, callback):
        self.events[event] = callback

    async def broadcast(self, path, event, data):
        for ws in self.clients[path]:
            await ws.send(json.dumps({"event": event, "data": data}))

    async def handler(self, websocket, path):
        path = path[1 : len(path)]
        self.clients[path].append(websocket)

        print(f"New connection: {path}, {len(self.clients[path])} clients connected.")
        if self.on_connect:
            await self.on_connect(websocket, path)
        try:
            while True:
                message = json.loads(await websocket.recv())
                event = message["event"]
                data = message["data"]
                print("Received:", event, data)

                if event in self.events:
                    await self.events[event](websocket, data)
        except websockets.ConnectionClosed:
            self.clients[path].remove(websocket)
            print(
                f"Connection closed: {path}, {len(self.clients[path])} clients connected."
            )

    async def main(self):
        print(f"Websocket server started on port {self.port}")
        async with websockets.serve(self.handler, "", self.port):
            await asyncio.Future()

    def start(self):
        asyncio.run(self.main())
