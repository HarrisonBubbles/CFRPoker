import numpy as np
import random
from treys import Card
from .player import PlayerAction

class Infoset:
    """
    Represents an infoset (node in game tree) in my simplifed poker game.
    """
    def __init__(self, num_actions):
        self.regret_sum = np.zeros(num_actions)
        self.strategy = np.zeros(num_actions)
        self.strategy_sum = np.zeros(num_actions)
        self.num_actions = num_actions
        
    def get_strategy(self):
        normalizing_sum = 0
        for a in range(self.num_actions):
            if self.regret_sum[a] > 0:
                self.strategy[a] = self.regret_sum[a]
            else:
                self.strategy[a] = 0
            normalizing_sum += self.strategy[a]
        
        for a in range(self.num_actions):
            if normalizing_sum > 0:
                self.strategy[a] /= normalizing_sum
            else:
                self.strategy[a] = 1.0 / self.num_actions
        
        return self.strategy
    
    def get_average_strategy(self):
        avg_strategy = np.zeros(self.num_actions)
        normalizing_sum = 0
        
        for a in range(self.num_actions):
            normalizing_sum += self.strategy_sum[a]
        
        for a in range(self.num_actions):
            if normalizing_sum > 0:
                avg_strategy[a] = self.strategy_sum[a] / normalizing_sum
            else:
                avg_strategy[a] = 1.0 / self.num_actions
        
        return avg_strategy


class MCCFR:
    """
    Handles the Monte Carlo Counterfactual Regret Minimization (MCCFR) algorithm logic
    """
    def __init__(self, game_class):
        self.game_class = game_class
        self.action_map = {
            PlayerAction.FOLD: 0,
            PlayerAction.CHECK: 1,
            PlayerAction.CALL: 2,
            PlayerAction.RAISE: 3
        }
        self.num_actions = 4
        self.nodes = {}

    def _sorted_cards(self, cards):
        return Card.ints_to_pretty_str(list(sorted(cards)))

    def get_infoset_key(self, hand, community_cards, history):
        hand_str = self._sorted_cards(hand)
        comm_str = self._sorted_cards(community_cards)
        bet_str = ','.join(map(str, history))
        return f"{hand_str}|{comm_str}|{bet_str}"

    def get_infoset(self, infoset_key) -> Infoset:
        if infoset_key not in self.nodes:
            self.nodes[infoset_key] = Infoset(self.num_actions)
        return self.nodes[infoset_key]
    
    def train(self, iterations=1000):
        print(f"Starting External Sampling MCCFR training for {iterations} iterations...")
        util = np.zeros(2)
        
        for i in range(1, iterations + 1):
            if i % (iterations // 10) == 0:
                print(f"Iteration {i}/{iterations}")
            
            for traversing_player in range(2):
                game = self.game_class(seed=i)
                game.setup()
                util[traversing_player] += self.external_cfr(game, [], traversing_player)
        
        print("MCCFR training complete!")
        print(f"Average game value: {util[0]/iterations}")
    
    def external_cfr(self, game, history, traversing_player):
        plays = len(history)
        acting_player = plays % 2
        acting_player_cards = game.player1_cards if acting_player == 0 else game.player2_cards

        # Terminal node check
        if game.is_terminal(history):
            return game.get_terminal_utility(history)
        
        valid_actions = game.valid_actions(history)
        valid_action_indices = [self.action_map[action] for action in valid_actions]

        infoset_key = self.get_infoset_key(acting_player_cards, game.community_cards, history)
        infoset = self.get_infoset(infoset_key)

        strategy = infoset.get_strategy()

        if acting_player == traversing_player:
            action_utils = np.zeros(self.num_actions)
            infoset_util = 0
            
            # Try each action and compute utility
            for a in valid_action_indices:
                next_history = history + [a]
                action_utils[a] = self.external_cfr(game, next_history, traversing_player)
                infoset_util += strategy[a] * action_utils[a]
            
            for a in valid_action_indices:
                regret = action_utils[a] - infoset_util
                infoset.regret_sum[a] += regret
            
            return infoset_util
        else: #acting_player != traversing_player
            action_idx = self.sample_action(strategy, valid_action_indices)
            next_history = history + [action_idx]
            
            util = self.external_cfr(game, next_history, traversing_player)
            
            for a in range(self.num_actions):
                infoset.strategy_sum[a] += strategy[a]
            
            return util
    
    def sample_action(self, strategy, valid_action_indices):
        r = random.random()
        cumulative_prob = 0
        
        for a in valid_action_indices:
            cumulative_prob += strategy[a]
            if r < cumulative_prob:
                return a
        
        # if all action probabilities are 0, just choose uniformly
        return random.choice(valid_action_indices)