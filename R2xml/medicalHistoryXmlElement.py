# medicalHistory element create
from bs4 import BeautifulSoup
from .helper import helper
from .dataFormatCalculation import dateFormatCalculation
import re
from inspect import currentframe, getframeinfo

current_filename = str(getframeinfo(currentframe()).filename)
medical_regex = r"[0-9][0-9]\.\s|[0-9]\.\s|[A-Z]\.\s"
medical_delimeter = "$"


class medicalHistoryXmlElement:

    def __init__(self, con, row, code_template):
        self.row = row
        self.con = con
        self.code_template = code_template
        self.text = open(self.con.xml_template_medicalHistory, "r", encoding="utf8").read()
        self.history_code_group_default = con.history_code_group_default
        self.helper = helper(row)

    # medical history episode tag calculation with information based on vendor groups
    def get_medicalHistory_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        if self.row['template'] == 'IRMS':
            return self.get_irms_medicalHistory_tag()
        elif self.row['template'] == 'linelist':
            return self.get_linelist_medicalHistory_tag()
        elif self.row['template'] == 'litrature':
            return self.get_litrature_medicalHistory_tag()
        elif self.row['template'] == 'MedWatch':
            return self.get_medwatch_medicalHistory_tag()
        
        
        # Default group mapping
        if self.code_template in self.history_code_group_default:
            complete_other_history = " "
            if self.helper.isNan("OtherRelevantHistory") == 1:
                complete_other_history = self.row['OtherRelevantHistory'].strip()
            if self.helper.isNan("Other relevant history (Cont...)") == 1:
                complete_other_history = complete_other_history + self.row['Other relevant history (Cont...)'].strip()

            complete_other_history = (complete_other_history).split("Continuing:")
            history_collection = []

            for x in range(0, len(complete_other_history)):
                try:
                    if complete_other_history[x + 1]:
                        history_collection.append(
                            complete_other_history[x] + "Continuing:" + complete_other_history[x + 1][
                                                                        :complete_other_history[
                                                                             x + 1].index(")") + 1])
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            for y in history_collection:
                try:
                    data_medra = y[y.index("[") + 1:y.index("[") + 15]
                    medra_code = re.findall(r'\d+', data_medra)[0]

                    r = re.compile(r"\byes\b|\bunk\b|\bno\b|\bunknown\b", flags=re.I | re.X)
                    Continuing = r.findall(y[y.index("Continuing:"):])[0].lower()
                    continue_value = ''
                    if Continuing == "yes":
                        continue_value = 1
                    elif Continuing == "no":
                        continue_value = 2
                    elif Continuing == "unk":
                        continue_value = 3
                    elif Continuing == "unknown":
                        continue_value = 3

                    date_raw = y[y.index("]") + 1:]

                    start_date = ""
                    end_date = ""

                    date_both = dateFormatCalculation().get_data(
                        date_raw[date_raw.find("("):date_raw.find(")")].replace("(", "").strip(),
                        1).split('_')
                    try:
                        if date_both[0]:
                            start_date = date_both[0]
                    except IndexError as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    try:
                        if date_both[1]:
                            end_date = date_both[1]
                    except IndexError as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    soup.find('patientepisodename').string = str(medra_code)
                    soup.find('patientmedicalstartdateformat').string = "102"
                    soup.find('patientmedicalstartdate').string = str(start_date)
                    soup.find('patientmedicalenddateformat').string = "102"
                    soup.find('patientmedicalenddate').string = str(end_date)
                    soup.find('patientmedicalcontinue').string = str(continue_value)

                    final_tag.append(soup)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return final_tag

    def get_medra_code(self, para):
        medical_history_list_final = 0
        try:
            result = self.helper.get_medra_with_string(para)
            medical_history_list = list(result['medra_code'])
            if len(medical_history_list) > 0:
                medical_history_list_final = int(medical_history_list[0])
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return medical_history_list_final

    def get_irms_medicalHistory_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')

        if self.code_template in self.history_code_group_default:
            try:
                self.helper.remove_junk_medical_history_irms(self.row['PAST MEDICAL HISTORY:'])
                data_medra = self.helper.remove_junk_medical_history_irms(self.row['PAST MEDICAL HISTORY:'])
                medra_code = re.sub(medical_regex, medical_delimeter, data_medra.strip())
                medra_code = [st.strip() for st in medra_code.split("$") if len(st) > 0]
                for x in medra_code:
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    if self.get_medra_code(x) != 0:
                        soup.find('patientepisodename').string = str(self.get_medra_code(x))

                    final_tag.append(soup)
            except Exception as e:
                self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return final_tag

    def get_linelist_medicalHistory_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        try:
            medra_code = self.row['past_medical_history_continue']
            medra_code = [st.strip() for st in medra_code.split(";") if len(st) > 0]
            for x in medra_code:
                soup = BeautifulSoup(self.text, 'lxml-xml')
                if self.get_medra_code(x) != 0:
                    soup.find('patientepisodename').string = str(self.get_medra_code(x))
                else:
                    soup.find('patientmedicalcomment').string = str(x)
                final_tag.append(soup)
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        try:
            medra_code = self.row['past_medical_history_continue1']
            medra_code = [st.strip() for st in medra_code.split(";") if len(st) > 0]
            for x in medra_code:
                soup = BeautifulSoup(self.text, 'lxml-xml')
                if self.get_medra_code(x) != 0:
                    soup.find('patientepisodename').string = str(self.get_medra_code(x))
                else:
                    soup.find('patientmedicalcomment').string = str(x)
                final_tag.append(soup)
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return final_tag

    def process_list_values(self, data):
        try:
            return ", ".join(str(v) for v in eval(str(data)))
        except Exception as e:
            return data

    def get_litrature_medicalHistory_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        row = self.row
        if 'patientepisodename' in row:
            epi_name = str(self.process_list_values(row['patientepisodename'])).split(',')
            if len(epi_name) > 0:
                for ename in epi_name:
                    try:
                        epi_name_meddra = self.get_medra_code(str(ename).strip())
                        if len(epi_name_meddra) > 0:
                            soup = BeautifulSoup(self.text, 'lxml-xml')
                            soup.find('patientepisodename').string = str(epi_name_meddra)
                            if 'patientmedicalstartdate' in row:
                                soup.find('patientmedicalstartdateformat').string = "102"
                                soup.find('patientmedicalstartdate').string = dateFormatCalculation().get_date.get_data(
                                    row['patientmedicalstartdate'], 1)

                            if 'patientmedicalenddate' in row:
                                soup.find('patientmedicalenddateformat').string = "102"
                                soup.find('patientmedicalenddate').string = dateFormatCalculation().get_date.get_data(
                                    row['patientmedicalenddate'], 1)

                            final_tag.append(soup)
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return final_tag


    def get_medwatch_medicalHistory_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        print("Medical History")

        # if self.code_template in self.history_code_group_default:
            # print("If Medical History")
        try:
            # OtherRelevantHistory, OtherRlevantHistoryContinue
            complete_other_history = " "
            if self.helper.isNan("OtherRelevantHistory") == 1:
                complete_other_history = self.row['OtherRelevantHistory'].strip()
            if self.helper.isNan("OtherRlevantHistoryContinue") == 1:
                complete_other_history = complete_other_history + self.row["OtherRlevantHistoryContinue"].strip()


            # Split the string based on "Spontaneous report"
            split_result = complete_other_history.split("Pregnant", 1)

            # Take the first part
            result_string = split_result[0].strip()

            words_to_remove = ['[continued]']

            # Remove matching words
            for word in words_to_remove:
                result_string = result_string.replace(word, '')

            # Split the string using commas and line breaks
            split_result = re.split(',', result_string)

            print("Medical History", split_result)

            # complete_other_history = (complete_other_history).split("Continuing:")
        
            # self.helper.remove_junk_medical_history_irms(self.row['PAST MEDICAL HISTORY:'])
            # data_medra = self.helper.remove_junk_medical_history_irms(self.row['PAST MEDICAL HISTORY:'])
            medra_code = re.sub(medical_regex, medical_delimeter, result_string)
            medra_code = [st.strip() for st in medra_code.split("$") if len(st) > 0]
            for x in medra_code:
                soup = BeautifulSoup(self.text, 'lxml-xml')
                if self.get_medra_code(x) != 0:
                    soup.find('patientepisodename').string = str(self.get_medra_code(x))

                final_tag.append(soup)
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return final_tag

    