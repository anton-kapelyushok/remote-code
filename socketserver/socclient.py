import asyncio
import websockets
import json
import sys

async def hello():
	async with websockets.connect('ws://localhost:8765/vk') as websocket:
		dic = {
			"action": "vk",
			"command": sys.argv[1]
		}

		await websocket.send(json.dumps(dic))

		message = await websocket.recv()
		print("< {}".format(message))

asyncio.get_event_loop().run_until_complete(hello())