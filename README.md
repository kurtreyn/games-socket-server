# Websockets Server

This server is designed to handle websocket connections and manage client interactions using FastAPI's WebSockets.
Requires `Python 3.11` or higher.

To run locally:
- Install dependencies: `pip install -r requirements.txt`
- In `main.py` change `use_production` to `False`

Render.com start command: ```
uvicorn main:app --host 0.0.0.0 --port $PORT```

