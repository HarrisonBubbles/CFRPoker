from .deck import Deck
from .player import Player, PlayerAction
from treys import Card, Evaluator

class SimpleGame:
    """
    An even-more-simplifed poker game for use with MCCFR
    """
    def __init__(self, player1_cards = [], player2_cards = [], community_cards = [], final_cards = [], seed: int = None):
        self.deck = Deck(seed=seed)
        self.player1_cards = player1_cards
        self.player2_cards = player2_cards
        self.community_cards = community_cards
        self.final_cards = final_cards
        self.evaluator = Evaluator()
        self.action_map = {
            PlayerAction.FOLD: 0,
            PlayerAction.CHECK: 1,
            PlayerAction.CALL: 2,
            PlayerAction.RAISE: 3
        }

    def is_terminal(self, history):
        """
        Checks if game is at a terminal state (needed for MCCFR)
        """
        if len(history) < 2:
            return False

        both_checked = history[-1] == 1 and history[-2] == 1 
        raised_and_called = 2 in history
        folded = 0 in history
        return both_checked or raised_and_called or folded

    def get_terminal_utility(self, history):
        """
        Assumes that player1 is the "hero" and returns a utility value based on player1's terminal performance
        """
        if not self.is_terminal(history):
            raise RuntimeError("Current game is not at a terminal state!")
        
        if 0 in history:
            if history.index(0) % 2 == 0:
                return -1
            else:
                return 1
        
        raised = 1 if 3 in history else 0
        return self.showdown() * (1 + raised)
    
    def setup(self):
        self.deck.reset()
        self.deck.shuffle()
        self.player1_cards = self.deck.draw(2)
        self.player2_cards = self.deck.draw(2)
        self.community_cards = self.deck.draw(2)
        self.final_cards = self.deck.draw(3)

    def valid_actions(self, history):
        actions = []
    
        if 3 not in history:
            actions.append(PlayerAction.CHECK)
            actions.append(PlayerAction.RAISE)
        else:
            actions.append(PlayerAction.CALL)
            actions.append(PlayerAction.FOLD)
        
        return actions
    
    def showdown(self):
        """
        1 if player1 wins
        0 if tie
        -1 if player2 wins
        """
        total_board = self.community_cards + self.final_cards
        p1_score = self.evaluator.evaluate(self.player1_cards, total_board)
        p2_score = self.evaluator.evaluate(self.player2_cards, total_board)

        if p1_score < p2_score:
            return 1
        elif p1_score > p2_score:
            return -1
        else:
            return 0
