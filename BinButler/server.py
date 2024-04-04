import asyncio
from SocketServer import SocketServer
from Move import Move
from Remap import Remap

async def main():
	
	mv = Move()
	rm = Remap()
	
	server = SocketServer()
	server.on("forward", lambda x:mv.move("forward"))
	server.on("backward", lambda x:mv.move("back"))
	server.on("left", lambda x:mv.move("left"))
	server.on("right", lambda x:mv.move("right"))
	server.on("startMapping", lambda x:rm.remap())
	await server.run()
	
asyncio.run(main())	
