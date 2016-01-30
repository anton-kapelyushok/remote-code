import asyncio
import websockets


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
		ext_socket = websocket
		await handle_ext(websocket)
	elif path == "/clt":
		clt_socket = websocket
		await handle_clt(websocket)


async def handle_ext(websocket):
	while True:
		listener_task = asyncio.ensure_future(websocket.recv())
		producer_task = asyncio.ensure_future(get_user_input())
		done, pending = await asyncio.wait(
			[listener_task, producer_task],
			return_when=asyncio.FIRST_COMPLETED)

		if listener_task in done:
			pass
		else:
			listener_task.cancel()

		if producer_task in done:
			message = producer_task.result()
			await websocket.send(message)
		else:
			producer_task.cancel()


async def handle_clt(websocket):
	pass


async def get_user_input():
	command = await asyncio.get_event_loop().run_in_executor(executor, input)
	return command


ext_socket = None
clt_socket = None
executor = MyExecutor()
start_server = websockets.serve(handler, 'localhost', 8765)


asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()