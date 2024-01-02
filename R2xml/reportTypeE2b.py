# report type e2b code mapping for checkbox field
class reportTypeE2b:
    def get_initial(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def get_follow_up(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def get_final(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def __init__(self, key):
        self.thisdict = {
            "yes": 1,
            "Yes": 1,
            "YES": 1,
            "no": 2,
            "No": 2,
            "NO": 2,
        }
        self.key = key