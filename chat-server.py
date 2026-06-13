import asyncio
import websockets

# Keep track of all connected client connections
connected_clients = set()


async def chat_handler(websocket):
	# Register the new client connection
	connected_clients.add(websocket)
	print(f"New client connected. Total clients: {len(connected_clients)}")

	try:
		# Listen for messages from this specific client
		async for message in websocket:
			print(f"Received message: {message}")

			# Broadcast the message to all OTHER connected clients
			# Use asyncio.gather to send them out concurrently
			broadcast_tasks = [
				client.send(message)
				for client in connected_clients
				if client != websocket
			]
			if broadcast_tasks:
				await asyncio.gather(*broadcast_tasks)

	except websockets.exceptions.ConnectionClosedError:
		print("A client disconnected abruptly.")
	finally:
		# Unregister the client when they disconnect
		connected_clients.remove(websocket)
		print(f"Client disconnected. Total clients: {len(connected_clients)}")


async def run_server():
	# Start the WebSocket server on localhost, port 8765
	async with websockets.serve(chat_handler, "localhost", 8765):
		print("WebSocket Chat Server is running on ws://localhost:8765")
		await asyncio.Future()  # This keeps the server running indefinitely


if __name__ == "__main__":
	asyncio.run(run_server())