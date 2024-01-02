# even occurence
class eventOccurE2b:
    def __init__(self, key):

        self.event_occur = {
            "yes": 1,
            "Yes": 1,
            "YES": 1,
            "no": 2,
            "No": 2,
            "NO": 2,
            "UNK": 3,
            "Unknown": 3
        }
        self.key = key

    def get_current_e2b(self):
        for x in self.event_occur:
            if self.key.find(x) > -1:
                return self.event_occur[self.key]
        else:
            return 0



