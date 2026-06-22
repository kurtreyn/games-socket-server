from fastapi import WebSocket, WebSocketDisconnect
from connection_manager import ConnectionManager


class GamesManager:
    def __init__(self, connection_manager: ConnectionManager, connect_four_mgr):
        self.connection_manager = connection_manager
        self.connect_four_mgr = connect_four_mgr
        self.connect_four_join_keys = []  # List of join keys for connect four games

    async def add_connect_four_join_key(self):
        retrieved_join_key = await self.connect_four_mgr.get_join_key()
        print(f"Connect Four join key retrieved: {retrieved_join_key}")

    async def remove_connect_four_join_key(self, join_key):
        self.connect_four_join_keys.remove(join_key)

    async def handle_lobby_stream(self, websocket: WebSocket):
        # Accept the new client listening to available games
        await self.connection_manager.connect(websocket)
        print(f"Lobby Listener Connected. Total listeners: {len(self.connection_manager.connections)}")

        try:
            # 1. Immediately send current active matches as soon as they link up
            await websocket.send_json(self._get_lobby_state())

            # 2. Keep the socket connection alive so it stays open!
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            self.connection_manager.disconnect(websocket)
            print(f"Lobby client disconnected.")

    async def broadcast_lobby_update(self):
        """Call this whenever a game is created or destroyed to update all listening clients."""
        await self.connection_manager.broadcast(self._get_lobby_state())

    def _get_lobby_state(self) -> dict:
        """Helper to compile currently joinable game rooms."""
        self.add_connect_four_join_key()

        available_keys = [
            key for key, (game_logic, room_connections) in self.connect_four_mgr.JOIN.items()
            if len(room_connections) < 2
        ]
        return {
            "type": "games_available",
            "games": [
                {"game": "connect_four", "join_key": key} for key in available_keys
            ]
        }