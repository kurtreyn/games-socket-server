from helper_functions import HelperFunctions
from typing import List

helper_functions = HelperFunctions()

# helper_functions.add_user("KurtReyn")

# site_data = helper_functions.load_site_data()
# print(site_data)

suits = ["hearts", "diamonds", "clubs", "spades"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
cards: List[dict] = [
            {"suit": suit, "rank": rank, "value": f"{rank}_{suit}"}
            for suit in suits
            for rank in ranks
        ]

print(cards)
print(len(cards))