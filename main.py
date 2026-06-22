from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
import os
import uvicorn

from connection_manager import ConnectionManager
from chat_manager import ChatManager
from connect_four_manager import ConnectFourManager
from games_manager import GamesManager

app = FastAPI()

# 1. Top-level network managers
connection_manager = ConnectionManager()
lobby_connection_manager = ConnectionManager() # Dedicated connection pool for lobby list

chat_manager = ChatManager(connection_manager)
connect_four_manager = ConnectFourManager()
games_manager = GamesManager(lobby_connection_manager, connect_four_manager) # Pass it here!

use_production = False


@app.head("/", response_class=PlainTextResponse)
@app.get("/", response_class=PlainTextResponse)
@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    return "OK"


@app.websocket("/chat")
async def chat_websocket(websocket: WebSocket):
    await chat_manager.handle_websocket_chat(websocket)


@app.websocket("/games")
async def game_websocket(websocket: WebSocket):
    # ✅ Let the manager handle connections natively
    await games_manager.handle_lobby_stream(websocket)


@app.websocket("/connect-four")
async def connect_four_websocket(websocket: WebSocket):
    # Pass the lobby manager down so Connect Four can trigger updates when a game room opens
    await connect_four_manager.handle_game(websocket, on_game_created=games_manager.broadcast_lobby_update)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001 if not use_production else 10000))
    host = "localhost" if not use_production else "0.0.0.0"
    print(f"Starting FastAPI server on host {host} on port {port}...")
    uvicorn.run(app, host=host, port=port)