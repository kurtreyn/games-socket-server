import asyncio
from chat_server import ChatServer


async def main():
    server = ChatServer()
    await server.run_server()


if __name__ == "__main__":
    asyncio.run(main())