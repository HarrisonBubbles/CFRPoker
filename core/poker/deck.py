from treys import Card
from typing import List
from random import Random

STR_RANKS: str = '23456789TJQKA'
STR_SUITS: str = 'shdc'

class Deck:
    """
    A standard deck of playing cards for a game of poker.
    """
    
    def __init__(self, seed: int = None):
        self._random = Random(seed)
        self.cards: List[Card] = []
        
        # Initialize standard 52 cards
        for rank in STR_RANKS:
            for suit in STR_SUITS:
                self.cards.append(Card.new(rank + suit))
    
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
        return Card.ints_to_pretty_str(self.cards)