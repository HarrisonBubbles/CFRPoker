import numpy as np
import random

class Infoset:
    """
    Represents an infoset (node in game tree) in my simplifed poker game.
    """
    def __init__(self, num_actions, valid_action_indices):
        self.regret_sum = np.zeros(num_actions)
        self.strategy = np.zeros(num_actions)
        self.strategy_sum = np.zeros(num_actions)
        self.num_actions = num_actions
        self.num_valid_actions = len(valid_action_indices)
        self.valid_action_indices = valid_action_indices
        self.visited_count = 0
        
    def get_strategy(self):
        normalizing_sum = 0
        for a in self.valid_action_indices:
            if self.regret_sum[a] > 0:
                self.strategy[a] = self.regret_sum[a]
            else:
                self.strategy[a] = 0
            normalizing_sum += self.strategy[a]
        
        for a in self.valid_action_indices:
            if normalizing_sum > 0:
                self.strategy[a] /= normalizing_sum
            else:
                self.strategy[a] = 1.0 / self.num_valid_actions
        
        return self.strategy
    
    def get_average_strategy(self):
        avg_strategy = np.zeros(self.num_actions)
        normalizing_sum = 0
        
        for a in self.valid_action_indices:
            normalizing_sum += self.strategy_sum[a]
        
        for a in self.valid_action_indices:
            if normalizing_sum > 0:
                avg_strategy[a] = self.strategy_sum[a] / normalizing_sum
            else:
                avg_strategy[a] = 1.0 / self.num_valid_actions
        
        return avg_strategy

    def increment_visited_count(self):
        self.visited_count += 1


class MCCFR:
    """
    Handles the Monte Carlo Counterfactual Regret Minimization (MCCFR) algorithm logic
    """
    def __init__(self, game_class, num_actions: int):
        self.game_class = game_class
        self.num_actions = num_actions
        self.nodes = {}

    def get_infoset(self, infoset_key, valid_action_indices) -> Infoset:
        if infoset_key not in self.nodes:
            self.nodes[infoset_key] = Infoset(self.num_actions, valid_action_indices)
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
        
        print("Training complete!")
        print(f"Average game value: {util[0]/iterations}")
        for i in sorted(self.nodes):
            print(i, self.nodes[i].get_average_strategy(), self.nodes[i].visited_count)
    
    def external_cfr(self, game, history, traversing_player):
        plays = len(history)
        acting_player = plays % 2

        # Terminal node check
        if game.is_terminal(history):
            mult = 1 if acting_player == traversing_player else -1
            return game.get_terminal_utility(history, acting_player) * mult
        
        valid_actions = game.valid_actions(history)
        valid_action_indices = [action.value for action in valid_actions]

        infoset_key = game.get_infoset_key(acting_player, history)
        infoset = self.get_infoset(infoset_key, valid_action_indices)

        infoset.increment_visited_count()
        strategy = infoset.get_strategy()
  
        for a in valid_action_indices:
            infoset.strategy_sum[a] += strategy[a]

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
            action_idx = self.sample_action(strategy)
            next_history = history + [action_idx]
            
            util = self.external_cfr(game, next_history, traversing_player)
            
            return util
    
    def sample_action(self, strategy):
        return random.choices([i for i in range(self.num_actions)], weights = strategy, k = 1)[0]
    
    def choose_move(self, infoset_key):
        infoset = self.nodes[infoset_key]
        strategy = infoset.get_average_strategy()
        return self.sample_action(strategy)