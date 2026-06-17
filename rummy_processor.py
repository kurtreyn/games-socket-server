class RummyProcessor:
    def __init__(self):
        suits = ["hearts", "diamonds", "clubs", "spades"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
        self.cards = [
            {"suit": suit, "rank": rank, "value": f"{rank}_{suit}"}
            for suit in suits
            for rank in ranks
        ]

    def shuffle(self):
        import random
        random.shuffle(self.cards)

    def deal_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None

    def __str__(self):
        return f"CardDeck with {len(self.cards)} cards remaining."


