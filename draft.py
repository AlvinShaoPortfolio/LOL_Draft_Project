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
    def __init__(self, champ_roles, picks=None, bans=None, step=0):
        #lookup table of every champion -> set of roles, so methods can use self.champ_roles
        self.champ_roles = champ_roles

        #each team starts with all 5 roles empty (None)
        self.picks = picks if picks is not None else {
            "A": {r: None for r in ROLES},
            "B": {r: None for r in ROLES},
        }
        self.bans = bans if bans is not None else set()
        self.step = step

    #updating gamestate
    def next_state(self, character):
        #team + pick/ban
        team, choice = DRAFT_ORDER[self.step]

        #creating a copy because i need to have a 
        #new state while retaining the previous state for MCTS
        new = DRAFT_STATE(
            self.champ_roles,
            {t: dict(roles) for t, roles in self.picks.items()},  
            set(self.bans),                                     
            self.step,
        )

        if choice == "ban": #adding to character to bans
            new.bans.add(character)
        else:
            #getting the role of the character 
            role = next(iter(self.champ_roles[character]))  

            #placing the character in that team's role slot
            #picks = {"A": {role: character or None}, "B": {role: character or None}}
            #e.g. team A picks 14 (mid):
            #  before: {"A": {"top": 3, "jungle": None, "mid": None, "bot": None, "support": None}, "B": {...}}
            #  after:  {"A": {"top": 3, "jungle": None, "mid": 14,   "bot": None, "support": None}, "B": {...}}
            new.picks[team][role] = character
        new.step += 1

        return new
    
    #returns list of characters if state is either a ban or pick
    def legal_moves(self):
        #getting the team and pick at current step
        team, choice = DRAFT_ORDER[self.step]

        #every champion already banned or picked by either team
        used = self.bans | {c for t in self.picks.values() for c in t.values() if c is not None}

        #all champions except taken
        available = set(self.champ_roles) - used

        #if current step is a ban return list of characters not picked or banned yet
        if choice == "ban":
            return list(available)

        #if current step is a pick then it has to be not picked or banned in the role
        moves = []
        for champ in available:
            role = next(iter(self.champ_roles[champ]))
            if self.picks[team][role] is None:
                moves.append(champ)

        return moves 

    #returns true if 20 steps is done.
    def is_done(self):
        return self.step == len(DRAFT_ORDER)
    