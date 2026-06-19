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


@pytest.mark.asyncio
async def test_handle_game_starts_new_game_successfully():
	"""
	Verifies that when a client connects and sends a valid INIT payload,
	the manager creates a fresh game, saves it to the JOIN lookup map,
	and returns an entry handshake containing a unique join_key string.
	"""
	# 1. Arrange Setup
	manager = ConnectFourManager()
	mock_ws = MockWebSocket()

	# Simulate the browser tab sending an initial INIT message payload string
	initial_payload = {StringEnum.TYPE: StringEnum.INIT}
	mock_ws.receive_text.return_value = json.dumps(initial_payload)

	# 2. Define an active-state assertion function
	async def assert_mid_game_state(*args, **kwargs):
		# This runs WHILE start_game is trapped in its try block,
		# right BEFORE the finally block deletes the game room!
		assert len(manager.JOIN) == 1, "Game room was not saved to JOIN map during active play"

		generated_join_key = list(manager.JOIN.keys())[0]
		assert generated_join_key is not None
		print(f"\nSuccessfully verified active room state for key: {generated_join_key}")

	# Attach our validator as a side-effect to the mock
	manager.play_game = AsyncMock(side_effect=assert_mid_game_state)

	# 3. Act
	await manager.handle_game(mock_ws)

	# 4. Post-Execution Assertions
	# Verify the manager opened the gate and accepted the handshake channel
	mock_ws.accept.assert_awaited_once()

	# Verify that the server broadcasted a clean setup packet back to Player 1
	mock_ws.send_json.assert_awaited_once()
	sent_event = mock_ws.send_json.call_args[0][0]

	assert sent_event[StringEnum.TYPE] == StringEnum.INIT
	assert StringEnum.JOIN in sent_event
	assert StringEnum.JOIN_URL in sent_event

	# (Optional) Verify that the room was successfully cleaned up at the very end
	assert len(manager.JOIN) == 0, "Game room was not cleaned up after connection closed"


@pytest.mark.asyncio
async def test_handle_game_crashes_on_invalid_handshake_type():
	"""
    Verifies that if a rogue client sends an invalid first message type
    (like a raw MOVE frame instead of an INIT/JOIN handshake), the assert gate
    trips and terminates the application execution stream cleanly.
    """
	# 1. Arrange Setup
	manager = ConnectFourManager()
	mock_ws = MockWebSocket()

	# Simulate a client sending a MOVE action out-of-order right at the start
	invalid_payload = {StringEnum.TYPE: StringEnum.MOVE, StringEnum.COLUMN: 3}
	mock_ws.receive_text.return_value = json.dumps(invalid_payload)

	# 2. Act & Assert
	# We explicitly expect an AssertionError to be thrown by your assetion verification check
	with pytest.raises(AssertionError):
		await manager.handle_game(mock_ws)

	# Verify the manager accepted the transport layer but crashed out before saving a game room
	mock_ws.accept.assert_awaited_once()
	assert len(manager.JOIN) == 0