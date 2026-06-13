import asyncio
import websockets
import json
from datetime import datetime

# Keep track of all connected client connections
connected_clients = set()


async def broadcast(message_dict, exclude_client=None):
	"""
	Helper function to serialize a dictionary to JSON and safely
	broadcast it to all connected clients concurrently.
	"""
	if not connected_clients:
		return

	# Convert Python dict (with ISO timestamp) to a raw JSON string
	json_string = json.dumps(message_dict)

	# Create network tasks for all target clients
	broadcast_tasks = [
		client.send(json_string)
		for client in connected_clients
		if client != exclude_client
	]

	if broadcast_tasks:
		await asyncio.gather(*broadcast_tasks)


async def chat_handler(websocket):
	# 1. Register the new client connection
	connected_clients.add(websocket)
	print(f"New client connected. Total clients: {len(connected_clients)}")

	# System announcement: Send a notification to everyone else that someone joined
	await broadcast({
		"type": "notification",
		"text": "A new user has joined the chatroom.",
		"timestamp": datetime.utcnow().isoformat() + "Z"  # 'Z' denotes UTC for JavaScript parsing
	}, exclude_client=websocket)

	try:
		# 2. Listen for messages from this specific client
		async for raw_message in websocket:
			print(f"Received raw message string: {raw_message}")

			try:
				# Parse JSON string into a Python dictionary to read or manipulate it if needed
				message_data = json.loads(raw_message)

				# We broadcast it exactly as is (it already contains text, type, and timestamp)
				# but we exclude the sender so they don't get a duplicate echo
				await broadcast(message_data, exclude_client=websocket)

			except json.JSONDecodeError:
				print("Received invalid JSON payload from a client. Ignoring.")

	except websockets.exceptions.ConnectionClosedError:
		print("A client disconnected abruptly.")
	finally:
		# 3. Unregister the client when they disconnect
		connected_clients.remove(websocket)
		print(f"Client disconnected. Total clients: {len(connected_clients)}")

		# System announcement: Send a notification to everyone remaining
		await broadcast({
			"type": "notification",
			"text": "A user has left the chatroom.",
			"timestamp": datetime.utcnow().isoformat() + "Z"
		})


async def run_server():
	# Start the WebSocket server on localhost, port 8001
	async with websockets.serve(chat_handler, "localhost", 8001):
		print("WebSocket Chat Server is running on ws://localhost:8001")
		await asyncio.Future()  # Keeps the server running indefinitely


if __name__ == "__main__":
	asyncio.run(run_server())