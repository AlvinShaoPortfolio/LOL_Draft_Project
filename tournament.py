#Experiments: pits two drafters against each other and judges the drafts.
#this is the JUDGE, so it CAN use referee.py (the true hidden rules).
import random
from draft import DRAFT_STATE, DRAFT_ORDER
from referee import exact_win_prob, play_match


#one full draft: each step, ask whichever drafter's turn it is for a move
def run_draft(drafter_a, drafter_b, champ_roles):
    state = DRAFT_STATE(champ_roles)
    while not state.is_done():
        team, _ = DRAFT_ORDER[state.step]
        drafter = drafter_a if team == "A" else drafter_b
        state = state.next_state(drafter.choose_move(state))
    return state


#plays num_drafts drafts, swapping sides every other draft (team A drafts first)
#returns drafter_1's average true win chance and its dice-rolled wins
def run_matchup(drafter_1, drafter_2, champ_roles, num_drafts=1000, seed=0):
    rng = random.Random(seed)
    total_chance = 0
    wins = 0

    for i in range(num_drafts):
        if i % 2 == 0:
            #drafter_1 is team A
            state = run_draft(drafter_1, drafter_2, champ_roles)
            chance = exact_win_prob(state.picks)
            won = play_match(state.picks, rng) == "A"
        else:
            #drafter_1 is team B, so flip A's numbers
            state = run_draft(drafter_2, drafter_1, champ_roles)
            chance = 1 - exact_win_prob(state.picks)
            won = play_match(state.picks, rng) == "B"

        total_chance += chance
        if won:
            wins += 1

    return total_chance / num_drafts, wins


def report(name_1, name_2, drafter_1, drafter_2, champ_roles, num_drafts=1000):
    chance, wins = run_matchup(drafter_1, drafter_2, champ_roles, num_drafts)
    print(f"{name_1} vs {name_2}: true win chance {chance:.1%}, record {wins}-{num_drafts - wins}")


if __name__ == "__main__":
    from learn import learn
    from bots import RandomBot, PickRateBot, GreedyBot

    s = learn()
    roles = s["champ_roles"]
    rand = RandomBot(random.Random(1))
    pickrate = PickRateBot(s["pick_rate"], s["ban_rate"], random.Random(2))
    greedy = GreedyBot(s["model"])

    report("Greedy", "Random", greedy, rand, roles)
    report("Pick-rate", "Random", pickrate, rand, roles)
    report("Greedy", "Pick-rate", greedy, pickrate, roles)
