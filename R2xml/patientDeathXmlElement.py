# reaction element create
from bs4 import BeautifulSoup
from .helper import helper
from inspect import currentframe, getframeinfo
from .dataFormatCalculation import dateFormatCalculation

current_filename = str(getframeinfo(currentframe()).filename)


class patientDeathXmlElement:

    def __init__(self, con, row, code_template):
        """constructor patient death tag data mapping"""
        text = open(con.xml_template_patientDeath, "r", encoding="utf8").read()
        self.soup = BeautifulSoup(text, 'lxml-xml')
        self.row = row
        self.code_template = code_template
        self.helper = helper(row)

    def autopsy(self, key):
        value_dict = {"yes": 1, "no": 2, 'unknown': 3}
        return str(value_dict.get(key.lower()))

    def get_patient_death_tag(self):
        """patient death tag data mapping"""
        soup = self.soup
        row = self.row
        if row['template'] == 'linelist':
            return self.get_patient_death_linelist_tag()
        try:
            if int(dateFormatCalculation().get_date(row.get('DATE OF DEATH (If died):', ''))) > 0:
                soup.find('patientdeathdateformat').string = "102"
                soup.find('patientdeathdate').string = str(
                    dateFormatCalculation().get_date(row.get('DATE OF DEATH (If died):', '')))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            if self.autopsy(str(row.get('AUTOPSY (YES/NO/UNKNOWN):', ''))) != "None":
                soup.find('patientautopsyyesno').string = self.autopsy(str(row.get('AUTOPSY (YES/NO/UNKNOWN):', '')))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return soup

    def get_patient_death_linelist_tag(self):
        """patient death tag data mapping"""
        soup = self.soup
        row = self.row

        try:
            row['death_date']

            death_date = row['death_date']
            soup.find('patientdeathdate').string = str(dateFormatCalculation().get_date(death_date))
            soup.find('patientdeathdateformat').string = "102"
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return soup
