import asyncio
# from chat_server import ChatServer
from echo_server import EchoServer


async def main():
    server = EchoServer(8001, "localhost")
    await server.run_server()


if __name__ == "__main__":
    asyncio.run(main())