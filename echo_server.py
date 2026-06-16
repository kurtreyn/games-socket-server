import websockets
import asyncio
import json

class EchoServer:
	def __init__(self, port: int, host_address: str):
		self.port = port
		self.host_address = host_address
		self.connected = set()

	async def echo(self, websocket):

		self.connected.add(websocket)

		print(f"Connected clients: {len(self.connected)}")

		try:
			async for raw_json in websocket:
				print(f"Received message from client: {raw_json}")
				# raw_json is a valid JSON object

				try:
					# 1. Parse the raw string into a Python dictionary/list
					message_data = json.loads(raw_json)
				except json.JSONDecodeError:
					print("Received invalid JSON payload from client. Ignoring.")
					continue

				# 2. Extract the "type" field from the message, defaulting to "unknown" if not present
				message_type = message_data.get("type", "unknown")

				# 3. Use the original raw_json string to broadcast (saves re-encoding)
				print(f"JSON: {raw_json}")

				for conn in self.connected:
					if conn != websocket:
						if message_type != "chat":
							print("Not a chat message, skipping broadcast.")
						else:
							await conn.send(raw_json)

		except websockets.exceptions.ConnectionClosed as ex:
			print("A client just disconnected")
		except json.JSONDecodeError:
			print("Received invalid JSON payload from client. Ignoring.")
		finally:
			self.connected.remove(websocket)

	async def run_server(self):
		print(f"Server listening on port: {self.port}")

		async with websockets.serve(self.echo, self.host_address, self.port):
			await asyncio.Future()