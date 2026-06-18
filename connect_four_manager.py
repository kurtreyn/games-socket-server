from fastapi import WebSocket, WebSocketDisconnect
from connection_manager import ConnectionManager
from connect_four_game_logic import ConnectFourGameLogic, PLAYER1, PLAYER2
from string_enum import StringEnum
import json
import secrets


class ConnectFourManager:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.JOIN = {}  # Maps join_key to (game_logic, set of connected websockets)

    async def broadcast_to_room(self, room_connections: set, event: dict):
        for connection in room_connections:
            try:
                await connection.send_json(event)
            except Exception as exc:
                print(f"Error broadcasting to a connection: {exc}")
                pass

    async def handle_error(self, websocket: WebSocket, error_message: str):
        await websocket.send_json({
            "type": "error",
            "text": error_message,
        })

    async def join_game(self, websocket: WebSocket, join_key: str):
        # Find a connect four game
        try:
            game_logic, room_connections = self.JOIN[join_key]
        except KeyError:
            await self.handle_error(websocket, "Game not found.")
            return
        # Register to receive moves from this game
        room_connections.add(websocket)
        print(f"def join_game - room_connections: {room_connections}")

        try:
            # Update the player count
            await self.broadcast_to_room(room_connections, {
                StringEnum.TYPE: StringEnum.PLAYER_JOINED,
                StringEnum.PLAYER_COUNT: len(room_connections),
            })
            # Send the first move, in case the first player already played it.
            await self.replay_moves(websocket, join_key)
            # Receive and process moves from the second player.
            await self.play_game(websocket, game_logic, PLAYER2, room_connections)
        finally:
            room_connections.remove(websocket)

    async def start_game(self, websocket: WebSocket):
        # Initialize a Connect Four game and secret access tokens.
        game_logic = ConnectFourGameLogic()
        room_connections = {websocket}

        join_key = secrets.token_urlsafe(12)
        self.JOIN[join_key] = game_logic, room_connections
        print(f"def start_game - game_logic: {game_logic}")
        print(f"def start_game - join_key: {join_key}")
        print(f"def start_game - JOIN[join_key]: {self.JOIN[join_key]}")

        try:
            # Send the secret access tokens to the browser of the first player,
            # where they'll be used for building "join" link.
            event = {
                StringEnum.TYPE: StringEnum.INIT,
                StringEnum.JOIN: join_key,
                StringEnum.JOIN_URL: f"http://localhost:8000/?join=/{join_key}",
                StringEnum.PLAYER_COUNT: len(room_connections),
            }
            print(f"def start_game - event: {event}")

            await websocket.send_json(event)

            # Receive and process moves from the first player.
            await self.play_game(websocket, game_logic, PLAYER1, room_connections)
        finally:
            del self.JOIN[join_key]

    async def play_game(self, websocket: WebSocket, game_logic: ConnectFourGameLogic, player: str, room_connections: set):
        try:
            while True:
                raw_text = await websocket.receive_text()
                event = json.loads(raw_text)

                # Sanity check the incoming event structure
                assert event.get(StringEnum.TYPE) == StringEnum.MOVE
                column = event[StringEnum.COLUMN]
                print(f"def play_game - websocket: {websocket}")
                print(f"def play - game_logic: {game_logic}")
                print(f"def play - player: {player}")
                print(f"def play - room_connections: {room_connections}")

                try:
                    row = game_logic.play(player, column)
                except (RuntimeError, ValueError) as exc:
                    # Assuming handle_error sends a personal socket message
                    await self.handle_error(websocket, str(exc))
                    continue  # Safe to use now! It skips the rest of this message broadcast

                # Broadcast the successful move to all connected clients
                move_event = {
                    StringEnum.TYPE: StringEnum.MOVE,
                    StringEnum.PLAYER: player,
                    StringEnum.COLUMN: column,
                    StringEnum.ROW: row,
                }
                await self.broadcast_to_room(room_connections, move_event)

                # Check if this move ended the game
                if game_logic.winner is not None:
                    win_event = {
                        StringEnum.TYPE: StringEnum.WIN,
                        StringEnum.PLAYER: game_logic.winner,
                    }
                    await self.broadcast_to_room(room_connections, win_event)

        except WebSocketDisconnect:
            # Clean up connection when the player drops or closes their browser tab
            if websocket in room_connections:
                room_connections.remove(websocket)
                print(f"Player {player} disconnected.")

    async def replay_moves(self, websocket: WebSocket, join_key: str):
        # Make a copy to avoid an exception if game.moves changes while iteration
        # is in progress. If a move is played while replay is running, moves will
        # be sent out of order but each move will be sent once and eventually the
        # UI will be consistent.

        # Unpack the tuple, pull game_logic out, and ignore the
        # room_connections set since we don't need it here
        game_logic, _ = self.JOIN[join_key]
        for player, column, row in game_logic.moves.copy():
            event = {
                StringEnum.TYPE: StringEnum.MOVE,
                StringEnum.PLAYER: player,
                StringEnum.COLUMN: column,
                StringEnum.ROW: row,
            }
            await websocket.send_json(event)

    async def handle_game(self, websocket: WebSocket):
        """
         Traffic controller for incoming connections.
         Primary objective is to look at the first message
         a client sends then figure out if they want to start a new game or
         join an existing one, and then route them to the appropriate handler.
         """
        # 1. Accept the WebSocket connection and wait for the client to send an "init" event
        await websocket.accept()

        try:
            # 2. Receive & parse the initial message from the client,
            # which should indicate whether they want to start a new
            # game or join an existing one
            raw_text = await websocket.receive_text()
            event = json.loads(raw_text)
            print(f"def - handle_game raw_text: {raw_text}")
            print(f"def - handle_game event: {event}")

            # Sanity check the incoming event structure
            allowed_types = {StringEnum.INIT, StringEnum.JOIN}
            assert event.get(StringEnum.TYPE) in allowed_types

            # 3. Inspect event & route to the appropriate handler based on
            # whether client wants to start a new game or join an existing one
            if StringEnum.JOIN in event:
                # Second player joins existing game
                await self.join_game(websocket, event[StringEnum.JOIN])
            else:
                # First player starts a new game
                await self.start_game(websocket)

        except json.JSONDecodeError:
            print("Received invalid JSON payload from client. Ignoring")
        except WebSocketDisconnect:
            print(f"A client just disconnected.")