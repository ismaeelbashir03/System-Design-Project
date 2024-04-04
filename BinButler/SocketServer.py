import asyncio
import websockets
import json

class SocketServer:
	def __init__(self):
		self.events = {}
	
	def on(self, event, callback):
		self.events[event] = callback
		
	async def handler(self, websocket):
		print("Client connected...")
		while True:
			try:
				message = json.loads(await websocket.recv())
				event = message["event"]
				data = message["data"]
				
				if event in self.events:
					self.events[event](data)
					
			except websockets.exceptions.ConnectionClosedError:
				print("Client disconnected...")
				break
				
	async def run(self):
		async with websockets.serve(self.handler, "", 8080):
			await asyncio.Future()
					
		
					
					
