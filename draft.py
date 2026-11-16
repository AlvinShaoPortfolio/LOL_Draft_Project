import copy

#adding roles and draft step tuples 
DRAFT_ORDER = [
    ("A", "ban"), ("B", "ban"), ("A", "ban"), ("B", "ban"), ("A", "ban"), ("B", "ban"),

    ("A", "pick"), ("B", "pick"), ("B", "pick"), 
    ("A", "pick"), ("A", "pick"), ("B", "pick"),

    ("B", "ban"), ("A", "ban"), ("B", "ban"), ("A", "ban"),

    ("B", "pick"), ("A", "pick"), ("A", "pick"), ("B", "pick"),
]
ROLES = ["top", "jungle", "mid", "bot", "support"]

#creating a draft state to be able to update the game state
class DRAFT_STATE:
    #constructor
    def __init__(self, picks=None, bans=None, step=0):
        #each team starts with all 5 roles empty (None)
        self.picks = picks if picks is not None else {
            "A": {r: None for r in ROLES},
            "B": {r: None for r in ROLES},
        }
        self.bans = bans if bans is not None else set()
        self.step = step

    #updating gamestate
    def next_state(self, character, champ_roles):
        #team + pick/ban
        team, choice = DRAFT_ORDER[self.step]

        #creating a copy because i need to have a 
        #new state while retaining the previous state for MCTS
        new = copy.deepcopy(self)
        if choice == "ban": #adding to character to bans
            new.bans.add(character)
        else:
            #getting the role of the character 
            role = next(iter(champ_roles[character]))  

            #placing the character in that team's role slot
            #picks = {"A": {role: character or None}, "B": {role: character or None}}
            #e.g. team A picks 14 (mid):
            #  before: {"A": {"top": 3, "jungle": None, "mid": None, "bot": None, "support": None}, "B": {...}}
            #  after:  {"A": {"top": 3, "jungle": None, "mid": 14,   "bot": None, "support": None}, "B": {...}}
            new.picks[team][role] = character
        new.step += 1

        return new
    
    
    


