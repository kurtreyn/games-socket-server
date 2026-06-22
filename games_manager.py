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
            # Send current active matches instantly on setup
            connect_four_lobby_state = self._get_lobby_state("connect_four")
            rummy_lobby_state = self._get_lobby_state("rummy")
            print(f"connect_four_lobby_state: {connect_four_lobby_state}")
            print(f"rummy_lobby_state: {rummy_lobby_state}")
            all_games_lobby_state = {
                "type": "games_available",
                "games_available": []
            }
            all_games_lobby_state["games_available"].append(connect_four_lobby_state["games_available"][0])
            # all_games_lobby_state["games_available"].append(rummy_lobby_state["games_available"][0])
            print(f"all_games_lobby_state: {all_games_lobby_state}")
            await websocket.send_json(connect_four_lobby_state)
            # await websocket.send_json(self._get_lobby_state("rummy"))




            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            self.connection_manager.disconnect(websocket)
            print(f"Lobby client disconnected.")

    async def broadcast_lobby_update(self):
        """Call this whenever a game is created or destroyed to update all listening clients."""
        await self.connection_manager.broadcast(self._get_lobby_state())

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