from fastapi import WebSocket, WebSocketDisconnect
from connection_manager import ConnectionManager
from connect_four_processor import ConnectFourProcessor, PLAYER1, PLAYER2
import json


class ConnectFourManager:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.game_processor = ConnectFourProcessor()

    async def handle_game(self, websocket: WebSocket):
        await self.connection_manager.connect(websocket)
        print(f"Connected clients: {len(self.connection_manager.connections)}")

        try:
            while True:
                raw_text = await websocket.receive_text()
                try:
                    message_data = json.loads(raw_text)
                    message_type = message_data.get("type", "unknown")

                    if message_type != "move":
                        print("Not a move message, skipping processing")
                        continue

                    player = message_data.get("player")
                    column = message_data.get("column")

                    if player not in (PLAYER1, PLAYER2):
                        print("Invalid player value, skipping processing")
                        continue

                    if not isinstance(column, int) or not (0 <= column <= 6):
                        print("Invalid column value, skipping processing")
                        continue

                    try:
                        row = self.game_processor.play(player, column)
                        await self.connection_manager.broadcast({
                            "type": "move",
                            "player": player,
                            "column": column,
                            "row": row,
                            "winner": self.game_processor.winner
                        })
                    except ValueError as e:
                        print(f"Move error: {e}")

                except json.JSONDecodeError:
                    print("Received invalid JSON payload from client. Ignoring")

        except WebSocketDisconnect:
            self.connection_manager.disconnect(websocket)
            print(f"A client just disconnected. Remaining clients: {len(self.connection_manager.connections)}")