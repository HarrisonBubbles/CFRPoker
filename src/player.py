from enum import Enum
from abc import ABC, abstractmethod
from .mccfr import MCCFR
import random

class PlayerAction(Enum):
    FOLD = 0
    CHECK = 1
    CALL = 2
    RAISE = 3


class Player(ABC):
    def __init__(self, name, chips: int = 10):
        self.name = name
        self.chips = chips
        self.hand = []
        self.folded = False
        self.all_in = False
        self.current_bet = 0

    def reset_player(self):
        self.__init__(self.name, self.chips)

    def get_hand(self):
        return self.hand

    def set_hand(self, cards):
        self.hand = cards

    def reset_hand(self):
        self.hand = []

    def get_chips(self):
        return self.chips
    
    def place_bet(self, amount: int):
        amount = min(self.chips, amount)
        self.chips -= amount
        self.current_bet += amount

        if self.chips == 0:
            self.all_in = True

        return amount
    
    def edit_chips(self, amount: int):
        self.chips += amount
        return amount
    
    def fold(self):
        self.folded = True

    def new_round(self):
        self.hand = []
        self.all_in = False
        self.folded = False
        self.current_bet = 0

    @abstractmethod
    def best_move(self, infoset_key, valid_actions) -> PlayerAction:
        pass


class RandomPlayer(Player):
    def best_move(self, infoset_key, valid_actions):
        return random.choice(valid_actions).value
    

class AggressivePlayer(Player):
    """
    Always bets or calls
    """
    def best_move(self, infoset_key, valid_actions):
        if PlayerAction.RAISE in valid_actions:
            return PlayerAction.RAISE.value
        else:
            return PlayerAction.CALL.value
    

class HumanPlayer(Player):
    def best_move(self, infoset_key, valid_actions):
        while True:
            print(f"{self.name} available actions:", ", ".join([a.name for a in valid_actions]))
            action = input("Your action: ").strip().lower()

            action_map = {
                "check": PlayerAction.CHECK,
                "call": PlayerAction.CALL,
                "fold": PlayerAction.FOLD,
                "raise": PlayerAction.RAISE,
            }

            mapped_action = action_map.get(action, "")

            if mapped_action in valid_actions:
                return mapped_action.value
            else:
                print("Invalid action, try again.")


class MCCFRPlayer(Player):
    def __init__(self, name, model: MCCFR, chips = 10):
        self.name = name
        self.chips = chips
        self.model = model
    
    def best_move(self, infoset_key, valid_actions):
        valid_action_indices = [a.value for a in valid_actions]
        return self.model.choose_move(infoset_key, valid_action_indices)