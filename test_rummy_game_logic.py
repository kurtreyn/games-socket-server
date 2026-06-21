import pytest
from rummy_game_logic import RummyGameLogic, IMoves

game_logic = RummyGameLogic()


def test_shuffle():
	original_order = game_logic.cards.copy()
	game_logic.shuffle()
	shuffled_order = game_logic.cards
	assert original_order != shuffled_order, "The cards should be in a different order after shuffling."


def test_deal_initial_hands():
	game_logic.deal_initial_hands()
	for player in game_logic.players:
		assert len(player.hand) == 7, f"Player {player.id} should have 7 cards in hand after dealing."
		print(f"Player {player.id} hand length: {len(player.hand)}")
	assert len(game_logic.discard_pile) == 1, "There should be one card in the discard pile after dealing."


def test_deal_card():
	initial_deck_size = len(game_logic.cards)
	print(f"Initial deck size: {initial_deck_size}")
	print(f"len(game_logic.cards): {len(game_logic.cards)}")
	game_logic.deal_card()
	new_deck_size = initial_deck_size - 1
	print(f"New deck size: {new_deck_size}")
	print(f"len(game_logic.cards): {len(game_logic.cards)}")
	assert len(game_logic.cards) == initial_deck_size - 1


def test_draw_from_deck_success():
	initial_deck_size = len(game_logic.cards)
	current_player_id = game_logic.players[0].id
	initial_moves_size = 0
	game_logic.shuffle()
	drawn_card = game_logic.draw_from_deck(current_player_id)
	assert drawn_card is not None, "A card should be drawn from the deck."
	assert len(game_logic.cards) == initial_deck_size - 1, "The deck size should decrease by one after drawing a card."
	updated_player = next(p for p in game_logic.players if p.id == current_player_id)
	print(f"drawn_card: {drawn_card}")
	print(f"updated_player.hand: {updated_player.hand}")
	assert drawn_card in updated_player.hand, "Drawn card should match the card in players hand"
	print(f"moves: {game_logic.moves}")
	assert len(game_logic.moves) == initial_moves_size + 1
	last_move = game_logic.moves[-1]
	assert last_move.action == "draw_from_deck"
	assert drawn_card in last_move.cards


def test_draw_from_deck_raises_error():
	game_logic.current_player_id = game_logic.players[0].id
	player_2 = game_logic.players[1]
	print(f"game_logic.current_player_id: {game_logic.current_player_id}")
	print(f"player_2.id: {player_2.id}")

	with pytest.raises(ValueError, match="It isn't your turn."):
		game_logic.draw_from_deck(player_2.id)


def test_last_player_after_discard():
	# 1. Arrange: Setup players and force it to be Player 1's turn
	player_1 = game_logic.players[0]
	player_2 = game_logic.players[1]
	game_logic.current_player_id = player_1.id

	# 2. Act: Player 1 draws, then immediately discards to finish their turn
	drawn_card = game_logic.draw_from_deck(player_1.id)

	# Simulate Player 1 discarding that card to complete their turn
	game_logic.moves.append(IMoves(id=player_1.id, action="discard", cards=[drawn_card]))

	# 3. Assert Scenario A: Player 1 was the last person to discard
	last_completed_turn_player = game_logic.last_player()
	assert last_completed_turn_player == player_1, "Player 1 just discarded, so they should be returned."

	# 4. Assert Scenario B (The Mid-Turn Test):
	# Switch the turn to Player 2, and have Player 2 draw a card.
	game_logic.current_player_id = player_2.id
	game_logic.draw_from_deck(player_2.id)  # This adds a "draw_from_deck" action to the top of history

	# Even though Player 2 just made a move, Player 1 was STILL the last person to DISCARD.
	# Backward scanner should bypass Player 2's draw and find Player 1's discard.
	assert game_logic.last_player() == player_1, "Should still return Player 1 because Player 2 hasn't discarded yet."