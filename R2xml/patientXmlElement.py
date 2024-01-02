# patient element create
from bs4 import BeautifulSoup
from .ageUnitE2b import ageUnitE2b
from .dataFormatCalculation import dateFormatCalculation
from .sexE2b import sexE2b
from .helper import helper
from .heightE2b import heightE2b
from .weightE2b import weightE2b
from inspect import currentframe, getframeinfo
import re

current_filename = str(getframeinfo(currentframe()).filename)


class patientXmlElement:
    def __init__(self, con, row, code_template):
        text = open(con.xml_template_patient, "r", encoding="utf8").read()
        self.soup = BeautifulSoup(text, 'lxml-xml')
        self.row = row
        self.code_template = code_template
        self.helper = helper(row)

    # Main patient tag with information return
    def get_patient_tag(self):
        soup = self.soup
        row = self.row
        try:
            if row['template'] == 'IRMS':
                return self.get_irms_patient_tag()
            elif row['template'] == 'linelist':
                return self.get_linelist_patient_tag()
            elif row['template'] == 'litrature':
                return self.get_litrature_patient_tag()
            elif row['template'] == 'MedWatch':               
                return self.get_medwatch_patient_tag()
            else:
                try:
                    if self.helper.isNan('PatientInitials') == 1:
                        soup.find('patientinitial').string = str(row['PatientInitials'])
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    soup.find('patientbirthdate').string = str(dateFormatCalculation().get_data(
                        str(row['Day_DOB']) + "-" + str(row['Month_DOB']) + "-" + str(row['Year_DOB']), 1))
                    soup.find('patientbirthdateformat').string = "102"
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    soup.find('patientonsetage').string = str(self.helper.get_integer('Age'))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    soup.find('patientonsetageunit').string = str(
                        ageUnitE2b().get_age_unit_e2b(self.helper.get_string('Age')))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    if self.helper.get_integer('Age') != "":
                        soup.find('patientagegroup').string = str(
                            ageUnitE2b().get_age_group(self.helper.get_integer('Age')))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    soup.find('patientweight').string = str(self.helper.get_float('Weight'))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    soup.find('patientheight').string = str(self.helper.get_float('Height'))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if self.helper.isNan('Sex') == 1:
                        soup.find('patientsex').string = str(sexE2b(row['Sex']).get_sex_e2b())
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    
                


        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return soup

    def get_preg_data_irms(self, data):
        if data.find("(") > -1:
            data = data[:data.find("(")]
        final_data = {'pre_data': re.findall(r'\d+', data), 'pre_str': data.strip()}
        return final_data

    def get_irms_patient_tag(self):
        soup = self.soup
        row = self.row
        try:
            weight = str(row.get('WEIGHT (POUNDS):', '').strip()) if 'WEIGHT (POUNDS):' in row.keys() else str(
                row.get('WEIGHT (Kg):', '').strip())
            weight = self.helper.remove_junk_patient_weight_irms(weight)
            soup.find('patientweight').string = str(weightE2b().weightUnit(str(weight), row))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            height = str(row.get('HEIGHT (INCHES):', '').strip())
            height = self.helper.remove_junk_patient_height_irms(height)
            soup.find('patientheight').string = str(heightE2b().heightUnit(str(height)))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            if dateFormatCalculation().get_date(row.get('DOB', '')) != '':
                soup.find('patientbirthdateformat').string = "102"
                soup.find('patientbirthdate').string = str(dateFormatCalculation().get_date(row.get('DOB', '')))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            soup.find('patientonsetage').string = str(self.helper.get_integer('AGE'))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            if int(ageUnitE2b().get_age_unit_e2b(self.helper.get_string('AGE'))) > 0:
                soup.find('patientonsetageunit').string = str(
                    ageUnitE2b().get_age_unit_e2b(self.helper.get_string('AGE')))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            if self.helper.get_integer('AGE') != "":
                soup.find('patientagegroup').string = str(ageUnitE2b().get_age_group(self.helper.get_integer('AGE')))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            if self.helper.isNan('Gender:') == 1:
                soup.find('patientsex').string = str(sexE2b(row['Gender:']).get_sex_e2b())
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:

            data = self.helper.remove_junk_patient_initials_irms(self.row['PATIENT INFORMATION:'])
            if len(data) == 0:
                data = "unknown"
            soup.find('patientinitial').string = str(data)
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            soup.find('patientmedicalhistorytext').string = str(
                self.helper.remove_junk_medical_history_irms(self.row['PAST MEDICAL HISTORY:']))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            patient_gp = row['GESTATION PERIOD:']
            result = self.get_preg_data_irms(patient_gp)

            if len(result['pre_data']) > 0:
                soup.find('gestationperiod').string = str(result['pre_data'][0])
            pre_unit_result = ageUnitE2b().get_pre_unit_irms(result['pre_str'])
            if pre_unit_result > 0:
                soup.find('gestationperiodunit').string = str(pre_unit_result)
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        try:
            patient_lmpd = row['LAST MENSTRUAL PERIOD DATE:']
            if int(dateFormatCalculation().get_data(patient_lmpd, 1)) > 0:
                soup.find('patientlastmenstrualdate').string = str(dateFormatCalculation().get_data(patient_lmpd, 1))
                soup.find('lastmenstrualdateformat').string = "102"
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return soup

    def get_linelist_patient_tag(self):
        soup = self.soup
        row = self.row
        try:
            weight = self.row['weight']
            soup.find('patientweight').string = str(weight)
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        # try:
        #     height = str(row.get('HEIGHT (INCHES):', '').strip())
        #     height = self.helper.remove_junk_patient_height_irms(height)
        #     soup.find('patientheight').string = str(heightE2b().heightUnit(str(height)))
        # except Exception as e:
        #     self.helper.error_log(
        #         current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            birth_date = row['birth_date']
            if birth_date != '':
                soup.find('patientbirthdate').string = str(dateFormatCalculation().get_date(birth_date))
                soup.find('patientbirthdateformat').string = "102"
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            soup.find('patientonsetage').string = str(self.row['age_val'])
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            age_unit = int(ageUnitE2b().get_age_unit_e2b(self.helper.get_string('age_unit')))
            if age_unit > 0:
                soup.find('patientonsetageunit').string = str(age_unit)
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            if self.row['age_val'] != "":
                soup.find('patientagegroup').string = str(ageUnitE2b().get_age_group(self.row['age_val']))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            if self.helper.isNan('sex') == 1:
                soup.find('patientsex').string = str(sexE2b(row['sex']).get_sex_e2b())
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            soup.find('patientinitial').string = str(row['patientinitial'])
        except Exception as e:
            soup.find('patientinitial').string = str("unknown")
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        # patientmedicalhistorytext = ''
        # try:
        #     patientmedicalhistorytext += self.row['past_medical_history_continue']
        #
        # except Exception as e:
        #     self.helper.error_log(
        #         current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        #
        # try:
        #     patientmedicalhistorytext += self.row['past_medical_history_continue1']
        #
        # except Exception as e:
        #     self.helper.error_log(
        #         current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        #
        # soup.find('patientmedicalhistorytext').string = str(patientmedicalhistorytext)
        return soup

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

    def get_litrature_patient_tag(self):
        soup = self.soup
        row = self.row
        try:
            if 'patientinitial' in row:
                soup.find('patientinitial').string = str(self.process_list_get_one(row['patientinitial']))

            if 'patientbirthdate' in row:
                soup.find('patientbirthdate').string = str(row['patientbirthdate'])
                soup.find('patientbirthdateformat').string = "102"

            # soup.find('patientbirthdate').string = str(dateFormatCalculation().get_data(
            #     str(row['Day_DOB']) + "-" + str(row['Month_DOB']) + "-" + str(row['Year_DOB']), 1))
            # soup.find('patientbirthdateformat').string = "102"

            if 'patientonsetage' in row:
                age = self.helper.return_int_if_exists(self.process_list_get_one(str(row['patientonsetage'])))
                if age != "":
                    soup.find('patientonsetage').string = str(age)
                    soup.find('patientagegroup').string = str(ageUnitE2b().get_age_group(int(age)))

                if 'patientonsetageunit' in row:
                    soup.find('patientonsetageunit').string = str(
                        ageUnitE2b().get_age_unit_e2b(self.helper.get_string('patientonsetageunit')))
                else:
                    soup.find('patientonsetageunit').string = str(ageUnitE2b().get_age_unit_e2b("years"))

            if 'patientweight' in row:
                soup.find('patientweight').string = str(
                    self.helper.return_float_if_exists(self.process_list_values(row['patientweight'])))

            if 'patientheight' in row:
                soup.find('patientheight').string = str(
                    self.helper.return_float_if_exists(self.process_list_values(row['patientheight'])))

            if 'patientsex' in row:
                soup.find('patientsex').string = str(sexE2b(self.process_list_get_one(row['patientsex'])).get_sex_e2b())

            if 'patientmedicalhistorytext' in row:
                soup.find('patientmedicalhistorytext').string = str(
                    self.process_list_values(row['patientmedicalhistorytext']))

            if 'resultstestsprocedures' in row:
                soup.find('resultstestsprocedures').string = str(
                    self.process_list_values(row['resultstestsprocedures']))

        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return soup

    def get_medwatch_patient_tag(self):
        soup = self.soup
        row = self.row
        # print("oooooo------")
        words_to_remove = [".", "in", "In", "confidence", ":"]
        # print(words_to_remove)
        try:
            if self.helper.isNan('PatientInitials') == 1:                
                soup.find('patientinitial').string = self.helper.remove_words(str(row['PatientInitials']), words_to_remove)
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            # soup.find('patientbirthdate').string = str(dateFormatCalculation().get_data(
            #     str(row['Day_DOB']) + "-" + str(row['Month_DOB']) + "-" + str(row['Year_DOB']), 1))
            # print(str(row['Date_of_Birth'].replace('/', '')))
            # Parse the date string in the "dd/mm/yyyy" format
            # print(str(row['Date_of_Birth']))

            # print(str(dateFormatCalculation().date_format_change(str(row['Date_of_Birth']))))

            soup.find('patientbirthdate').string = str(dateFormatCalculation().date_format_change(str(row['Date_of_Birth'])))
            soup.find('patientbirthdateformat').string = "102"
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            soup.find('patientonsetage').string = str(self.helper.get_integer('Age'))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            soup.find('patientonsetageunit').string = str(
                ageUnitE2b().get_age_unit_e2b(self.helper.get_string('Age')))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        try:
            if self.helper.get_integer('Age') != "":
                soup.find('patientagegroup').string = str(
                    ageUnitE2b().get_age_group(self.helper.get_integer('Age')))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:                  
            soup.find('patientweight').string = str(self.helper.weight_logic(str(row['Weight'])))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            soup.find('patientheight').string = str(self.helper.get_float('Height'))
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            print("sex try")
            print(str(row['Female']))
            print(str(row['Male']))
            soup.find('patientsex').string = str(self.helper.patient_sex_logic(str(row['Female']), str(row['Male'])))
            # if self.helper.isNan('Female') == 1:                
            #     soup.find('patientsex').string = str("2")
            # elif self.helper.isNan('Male') == 1:
            #     soup.find('patientsex').string = str("1")

        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            
        try:
            complete_other_history = " "
            if self.helper.isNan("OtherRelevantHistory") == 1:
                complete_other_history = self.row['OtherRelevantHistory'].strip()
            if self.helper.isNan("OtherRlevantHistoryContinue") == 1:
                complete_other_history = complete_other_history + self.row["OtherRlevantHistoryContinue"].strip()

            soup.find('patientmedicalhistorytext').string = str(complete_other_history)

        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return soup