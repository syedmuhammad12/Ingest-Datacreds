# its a helper class
import math
import re
import logging
from . import configuration as con
import pandas as pd
from inspect import currentframe, getframeinfo
from spellchecker import SpellChecker

current_filename = str(getframeinfo(currentframe()).filename)


class helper(object):

    def __init__(self, row=None):
        self.row = row

    def isNan(self, key):
        if key in self.row:
            try:
                if math.isnan(self.row[key]):
                    return 0
                else:
                    return 1
            except Exception as e:
                return 1
        else:
            return 0

    def get_integer(self, key):
        if not any(item in self.row[key].lower() for item in ["unk", "np"]):
            if self.isNan(key) == 1:
                if type(self.row[key]).__name__ == "str":
                    return int(re.findall(r'\d+', self.row[key])[0])
                else:
                    return self.row[key]
            else:
                return ""
        else:
            return ""

    def get_float(self, key):
        if self.isNan(key) == 1:
            if type(self.row[key]).__name__ == "str":
                return float(re.findall(r'\d+\.\d+', self.row[key])[0])
            else:
                return self.row[key]
        else:
            return ""

    def return_float_if_exists(self, data):
        fd = re.findall(r"[-+]?\d*\.\d+|\d+", data)
        if len(fd) > 0:
            return float(fd[0])
        return ""

    def return_int_if_exists(self, data):
        fd = re.findall(r"[-+]?\d*\.\d+|\d+", str(data))
        if len(fd) > 0:
            return int(fd[0])
        return ""

    def get_string(self, key):
        if self.isNan(key) == 1:
            if type(self.row[key]).__name__ == "str":
                return ''.join(filter(str.isalpha, self.row[key]))
            else:
                return ""
        else:
            return ""

    def duration_filter(self, duration):
        returnduration = ""

        try:
            duration = duration.lower().replace("(s)", "")
        except Exception as e:
            duration = duration.lower()
        duration_total = 0
        year = 356
        month = 30
        week = 7
        cycle = 7

        try:
            if duration.find(")") > -1:
                returnduration = duration[duration.find(")") + 1:]
            else:
                returnduration = duration
        except Exception as e:
            returnduration = duration

        try:
            if duration.find("#1") > -1:
                returnduration = duration[duration.find("#1") + 2:].strip()
            else:
                returnduration = duration
        except Exception as e:
            returnduration = duration

        try:
            if duration.find("#2") > -1:
                returnduration = duration[duration.find("#2") + 2:].strip()
            else:
                returnduration = duration
        except Exception as e:
            returnduration = duration

        try:
            index_year = returnduration[:returnduration.find("year")].strip()
            duration_total += (int(str(index_year)) * year)
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            index_month = returnduration[returnduration.find("month") - 2: returnduration.find("month")].strip()
            duration_total += (int(str(index_month)) * month)
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        try:
            index_week = returnduration[returnduration.find("week") - 2: returnduration.find("week")].strip()
            duration_total += (int(str(index_week)) * week)
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            index_cycle = returnduration[returnduration.find("cycle") - 2: returnduration.find("cycle")].strip()
            duration_total += (int(str(index_cycle)) * cycle)
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:

            index_day = returnduration[returnduration.find("day") - 3:returnduration.find("day")].strip()
            duration_total += int(str(index_day))
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        if duration_total == 0:
            return ""
        else:
            return str(duration_total)

    def remove_headers(self, value):
        try:
            if self.isNan("MFRControlNo") == 1:
                MFRControlNo = self.row['MFRControlNo'].replace("O", "0");
            if self.isNan("NameAndAddresManufacturer") == 1:
                NameAndAddresManufacturer = self.row['NameAndAddresManufacturer'].split()
            substring = value[value.find(NameAndAddresManufacturer[0]): value.find(MFRControlNo) + len(MFRControlNo)]
            return value.replace(substring, "")
        except Exception as e:
            return value

    def error_log(self, message):
        logging.basicConfig(filename=con.logs_path + con.current_date + '.txt',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%d-%m-%Y %H:%M:%S',
                            level=logging.DEBUG, force=True)
        logging.error(message)

        self.logger = logging.getLogger('urbanGUI')

    def get_medra_with_string(self, string):
        returnstring = ""
        try:
            if string.find(")") > -1:
                returnstring = string[:string.find("(")]
            else:
                returnstring = string
        except Exception as e:
            returnstring = string

        try:
            if returnstring.find(")") > -1:
                returnstring = returnstring[returnstring.find(")") + 1:]
            else:
                returnstring = returnstring
        except Exception as e:
            returnstring = returnstring

        try:
            if returnstring.find("#1") > -1:
                returnstring = returnstring[returnstring.find("#1") + 2:]
            else:
                returnstring = returnstring
        except Exception as e:
            returnstring = returnstring

        try:
            if returnstring.find("#2") > -1:
                returnstring = returnstring[returnstring.find("#2") + 2:]
            else:
                returnstring = returnstring
        except Exception as e:
            returnstring = returnstring

        df = pd.read_csv(con.medra_path)
        # dropping null value columns to avoid errors
        df.dropna(inplace=True)
        code = df.loc[df['medra_name'].str.lower() == returnstring.strip().lower()]
        return code

    def get_medra_with_keyword(self, keyword):
        df = pd.read_csv(con.medra_path)
        # dropping null value columns to avoid errors
        df.dropna(inplace=True)
        df["Indexes"] = df["medra_name"].str.find(keyword)
        code = df.loc[df['Indexes'] > -1]
        return code

    def get_medra_name_list(self):
        df = pd.read_csv(con.medra_path)
        # dropping null value columns to avoid errors
        df.dropna(inplace=True)
        return list(df["medra_name"])

    def remove_junk_medical_history_irms(self, data):
        remove_arr = [' 8.', ' 9.']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_seriousness_criteria_irms(self, data):
        remove_arr = ['6.']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_patient_initials_irms(self, data):
        remove_arr = ['a. dob', 'a.dob']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_patient_weight_irms(self, data):
        remove_arr = ['2. date', '2.date']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_patient_height_irms(self, data):
        remove_arr = ['c.', 'c. weight', 'c.weight']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_suspect_drug_irms(self, data):
        remove_arr = ['a. indication', 'a.indication']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_suspect_indication_irms(self, data):
        remove_arr = [' b.']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_suspect_start_date_irms(self, data):
        remove_arr = [' c.']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_suspect_end_date_irms(self, data):
        remove_arr = ['4. death', '4.death']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def ambiguity_data_fix(self, data):
        remove_arr = ['or', '(']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_special_characters(self, key):
        characters = {'"': ["&quot;", "&#x22;"],
                      "&": ["&amp;", "&#x26;"],
                      "'": ["&#x27;"]
                      }
        for k, v in characters.items():
            for value in v:
                if value in key:
                    key = key.replace(value, k)
        return key

    def remove_junk_reaction_primary_irms(self, data):
        remove_arr = [' b.']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_reaction_start_date_irms(self, data):
        remove_arr = [' c.', '(']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_reaction_stop_date_irms(self, data):
        remove_arr = [' d.', '(']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def ambiguity_outcome_fix(self, data):
        remove_arr = [' e.', '(']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_concomitant_drug_irms(self, data):
        remove_arr = [' b.']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_concomitant_indication_irms(self, data):
        remove_arr = [' c.']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_concomitant_daily_dosage_irms(self, data):
        remove_arr = [' d.']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_concomitant_start_date_irms(self, data):
        remove_arr = [' e.']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def remove_junk_concomitant_end_date_irms(self, data):
        remove_arr = ['10. pregnancy', '10.pregnancy']
        st_index = -1
        for start_index in remove_arr:
            if data.lower().find(start_index) > -1:
                st_index = data.lower().find(start_index)
                break
        if st_index > -1:
            data = data[:st_index]
        return data.strip()

    def get_relation(self, relation_name):

        relations = []
        if 'relations' in self.row:
            for rel in self.row['relations']['relations']:
                if rel["predicted_relation"] == relation_name:
                    relations.append(rel)
        return relations

    def remove_words(self, text, words_to_remove):
        # Create a regular expression pattern that matches the words to remove
        pattern = r'\b(?:' + '|'.join(re.escape(word) for word in words_to_remove) + r')\b'
        
        # Use re.sub to replace the matched words with an empty string
        result = re.sub(pattern, '', text)
        
        return result
    

    def weight_logic(self, data):       
        # Split the string using 'or' as the delimiter
        parts = data.split('or')
        integer_part = 0
        # Process the first part to separate the integer and string
        if len(parts) > 0:
            first_part = parts[0].strip()
            split_first_part = first_part.split(None, 1)

            if len(split_first_part) == 2:
                integer_part, string_part = split_first_part
                integer_part = int(integer_part)
                string_part = string_part.strip()
                
                print("String part:", string_part)
                integer_part = integer_part * 0.45359237
                print("Integer part:", integer_part)
            else:
                print("Invalid format for the first part.")
        else:
            print("Invalid format for the input string.")

        return round(integer_part)
    

    def remove_junk_medwatch_suspect_name(self, drugName):
        print(drugName)
        # Define a pattern to match numbers and square brackets
        pattern = r'\d+|\[|\]'

        # Use re.sub() to replace the matched pattern with an empty string
        cleaned_str = re.sub(pattern, '', drugName)

        cleaned_str = cleaned_str.replace("\n", "")

        result_list = cleaned_str.split("continued")

        # # Remove strings with only whitespace from the list
        # result_list = [item.strip() for item in result_list if item.strip()]

        # Define a list of invalid data to be removed
        invalid_data = [' | ', '']

        # Use list comprehension to filter out invalid data
        result_list = [item.strip() for item in result_list if item not in invalid_data]

        return result_list
    

    def get_meaningful_words(self, input_str):
        spell = SpellChecker()

        # Tokenize the input string into words
        words = input_str.split()
        # print(words)

        # Correct spelling for each word
        # corrected_words = [spell.correction(word) for word in words]
        corrected_words = [spell.correction(word) or word for word in words]
        # print("corrected word")
        # print(corrected_words)
        return ' '.join(corrected_words)

    
    def remove_junk_medwatch_dose_used(self, input_str):
        # Remove any single numeric digit following a #
        cleaned_str = re.sub(r'#\d+', '', input_str)        
        # cleaned_str = re.sub(r'\b\w\b|\W|\d\b', '', cleaned_str)
        str_example = cleaned_str.strip()
        # print(cleaned_str)
        
        # Replace ' ne ' with ' One ' (case-insensitive)
        # result_str = str_example.lower().replace('ne', 'One')
        # result_str = str_example.replace('ne', 'One')
        # Replace only standalone word 'ne' with 'One'
        result_str = re.sub(r'\bne\b', 'One', str_example)
        # Remove the character '#'
        result_str = result_str.replace('#', '')

        # Remove single characters
        result = re.sub(r'\b\w\b|[^\w\s]|\d\b', '', result_str)
        meaningful_str = self.get_meaningful_words(result)
        # print("meaningful_str",meaningful_str)
        # Split the string using '[continued]'
        result_list = meaningful_str.split('continued')

        # Remove strings with only whitespace from the list
        result_list = [item for item in result_list if item.strip()]
        
        return result_list
    

    def extract_alphanumeric_words(self, input_string):
        pattern = r'\b\w*\d\w*\b'
        matches = re.findall(pattern, input_string)
        return matches
    
    def extract_time_related_word(self, input_string):
        pattern = r'\b(?:day(?:s)?|week(?:s)?|month(?:s)?|year(?:s)?)\b'
        matches = re.findall(pattern, input_string, flags=re.IGNORECASE)
        if matches:
            return matches[0]
        else:
            return None
        

    def extract_indication_data(self, input_string):
        # Extract words containing only the word "data" and words with more than two characters
        pattern = r'\bdata\b|\b\w{5,}\b'
        matches = re.findall(pattern, input_string)
        # Remove digits from each word in the list
        arr_without_digits = [''.join(char for char in word if not char.isdigit()) for word in matches]

        return arr_without_digits
    

    def extract_frequesncy_route_used(self, input_string, index):
        data = ""
        # Split the string using commas
        split_result = input_string.split(',')
        str_length = len(split_result)

        # if str_length > 0:
        #     data = split_result[index]

        # If there is only one element in the list and it is the original string, return the original string
        if len(split_result) == 1 and split_result[0] == input_string:           
            data = input_string
        else:
            data = split_result[index]     


        return data
    

    def custom_split_medwatch_describe_reaction(self, input_string):

        delimiters = ["spontaneous report"]
        # Create a regular expression pattern with the specified delimiters
        pattern = '|'.join(re.escape(d) for d in delimiters)

        # Use re.split to split the string based on the pattern
        split_list = re.split(pattern, input_string, flags=re.IGNORECASE)
        print(split_list)
        # Take the first part
        result_string = split_list[0].strip()

        # Split the string using commas and line breaks
        split_result = re.split(',', result_string)

        # Remove empty strings from the result
        split_list = [item.strip() for item in split_result if item.strip()]

        return split_list
    

    def patient_sex_logic(self, female, male):
        print("inside patient sex logic")
        result = ""
        if female == "1":
            result = "2"
        elif male == "1":
            result = "1"
        
        return result
    
    def linelist_scripting(self, data):
        delimeter = ''
        result = [data]
        delimeters_line_list = [";", "\n"]
        for val in delimeters_line_list:
            if val in data:
                delimeter = val
                break
        if delimeter != '':
            result = data.split(delimeter)

        return result

    def remove_junk_linelist(self, data):
        patern = r"[0-9][0-9]\.\s|[0-9]\.\s|[a-zA-Z]\.\s"
        data = re.sub(patern, '', data)
        return data.strip()