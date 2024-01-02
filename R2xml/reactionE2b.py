# reaction e2b code mapping
class reactionE2b:
    def get_reaction_outcome_e2b(self):

        if self.key in self.reaction_outcome:
            return self.reaction_outcome[self.key]
        else:
            return 0

    def __init__(self, key):

        self.reaction_outcome = {
            "recovered/resolved": 1,
            "recovered": 1,
            "resolved": 1,
            "recovering/resolving": 2,
            "recovering": 2,
            "resolving": 2,
            "not recovered/not resolved": 3,
            "not recovered": 3,
            "not resolved": 3,
            "recovered/resolved with sequel": 4,
            "recovered with sequel": 4,
            "resolved with sequel": 4,
            "fatal": 5,
            "unknown": 6,
            "unk": 6
        }
        self.key = key.lower()
