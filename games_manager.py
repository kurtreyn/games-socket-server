from fastapi import WebSocket, WebSocketDisconnect
from connection_manager import ConnectionManager

class GamesManager:
    def __init__(self, connection_manager: ConnectionManager, connect_four_mgr):
        self.connection_manager = connection_manager
        self.connect_four_mgr = connect_four_mgr

    async def handle_lobby_stream(self, websocket: WebSocket):
        await self.connection_manager.connect(websocket)
        print(f"Lobby Listener Connected. Total listeners: {len(self.connection_manager.connections)}")

        try:
            # Send current active matches instantly on setup
            await websocket.send_json(self._get_lobby_state())

            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            self.connection_manager.disconnect(websocket)
            print(f"Lobby client disconnected.")

    async def broadcast_lobby_update(self):
        """Call this whenever a game is created or destroyed to update all listening clients."""
        await self.connection_manager.broadcast(self._get_lobby_state())

    def _get_lobby_state(self) -> dict:
        """Helper to compile currently joinable game rooms directly from memory state."""
        # ✅ Standard synchronized list comprehension reading right from the manager dictionary
        available_keys = [
            key for key, (game_logic, room_connections) in self.connect_four_mgr.JOIN.items()
            if len(room_connections) < 2
        ]
        return {
            "type": "games_available",
            "games_available": [
                {"game": "connect_four", "join_key": key} for key in available_keys
            ]
        }