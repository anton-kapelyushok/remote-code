import asyncio
import websockets
import json


# input is the same for every socket
from concurrent.futures import ThreadPoolExecutor, Future
class MyExecutor(ThreadPoolExecutor):
	input_future = None
	def __init__(self):
		super().__init__(max_workers=1)

	def submit(self, fn, *args, **kwargs):

		if fn == input:
			if self.input_future is not None and not self.input_future.done():
				return self.input_future
			else:
				self.input_future = super().submit(fn, *args, **kwargs)
				return self.input_future

		return super().submit(fn, *args, **kwargs)


async def handler(websocket, path):
	if path == "/ext":
		global ext_socket
		ext_socket = websocket
		await handle_ext(websocket)
	elif path == "/vk":
		await handle_vk(websocket)
	elif path == "/dist":
		await handle_dist(websocket)


async def handle_dist(websocket):
	while True:
		message = await websocket.recv()
		splitted_message = message.split(" ")
		tab_index = int(splitted_message[0])
		command = " ".join(splitted_message[1:])
		request = {}
		request["action"] = "input"
		request["tab_index"] = tab_index
		request["command"] = command
		print(json.dumps(request))
		await ext_socket.send(json.dumps(request))
		await websocket.send("Ты охуел что ли, что ты всякую хуйню тут пишешь?!")


async def handle_ext(websocket):
	while True:
		if not websocket.open:
			return
		receiver_task = asyncio.ensure_future(websocket.recv())
		user_input_task = asyncio.ensure_future(get_user_input())

		done, pending = await asyncio.wait(
			[user_input_task, receiver_task],
			return_when=asyncio.FIRST_COMPLETED)

		for task in pending:
			task.cancel()

		if receiver_task in done:
			if len(vk_connected) > 0:
				await asyncio.wait([ws.send(receiver_task.result()) for ws in vk_connected])

		if user_input_task in done:
			try: 
				print('send user input')
				message = user_input_task.result()
				splitted_message = message.split(" ")
				tab_index = int(splitted_message[0])
				command = " ".join(splitted_message[1:])
				request = {}
				request["action"] = "input"
				request["tab_index"] = tab_index
				request["command"] = command
				await ext_socket.send(json.dumps(request))
			except:
				pass


async def handle_vk(websocket):
	global vk_connected
	vk_connected.add(websocket)	
	try:
		while True:
			message = await websocket.recv()
			print(message)
			if ext_socket:
				await ext_socket.send(message)
	except:
		vk_connected.remove(websocket)


async def get_user_input():
	command = await asyncio.get_event_loop().run_in_executor(executor, input)
	return command


vk_connected = set()
ext_socket = None
clt_socket = None
executor = MyExecutor()
start_server = websockets.serve(handler, '0.0.0.0', 8765)

asyncio.get_event_loop().set_debug(True)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()