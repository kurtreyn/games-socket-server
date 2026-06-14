import websockets
import asyncio
# import json

PORT = 8001
connected = set()


async def echo(websocket):
	print("A client just connected")

	connected.add(websocket)

	try:
		async for message in websocket:
			print(f"Received message from client: {message}")
			print(f"Websocket: {websocket}")

			# json_formatted_message = json.loads(message)

			for conn in connected:
				if conn != websocket:
					await conn.send(message)

	except websockets.exceptions.ConnectionClosed as ex:
		print("A client just disconnected")
	finally:
		connected.remove(websocket)


async def start_server():
	print(f"Server listening on port: {PORT}")

	async with websockets.serve(echo, "localhost", PORT):
		await asyncio.Future()


if __name__ == "__main__":
	asyncio.run(start_server())