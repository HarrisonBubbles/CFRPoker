from .deck import Deck
from .player import Player, PlayerAction
from treys import Card, Evaluator
from enum import Enum

class GameStage(Enum):
    SETUP = 0
    PREFLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    SHOWDOWN = 5


class PokerGame:
    """
    Handles the game logic for setting up and running through the stages of a poker game.
    """
    def __init__(
        self,
        player1: Player,
        player2: Player,
        bet_size: int = 1,
        seed: int = None
    ):
        self.player1 = player1
        self.player2 = player2
        self.bet_size = bet_size
        self.deck = Deck(seed=seed)
        self.pot = 0
        self.community_cards = []
        self.dealer = 0 # 0 for player1, 1 for player2
        self.game_stage = GameStage.SETUP
        self.evaluator = Evaluator()
    
    def new_round(self):
        self.deck.reset()
        self.deck.shuffle()
        self.player1.new_round()
        self.player2.new_round()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.raised = False # if someone raised this round

    def preflop(self):
        player1_cards = self.deck.draw(n=2)
        player2_cards = self.deck.draw(n=2)

        self.player1.set_hand(player1_cards)
        self.player2.set_hand(player2_cards)
    
    def deal_to_community(self, n: int):
        self.community_cards.extend(self.deck.draw(n=n))
    
    def make_bet(self, bet_value: int):
        self.pot += bet_value

    def progress_stage(self):
        self.game_stage = GameStage((self.game_stage.value + 1) % 6)
        return self.game_stage
    
    def valid_actions(self, player: Player):
        # can always fold
        actions = [PlayerAction.FOLD]
    
        if self.current_bet == player.current_bet:
            actions.append(PlayerAction.CHECK)
        elif not player.all_in:
            actions.append(PlayerAction.CALL)
        
        if not self.raised and player.chips >= self.current_bet - player.current_bet + self.bet_size:
            actions.append(PlayerAction.RAISE)
        
        return actions
    
    def handle_action(self, player: Player, action: PlayerAction):
        if action == PlayerAction.CHECK:
            print(f"{player.name} checks.")
        
        elif action == PlayerAction.CALL:
            call_amount = self.current_bet - player.current_bet
            bet_amount = player.place_bet(call_amount)
            self.pot += bet_amount
            print(f"{player.name} calls ${bet_amount}.")
        
        elif action == PlayerAction.FOLD:
            player.fold()
            print(f"{player.name} folds.")
        
        elif action == PlayerAction.RAISE:
            total_bet = self.current_bet - player.current_bet + self.bet_size
            bet_amount = player.place_bet(total_bet)
            self.pot += bet_amount
            self.current_bet = player.current_bet
            self.raised = True
            print(f"{player.name} raises by ${bet_amount} to ${self.current_bet}.")
    
    def betting_round(self, current_player):
        players_acted = 0
        self.raised = False

        if self.player1.all_in or self.player2.all_in:
            return
        
        while players_acted < 2:
            if not current_player.all_in:
                valid_actions = self.valid_actions(current_player)
                action = current_player.best_move(valid_actions)
                self.handle_action(current_player, action)
            
            if self.player1.folded or self.player2.folded:
                break
            
            if self.player1.current_bet == self.player2.current_bet:
                players_acted += 1
            else: # someone raised
                players_acted = 1
            
            current_player = self.player2 if current_player == self.player1 else self.player1

    def check_winner(self):
        if self.player1.folded:
            print(f"\n{self.player1.name} folded. {self.player2.name} wins ${self.pot}!")
            self.player2.edit_chips(self.pot)
            return True
        elif self.player2.folded:
            print(f"\n{self.player2.name} folded. {self.player1.name} wins ${self.pot}!")
            self.player1.edit_chips(self.pot)
            return True
        return False
    
    def showdown(self):
        p1_score = self.evaluator.evaluate(self.player1.hand, self.community_cards)
        p2_score = self.evaluator.evaluate(self.player2.hand, self.community_cards)

        p1_class = self.evaluator.get_rank_class(p1_score)
        p2_class = self.evaluator.get_rank_class(p2_score)

        if p1_score < p2_score:
            print(f"\n{self.player1.name} wins ${self.pot} with a {self.evaluator.class_to_string(p1_class)}!")
            self.player1.chips += self.pot
        elif p1_score > p2_score:
            print(f"\n{self.player2.name} wins ${self.pot} with a {self.evaluator.class_to_string(p2_class)}!")
            self.player2.chips += self.pot
        else:
            split_amount = self.pot // 2
            remainder = self.pot % 2
            
            self.player1.chips += split_amount
            self.player2.chips += split_amount
            
            if remainder > 0:
                if self.dealer == 0:
                    self.player1.chips += remainder
                else:
                    self.player2.chips += remainder
            
            print(f"\nIt's a tie! Pot is split: {self.player1.name}: ${split_amount}, {self.player2.name}: ${split_amount}")
    
    def play_round(self):
        self.render_header(stage="New Round")
        
        # Reset for new round
        self.new_round()

        # PREFLOP
        self.preflop()
        print(self.render_game())

        dealer_player = self.player1 if self.dealer == 0 else self.player2
        non_dealer_player = self.player2 if self.dealer == 0 else self.player1
        
        dealer_bet = dealer_player.place_bet(self.bet_size)
        non_dealer_bet = non_dealer_player.place_bet(self.bet_size)
        
        self.pot += dealer_bet + non_dealer_bet
        self.current_bet = self.bet_size
        
        print(f"\n{dealer_player.name} posts: ${dealer_bet}")
        print(f"{non_dealer_player.name} posts: ${non_dealer_bet}")

        self.betting_round(dealer_player)
        
        if self.check_winner():
            return

        # FLOP
        self.render_header(stage="Flop")

        self.deal_to_community(n=3)
        print(self.render_game())

        self.betting_round(dealer_player)

        if self.check_winner():
            return
        
        # TURN
        self.render_header(stage="Turn")

        self.deal_to_community(n=1)
        print(self.render_game())

        self.betting_round(dealer_player)

        if self.check_winner():
            return
        
        # RIVER
        self.render_header(stage="River")

        self.deal_to_community(n=1)
        print(self.render_game())

        self.betting_round(dealer_player)

        if self.check_winner():
            return
        
        # SHOWDOWN
        self.render_header(stage="Showdown")

        self.showdown()

    def play_game(self):
        while self.player1.chips > 0 and self.player2.chips > 0:
            self.play_round()
            self.dealer = (self.dealer + 1) % 2
            
            # Ask to continue
            if self.player1.chips > 0 and self.player2.chips > 0:
                continue_game = input("\nContinue playing? (y/n): ").strip().lower()
                if continue_game != 'y':
                    break
        
        print("\nGame Over!")
        if self.player1.chips <= 0:
            print(f"{self.player1.name} is out of chips! {self.player2.name} wins!")
        elif self.player2.chips <= 0:
            print(f"{self.player2.name} is out of chips! {self.player1.name} wins!")
        else:
            print(f"Final chips - Player 1: ${self.player1.chips} | Player 2: ${self.player2.chips}")


    def render_header(self, stage) -> str:
        print("\n" + "=" * 50)
        print(f"{stage} starting. Player 1: ${self.player1.chips} | Player 2: ${self.player2.chips}")
        print("=" * 50)

    def render_game(self) -> str:
        comm_cards = Card.ints_to_pretty_str(self.community_cards)
        p1_cards =  Card.ints_to_pretty_str(self.player1.get_hand())
        p2_cards =  Card.ints_to_pretty_str(self.player2.get_hand())
        lines = [
            f"Pot: {self.pot}",
            f"Community cards: {comm_cards}",
            f"\nPlayer 1 Hand: {p1_cards}",
            f"Player 2 Hand: {p2_cards}",
        ]
        return "\n".join(lines)