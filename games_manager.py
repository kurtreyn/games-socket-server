from fastapi import WebSocket, WebSocketDisconnect
from connection_manager import ConnectionManager


class GamesManager:
    def __init__(self, connection_manager: ConnectionManager, connect_four_mgr, rummy_manager):
        self.connection_manager = connection_manager
        self.connect_four_mgr = connect_four_mgr
        self.rummy_mgr = rummy_manager

    async def handle_lobby_stream(self, websocket: WebSocket):
        await self.connection_manager.connect(websocket)
        print(f"Lobby Listener Connected. Total listeners: {len(self.connection_manager.connections)}")

        try:
            # 1. Fetch the raw open rooms for both games safely
            c4_rooms = self._get_open_rooms("connect_four")
            rummy_rooms = self._get_open_rooms("rummy")

            # 2. Combine them seamlessly into a single consolidated array
            all_games_lobby_state = {
                "type": "games_available",
                "games_available": c4_rooms + rummy_rooms  # Safely merges lists even if they're empty!
            }

            print(f"Unified Lobby Broadcast Payload: {all_games_lobby_state}")
            await websocket.send_json(all_games_lobby_state)

            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            self.connection_manager.disconnect(websocket)
            print(f"Lobby client disconnected.")

    async def broadcast_lobby_update(self):
        """Call this whenever a game is created or destroyed to update all listening clients."""
        unified_state = {
            "type": "games_available",
            "games_available": self._get_open_rooms("connect_four") + self._get_open_rooms("rummy")
        }
        await self.connection_manager.broadcast(unified_state)

    def _get_open_rooms(self, game_type) -> list:
        """Helper to return an array of available rooms for a specific game type."""
        mgr = self.connect_four_mgr if game_type == "connect_four" else self.rummy_mgr

        # Extract keys where room connections are less than 2
        available_keys = [
            key for key, (game_logic, room_connections) in mgr.JOIN.items()
            if len(room_connections) < 2
        ]
        # Return a flat list of room dictionaries
        return [{"game": game_type, "join_key": key} for key in available_keys]

    def _get_lobby_state(self, game: str) -> dict:
        """Helper to compile currently joinable game rooms directly from memory state."""
        if game == "connect_four":
            mgr = self.connect_four_mgr
        elif game == "rummy":
            mgr = self.rummy_mgr

        # Standard synchronized list comprehension reading right from the manager dictionary
        available_keys = [
            key for key, (game_logic, room_connections) in mgr.JOIN.items()
            if len(room_connections) < 2
        ]
        return {
            "type": "games_available",
            "games_available": [
                {"game": game, "join_key": key} for key in available_keys
            ]
        }