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


def test_draw_from_deck():
	initial_deck_size = len(game_logic.cards)
	current_player_id = game_logic.players[0].id
	game_logic.shuffle()
	drawn_card = game_logic.draw_from_deck(current_player_id)
	assert drawn_card is not None, "A card should be drawn from the deck."
	assert len(game_logic.cards) == initial_deck_size - 1, "The deck size should decrease by one after drawing a card."
	updated_player = next(p for p in game_logic.players if p.id == current_player_id)
	print(f"drawn_card: {drawn_card}")
	print(f"updated_player.hand: {updated_player.hand}")
	assert drawn_card in updated_player.hand, "Drawn card should match the card in players hand"
