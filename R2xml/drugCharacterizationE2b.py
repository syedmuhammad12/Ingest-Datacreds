# drug characterization e2b code mapping
class drugCharacterizationE2b:
    def get_current_e2b(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def __init__(self, key):
        self.thisdict = {
            "Suspect": 1,
            "Concomitant": 2,
            "Interacting": 3
        }
        self.key = key
