#for simulating games --> ref just determines who wins 
#gets the strength of each laner and the synergy of both teams
#then calculates fight win probability using this strength/synergy
#then simulate the game with these value by rolling lanes and teamfight
import math
import random
from itertools import product
from draft import ROLES
from rules import strength, counter, synergy

#points: each lane is worth 1, the team fight is worth 2 -> 7 total, first to 4 wins (no ties)
LANE_POINTS = 1
FIGHT_POINTS = 2
POINTS_TO_WIN = 4

#so i can turn any num into a probability
def sigmoid(x):
    return 1 / (1 + math.exp(-x))

#getting the chance that A Laner beats B laner 0.0:1.0
def lane_prob(a, b):
    return sigmoid(strength[a] - strength[b] + counter[a][b])

#getting the sum of the team's synergy
def team_synergy(team):
    total = 0
    for i in range(len(team)):
        for j in range(i + 1, len(team)):
            total += synergy[team[i]][team[j]]
    return total

#getting the chance that A wins the teamfight according to the strength
#of each character combined with the synergy of the team
def fight_prob(team_a, team_b):
    strength_diff = sum(strength[c] for c in team_a) - sum(strength[c] for c in team_b)
    synergy_diff = team_synergy(team_a) - team_synergy(team_b)
    return sigmoid(strength_diff + synergy_diff)

#the 6 rolls of a match: (name, points, chance A wins)
#match_rolls(picks) returns a list of 6 (name, points, chance A wins), e.g.
# [
#     ("top",       1, 0.49),
#     ("jungle",    1, 0.47),
#     ("mid",       1, 0.47),
#     ("bot",       1, 0.55),
#     ("support",   1, 0.51),
#     ("teamfight", 2, 0.59),
# ]
def match_rolls(picks):

    team_a = picks["A"]
    team_b = picks["B"]
    rolls = []

    #5 lane rolls, worth 1 point each
    for role in ROLES:
        a_laner = team_a[role]
        b_laner = team_b[role]
        chance = lane_prob(a_laner, b_laner)
        rolls.append((role, LANE_POINTS, chance))

    #teamfight roll, worth 2 points
    a_champs = list(team_a.values())
    b_champs = list(team_b.values())
    chance = fight_prob(a_champs, b_champs)
    rolls.append(("teamfight", FIGHT_POINTS, chance))

    return rolls

#simulating a match: rolls each of the 6 once, returns the winner ("A" or "B")
#match_rolls(picks) returns a list of 6 (name, points, chance A wins), e.g.
# [
#     ("top",       1, 0.49),
#     ("jungle",    1, 0.47),
#     ("mid",       1, 0.47),
#     ("bot",       1, 0.55),
#     ("support",   1, 0.51),
#     ("teamfight", 2, 0.59),
# ]
def play_match(picks, rng=random):
    a_points = 0
    for name, points, p in match_rolls(picks):
        if rng.random() < p:  #A wins this roll
            a_points += points
    return "A" if a_points >= POINTS_TO_WIN else "B"

#true chance team A wins the match, no dice
#finds all matches where A wins by running all 64 combinations
def exact_win_prob(picks):
    rolls = match_rolls(picks)
    total = 0

    #outcome is one combination, e.g. (True, False, ...) = A wins top, B wins jungle, ...
    for outcome in product([True, False], repeat=len(rolls)):
        chance = 1   
        a_points = 0

        for a_won, (_, points, p) in zip(outcome, rolls):
            if a_won:
                chance *= p
                a_points += points
            else:
                chance *= 1 - p

        if a_points >= POINTS_TO_WIN:
            total += chance

    return total

#----- demo only (presentation): same as play_match but prints each roll -----
def demo_match(picks, rng=random):
    a_points = 0
    total = 0
    for name, points, p in match_rolls(picks):
        roll = rng.random()
        winner = "A" if roll < p else "B"
        total += points
        if winner == "A":
            a_points += points
        print(f"{name:<9} A {p:.0%} -> rolled {roll:.2f} -> {winner} wins (+{points})")
    print(f"final     A {a_points} - {total - a_points} B")
    return "A" if a_points >= POINTS_TO_WIN else "B"

if __name__ == "__main__":
    from rules import champ_roles
    from draft import DRAFT_STATE

    #make a random finished draft
    state = DRAFT_STATE(champ_roles)
    while not state.is_done():
        state = state.next_state(random.choice(state.legal_moves()))

    print(state.picks)
    print("winner:", demo_match(state.picks))