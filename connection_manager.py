from fastapi import WebSocket


class ConnectionManager:
	def __init__(self):
		self.connections: set[WebSocket] = set()

	async def connect(self, websocket: WebSocket):
		await websocket.accept()
		self.connections.add(websocket)

	def disconnect(self, websocket: WebSocket):
		self.connections.remove(websocket)

	async def broadcast(self, message_dict: dict, exclude: WebSocket = None):
		if not self.connections:
			return

		for connection in self.connections:
			if connection != exclude:
				# FastAPI handles the json.dumps() internally
				await connection.send_json(message_dict)