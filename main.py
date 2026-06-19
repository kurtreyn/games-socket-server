from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
import os
import uvicorn
from connection_manager import ConnectionManager
from chat_manager import ChatManager
from connect_four_manager import ConnectFourManager

app = FastAPI()
connection_manager = ConnectionManager()
chat_manager = ChatManager(connection_manager)
connect_four_manager = ConnectFourManager()

# TOGGLE BETWEEN LOCAL DEVELOPMENT AND PRODUCTION RENDER.COM ENVIRONMENT
use_production = True


# Handle Render.com health checks
@app.head("/", response_class=PlainTextResponse)
@app.get("/", response_class=PlainTextResponse)
@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    return "OK"


@app.websocket("/chat")
async def chat_websocket(websocket: WebSocket):
    await chat_manager.handle_websocket_chat(websocket)


@app.websocket("/connect-four")
async def connect_four_websocket(websocket: WebSocket):
    await connect_four_manager.handle_game(websocket)


if __name__ == "__main__":
    if use_production:
        # FOR RUNNING LOCALLY
        port = int(os.environ.get("PORT", 10000))
        print(f"Starting FastAPI server on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # FOR RUNNING ON RENDER.COM
        port = int(os.environ.get("PORT", 8001))
        print(f"Starting FastAPI server on port {port}...")
        uvicorn.run(app, host="localhost", port=port)
