# getting e2b for patient age
class ageUnitE2b(object):
    def get_age_unit_e2b(self, key):
        if key.lower() in self.age_unit:
            return self.age_unit[key.lower()]
        else:
            return 0

    def get_pre_unit_irms(self, key):
        exist = 0
        for val in self.preg_irms:
            if key.lower().find(self.preg_irms[val]) > -1:
                exist = val
                break

        return exist

    def get_age_group(self, age):
        if age >= 50:
            result = 6
        elif 20 <= age < 50:
            result = 5
        elif 10 <= age < 20:
            result = 4
        elif 2 <= age < 10:
            result = 3
        elif 1 <= age < 2:
            result = 2
        else:
            result = 1
        return result

    def get_age_group_string(self):
        if self.key in self.age_group_string:
            return self.age_group_string[self.key]
        else:
            return 0

    def __init__(self):
        self.age_unit = {}
        self.age_unit = self.age_unit.fromkeys([
            "year",
            "years",
            "yrs",
            "YRS",
            "vs",
            "us",
            "vs",
            "irs",
            "ns",
            "years",
            "Years",
            "s",
            "ears",
            "¥ears","year(s)","years-old","Years Old","year old","yearold"], 801)
        self.age_unit.update(self.age_unit.fromkeys(["decade", "decades"], 800))
        self.age_unit.update(self.age_unit.fromkeys(["month", "months"], 802))
        self.age_unit.update(self.age_unit.fromkeys(["week", "weeks"], 803))
        self.age_unit.update(self.age_unit.fromkeys(["day", "days"], 804))
        self.age_unit.update(self.age_unit.fromkeys(["hour", "hours"], 805))
        self.age_unit.update(self.age_unit.fromkeys(["minute", "minutes"], 806))
        self.age_group_string = {
            "Neonate": 1,
            "Infant": 2,
            "Child": 3,
            "Adolescent": 4,
            "Adult": 5,
            "Elderly": 6,
        }

        self.preg_irms = {802: 'month', 803: 'week', 804: 'day', 810: 'trimester'}

