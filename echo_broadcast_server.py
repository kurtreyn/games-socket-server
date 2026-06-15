import websockets
import asyncio
import json

PORT = 8001
connected = set()


async def echo(websocket):
	print("A client just connected")

	connected.add(websocket)

	try:
		async for raw_message in websocket:
			print(f"Received message from client: {raw_message}")

			try:
				# 1. Parse the raw string into a Python dictionary/list
				message_data = json.loads(raw_message)
			except json.JSONDecodeError:
				print("Received invalid JSON payload from client. Ignoring.")
				continue

			# 2. Extract the "type" field from the message, defaulting to "unknown" if not present
			message_type = message_data.get("type", "unknown")

			# 3. Use the original raw_message string to broadcast (saves re-encoding)
			print(f"JSON: {raw_message}")

			json_formatted_message = json.dumps(raw_message)
			print(f"JSON: {json_formatted_message}")

			for conn in connected:
				if conn != websocket:
					if message_type != "chat":
						print("Not a chat message, skipping broadcast.")
					else:
						await conn.send(json_formatted_message)

	except websockets.exceptions.ConnectionClosed as ex:
		print("A client just disconnected")
	except json.JSONDecodeError:
		print("Received invalid JSON payload from client. Ignoring.")
	finally:
		connected.remove(websocket)


async def start_server():
	print(f"Server listening on port: {PORT}")

	async with websockets.serve(echo, "localhost", PORT):
		await asyncio.Future()


if __name__ == "__main__":
	asyncio.run(start_server())