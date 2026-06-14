import asyncio
import websockets
import json
from datetime import datetime


class ChatServer:
	def __init__(self):
		self.connected_clients = set()

	async def broadcast(self, message_dict, exclude_client=None):
		if not self.connected_clients:
			return

		# Convert Python dictionary (with ISO timestamp) to raw JSON string
		json_string = json.dumps(message_dict)

		broadcast_task = [
			client.send(json_string)
			for client in self.connected_clients
			if client != exclude_client
		]

		if broadcast_task:
			await asyncio.gather(*broadcast_task)

	async def chat_handler(self, websocket):
		# 1. Register new client connection
		self.connected_clients.add(websocket)
		print(f"New client connected. Total clients: {len(self.connected_clients)}")

		# System announcement: Send notification to everyone that someone joined
		await self.broadcast({
			"type": "notification",
			"text": "A new user has joined the chatroom.",
			"timestamp": datetime.utcnow().isoformat() + "Z"  # 'Z' denotes UTC for JavaScript parsing
		}, exclude_client=websocket)

		try:
			# 2. Listen for messages from this specific client
			async for raw_message in websocket:
				print(f"Received raw message string: {raw_message}")

				try:
					# Parse JSON string into a Python dictionary
					message_data = json.loads(raw_message)

					# Broadcast it exactly as is (it already contains text, type, and timestamp)
					# but we exclude the sender so they don't get a duplicate echo
					await self.broadcast(message_data, exclude_client=websocket)

				except json.JSONDecodeError:
					print("Received invalid JSON payload from client. Ignoring")

		except websockets.exceptions.ConnectionClosedError:
			print("Client disconnected abruptly")
		finally:
			# 3. Unregister the client when they disconnect
			self.connected_clients.remove(websocket)
			print(f"Client disconnected. Total clients: {len(self.connected_clients)}")

			# System annoncement: Send notification to everyone remaining
			await self.broadcast({
				"type": "notification",
				"text": "A user has left the chatroom.",
				"timestamp": datetime.utcnow().isoformat() + "Z"
			})

	async def run_server(self):
		# Start the Websocket server on localhost, port 8001
		async with websockets.serve(self.chat_handler, "localhost", 8001):
			print("WebSocket Chat Server is running on ws://localhost:8001")
			await asyncio.Future() # Keeps server running indefinitely



