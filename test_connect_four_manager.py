import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from string_enum import StringEnum
from connect_four_manager import ConnectFourManager

# Define a mock WebSocket class to simulate browser send/receive channels
class MockWebSocket:
    def __init__(self):
        self.accept = AsyncMock()
        self.close = AsyncMock()
        self.send_json = AsyncMock()
        self.receive_text = AsyncMock()