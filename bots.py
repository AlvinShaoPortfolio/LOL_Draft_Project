#Solver: baseline drafters that MCTS is compared against.
import random
from draft import DRAFT_ORDER

#picks or bans any legal champion at random (no strategy)
class RandomBot:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()

    def choose_move(self, state):
        return self.rng.choice(state.legal_moves())

#drafts like a typical player: popular champions are more likely
#picks weighted by pick rate, bans weighted by ban rate
class PickRateBot:
    def __init__(self, pick_rate, ban_rate, rng=None):
        self.pick_rate = pick_rate
        self.ban_rate = ban_rate
        self.rng = rng or random.Random()

    def choose_move(self, state):
        moves = state.legal_moves()
        _, choice = DRAFT_ORDER[state.step]
        rates = self.ban_rate if choice == "ban" else self.pick_rate
        weights = [rates[c] + 1e-6 for c in moves]  
        return self.rng.choices(moves, weights=weights)[0]

#always takes the best champion right now 
#for both picks and bans -- never thinks about what the opponent does next
class GreedyBot:
    def __init__(self, model):
        self.weights = model.weights

    def choose_move(self, state):
        moves = state.legal_moves()
        return max(moves, key=lambda c: self.weights[c])
