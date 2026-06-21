import random
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class IRummyPlayer:
	id: str
	hand: List[dict]
	score: int

@dataclass
class IMoves:
	id: str
	action: str
	cards: List[dict]


@dataclass
class IRummyGameState:
	players: List[IRummyPlayer]
	current_player_id: str
	card_deck: List[dict]
	discard_pile: List[dict]
	moves: List[dict]
	is_over: bool
	winner_id: Optional[str] = None


class RummyGameLogic:
	def __init__(self):
		# 1. Build the raw card deck using the values match frontend map ('2_hearts', 'jack_spades', etc.)
		suits = ["hearts", "diamonds", "clubs", "spades"]
		ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
		self.cards: List[dict] = [
			{"suit": suit, "rank": rank, "value": f"{rank}_{suit}"}
			for suit in suits
			for rank in ranks
		]

		# 2. Track game state properties locally using dataclass types
		self.players = [
			IRummyPlayer(id="p1", hand=[], score=0),
			IRummyPlayer(id="p2", hand=[], score=0)
		]

		self.moves: List[IMoves] = []  # List to track moves in the format {"id": str, "action": str, "card": dict}
		self.current_player_id = self.players[0].id  # Start with player 1
		self.discard_pile: List[dict] = []
		self.is_over: bool = False
		self.winner_id: Optional[str] = None

	def shuffle(self):
		random.shuffle(self.cards)

	def deal_initial_hands(self, cards_per_player: int = 7):
		"""Helper to deal out starting cards to players"""
		self.shuffle()
		for _ in range(cards_per_player):
			for player in self.players:
				card = self.deal_card()
				if card:
					player.hand.append(card)

		# Flip the top card to start the discard pile
		top_card = self.deal_card()
		if top_card:
			self.discard_pile.append(top_card)

	def deal_card(self) -> Optional[dict]:
		if len(self.cards) > 0:
			return self.cards.pop()
		return None

	def draw_from_deck(self, player_id: str) -> Optional[dict]:
		if self.current_player_id != player_id:
			raise ValueError("It isn't your turn.")

		card = self.deal_card()
		if card:
			player = next(p for p in self.players if p.id == player_id)
			player.hand.append(card)
			self.moves.append(IMoves(id=player.id, action="draw_from_deck", cards=[card]))
			return card
		return None

	def last_player(self):
		"""
		Scans backward through game history to find the player who completed
		the most recent turn with a discard.
		"""
		if not self.moves:
			return None  # No moves have been made yet

		# Loop through the moves list backwards (from newest to oldest)
		for move in reversed(self.moves):
			# Handle object format (.action) or dict format (["action"]) depending on your setup
			action = move.action if hasattr(move, 'action') else move.get("action")
			player_id = move.id if hasattr(move, 'id') else move.get("id")

			if action == "discard":
				return next(p for p in self.players if p.id == player_id)

		return None  # Moves exist, but no one has discarded yet (e.g., during initial setup)

	def get_state(self) -> IRummyGameState:
		"""
		Gathers all up-to-date variables and packages them into the state dataclass
		"""
		return IRummyGameState(
			players=self.players,
			current_player_id=self.current_player_id,
			card_deck=self.cards,
			discard_pile=self.discard_pile,
			moves=self.moves,
			is_over=self.is_over,
			winner_id=self.winner_id
		)

	def get_state_json_ready(self) -> dict:
		"""
		Converts the entire nested dataclass structure into a standard Python dict.
		"""
		return asdict(self.get_state())

	def __str__(self):
		return f"CardDeck with {len(self.cards)} cards remaining."
