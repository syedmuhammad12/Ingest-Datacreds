# seriousness e2b code mapping
class seriousnessE2b:
    def get_seriousness_irms(self):
        exist = 0
        if self.key in self.seriousness_irms:
            exist = self.seriousness_irms[self.key]

        return exist

    def __init__(self, key):
        self.seriousness_irms = {}
        self.seriousness_irms = self.seriousness_irms.fromkeys([
            "death", "dead"], 1)
        self.seriousness_irms.update(self.seriousness_irms.fromkeys(["life threatening", "life-threatening"], 2))
        self.seriousness_irms.update(self.seriousness_irms.fromkeys(["hospitalization", "hospitalisation"], 3))
        self.seriousness_irms.update(self.seriousness_irms.fromkeys(["disabling","incapacitating"], 4))
        self.seriousness_irms.update(self.seriousness_irms.fromkeys(
            ["congenital anomali", "congenital-anomali", 'congenital anomalies', "congenital-anomalies"], 5))
        self.seriousness_irms.update(self.seriousness_irms.fromkeys(["other"], 6))
        self.key = key.lower()

    def get_seriousness_linelist(self):
        exist = []
        for val in self.seriousness_irms:
            if self.key.find(val) > -1:
                exist.append(self.seriousness_irms[val])
        return exist
