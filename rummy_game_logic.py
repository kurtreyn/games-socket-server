import random
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class IRummyPlayer:
	id: str
	hand: List[str]
	score: int


@dataclass
class IRummyGameState:
	players: List[IRummyPlayer]
	current_player_id: str
	card_deck: List[str]
	discard_pile: List[str]
	is_over: bool
	winner_id: Optional[str] = None


class RummyGameLogic:
	def __init__(self):
		# 1. Build the raw card deck using the values match frontend map ('2_hearts', 'jack_spades', etc.)
		suits = ["hearts", "diamonds", "clubs", "spades"]
		ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
		self.cards: List[str] = [
            {"suit": suit, "rank": rank, "value": f"{rank}_{suit}"}
            for suit in suits
            for rank in ranks
        ]

		# 2. Track game state properties locally using dataclass types
		self.players = [
			IRummyPlayer(id="p1", hand=[], score=0),
			IRummyPlayer(id="p2", hand=[], score=0)
		]

		self.current_player_id: str = "p1"
		self.discard_pile: List[str] = []
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

	def deal_card(self):
		if len(self.cards > 0):
			return self.cards.pop()
		return None

	def get_state(self) -> IRummyGameState:
		"""
		Gathers all up-to-date variables and packages them into the state dataclass
		"""
		return IRummyGameState(
			players=self.players,
			current_player_id=self.current_player_id,
			card_deck=self.cards,
			discard_pile=self.discard_pile,
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