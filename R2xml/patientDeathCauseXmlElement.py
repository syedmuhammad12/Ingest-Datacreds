# reaction element create
from bs4 import BeautifulSoup
from .helper import helper
from inspect import currentframe, getframeinfo

current_filename = str(getframeinfo(currentframe()).filename)


class patientDeathCauseXmlElement:

    def __init__(self, con, row, code_template):
        """constructor reaction DeathCause tag data mapping"""
        self.text = open(con.xml_template_patientDeathCause, "r", encoding="utf8").read()
        self.soup = BeautifulSoup(self.text, 'lxml-xml')
        self.row = row
        self.code_template = code_template
        self.helper = helper(row)

    def get_medra_code(self, para):
        death_cause_list_final = 0
        try:
            result = self.helper.get_medra_with_string(para)
            death_cause_list = list(result['medra_code'])
            if len(death_cause_list) > 0:
                death_cause_list_final = int(death_cause_list[0])
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return death_cause_list_final

    def get_patient_death_cause_tag(self):
        """reaction DeathCause tag data mapping"""
        final_tag = BeautifulSoup("", 'lxml-xml')
        if self.row['template'] == 'litrature':
            return self.get_patient_death_cause_litrature_tag()
        elif self.row['template'] == 'linelist':
            soup = BeautifulSoup(self.text, 'lxml-xml')
            row = self.row
            try:
                soup.find('patientdeathreport').string = str(self.get_medra_code(row['death_cause']))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            final_tag.append(soup)

        return final_tag

    def process_list_values(self, data):
        try:
            return ", ".join(str(v) for v in eval(str(data)))
        except Exception as e:
            return data

    def process_list_get_one(self, data):
        try:
            return eval(str(data))[0]
        except Exception as e:
            return data

    def get_patient_death_cause_litrature_tag(self):
        soup = self.soup
        row = self.row
        try:
            if 'patientdeathreport' in row:
                pat_death_repo = str(self.process_list_values(row['patientdeathreport'])).split(',')
                if len(pat_death_repo) > 0:
                    for pdr in pat_death_repo:
                        pdr_medra = self.get_medra_code(str(pdr).strip())
                        if len(pdr_medra) > 0:
                            past_prod = BeautifulSoup(self.text, 'lxml-xml')
                            past_prod.find('patientdeathreport').string = str(pdr_medra)
                            soup.append(past_prod)
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return soup
