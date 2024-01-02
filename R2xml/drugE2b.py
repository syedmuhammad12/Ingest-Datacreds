# Action taken with drug e2b code mapping
class drugE2b:
    def __init__(self, key):
        self.drug_action = {
            "Drug withdrawn": 1,
            "Dose reduced": 2,
            "Dose increased": 3,
            "Dose not changed": 4,
            "Dosage maintained": 4,
            "Drug discontinued": 1,
            "Unknown": 5,
            "drug withdrawn": 1,
            "dose reduced": 2,
            "dose increased": 3,
            "dose not changed": 4,
            "dosage maintained": 4,
            "drug discontinued": 1,
            "unknown": 5,
            "not applicable": 6,
            "Not Applicable": 6,
            "Drug Withdrawn": 1,
            "Dose Reduced": 2,
            "Dose Increased": 3,
            "Dose Not Changed": 4,
            "Dosage Maintained": 4,
            "Drug Discontinued": 1,
            "Not applicable": 6,
            "Treatment_Stop": 1,
            "Treatment_Increase": 2,
            "Treatment_Decrease": 3,
            "Treatment_Continue": 4,
            "Treatment_NA": 6
        }

        self.route_of_admin = {
            "Auricular (otic)": "001",
            "Buccal": "002",
            "Cutaneous": "003",
            "Dental": "004",
            "Endocervical": "005",
            "Endosinusial": "006",
            "Endotracheal": "007",
            "Epidural": "008",
            "Extra-amniotic": "009",
            "Hemodialysis": "010",
            "Intra corpus cavernosum": "011",
            "Intra-amniotic": "012",
            "Intra-arterial": "013",
            "Intra-articular": "014",
            "Intra-uterine": "015",
            "Intracardiac": "016",
            "Intracavernous": "017",
            "Intracerebral": "018",
            "Intracervical": "019",
            "Intracisternal": "020",
            "Intracorneal": "021",
            "Intracoronary": "022",
            "Intradermal": "023",
            "Intradiscal (ntraspinal)": "024",
            "Intrahepatic": "025",
            "Intralesional": "026",
            "Intralymphatic": "027",
            "Intramedullar (bone marrow)": "028",
            "Intrameningeal": "029",
            "Intramuscular": "030",
            "Intraocular": "031",
            "Intrapericardial": "032",
            "Intraperitoneal": "033",
            "Intrapleural": "034",
            "Intrasynovial": "035",
            "Intratumor": "036",
            "Intrathecal": "037",
            "Intrathoracic": "038",
            "Intratracheal": "039",
            "Intravenous bolus": "040",
            "Intravenous drip": "041",
            "Intravenous (not otherwise specified)": "042",
            "Intravenous": "042",
            "Intravesical": "043",
            "Iontophoresis": "044",
            "Nasal": "045",
            "Occlusive dressing technique": "046",
            "Ophthalmic": "047",
            "Oral": "048",
            "Oropharingeal": "049",
            "Other": "050",
            "Parenteral": "051",
            "Periarticular": "052",
            "Perineural": "053",
            "Rectal": "054",
            "Respiratory (inhalation)": "055",
            "Retrobulbar": "056",
            "Sunconjunctival": "057",
            "Subcutaneous": "058",
            "Subdermal": "059",
            "Sublingual": "060",
            "Topical": "061",
            "Transdermal": "062",
            "Transmammary": "063",
            "Transplacental": "064",
            "Unknown": "065",
            "Urethral": "066",
            "Vaginal": "067"
        }

        self.drug_dosage_unit = {
            "kg kilogram(s)": "001",
            "G gram(s)": "002",
            "Mg milligram(s)": "003",
            "μg microgram(s)": "004",
            "ng nanogram(s)": "005",
            "pg picogram(s)": "006",
            "mg/kg milligram(s)/kilogram": "007",
            "μg/kg microgram(s)/kilogram": "008",
            "mg/m 2 milligram(s)/sq. meter": "009",
            "μg/m 2 microgram(s)/ sq. Meter": "010",
            "l litre(s)": "011",
            "ml millilitre(s)": "012",
            "μl microlitre(s)": "013",
            "Bq becquerel(s)": "014",
            "GBq gigabecquerel(s)": "015",
            "MBq megabecquerel(s)": "016",
            "Kbq kilobecquerel(s)": "017",
            "Ci curie(s)": "018",
            "MCi millicurie(s)": "019",
            "μCi microcurie(s)": "020",
            "NCi nanocurie(s)": "021",
            "Mol mole(s)": "022",
            "Mmol millimole(s)": "023",
            "μmol micromole(s)": "024",
            "Iu international unit(s)": "025",
            "Kiu iu(1000s)": "026",
            "Miu iu(1:000:000s)": "027",
            "iu/kg iu/kilogram": "028",
            "Meq milliequivalent(s)": "029",
            "% percent": "030",
            "Gtt drop(s)": "031",
            "DF dosage form": "032",
        }
        self.key = key

    def get_drug_action_e2b(self):
        for x in self.drug_action:
            if self.key.find(x) > -1:
                return self.drug_action[x]
        else:
            return 0

    def get_route_of_admin_e2b(self):
        for x in self.route_of_admin:
            if self.key.find(x) > -1:
                return self.route_of_admin[x]
        else:
            return 0

    def get_drug_dosage_unit_e2b(self):
        if self.key in self.drug_dosage_unit:
            return self.drug_dosage_unit[self.key]
        else:
            return 0

    def get_drug_dosage_linelist_unit_e2b(self):
        for x in self.drug_dosage_unit:
            lower_case = x.lower()
            if lower_case.find(self.key.lower()) > -1:
                return self.drug_dosage_unit[x]
        else:
            return 0
