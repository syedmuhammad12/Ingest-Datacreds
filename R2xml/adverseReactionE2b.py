# Adverse reaction with drug e2b code mapping
class adverseReactionE2b:
    def get_patient_died(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def get_life_threatening(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def get_inpatient_hospitalization(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def get_congenital_anomaly(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def other_medically_important_condition(self):
        if self.key in self.thisdict:
            return self.thisdict[self.key]
        else:
            return 0

    def disability(self):
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
