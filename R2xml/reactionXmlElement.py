# reaction element create
from bs4 import BeautifulSoup
import re
from .dataFormatCalculation import dateFormatCalculation
from .helper import helper
from inspect import currentframe, getframeinfo
from .reactionE2b import reactionE2b
import pandas as pd

current_filename = str(getframeinfo(currentframe()).filename)
reaction_regex = r"[0-9][0-9]\.\s|[0-9]\.\s|[A-Z]\.\s"
reaction_delimeter = "$"


class reactionXmlElement:

    def __init__(self, con, row, code_template):
        self.text = open(con.xml_template_reaction, "r", encoding="utf8").read()
        self.row = row
        self.code_template = code_template
        self.helper = helper(row)
        self.reaction_code_group_default = con.reaction_code_group_default
        self.reaction_code_group_1 = con.reaction_code_group_1
        self.reactionE2b = reactionE2b

    # making string constant
    def remove_junk_reactions(self, reactions):
        reactions = reactions.replace("Sn.Nm", "Seq. No.")
        reactions = reactions.replace("Seq.No.", "Seq. No.")
        reactions = reactions.replace("StartDate", "Start Date")
        reactions = reactions.replace("StanDate", "Start Date")
        reactions = reactions.replace("StopDate", "Stop Date")
        reactions = reactions.replace("Ramﬁon", "Reaction")
        reactions = reactions.replace("Resetion", "Reaction")
        reactions = reactions.replace("StanDaIe", "Start Date")
        reactions = reactions.replace("Stan Date", "Start Date")
        reactions = reactions.replace("SmnDaw", "Start Date")
        reactions = reactions.replace("StopDaIe", "Stop Date")
        reactions = reactions.replace("SmpDaw", "Stop Date")
        reactions = reactions.replace("SmpDaw", "Stop Date")
        reactions = reactions.replace("Dumﬁon", "Duration")
        return reactions

    # adverse events calculation based vendor groups
    def get_reaction_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        if self.row['template'] == "IRMS":
            return self.get_irms_reaction_tag()
        elif self.row['template'] == "linelist":
            return self.get_linelist_reaction_tag()
        elif self.row['template'] == "litrature":
            return self.get_litrature_reaction_tag()
        elif self.row['template'] == "MedWatch":
            return self.get_medwatch_reaction_tag()
        # Default group mapping
        if self.code_template in self.reaction_code_group_default:

            if self.helper.isNan('Reaction Information ( Cont...)') == 1:

                # print(self.row['Reaction Information ( Cont...)'])
                # reactions = self.remove_junk_reactions(self.row['Reaction Information ( Cont...)']).split("Seq. No.")
                # print(reactions,len(reactions))
                # for x in reactions:
                # try:
                '''if x.strip() != "":
                    # if not x.find("Reaction"):
                    pattern = r'^(.*?:.*?):'
                    output_string = re.sub(pattern, r'\1Reaction :', x)
                    print(output_string,'--6666')

                    match = re.search(r'Reaction\s*:\s*(.*?)\s*(?:\w+\s*:|$)', output_string)

                    if match:
                        reaction_value = match.group(1).strip()
                    # primary_reaction = x[x.find("Reaction"):x.find("Start Date")]
                    primary_reaction=reaction_value
                    print('111111111111111111')
                    pattern = r'\d{8}'
                    medracode_llt_apt=[]
                    # Search for the pattern in the text
                    if re.search(pattern, reaction_value):
                        matches = re.findall(pattern, reaction_value)
                        if len(matches)>1:
                             medracode_llt_apt=matches
                    elif re.search(r'\((.*?)\)', primary_reaction):
                        match=re.search(r'\((.*?)\)', primary_reaction)
                        extracted_text = match.group(1)
                        extracted_text_1 = match.group(1).strip()
                        if self.get_medra_code(str(extracted_text)) != 0:
                                medracode=self.get_medra_code(str(extracted_text))
                        elif self.get_medra_code(str(extracted_text_1)) != 0:
                            medracode=self.get_medra_code(str(extracted_text))
                        print(medracode,'333')
                    elif re.search(r'\(\d+\)', primary_reaction):
                        match=re.search(r'\(\d+\)', primary_reaction) 
                        # Extract the numeric part
                        numeric_part = match.group(0)[1:-1]  # Remove the parentheses
                        if numeric_part.isdigit():
                            print("Found and extracted:", numeric_part)
                            medracode=numeric_part
                            print(medracode,'222')
                    # match = re.search(r'\((.*?)\)', primary_reaction)
                    # if match:
                    #     extracted_text = match.group(1)
                    #     extracted_text_1 = match.group(1).strip()
                    #     print(extracted_text)
                    #     if self.get_medra_code(str(extracted_text)) != 0:
                    #             medracode=self.get_medra_code(str(extracted_text))
                    #     elif self.get_medra_code(str(extracted_text_1)) != 0:
                    #         medracode=self.get_medra_code(str(extracted_text))
                    #     print(medracode,'333')

                    primary_reaction = primary_reaction[
                                       primary_reaction.find(":") + 1:primary_reaction.find("(")].strip()
                    start_date = x[x.find("Start Date"):x.find("Stop Date")]
                    print('111133333333333311111111111111',start_date)
                    start_date = dateFormatCalculation().get_data(start_date[start_date.find(":") + 1:].strip(),
                                                                  1)
                    stop_date = x[x.find("Stop Date"):x.find("Duration")]
                    print('111111444444444444444111111111111',stop_date)
                    stop_date = dateFormatCalculation().get_data(stop_date[stop_date.find(":") + 1:].strip(), 1)
                    Duration = x[x.find("Duration"):]
                    Duration = self.helper.duration_filter(Duration[Duration.find(":") + 1:].strip())
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    soup.find('primarysourcereaction').string = str(primary_reaction)
                    if len(medracode_llt_apt) >1:
                        soup.find('reactionmeddrallt').string = str(medracode_llt_apt[0])
                        soup.find('reactionmeddrapt').string = str(medracode_llt_apt[1])
                    elif len(medracode_llt_apt) ==1:
                        soup.find('reactionmeddrallt').string = str(medracode_llt_apt[0])
                        soup.find('reactionmeddrapt').string = str(medracode_llt_apt[0])
                    else:
                        soup.find('reactionmeddrallt').string = str(medracode)
                        soup.find('reactionmeddrapt').string = str(medracode)
                    soup.find('reactionstartdateformat').string = str("102")
                    soup.find('reactionstartdate').string = str(start_date)
                    soup.find('reactionenddateformat').string = str("102")
                    soup.find('reactionenddate').string = str(stop_date)
                    soup.find('reactionduration').string = str(Duration)
                    soup.find('reactiondurationunit').string = str("804")
                    final_tag.append(soup)

                else:
                    # exit(3)
                    continue
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    # print( soup.find('primarysourcereaction'))
                    soup.find('primarysourcereaction').string = "Not Reported"
                    final_tag.append(soup)'''
                try:
                    data = self.row['png-data']

                    data = data[data.find('Reaction Information ( Cont...)'):data.find(
                        "Describe Reaction(s)(Include relevant test/lab data) ( Cont...)")]

                    data = data.split('Seq. No.')[1:]
                    for x in data:
                        primary_reaction = x[x.find("Reaction"):x.find("Start Date")]
                        if ':' in primary_reaction:
                            primary_reaction = primary_reaction.split(':')[1]
                        print(primary_reaction, '-----')
                        # Search for the pattern in the text
                        medracode_llt_apt = []
                        if re.findall(r'\d{8}', primary_reaction):
                            print('&&&&&&&&&&')
                            matches = re.findall(r'\d{8}', primary_reaction)
                            for i in matches:
                                medracode_llt_apt.append(i)
                            print(medracode_llt_apt, '111')
                        elif re.findall(r'\((.*?)\)', primary_reaction):
                            print('&&&&&3333333333&&&&&')
                            # match=re.search(r'\((.*?)\)', primary_reaction)
                            matches = re.findall(r'\((.*?)\)', primary_reaction)
                            print(matches)
                            match = matches[0].split(',')
                            if len(match) > 1:
                                print(match)
                                extracted_text = match[0]
                                extracted_text_1 = match[1]
                                print(extracted_text)
                                print(extracted_text_1)
                                if self.get_medra_code(str(extracted_text)) != 0:
                                    medracode_llt_apt.append(self.get_medra_code(str(extracted_text)))
                                elif self.get_medra_code(str(extracted_text_1)) != 0:
                                    medracode_llt_apt.append(self.get_medra_code(str(extracted_text_1)))
                            else:
                                if self.get_medra_code(str(matches[0])) != 0:
                                    medracode = self.get_medra_code(str(matches[0]))
                            print(medracode_llt_apt, '333')
                        elif re.search(r'\(\d+\)', primary_reaction):
                            match = re.search(r'\(\d+\)', primary_reaction)
                            numeric_part = match.group(0)[1:-1]  # Remove the parentheses
                            if numeric_part.isdigit():
                                print("Found and extracted:", numeric_part)
                                medracode = numeric_part
                                print(medracode, '222')
                        else:
                            exit(3)
                        try:
                            start_date = x[x.find("Start Date"):x.find("Stop Date")]
                            start_date = dateFormatCalculation().get_data(start_date.split(':')[1], 1)
                            print(start_date, '---start_date---')
                        except Exception as e:
                            start_date = 'UNK'

                        try:
                            stop_date = x[x.find("Stop Date"):x.find("Duration")]
                            stop_date = dateFormatCalculation().get_data(stop_date.split(':')[1], 1)
                        except Exception as e:
                            stop_date = 'UNK'

                        try:
                            Duration = x[x.find("Duration"):]
                            Duration = self.helper.duration_filter(Duration.split(':')[1])
                        except Exception as e:
                            Duration = 'UNK'
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        soup = BeautifulSoup(self.text, 'lxml-xml')
                        soup.find('primarysourcereaction').string = str(primary_reaction)
                        if len(medracode_llt_apt) > 1:
                            soup.find('reactionmeddrallt').string = str(medracode_llt_apt[0])
                            soup.find('reactionmeddrapt').string = str(medracode_llt_apt[1])
                        elif len(medracode_llt_apt) == 1:
                            soup.find('reactionmeddrallt').string = str(medracode_llt_apt[0])
                            soup.find('reactionmeddrapt').string = str(medracode_llt_apt[0])
                        else:
                            soup.find('reactionmeddrallt').string = str(medracode)
                            soup.find('reactionmeddrapt').string = str(medracode)
                        soup.find('reactionstartdateformat').string = str("102")
                        soup.find('reactionstartdate').string = str(start_date)
                        soup.find('reactionenddateformat').string = str("102")
                        soup.find('reactionenddate').string = str(stop_date)
                        soup.find('reactionduration').string = str(Duration)
                        soup.find('reactiondurationunit').string = str("804")
                        final_tag.append(soup)
                except Exception as e:
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    # print( soup.find('primarysourcereaction'))
                    soup.find('primarysourcereaction').string = "Not Reported"
                    final_tag.append(soup)
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    # else:
        #     soup = BeautifulSoup(self.text, 'lxml-xml')
        #     # print( soup.find('primarysourcereaction'))
        #     soup.find('primarysourcereaction').string = "Not Reported"
        #     final_tag.append(soup)
        # group 1 mapping drug_code_group_1
        elif self.helper.isNan('ReactionInformation') == 1:
            start_date = str(dateFormatCalculation().get_data(
                str(self.row['Day_ReactionOnset']) + "-" + str(self.row['Month_ReactionOnset']) + "-" + str(
                    self.row['Year_ReactionOnset']), 1))
            if self.row['ReactionInformation'].find(")") > 0:
                try:
                    ReactionInformation = self.row['ReactionInformation'].split(")")

                    for index, x in enumerate(ReactionInformation):
                        primary_reaction = ""
                        if x.find("-") > 0 and x.find("[") > 0:
                            primary_reaction = self.replaceOutcome(x[x.find("-") + 1:x.find("[")])

                        elif x.find("[") > 0:
                            primary_reaction = self.replaceOutcome(x[:x.find("[")])
                            # print(x, primary_reaction)

                        if x.find("(") > 0:
                            medracode = re.findall(r'\d+', x[x.find("("): x.find("v")])[0]

                        if primary_reaction != "":
                            soup = BeautifulSoup(self.text, 'lxml-xml')
                            soup.find('primarysourcereaction').string = str(primary_reaction)
                            soup.find('reactionmeddrallt').string = str(medracode)
                            soup.find('reactionmeddrapt').string = str(medracode)
                        if index == 0:
                            soup.find('reactionstartdateformat').string = str("102")
                            soup.find('reactionstartdate').string = str(start_date)
                        final_tag.append(soup)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            elif self.row['ReactionInformation'].find("]") > 0:
                ReactionInformation = self.row['ReactionInformation'].split("]")
                try:
                    for index, x in enumerate(ReactionInformation):
                        if x.find("[") > 0:
                            primary_reaction = self.replaceOutcome(x[:x.find("[")])

                            soup = BeautifulSoup(self.text, 'lxml-xml')
                            soup.find('primarysourcereaction').string = str(primary_reaction)
                            if index == 0:
                                soup.find('reactionstartdateformat').string = str("102")
                                soup.find('reactionstartdate').string = str(start_date)
                            final_tag.append(soup)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        descripion_data = self.row['DescribeReaction']

        png_data = self.row['png-data']

        try:
            if 'Case Description' in descripion_data:
                prm_reaction = []
                if descripion_data.find('Case Description'):
                    descripion_data = descripion_data.split('Case Description')
                    if descripion_data[0].find('(Related symptoms if any separated by commas'):
                        if 'Event Verbatim [LOWER LEVEL TERM] (Related symptoms if any separated by commas' in \
                                descripion_data[0]:
                            descripion_data[0] = descripion_data[0].replace(
                                'Event Verbatim [LOWER LEVEL TERM] (Related symptoms if any separated by commas)', '')
                        # data=data[0].split('(Related symptoms if any separated by commas)')
                        # print(descripion_data[0])
                        # exit(0)
                        extracted_terms = re.findall(r'\[(.*?)\]', descripion_data[0].replace('\n', ' '))

                        # Print the extracted terms
                        for term in extracted_terms:
                            prm_reaction.append(term)
                    print(prm_reaction, '------------')
                    for reaction in prm_reaction:
                        if self.get_medra_code(str(reaction)) != 0:
                            medracode = self.get_medra_code(str(reaction))
                            soup = BeautifulSoup(self.text, 'lxml-xml')
                            soup.find('primarysourcereaction').string = str(reaction)
                            soup.find('reactionmeddrallt').string = str(medracode)
                            # soup.find('reactionstartdateformat').string = str("102")
                            # soup.find('reactionstartdate').string = str(start_date)
                            # soup.find('reactionenddateformat').string = str("102")
                            # soup.find('reactionenddate').string = str(stop_date)
                            # soup.find('reactionduration').string = str(Duration)
                            # soup.find('reactiondurationunit').string = str("804")
                            final_tag.append(soup)
                    return final_tag
            elif re.findall(r"(.+?)\s*\[v\.\d+\.\d+\]", descripion_data):
                matches = re.findall(r"(.+?)\s*\[v\.\d+\.\d+\]", descripion_data)
                for i in matches:
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    reaction = i[:i.find('(')]
                    print(i)
                    print(reaction)
                    soup.find('primarysourcereaction').string = str(reaction)
                    if re.findall(r'\d{8}', i):
                        # reaction=i[:i.find('(')]
                        # print(i)
                        # print(reaction)
                        # soup.find('primarysourcereaction').string = str(reaction)
                        print('000000')
                        m = re.findall(r'\d{8}', i)
                        print('88888888')
                        # print(i)
                        print(m)
                        if len(m) > 1:
                            medracode_llt = m[0]
                            soup.find('reactionmeddrallt').string = str(medracode_llt)
                            print(medracode_llt)
                            medra_apt = m[1]
                            soup.find('reactionmeddrapt').string = str(medra_apt)
                            print(medra_apt)
                        else:
                            medracode = m[0]
                            soup.find('reactionmeddrallt').string = str(medracode)
                            soup.find('reactionmeddrapt').string = str(medracode)
                    elif re.findall(r'\((.*?)\)', i):
                        m = re.findall(r'\((.*?)\)', i)
                        if len(m) > 1:
                            medra_llt = m[0]
                            if self.get_medra_code(str(medra_llt)) != 0:
                                medracode = self.get_medra_code(str(medra_llt))
                                soup.find('reactionmeddrallt').string = str(medracode)
                            medra_apt = m[1]
                            if self.get_medra_code(str(medra_apt)) != 0:
                                medracode = self.get_medra_code(str(medra_apt))
                                soup.find('reactionmeddrapt').string = str(medracode)
                        else:
                            medracode = m[0]
                            if self.get_medra_code(str(medracode)) != 0:
                                medracode = self.get_medra_code(str(medracode))
                                soup.find('reactionmeddrapt').string = str(medracode)
                                soup.find('reactionmeddrallt').string = str(medracode)
                    elif 'Case level outcome' in descripion_data:
                        a = a[:a.find('Case level outcome')]
                        a = a.split('\n')
                        l = []
                        medra = []
                        for i in a:
                            soup = BeautifulSoup(self.text, 'lxml-xml')
                            if '(' in i and re.findall(r'\d{8}|\((.*?)\)', i):
                                m = re.findall(r'\d{8}', i)
                                reaction = i[:i.find('(')]
                                soup.find('primarysourcereaction').string = str(reaction)
                                print(m, '----')
                                l.append(i[:i.find('(')])
                            if '(' in i and re.findall(r'\((.*?)\)', i):
                                medra.append(re.findall(r'\((.*?)\)', i))

                    final_tag.append(soup)
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        else:
            soup = BeautifulSoup(self.text, 'lxml-xml')
            soup.find('primarysourcereaction').string = "Not Reported"
            final_tag.append(soup)
        return final_tag

    # removal of outcome
    def replaceOutcome(self, value):
        outcomes = ["unknown", "fatal", "recovered/resolved with sequelae", "not recovered/not resolved",
                    "recovering/resolving", "recovered/resolved"]
        outcomes_value = value
        value_low = value.lower()
        for i in outcomes:
            if value_low.find(i) > -1:
                outcomes_value = value_low.replace(value_low[:value_low.find(i) + len(i)], "")
                break
        return outcomes_value.strip()

    def get_medra_code(self, name):
        medra_code_list_final = 0
        try:
            result = self.helper.get_medra_with_string(name.strip())
            medra_code = list(result['medra_code'])
            if len(medra_code) > 0:
                medra_code_list_final = int(medra_code[0])
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return medra_code_list_final

    def get_irms_reaction_tag(self):
        try:
            keys = self.row.keys()
            final_tag = BeautifulSoup("", 'lxml-xml')
            primary_reaction = [st for st in (re.sub(reaction_regex, reaction_delimeter,
                                                     self.helper.remove_junk_reaction_primary_irms(
                                                         self.row['EVENT TERM:']))).split(reaction_delimeter) if
                                len(st) > 1]

            start_date = [st for st in
                          (re.sub(reaction_regex, reaction_delimeter, self.row['START DATE OF EVENT:'])).split(
                              reaction_delimeter) if
                          len(st) > 1]

            stop_date = [st for st in
                         (re.sub(reaction_regex, reaction_delimeter, self.row['STOP DATE OF EVENT:'])).split(
                             reaction_delimeter) if
                         len(st) > 1]

            outcome = 'OUTCOME (NOT RECOVERED/UNKNOWN/RECOVERING/RECOVERED):' if 'OUTCOME (NOT RECOVERED/UNKNOWN/RECOVERING/RECOVERED):' in keys else 'OUTCOME(NOTRECOVERED/UNKNOWN/RECOVERING/RECOVERED):'

            outcome = [st for st in (
                re.sub(reaction_regex, reaction_delimeter, self.helper.ambiguity_outcome_fix(self.row[outcome]))).split(
                reaction_delimeter)
                       if len(st) > 1]

            for i, x in enumerate(primary_reaction):
                soup = BeautifulSoup(self.text, 'lxml-xml')
                try:
                    if str(x) != "":
                        soup.find('primarysourcereaction').string = str(x)
                    else:
                        soup.find('primarysourcereaction').string = str("Not Reported")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if self.get_medra_code(str(x)) != 0:
                        soup.find('reactionmeddrallt').string = str(self.get_medra_code(str(x)))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    soup.find('reactionstartdateformat').string = str("102")
                    soup.find('reactionstartdate').string = str(dateFormatCalculation().get_date(
                        self.helper.remove_junk_reaction_start_date_irms(
                            self.helper.ambiguity_data_fix(start_date[i]))))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    soup.find('reactionenddateformat').string = str("102")
                    soup.find('reactionenddate').string = str(dateFormatCalculation().get_date(
                        self.helper.remove_junk_reaction_stop_date_irms(self.helper.ambiguity_data_fix(stop_date[i]))))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if self.reactionE2b(outcome[i].strip()).get_reaction_outcome_e2b() != 0:
                        soup.find('reactionoutcome').string = str(
                            self.reactionE2b(outcome[i].strip()).get_reaction_outcome_e2b())
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                final_tag.append(soup)
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return final_tag

    def get_linelist_reaction_tag(self):
        try:
            final_tag = BeautifulSoup("", 'lxml-xml')
            loop_len = []
            primary_source_reaction = []
            reaction_pt = []
            onset_reaction = []
            reaction_end_date = []
            outcome_reaction = []
            reaction_seriousness = []

            try:
                primary_source_reaction = self.helper.linelist_scripting(self.row['primary_source_reaction'])
                loop_len.append(len(primary_source_reaction))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                reaction_pt = self.helper.linelist_scripting(self.row['reaction_pt'])
                loop_len.append(len(reaction_pt))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            try:
                onset_reaction = self.helper.linelist_scripting(self.row['onset_reaction'])
                loop_len.append(len(onset_reaction))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            try:
                reaction_end_date = self.helper.linelist_scripting(self.row['reaction_end_date'])
                loop_len.append(len(reaction_end_date))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            try:
                outcome_reaction = self.helper.linelist_scripting(self.row['outcome_reaction'])
                loop_len.append(len(outcome_reaction))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                reaction_seriousness = self.helper.linelist_scripting(self.row['reaction_seriousness'])
                loop_len.append(len(reaction_seriousness))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            for i in range(0, max(loop_len)):

                soup = BeautifulSoup(self.text, 'lxml-xml')
                try:
                    if i < len(primary_source_reaction):

                        primary_reaction = self.helper.remove_junk_linelist(primary_source_reaction[i])

                        if str(primary_reaction) != "":
                            soup.find('primarysourcereaction').string = str(primary_reaction)
                        else:
                            soup.find('primarysourcereaction').string = str("Not Reported")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(primary_source_reaction):
                        primary_reaction = self.helper.remove_junk_linelist(primary_source_reaction[i])
                        if self.get_medra_code(str(primary_reaction)) != 0:
                            soup.find('reactionmeddrallt').string = str(self.get_medra_code(str(primary_reaction)))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(reaction_pt):
                        primary_reaction_pt = self.helper.remove_junk_linelist(reaction_pt[i])
                        if self.get_medra_code(str(primary_reaction_pt)) != 0:
                            soup.find('reactionmeddrapt').string = str(self.get_medra_code(str(primary_reaction_pt)))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(onset_reaction):
                        start_date = self.helper.remove_junk_linelist(onset_reaction[i])
                        soup.find('reactionstartdate').string = str(dateFormatCalculation().get_date(start_date))
                        soup.find('reactionstartdateformat').string = str("102")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(reaction_end_date):
                        print(reaction_end_date[i])
                        end_date = self.helper.remove_junk_linelist(reaction_end_date[i])
                        soup.find('reactionenddate').string = str(dateFormatCalculation().get_date(end_date))
                        soup.find('reactionenddateformat').string = str("102")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(outcome_reaction):
                        outcome = self.helper.remove_junk_linelist(outcome_reaction[i])
                        if self.reactionE2b(outcome.strip()).get_reaction_outcome_e2b() != 0:
                            soup.find('reactionoutcome').string = str(
                                self.reactionE2b(outcome.strip()).get_reaction_outcome_e2b())
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(reaction_seriousness):
                        reaction_seriousness_data = self.helper.remove_junk_linelist(reaction_seriousness[i])
                        serious = 2
                        if reaction_seriousness_data.lower() == "serious" or reaction_seriousness_data.lower() == 'yes' or reaction_seriousness_data.lower() == "y" or reaction_seriousness_data.lower() == "1":
                            serious = 1
                        soup.find('termhighlighted').string = str(serious)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                final_tag.append(soup)
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return final_tag

    def process_list_values(self, data):
        try:
            return ", ".join(str(v) for v in eval(str(data)))
        except Exception as e:
            return data

    def get_litrature_reaction_tag(self):
        reaction_soup = BeautifulSoup("", 'lxml-xml')
        SUSPECTREACTION = self.helper.get_relation('SUSPECTREACTION')
        if len(SUSPECTREACTION) > 0:
            return self.get_litrature_reaction_by_realtion_tag(SUSPECTREACTION)
        try:
            row = self.row
            print(row)
            if 'primarysourcereaction' in row:
                psrs = str(self.process_list_values(row['primarysourcereaction'])).split(",")
                print(psrs)
                if len(psrs) > 0:
                    for psr in psrs:

                        soup = BeautifulSoup(self.text, 'lxml-xml')
                        soup.find('primarysourcereaction').string = str(psr).strip()
                        psr_meddra = self.get_medra_code(psr)
                        if psr_meddra > 0:
                            soup.find('reactionmeddrallt').string = str(psr_meddra)

                        if 'reactionstartdate' in row:
                            soup.find('reactionstartdate').string = str(row['reactionstartdate'])
                            soup.find('reactionstartdateformat').string = str("102")

                        if 'reactionenddate' in row:
                            soup.find('reactionenddate').string = str(row['reactionenddate'])
                            soup.find('reactionenddateformat').string = str("102")

                        if 'reactionoutcome' in row:
                            soup.find('reactionoutcome').string = str(
                                self.process_list_values(row['reactionoutcome']))
                        reaction_soup.append(soup)

        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return reaction_soup

    def get_litrature_reaction_by_realtion_tag(self, SUSPECTREACTION):
        reaction_soup = BeautifulSoup("", 'lxml-xml')
        for val in SUSPECTREACTION:
            entities = val['entities']
            soup = BeautifulSoup(self.text, 'lxml-xml')
            try:
                soup.find('primarysourcereaction').string = str(entities[1]["PRIMARYSOURCEREACTION"]).strip()
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                psr_meddra = self.get_medra_code(str(entities[1]["PRIMARYSOURCEREACTION"]).strip())
                soup.find('reactionmeddrallt').string = str(psr_meddra)
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            reaction_soup.append(soup)
        return reaction_soup

    def get_medwatch_reaction_tag(self):
        try:
            keys = self.row.keys()
            final_tag = BeautifulSoup("", 'lxml-xml')

            DescribeReaction = str(self.row['DescribeReaction'])

            primary_reaction = self.helper.custom_split_medwatch_describe_reaction(DescribeReaction)

            # # Split the string based on "Spontaneous report"
            # split_result = DescribeReaction.split("Spontaneous report", 1)

            # # Take the first part
            # result_string = split_result[0].strip()

            # # Split the string using commas and line breaks
            # split_result = re.split(',', result_string)

            # # Remove empty strings and leading/trailing whitespaces
            # primary_reaction = [item.strip() for item in split_result if item.strip()]

            print(primary_reaction)

            # primary_reaction = [st for st in (re.sub(reaction_regex, reaction_delimeter,
            #                                          self.helper.remove_junk_reaction_primary_irms(
            #                                              self.row['EVENT TERM:']))).split(reaction_delimeter) if
            #                     len(st) > 1]

            # start_date = str(dateFormatCalculation().date_format_change(str(self.row['DateOfEvent'])))
            # start_date = [st for st in
            #               (re.sub(reaction_regex, reaction_delimeter, self.row['START DATE OF EVENT:'])).split(
            #                   reaction_delimeter) if
            #               len(st) > 1]

            stop_date = ""
            # stop_date = [st for st in
            #              (re.sub(reaction_regex, reaction_delimeter, self.row['STOP DATE OF EVENT:'])).split(
            #                  reaction_delimeter) if
            #              len(st) > 1]

            # outcome = 'OUTCOME (NOT RECOVERED/UNKNOWN/RECOVERING/RECOVERED):' if 'OUTCOME (NOT RECOVERED/UNKNOWN/RECOVERING/RECOVERED):' in keys else 'OUTCOME(NOTRECOVERED/UNKNOWN/RECOVERING/RECOVERED):'

            # outcome = [st for st in (
            #     re.sub(reaction_regex, reaction_delimeter, self.helper.ambiguity_outcome_fix(self.row[outcome]))).split(
            #     reaction_delimeter)
            #            if len(st) > 1]

            for i, x in enumerate(primary_reaction):
                soup = BeautifulSoup(self.text, 'lxml-xml')
                try:
                    if str(x) != "":
                        soup.find('primarysourcereaction').string = str(x)
                    else:
                        soup.find('primarysourcereaction').string = str("Not Reported")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if self.get_medra_code(str(x)) != 0:
                        soup.find('reactionmeddrallt').string = str(self.get_medra_code(str(x)))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    soup.find('reactionstartdateformat').string = str("102")
                    soup.find('reactionstartdate').string = str(
                        dateFormatCalculation().date_format_change(str(self.row['DateOfEvent'])))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    soup.find('reactionenddateformat').string = str("102")
                    # soup.find('reactionenddate').string = str(dateFormatCalculation().get_date(
                    #     self.helper.remove_junk_reaction_stop_date_irms(self.helper.ambiguity_data_fix(stop_date[i]))))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                # try:
                #     if self.reactionE2b(outcome[i].strip()).get_reaction_outcome_e2b() != 0:
                #         soup.find('reactionoutcome').string = str(
                #             self.reactionE2b(outcome[i].strip()).get_reaction_outcome_e2b())
                # except Exception as e:
                #     self.helper.error_log(
                #         current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                final_tag.append(soup)
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return final_tag
