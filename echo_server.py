import websockets
import asyncio
import json
import http
from datetime import datetime
from websockets.asyncio.server import ServerConnection


# 1. Tiny custom protocol to intercept the raw HTTP bytes
class RenderSafeConnection(ServerConnection):
    def parse_http_request(self, read_line, headers):
        try:
            return super().parse_http_request(read_line, headers)
        except ValueError as e:
            # Catching Render's HEAD probe exactly the same way
            if "got HEAD" in str(e):
                return http.HTTPStatus.OK, [], b"Server Running"
            raise e


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

	async def broadcast(self, message_dict, exclude_client=None):
		if not self.connected:
			return

		json_string = json.dumps(message_dict)

		broadcast_task = [
			client.send(json_string)
			for client in self.connected
			if client != exclude_client
		]

		if broadcast_task:
			await asyncio.gather(*broadcast_task)

	async def echo(self, websocket):
		self.connected.add(websocket)

		print(f"Connected clients: {len(self.connected)}")

		# 1. Broadcast the new user notification AND the updated client count
		await self.broadcast({
			"type": "notification",
			"text": "A new user has joined the echo server.",
			"timeStamp":   datetime.utcnow().isoformat() + "Z"
		}, exclude_client=websocket)

		await self.broadcast({
			"type": "user_count",
			"count": len(self.connected),
		})

		try:
			async for raw_json in websocket:
				print(f"Received message from client: {raw_json}")
				# raw_json is a valid JSON object

				try:
					# 1. Parse the raw string into a Python dictionary/list
					message_data = json.loads(raw_json)

					# 2. Extract the "type" field from the message, defaulting to "unknown" if not present
					message_type = message_data.get("type", "unknown")

					if message_type != "chat" and message_type != "notification":
						print("Not a chat message or notification, skipping broadcast.")
					else:
						# Broadcast it exactly as is (it already contains text, type, and timestamp)
						# but we exclude the sender, so they don't get a duplicate echo
						await self.broadcast(message_data, exclude_client=websocket)

				except json.JSONDecodeError:
					print("Received invalid JSON payload from client. Ignoring.")

		except websockets.exceptions.ConnectionClosed as ex:
			print("A client just disconnected")
		except json.JSONDecodeError:
			print("Received invalid JSON payload from client. Ignoring.")
		finally:
			self.connected.remove(websocket)
			print(f"Connected clients remaining: {len(self.connected)}")

			await self.broadcast({
				"type": "user_count",
				"count": len(self.connected),
			})

	async def run_server(self):
		print(f"Server listening on port: {self.port}")

		async with websockets.serve(
				self.echo,
				self.host_address,
				self.port,
				process_request=self.process_request,
				ping_interval=20,  # Send a ping frame every 20 seconds
				ping_timeout=20,  # Wait up to 20 seconds for a pong response
				close_timeout=10  # Time allowed for closing handshake
		):
			await asyncio.Future()