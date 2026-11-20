#Solver: learns from game results only.
import csv
import math
import random
from sklearn.linear_model import LogisticRegression
from draft import ROLES

GAMES_FILE = "data/games.csv"
TEST_FRACTION = 0.2

#converts a csv line to picks. Basically just reversing what generator.py did
def load_games(path=GAMES_FILE):
    games = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            game = {
                "A": {role: int(row[f"a_{role}"]) for role in ROLES},
                "B": {role: int(row[f"b_{role}"]) for role in ROLES},
                "bans": [int(c) for c in row["bans"].split(";")],
                "a_win": int(row["a_win"]),
            }
            games.append(game)
    return games

#shuffling and splitting games into 80% training and 20% testing
def split_games(games, test_fraction=TEST_FRACTION, seed=0):
    games = games[:]
    random.Random(seed).shuffle(games)
    cut = int(len(games) * (1 - test_fraction))
    return games[:cut], games[cut:]

#creates a dictionary to keep track of all roles a character plays char_num: {roles}
def champ_roles_from(games):
    champ_roles = {}
    for game in games:
        for team in ["A", "B"]:
            for role, champ in game[team].items():
                champ_roles.setdefault(champ, set()).add(role)
    return champ_roles

#how often each champion is picked / banned, out of all games 
def pick_ban_rates(games, champions):
    picks = {c: 0 for c in champions}
    bans = {c: 0 for c in champions}
    for game in games:
        for team in ["A", "B"]:
            for champ in game[team].values():
                picks[champ] += 1
        for champ in game["bans"]:
            bans[champ] += 1
    n = len(games)
    pick_rate = {c: picks[c] / n for c in champions}
    ban_rate = {c: bans[c] / n for c in champions}
    return pick_rate, ban_rate

#turning the team dictionary into a list of 0, -1, 1. The 1 indicates on team A, -1 on team B
#and 0 is unpicked. Used for logistic regression
def features(picks, champions):
    index = {c: i for i, c in enumerate(champions)}
    x = [0] * len(champions)
    for champ in picks["A"].values():
        x[index[champ]] = 1
    for champ in picks["B"].values():
        x[index[champ]] = -1
    return x

#trained win model: stores the learned weights over training 8000 games. 
class WinModel:
    def __init__(self, bias, weights):
        self.bias = bias          
        self.weights = weights    

    #chance team A wins, from a finished draft's picks
    def predict_win(self, picks):
        score = self.bias
        for champ in picks["A"].values():
            score += self.weights[champ]
        for champ in picks["B"].values():
            score -= self.weights[champ]
        return 1 / (1 + math.exp(-score))

#trains logistic regression on the training games
def train_model(train_games, champions):
    #inputs 
    X = [features(g, champions) for g in train_games]

    #the answers
    y = [g["a_win"] for g in train_games]

    #creating the model
    lr = LogisticRegression()

    #training 
    lr.fit(X, y)

    #building a dict of each champion's learned weight 
    weights = {c: float(lr.coef_[0][i]) for i, c in enumerate(champions)}
    return WinModel(float(lr.intercept_[0]), weights)

#fraction of games where the model picked the right winner
def accuracy(model, games):
    correct = 0
    for g in games:
        predicted_a = model.predict_win(g) >= 0.5

        if predicted_a == (g["a_win"] == 1):
            correct += 1
    return correct / len(games)

#runs the entire pipeline to learn
def learn(path=GAMES_FILE):
    games = load_games(path) #reading games.csv
    train, test = split_games(games) # splitting games 80/20
    champ_roles = champ_roles_from(games) # who plays what roles
    champions = sorted(champ_roles) # getting the list of all champion ids
    pick_rate, ban_rate = pick_ban_rates(train, champions) # getting the popularity of characters
    model = train_model(train, champions) #train the model
    return { #putting everything in one dict
        "champ_roles": champ_roles,
        "pick_rate": pick_rate,
        "ban_rate": ban_rate,
        "model": model,
        "train": train,
        "test": test,
    }

if __name__ == "__main__":
    s = learn()
    model = s["model"]
    print(f"champions: {len(s['champ_roles'])}")
    print(f"train accuracy: {accuracy(model, s['train']):.3f}")
    print(f"test accuracy:  {accuracy(model, s['test']):.3f}")
    top = sorted(model.weights, key=lambda c: -model.weights[c])[:5]
    print("highest learned weights:", [(c, round(model.weights[c], 3)) for c in top])
