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


async def holder(websocket, path):
	while True:
		message = await get_command()
		await websocket.send(message)


async def get_command():
	command = await asyncio.get_event_loop().run_in_executor(executor, input)
	return command


executor = MyExecutor()
start_server = websockets.serve(holder, 'localhost', 8765)


asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()