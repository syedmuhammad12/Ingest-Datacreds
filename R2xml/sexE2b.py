# gender e2b code mapping
class sexE2b:
    def get_sex_e2b(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return ''

    def __init__(self, key):
        self.thisdict = {
            "M": 1,
            "m": 1,
            "male": 1,
            "Male": 1,
            "MALE": 1,
            "F": 2,
            "f": 2,
            "female": 2,
            "Female": 2,
            "FEMALE": 2
        }
        self.key = key
