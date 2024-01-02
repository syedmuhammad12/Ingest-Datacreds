# report source e2b code mapping for checkbox field
class reportSourceE2b:
    def get_study(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def get_litrature(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def get_authority(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def get_other_health_professional(self):
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
