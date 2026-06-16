import asyncio
import os
from echo_server import EchoServer

port = int(os.environ.get("PORT", 8001))


async def main():
    # server = EchoServer(8001, "localhost")

    # Binding to 0.0.0.0 allows public connections
    server = EchoServer(port, "0.0.0.0")
    await server.run_server()


if __name__ == "__main__":
    asyncio.run(main())