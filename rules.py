import random
from draft import ROLES

random.seed(67)
N = 60

#champion -> set of roles; 12 per role (0-11 top, 12-23 jungle, 24-35 mid, 36-47 bot, 48-59 support)
champ_roles = {c: {ROLES[c // 12]} for c in range(N)}

#N x N matrices, all 0 to start
synergy = [[0] * N for _ in range(N)]
counter = [[0] * N for _ in range(N)]

for i in range(N):
    for j in range(i + 1, N):
        #skip if both fill the same role
        if champ_roles[i] == champ_roles[j]:
            continue

        #every cross-role pair gets a small synergy:
        #mostly 0-6% edge
        v = abs(random.gauss(0, 0.1))
        v = min(0.4, v)
        synergy[i][j] = v
        synergy[j][i] = v  #mirror to bottom-left

for i in range(N):
    for j in range(i + 1, N):
        #counters only happen between champions in the same lane
        if champ_roles[i] != champ_roles[j]:
            continue

        #mostly small edges (~90% under 5%), rare strong ones, capped at ~10%
        #the sign decides who has the edge
        v = random.gauss(0, 0.12)
        v = max(-0.4, min(0.4, v))
        counter[i][j] = v
        counter[j][i] = -v  #mirror to bottom-left, flipped

#individual strengths of champions
strength = {c: random.gauss(0, 0.08) for c in range(N)}

#adding traps so that strong characters have really bad counter matchups so greedy fails
for r in ROLES:
    lane = [c for c in range(N) if r in champ_roles[c]]
    best = max(lane, key=lambda c: strength[c])
    rival = random.choice([c for c in lane if c != best])
    counter[rival][best] = 0.4
    counter[best][rival] = -0.4  #mirror, flipped

#so that it only runs when rules.py directly called
if __name__ == "__main__":
    for i in range(N):
        for j in range(i + 1, N):
            if synergy[i][j] != 0:
                print(i, j, round(synergy[i][j], 2))