# initial reporter qualification e2b code mapping
class initialReporterQualificationE2b:
    def get_current_e2b(self):

        if self.key in self.qualification:
            return self.qualification[self.key]
        else:
            return 0

    def __init__(self, key):

        self.qualification = {
            "physician": 1,
            "pharmacist": 2,
            "other health professional": 3,
            "nurse": 3,
            "lawyer": 4,
            "consumer": 5,
            "consumer or other non-health professional": 5
        }
        self.key = key
