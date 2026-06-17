from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
import os
import uvicorn
from connection_manager import ConnectionManager
from chat_manager import ChatManager

app = FastAPI()
connection_manager = ConnectionManager()
chat_manager = ChatManager(connection_manager)

# TOGGLE BETWEEN LOCAL DEVELOPMENT AND PRODUCTION RENDER.COM ENVIRONMENT
use_localhost = True


# Handle Render.com health checks
@app.head("/", response_class=PlainTextResponse)
@app.get("/", response_class=PlainTextResponse)
@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    return "OK"


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await chat_manager.handle_websocket_chat(websocket)

if __name__ == "__main__":
    if use_localhost:
        # FOR RUNNING LOCALLY
        port = int(os.environ.get("PORT", 8001))
        print(f"Starting FastAPI server on port {port}...")
        uvicorn.run(app, host="localhost", port=port)
    else:
        # FOR RUNNING ON RENDER.COM
        port = int(os.environ.get("PORT", 10000))
        print(f"Starting FastAPI server on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
