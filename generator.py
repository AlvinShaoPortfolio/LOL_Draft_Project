#Mini-LoL game generator: makes the "past games" the solver learns from
import csv
import math
import random
from draft import DRAFT_STATE, ROLES
from rules import champ_roles, strength
from referee import play_match

NUM_GAMES = 10000
TEMPERATURE = 0.1   #lower = bots almost always take the strongest champ, higher = closer to random
OUTPUT = "data/games.csv"

#noisy bot: a decent but imperfect player
#weighs each legal champion based on strength and then picks one at random 
def noisy_choice(state, rng):
    moves = state.legal_moves()
    weights = [math.exp(strength[c] / TEMPERATURE) for c in moves]
    return rng.choices(moves, weights=weights)[0]

#two noisy bots draft one full game using noisy choices
#get a finished draft state
def noisy_draft(rng):
    state = DRAFT_STATE(champ_roles)
    while not state.is_done():
        state = state.next_state(noisy_choice(state, rng))
    return state

#changes picks, bans, and winner into a flat dict
#{
#    "a_top": 8, "a_jungle": 23, "a_mid": 25, "a_bot": 45, "a_support": 55,
#    "b_top": 10, "b_jungle": 14, "b_mid": 31, "b_bot": 37, "b_support": 56,
#    "bans": "7;9;13;19;20;28;34;42;46;48",
#    "a_win": 1,
#}
def game_row(state, winner):
    row = {}
    for team in ["A", "B"]:
        for role in ROLES:
            row[f"{team.lower()}_{role}"] = state.picks[team][role]
    row["bans"] = ";".join(str(c) for c in sorted(state.bans))
    row["a_win"] = 1 if winner == "A" else 0
    return row

#repeating the game for 10000 games 
def generate(num_games=NUM_GAMES, seed=0):
    rng = random.Random(seed)   #own generator so the games are repeatable
    rows = []
    for _ in range(num_games):
        state = noisy_draft(rng)
        winner = play_match(state.picks, rng)
        rows.append(game_row(state, winner))
    return rows

#writes the results of the 10000 games to a csv
def save(rows, path=OUTPUT):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    rows = generate()
    save(rows)
    print(f"saved {len(rows)} games to {OUTPUT}")
