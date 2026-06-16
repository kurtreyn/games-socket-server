import websockets
import asyncio
import json
import http


class EchoServer:
	def __init__(self, port: int, host_address: str):
		self.port = port
		self.host_address = host_address
		self.connected = set()

	# METHOD to catch Render's Health Checks
	async def process_request(self, *args, **kwargs):
		request = args[-1] if args else kwargs.get("request")
		if not request:
			return None

		# Fallback to headers: Render health checks always send specific paths/methods
		# In websockets v14, headers behaves like a standard dict-like lookup
		headers = getattr(request, "headers", {})

		# Method 1: Check the raw path if available (most reliable way to intercept pings)
		path = getattr(request, "path", "")

		# Render's health check pings the root directory "/" with a HEAD request.
		# Standard users connecting via WebSockets use "ws://..." or "wss://..." with an Upgrade header.
		if "upgrade" not in headers:
			# If there's no upgrade header, it's a web probe (like Render's HEAD or GET health checks)
			# We can safely return 200 OK right here to pass the check!
			return http.HTTPStatus.OK, [], b"Server Running"

		return None  # If "upgrade" is present, let it proceed to normal WebSocket logic

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

		async with websockets.serve(
				self.echo,
				self.host_address,
				self.port,
				process_request=self.process_request
		):
			await asyncio.Future()