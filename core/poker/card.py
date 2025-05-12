from enum import Enum
from functools import total_ordering

class Suit(Enum):
    SPADES = "S"
    CLUBS = "C"
    HEARTS = "H"
    DIAMONDS = "D"


class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def short_name(self) -> str:
        if self.value <= 10:
            return str(self.value)
        
        rank_to_name = {
            self.JACK: "J",
            self.QUEEN: "Q",
            self.KING: "K",
            self.ACE: "A"
        }
        return rank_to_name[self]


@total_ordering
class Card:
    """
    Represents a playing card (with suit and rank) in a typical poker deck.
    """

    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __str__(self) -> str:
        return f"{self.rank.short_name()}{self.suit.value}"
    
    def __repr__(self) -> str:
        return f"Card({self.rank.name}, {self.suit.name})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __lt__(self, other):
        if not isinstance(other, Card):
            raise TypeError(f"Cannot compare type card with type {type(other)}")
        return self.rank.value < other.rank.value
    
    def __hash__(self) -> int:
        return hash((self.rank, self.suit))