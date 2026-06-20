from rummy_game_logic import RummyGameLogic

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
	assert len(game_logic.discard_pile) == 1, "There should be one card in the discard pile after dealing."


def test_deal_card():
	initial_deck_size = len(game_logic.cards)
	print(f"cards: {game_logic.cards}")
	game_logic.current_player_id = "p1"
	assert len(game_logic.cards) == initial_deck_size - 1