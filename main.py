from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import json
import os
import uvicorn
from datetime import datetime, timezone
from connection_manager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()


# Handle Render.com health checks
@app.head("/", response_class=PlainTextResponse)
@app.get("/", response_class=PlainTextResponse)
@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    return "OK"


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print(f"Connected clients: {len(manager.connections)}")

    # Broadcast new user notification and update count
    await manager.broadcast({
        "type": "notification",
        "text": "A new user has joined",
        "timeStamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }, exclude=websocket)

    await manager.broadcast({
        "type": "user_count",
        "count": len(manager.connections),
    })

    try:
        while True:
            # Receive raw json from the client
            raw_text = await websocket.receive_text()

            try:
                message_data = json.loads(raw_text)
                message_type = message_data.get("type", "unknown")

                if message_type not in ("chat", "notification"):
                    print("Not a chat message or notification, skipping broadcast")
                else:
                    await manager.broadcast(message_data, exclude=websocket)

            except json.JSONDecodeError:
                print("Received invalid JSON payload from client. Ignoring")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"A client just disconnected. Remaining clients: {len(manager.connections)}")

        # Broadcast updated user count upon disconnect
        await manager.broadcast({
            "type": "user_count",
            "count": len(manager.connections),
        })

if __name__ == "__main__":
    # port = int(os.environ.get("PORT", 10000))
    # print(f"Starting FastAPI server on port {port}...")
    # uvicorn.run(app, host="0.0.0.0", port=port)

    # FOR RUNNING LOCALLY
    port = int(os.environ.get("PORT", 8001))
    print(f"Starting FastAPI server on port {port}...")
    uvicorn.run(app, host="localhost", port=port)