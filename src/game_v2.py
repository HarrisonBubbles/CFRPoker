from .deck import Deck, PocketPokerDeck, KuhnPokerDeck
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

    def is_terminal(self, history):
        """
        Checks if game is at a terminal state (needed for MCCFR)
        """
        if len(history) < 2:
            return False

        both_checked = history[-1] == PlayerAction.CHECK.value and history[-2] == PlayerAction.CHECK.value
        raised_and_called = PlayerAction.CALL.value in history
        folded = PlayerAction.FOLD.value in history
        return both_checked or raised_and_called or folded

    def get_terminal_utility(self, history, acting_player):
        """
        Assumes that player1 is the "hero" and returns a utility value based on player1's terminal performance
        """
        if not self.is_terminal(history):
            raise RuntimeError("Current game is not at a terminal state!")
        
        if PlayerAction.FOLD.value in history:
            if history.index(PlayerAction.FOLD.value) % 2 == acting_player:
                return -1
            else:
                return 1
        
        raised = 1 if PlayerAction.RAISE.value in history else 0
        return self.showdown(acting_player) * (1 + raised)
    
    def _sorted_cards(self, cards):
        return "".join([Card.int_to_str(c) for c in list(sorted(cards))])
    
    def get_infoset_key(self, acting_player, history):
        hand = self.player1_cards if acting_player == 0 else self.player2_cards
        hand_str = self._sorted_cards(hand)
        comm_str = self._sorted_cards(self.community_cards)
        bet_str = ','.join(map(lambda x: list(PlayerAction)[x].name, history))
        return f"{hand_str}|{comm_str}|{bet_str}"
    
    def setup(self):
        self.deck.reset()
        self.deck.shuffle()
        self.player1_cards = self.deck.draw(1)
        self.player2_cards = self.deck.draw(1)
        self.community_cards = self.deck.draw(1)
        self.final_cards = self.deck.draw(4)

    def valid_actions(self, history):
        actions = []
    
        if PlayerAction.RAISE.value not in history:
            actions.append(PlayerAction.CHECK)
            actions.append(PlayerAction.RAISE)
        else:
            actions.append(PlayerAction.CALL)
            actions.append(PlayerAction.FOLD)
        
        return actions
    
    def evaluate(self, hand, board):
        return self.evaluator.evaluate(hand, board)
    
    def showdown(self):
        """
        1 if player1 wins
        0 if tie
        -1 if player2 wins
        """
        total_board = self.community_cards + self.final_cards
        p1_score = self.evaluate(self.player1_cards, total_board)
        p2_score = self.evaluate(self.player2_cards, total_board)

        if p1_score < p2_score:
            return 1
        elif p1_score > p2_score:
            return -1
        else:
            return 0


class PocketPoker(SimpleGame):
    def __init__(self, player1_cards=[], player2_cards=[], community_cards=[], seed = None):
        self.deck = PocketPokerDeck(seed=seed)
        self.player1_cards = player1_cards
        self.player2_cards = player2_cards
        self.community_cards = community_cards

    def setup(self):
        self.deck.reset()
        self.deck.shuffle()
        self.player1_cards = self.deck.draw(2)
        self.player2_cards = self.deck.draw(2)
        self.community_cards = self.deck.draw(1)

    def _sorted_cards(self, cards):
        return "".join([Card.int_to_str(c)[:1] for c in list(sorted(cards))])

    def evaluate(self, hand, community):
        cards = hand + community
        ranks = [Card.get_rank_int(card) for card in cards]
        rank_counts = {r: ranks.count(r) for r in set(ranks)}
        
        if 3 in rank_counts.values():
            # Three of a kind
            trip_rank = ranks[0]
            return (3, trip_rank)
        elif 2 in rank_counts.values():
            # Pair
            pair_rank = [r for r, count in rank_counts.items() if count == 2][0]
            return (2, pair_rank)
        else:
            # High card
            high_rank = max(ranks)
            return (1, high_rank)
    
    def showdown(self, acting_player):
        """
        1 if player1 wins
        0 if tie
        -1 if player2 wins
        """
        p1_score = self.evaluate(self.player1_cards, self.community_cards)
        p2_score = self.evaluate(self.player2_cards, self.community_cards)

        if p1_score > p2_score:
            return 1 if acting_player == 0 else -1
        elif p1_score < p2_score:
            return -1 if acting_player == 0 else 1
        else:
            return 0

class KuhnPoker(SimpleGame):
    def __init__(self, player1_cards=[], player2_cards=[], seed = None):
        self.deck = KuhnPokerDeck(seed=seed)
        self.player1_cards = player1_cards
        self.player2_cards = player2_cards

    def setup(self):
        self.deck.reset()
        self.deck.shuffle()
        self.player1_cards = self.deck.draw(1)
        self.player2_cards = self.deck.draw(1)

    def _sorted_cards(self, cards):
        return "".join([Card.int_to_str(c)[:1] for c in list(sorted(cards))])
    
    def get_infoset_key(self, acting_player, history):
        hand = self.player1_cards if acting_player == 0 else self.player2_cards
        hand_str = self._sorted_cards(hand)
        bet_str = ','.join(map(lambda x: list(PlayerAction)[x].name, history))
        return f"{hand_str}|{bet_str}"
    
    def showdown(self, acting_player):
        """
        1 if player1 wins
        -1 if player2 wins
        """
        p1_card = Card.get_rank_int(self.player1_cards[0])
        p2_card = Card.get_rank_int(self.player2_cards[0])

        if p1_card > p2_card:
            return 1 if acting_player == 0 else -1
        else:
            return -1 if acting_player == 0 else 1