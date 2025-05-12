from .card import Suit, Rank, Card
from typing import List
from random import Random
import random

class Deck:
    """
    A standard deck of playing cards for a game of poker.
    """
    
    def __init__(self, seed: int = None):
        self._random = Random(seed)
        self.cards: List[Card] = []
        
        # Initialize standard 52 cards
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(rank, suit))
    
    def shuffle(self) -> None:
        self._random.shuffle(self.cards)
    
    def draw(self, n: int = 1) -> List[int]:
        cards = []
        for _ in range(n):
            cards.append(self.cards.pop())
        return cards
    
    def reset(self) -> None:
        self.__init__()

    def __str__(self) -> str:
        return f"{[str(self.cards[i]) for i in range(len(self.cards))]}"