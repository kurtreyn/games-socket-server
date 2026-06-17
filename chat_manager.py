from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
from connection_manager import ConnectionManager
import json


class ChatManager:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager

    async def handle_websocket_chat(self, websocket: WebSocket):
        await self.connection_manager.connect(websocket)
        print(f"Connected clients: {len(self.connection_manager.connections)}")

        # Broadcast new user notification and update count
        await self.connection_manager.broadcast({
            "type": "notification",
            "text": "A new user has joined",
            "timeStamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }, exclude=websocket)

        await self.connection_manager.broadcast({
            "type": "user_count",
            "count": len(self.connection_manager.connections),
        })

        try:
            while True:
                raw_text = await websocket.receive_text()
                try:
                    message_data = json.loads(raw_text)
                    message_type = message_data.get("type", "unknown")

                    if message_type not in ("chat", "notification"):
                        print("Not a chat message or notification, skipping broadcast")
                    else:
                        await self.connection_manager.broadcast(message_data, exclude=websocket)

                except json.JSONDecodeError:
                    print("Received invalid JSON payload from client. Ignoring")

        except WebSocketDisconnect:
            self.connection_manager.disconnect(websocket)
            print(f"A client just disconnected. Remaining clients: {len(self.connection_manager.connections)}")

            await self.connection_manager.broadcast({
                "type": "user_count",
                "count": len(self.connection_manager.connections),
            })