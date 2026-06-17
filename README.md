# Websockets Server

Render.com start command: ```
uvicorn main:app --host 0.0.0.0 --port $PORT```

To run locally:
- Install dependencies: `pip install -r requirements.txt`
- comment out the three lines in `main.py` under the `if __name__ == "__main__":` block
- Replace with:

```
port = int(os.environ.get("PORT", 8001))
    print(f"Starting FastAPI server on port {port}...")
    uvicorn.run(app, host="localhost", port=port)
```

