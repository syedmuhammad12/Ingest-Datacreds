# drug element create
from bs4 import BeautifulSoup
import re

from .eventOccurE2b import eventOccurE2b
from .helper import helper
from .dataFormatCalculation import dateFormatCalculation
from .drugE2b import drugE2b
from inspect import currentframe, getframeinfo

current_filename = str(getframeinfo(currentframe()).filename)
drugassessmentmethod = "Global Introspection"
drug_regex = r"[0-9][0-9]\.\s|[0-9]\.\s|[A-Z]\.\s"
drug_delimeter = "$"


class drugXmlElement:
    def __init__(self, con, row, code_template):
        self.text = open(con.xml_template_drug, "r", encoding="utf8").read()
        self.text_drug_reaction_relatedness = open(con.xml_template_drug_reaction_relatedness, "r",
                                                   encoding="utf8").read()
        self.row = row
        self.code_template = code_template
        self.drug_code_group_default = con.drug_code_group_default
        self.helper = helper(row)
        self.drug_code_group_1 = con.drug_code_group_1

    # removing indexes from the string
    def item_indexing(self, para, key=0, interval=0):
        final_para = ""
        if interval == 0:
            if self.helper.isNan(key) == 1:
                junk_list = ["2)", "2 )", "#2"]
                final_para = para
                for x in junk_list:
                    if para.find(x) > -1:
                        final_para = para[:para.find(x)]
        else:
            junk_list = ["2)", "2 )", "#2"]
            final_para = para
            for x in junk_list:
                if para.find(x) > -1:
                    final_para = para[:para.find(x)]
        return final_para

    # removing indexes from the string for group1 second drug
    def item_indexing_second_drug_group1(self, para, key=0, interval=0):
        final_para = ""
        if interval == 0:
            if self.helper.isNan(key) == 1:
                junk_list = ["2)", "2 )", "#2"]
                final_para = para
                for x in junk_list:
                    if para.find(x) > -1:
                        final_para = para[para.find(x):]
        else:
            junk_list = ["2)", "2 )", "#2"]
            final_para = para
            for x in junk_list:
                if para.find(x) > -1:
                    final_para = para[para.find(x):]
        return final_para

    # removing indexes from the string with '#"."
    def splitting_string(self, string):
        split_strings = string.split("#")
        return split_strings[1:]

    # 8 digit medracode extraction
    def get_medra_code(self, para, key=0, interval=0, second_drug=0, irms=0):
        indication_list_final = 0
        try:
            if irms == 1:
                result = self.helper.get_medra_with_string(para)
                indication_list = list(result['medra_code'])
                if len(indication_list) > 0:
                    indication_list_final = int(indication_list[0])
            else:
                if second_drug == 0:
                    regex_str = self.item_indexing(para, key, interval)
                else:
                    regex_str = self.item_indexing_second_drug_group1(para, key, interval)
                indication_list = re.findall(r'\d+', regex_str)
                indication_list_final = [x for x in indication_list if len(x) == 8]

                if (len(indication_list_final)) == 0:
                    result = self.helper.get_medra_with_string(regex_str)
                    indication_list_final = list(result['medra_code'])
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return indication_list_final

    def get_drug_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        # default template calculation
        if self.row['template'] == 'IRMS':
            return self.get_irms_drug_tag()
        elif self.row['template'] == 'linelist':
            return self.get_linelist_drug_tag()
        elif self.row['template'] == 'litrature':
            return self.get_litrature_drug_tag()
        elif self.row['template'] == 'MedWatch':
            return self.get_medwatch_drug_tag()
        if self.code_template in self.drug_code_group_default:
            try:
                if "#" in self.row['SuspectDrug'] and self.row['SuspectDrug'].count("#") > 1:
                    SuspectDrug = self.splitting_string(self.row['SuspectDrug'])
                else:
                    SuspectDrug = self.item_indexing(self.row['SuspectDrug'], 'SuspectDrug')
                try:
                    if "#" in self.row['DailyDose'] and self.row['DailyDose'].count("#") > 1:
                        DailyDose = self.splitting_string(self.row['DailyDose'])
                    else:
                        DailyDose = self.item_indexing(self.row['DailyDose'], 'DailyDose')
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                if "#" in self.row['TherapyDatesFromTo'] and self.row['TherapyDatesFromTo'].count("#") > 1:
                    TherapyDatesFromTo = dateFormatCalculation().get_data(
                        self.splitting_string(self.row['TherapyDatesFromTo']))
                else:
                    TherapyDatesFromTo = dateFormatCalculation().get_data(
                        self.item_indexing(self.row['TherapyDatesFromTo'], "TherapyDatesFromTo"), 1).split('_')
                    date_pattern = r'\d{1,2}-[A-Za-z]{3}-\d{4}'
                    dates = re.findall(date_pattern, self.row['TherapyDatesFromTo'])
                    if dates != []:
                        if len(dates) > 1:
                            ls = []
                            for i in dates:
                                print(i)
                                a = str((dateFormatCalculation().get_data(i)[:8]))
                                ls.append(a)
                            TherapyDatesFromTo = ls
                        else:
                            TherapyDatesFromTo = dateFormatCalculation().get_data(
                                self.item_indexing(self.row['TherapyDatesFromTo'], "TherapyDatesFromTo"), 1).split('_')
                    else:
                        TherapyDatesFromTo = dateFormatCalculation().get_data(
                            self.item_indexing(self.row['TherapyDatesFromTo'], "TherapyDatesFromTo"), 1).split('_')
                if TherapyDatesFromTo == ['']:
                    TherapyDatesFromTo = ['Unk']

                try:
                    if self.row['DidReactionReappearAfterReintroduction'][0] == 1:
                        ReactionReappearAfterReintroduction = '1'
                    elif self.row['DidReactionReappearAfterReintroduction'][1] == 1:
                        ReactionReappearAfterReintroduction = '2'
                    else:
                        ReactionReappearAfterReintroduction = '3'
                except Exception as e:
                    ReactionReappearAfterReintroduction = '3'
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    drugE2b_data = drugE2b(
                        self.item_indexing(self.row['RouteOfAdministration'], 'RouteOfAdministration'))
                    RouteOfAdministration = drugE2b_data.get_route_of_admin_e2b()
                except Exception as e:
                    ReactionReappearAfterReintroduction = '3'
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    drug_indication = ''
                    IndicationForUse = self.row['IndicationForUse']
                    matches = re.findall(r'\((.*?)\)', IndicationForUse)
                    print('11111')
                    if matches:
                        for match in matches:
                            if self.get_medra_code(str(match), 'IndicationForUse', irms=1) != 0:
                                drug_indication = str(
                                    self.get_medra_code(str(match), 'IndicationForUse', irms=1))
                                print(drug_indication, '----drug_indication----')
                    elif re.findall(r'\d{8}', IndicationForUse):
                        print('55500055')
                        matches = re.findall(r'\d{8}', IndicationForUse)
                        drug_indication = matches
                        print(drug_indication)
                    elif re.sub(r'\d+\)\s+', ',', IndicationForUse):
                        print('100001111')
                        match = re.sub(r'\d+\)\s+', ',', IndicationForUse)
                        drug_indication = match.split(',')[1:]
                        if drug_indication == []:
                            drug_indication = str(
                                self.get_medra_code(str(IndicationForUse), 'IndicationForUse', irms=1))

                    elif re.search(r'([A-Z]+)\[', IndicationForUse):
                        print('2222')
                        extracted_term = re.search(r'([A-Z]+)\[', IndicationForUse).group(1)
                        print(extracted_term)
                        if self.get_medra_code(str(extracted_term), 'IndicationForUse', irms=1) != 0:
                            drug_indication = str(
                                self.get_medra_code(str(extracted_term), 'IndicationForUse', irms=1))

                    elif re.match(r'^\w+', IndicationForUse):
                        print('33333')
                        match = re.match(r'^\w+', IndicationForUse)
                        if match:
                            result = match.group(0)
                            if self.get_medra_code(str(result), 'IndicationForUse', irms=1) != 0:
                                drug_indication = str(
                                    self.get_medra_code(str(result), 'IndicationForUse', irms=1))
                            elif re.match(r'(.+?) \[v\.\d+\.\d+\]', IndicationForUse):
                                print('44333344')
                                match = re.match(r'(.+?) \[v\.\d+\.\d+\]', IndicationForUse)
                                if match:
                                    result = match.group(1)
                                    print(result)
                                    if self.get_medra_code(str(result), 'IndicationForUse', irms=1) != 0:
                                        drug_indication = str(
                                            self.get_medra_code(str(result), 'IndicationForUse', irms=1))
                                    print(drug_indication)

                    elif re.match(r'(.+?) \[v\.\d+\.\d+\]', IndicationForUse):
                        print('4444')
                        match = re.match(r'(.+?) \[v\.\d+\.\d+\]', IndicationForUse)
                        if match:
                            result = match.group(1)
                            print(result)
                            if self.get_medra_code(str(result), 'IndicationForUse', irms=1) != 0:
                                drug_indication = str(
                                    self.get_medra_code(str(result), 'IndicationForUse', irms=1))
                            print(drug_indication)
                            exit(0)
                    else:
                        print('5555')
                        # exit(1)
                        if self.get_medra_code(str(IndicationForUse), 'IndicationForUse', irms=1) != 0:
                            drug_indication = str(
                                self.get_medra_code(str(IndicationForUse), 'IndicationForUse', irms=1))
                        print(self.get_medra_code(str(IndicationForUse), 'IndicationForUse', irms=1))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                start_date = ""
                end_date = ""
                try:
                    if TherapyDatesFromTo[0]:
                        start_date = TherapyDatesFromTo[0]
                except IndexError as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    if TherapyDatesFromTo[1]:
                        end_date = TherapyDatesFromTo[1]
                except IndexError as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    if "#" in self.row['TherapyDuration'] and self.row['TherapyDuration'].count("#") > 1:
                        TherapyDuration = self.splitting_string(self.row['TherapyDuration'])
                    else:
                        TherapyDuration = self.helper.duration_filter(
                            self.item_indexing(self.row['TherapyDuration'], "TherapyDuration"))
                except IndexError as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                if "#" in self.row['SuspectDrug'] and self.row['SuspectDrug'].count("#") > 1:
                    for i, x in enumerate(SuspectDrug):
                        soup = BeautifulSoup(self.text, 'lxml-xml')

                        soup.find('drugcharacterization').string = str("1")
                        try:
                            soup.find('medicinalproduct').string = str(SuspectDrug[i])
                        except IndexError as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        soup.find('drugauthorizationholder').string = str("NA")
                        try:
                            soup.find('drugdosagetext').string = str(DailyDose[i])
                        except IndexError as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('drugadministrationroute').string = str(RouteOfAdministration)
                        except IndexError as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('drugindication').string = str(drug_indication)
                        except IndexError as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('drugstartdate').string = str(start_date)
                            soup.find('drugstartdateformat').string = str("102")
                        except IndexError as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('drugenddate').string = str(end_date)
                            soup.find('drugenddateformat').string = str("102")
                        except IndexError as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('drugtreatmentduration').string = str(TherapyDuration[i])
                            soup.find('drugtreatmentdurationunit').string = str("804")
                        except IndexError as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('drugrecurreadministration').string = str(ReactionReappearAfterReintroduction)
                        except IndexError as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('activesubstancename').string = str(SuspectDrug[i])
                        except IndexError as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        final_tag.append(soup)
                    result_con = self.get_concomitant_drug_tag()

                elif type(drug_indication) == type([]) and len(drug_indication) > 0:
                    print('222----drug_indication----')
                    for i in drug_indication:
                        soup = BeautifulSoup(self.text, 'lxml-xml')
                        soup.find('drugcharacterization').string = str("1")
                        soup.find('medicinalproduct').string = str(SuspectDrug)
                        soup.find('drugauthorizationholder').string = str("NA")
                        try:
                            soup.find('drugdosagetext').string = str(DailyDose)
                        except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                        try:
                            soup.find('drugadministrationroute').string = str(RouteOfAdministration)
                        except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            if self.get_medra_code(str(i), 'IndicationForUse', irms=1) != 0:
                                print('nooooo')
                                drug_indication = str(
                                    self.get_medra_code(str(i), 'IndicationForUse', irms=1))
                                soup.find('drugindication').string = str(drug_indication)
                            else:
                                if re.findall(r'\d{8}', i):
                                    print('yess')
                                    soup.find('drugindication').string = str(i)
                        except Exception as e:
                            print(str(e))
                        soup.find('drugstartdateformat').string = str("102")
                        soup.find('drugstartdate').string = str(start_date)
                        soup.find('drugenddateformat').string = str("102")
                        soup.find('drugenddate').string = str(end_date)
                        soup.find('drugtreatmentduration').string = str(TherapyDuration)
                        soup.find('drugtreatmentdurationunit').string = str("804")
                        soup.find('drugrecurreadministration').string = str(ReactionReappearAfterReintroduction)
                        soup.find('activesubstancename').string = str(SuspectDrug)
                        final_tag.append(soup)
                    result_con = self.get_concomitant_drug_tag()
                elif len(IndicationForUse) > 0:
                    print('3333----drug_indication----')
                    # result_con = self.get_concomitant_drug_continue_tag()
                    # for x in IndicationForUse:
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    soup.find('drugcharacterization').string = str("1")
                    soup.find('medicinalproduct').string = str(SuspectDrug)
                    soup.find('drugauthorizationholder').string = str("NA")
                    try:
                        soup.find('drugdosagetext').string = str(DailyDose)
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    try:
                        soup.find('drugadministrationroute').string = str(RouteOfAdministration)
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    soup.find('drugindication').string = str(drug_indication)
                    soup.find('drugstartdateformat').string = str("102")
                    soup.find('drugstartdate').string = str(start_date)
                    soup.find('drugenddateformat').string = str("102")
                    soup.find('drugenddate').string = str(end_date)
                    soup.find('drugtreatmentduration').string = str(TherapyDuration)
                    soup.find('drugtreatmentdurationunit').string = str("804")
                    soup.find('drugrecurreadministration').string = str(ReactionReappearAfterReintroduction)
                    soup.find('activesubstancename').string = str(SuspectDrug)
                    final_tag.append(soup)
                    final_tag.append(self.get_concomitant_drug_tag())

                else:
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    soup.find('drugcharacterization').string = str("1")
                    soup.find('medicinalproduct').string = str(SuspectDrug)
                    soup.find('drugauthorizationholder').string = str("NA")
                    soup.find('drugdosagetext').string = str(DailyDose)
                    soup.find('drugadministrationroute').string = str(RouteOfAdministration)
                    soup.find('drugindication').string = str(drug_indication)
                    soup.find('drugstartdateformat').string = str("102")
                    soup.find('drugstartdate').string = str(start_date)
                    soup.find('drugenddateformat').string = str("102")
                    soup.find('drugenddate').string = str(end_date)
                    soup.find('drugtreatmentduration').string = str(TherapyDuration)
                    soup.find('drugtreatmentdurationunit').string = str("804")
                    soup.find('drugrecurreadministration').string = str(ReactionReappearAfterReintroduction)
                    soup.find('activesubstancename').string = str(SuspectDrug)
                    final_tag.append(soup)

            except Exception as e:
                print("371..", str(e))
                self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            result = self.get_drug_continue_tag()
            if result != "":
                final_tag.append(result)

            try:
                if not ("#" in self.row['SuspectDrug'] and self.row['SuspectDrug'].count("#") > 1):
                    result_con = self.get_concomitant_drug_continue_tag()

                if result_con != "":
                    final_tag.append(result_con)
            except Exception as e:
                self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))


        # group1 template calculation
        elif self.code_template in self.drug_code_group_1:
            try:
                SuspectDrug = self.item_indexing(self.row['SuspectDrug'], 'SuspectDrug')
                DailyDose = self.item_indexing(self.row['DailyDose'], 'DailyDose')
                drugE2b_data = drugE2b(
                    self.item_indexing(self.row['RouteOfAdministration'], 'RouteOfAdministration'))
                RouteOfAdministration = drugE2b_data.get_route_of_admin_e2b()
                IndicationForUse = self.get_medra_code(self.row['IndicationForUse'], 'IndicationForUse')
                TherapyDatesFromTo = dateFormatCalculation().get_data(
                    self.item_indexing(self.row['TherapyDatesFromTo'], "TherapyDatesFromTo"), 1).split('_')

                start_date = ""
                end_date = ""
                try:
                    if TherapyDatesFromTo[0]:
                        start_date = TherapyDatesFromTo[0]
                except IndexError as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    if TherapyDatesFromTo[1]:
                        end_date = TherapyDatesFromTo[1]
                except IndexError as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                TherapyDuration = self.helper.duration_filter(
                    self.item_indexing(self.row['TherapyDuration'], "TherapyDuration"))
                if len(IndicationForUse) > 0:
                    for x in IndicationForUse:
                        soup = BeautifulSoup(self.text, 'lxml-xml')
                        soup.find('drugcharacterization').string = str("1")
                        soup.find('medicinalproduct').string = str(SuspectDrug)
                        soup.find('drugauthorizationholder').string = str("NA")
                        try:
                            soup.find('drugdosagetext').string = str(DailyDose)
                        except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                        try:
                            soup.find('drugadministrationroute').string = str(RouteOfAdministration)
                        except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        soup.find('drugindication').string = str(drug_indication)
                        soup.find('drugstartdateformat').string = str("102")
                        soup.find('drugstartdate').string = str(start_date)
                        soup.find('drugenddateformat').string = str("102")
                        soup.find('drugenddate').string = str(end_date)
                        soup.find('drugtreatmentduration').string = str(TherapyDuration)
                        soup.find('drugtreatmentdurationunit').string = str("804")
                        soup.find('drugrecurreadministration').string = str(ReactionReappearAfterReintroduction)
                        soup.find('activesubstancename').string = str(SuspectDrug)
                        final_tag.append(soup)
                else:
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    soup.find('drugcharacterization').string = str("1")
                    soup.find('medicinalproduct').string = str(SuspectDrug)
                    soup.find('drugauthorizationholder').string = str("NA")
                    try:
                        soup.find('drugdosagetext').string = str(DailyDose)
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    try:
                        soup.find('drugadministrationroute').string = str(RouteOfAdministration)
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    soup.find('drugstartdateformat').string = str("102")
                    soup.find('drugstartdate').string = str(start_date)
                    soup.find('drugenddateformat').string = str("102")
                    soup.find('drugenddate').string = str(end_date)
                    soup.find('drugtreatmentduration').string = str(TherapyDuration)
                    soup.find('drugtreatmentdurationunit').string = str("804")
                    soup.find('drugrecurreadministration').string = str(ReactionReappearAfterReintroduction)
                    soup.find('activesubstancename').string = str(SuspectDrug)
                    final_tag.append(soup)
            except Exception as e:
                self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            result_con = self.get_concomitant_drug_tag()

            if result_con != "":
                final_tag.append(result_con)
        return final_tag

    # second page drug information default group
    def get_drug_continue_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        if self.helper.isNan('Suspect Drugs (Cont...)') == 1:
            Suspect_drug_cont = self.row['Suspect Drugs (Cont...)'].replace("Seq. No", "Seq.No.").replace(
                "SeqNo.", "Seq.No.").replace("...)", "").strip().split("Seq.No.")

            for index, x in enumerate(Suspect_drug_cont):
                if x != "" and index > 0:
                    # print(x)
                    # exit(1)
                    row = 20
                    column = 4
                    max_combination = 1
                    final_drug_combination = [[0 for x in range(column)] for x in range(row)]
                    drug_characterization = "1"
                    drug_date_format = "102";
                    item_block = self.helper.remove_headers(x).strip()
                    try:
                        item = item_block[item_block.find("Drug"):]
                        DrugName = ""
                        if item.find("Daily") > 0:
                            DrugName = item[item.find(":") + 1:item.find("Daily")]
                        elif item.find("Route") > 0:
                            DrugName = item[item.find(":") + 1:item.find("Route")]
                        elif item.find("Indication") > 0:
                            DrugName = item[item.find(":") + 1:item.find("Indication")]
                        elif item.find("Therapy") > 0:
                            DrugName = item[item.find(":") + 1:item.find("Therapy")]
                        elif item.find("Causality") > 0:
                            DrugName = item[item.find(":") + 1:item.find("Causality")]
                        else:
                            DrugName = item[item.find(":") + 1:]
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        item = item_block[item_block.find("Daily"):]
                        if item_block.find("Daily") > 0:
                            Daily = ""
                            if item.find("Route") > 0:
                                Daily = item[item.find(":") + 1:item.find("Route")]
                            elif item.find("Indication") > 0:
                                Daily = item[item.find(":") + 1:item.find("Indication")]
                            elif item.find("Therapy") > 0:
                                Daily = item[item.find(":") + 1:item.find("Therapy")]
                            elif item.find("Causality") > 0:
                                Daily = item[item.find(":") + 1:item.find("Causality")]
                            else:
                                Daily = item[item.find(":") + 1:]

                            result = self.insert_in_location(0, Daily, final_drug_combination, max_combination)
                            final_drug_combination = result[0]
                            max_combination = result[1]
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        item = item_block[item_block.find("Route"):]
                        if item_block.find("Route") > 0:
                            Route = ""
                            if item.find("Indication") > 0:
                                Route = item[item.find(":") + 1:item.find("Indication")]
                            elif item.find("Therapy") > 0:
                                Route = item[item.find(":") + 1:item.find("Therapy")]
                            elif item.find("Causality") > 0:
                                Route = item[item.find(":") + 1:item.find("Causality")]
                            else:
                                Route = item[item.find(":") + 1:]

                            result = self.insert_in_location(1, Route, final_drug_combination, max_combination)
                            final_drug_combination = result[0]
                            max_combination = result[1]

                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        item = item_block[item_block.find("Indication"):]
                        if item_block.find("Indication") > 0:
                            Indication = ""
                            if item.find("Therapy") > 0:
                                Indication = item[item.find(":") + 1:item.find("Therapy")]
                            elif item.find("Causality") > 0:
                                Indication = item[item.find(":") + 1:item.find("Causality")]
                            else:
                                Indication = item[item.find(":") + 1:]

                            result = self.insert_in_location(2, Indication, final_drug_combination, max_combination)
                            final_drug_combination = result[0]
                            max_combination = result[1]
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        item = item_block[item_block.find("Therapy"):]
                        if item_block.find("Therapy") > 0:
                            Therapy = ""
                            if item.find("Causality") > 0:
                                Therapy = item[item.find(":") + 1:item.find("Causality")]
                            else:
                                Therapy = item[item.find(":") + 1:]
                            Therapy = Therapy.strip().split("\n")
                            result = self.insert_in_location(3, Therapy, final_drug_combination, max_combination)
                            final_drug_combination = result[0]
                            max_combination = result[1]
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        if item_block.find("Causality") > 0:
                            Causality = item_block[item_block.find("Causality"):]

                            # result_Causality = self.get_drug_reaction_relatedness_tag(Causality)
                            result_Causality = self.get_drug_reaction_relatedness_tag_png()
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    soup = self.get_mapping_done(DrugName, drug_characterization, final_drug_combination,
                                                 max_combination)
                    try:
                        if result_Causality['drug']:

                            if result_Causality['drug'].split('_')[0] != '0':
                                soup.find('actiondrug').string = str(result_Causality['drug'].split('_')[0])
                            if result_Causality['drug'].split('_')[1] != '0':
                                soup.find('drugrecurreadministration').string = str(
                                    result_Causality['drug'].split('_')[1])
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    try:
                        if result_Causality['tag']:
                            soup.find('drug').append(result_Causality['tag'])
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    final_tag.append(soup)

        return final_tag

    # first page drug information group 1
    def get_concomitant_drug_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        if self.helper.isNan('ConcomitantDrugs') == 1:
            ConcomitantDrugs = self.row["ConcomitantDrugs"]
            index = 1
            flag = 0
            drugName = ""
            start_date = ""
            end_date = ""
            try:
                while (index > 0):
                    if ConcomitantDrugs.find("#" + str(index)) > -1 and ConcomitantDrugs.find(
                            "#" + str(index + 1)) > -1:
                        flag = 1
                        ConcomitantDrug = ConcomitantDrugs[
                                          ConcomitantDrugs.find("#" + str(index)):ConcomitantDrugs.find(
                                              "#" + str(index + 1))].split(";")
                    elif ConcomitantDrugs.find("#" + str(index)) > -1:
                        flag = -1
                        ConcomitantDrug = ConcomitantDrugs[ConcomitantDrugs.find("#" + str(index)):].split(";")

                    for con_index, x in enumerate(ConcomitantDrug):

                        if con_index == 0:
                            drugName = x[:x.find('(')]
                        if con_index == 1:

                            TherapyDatesFromTo = dateFormatCalculation().get_data(x, 1).split('_')
                            try:
                                if TherapyDatesFromTo[0]:
                                    start_date = TherapyDatesFromTo[0]
                            except IndexError as e:
                                self.helper.error_log(
                                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                            try:
                                if TherapyDatesFromTo[1]:
                                    end_date = TherapyDatesFromTo[1]
                            except IndexError as e:
                                self.helper.error_log(
                                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    if flag == -1:
                        index = 0
                    else:
                        index = index + 1
                    print(drugName, start_date, end_date, '----concatimant----')
                    # exit(0)
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    soup.find('drugcharacterization').string = str("2")
                    soup.find('medicinalproduct').string = str(drugName)
                    soup.find('drugauthorizationholder').string = str("NA")
                    soup.find('drugstartdateformat').string = str("102")
                    try:
                        soup.find('drugstartdate').string = str(start_date)
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    soup.find('drugenddateformat').string = str("102")
                    try:
                        soup.find('drugenddate').string = str(end_date)
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    soup.find('drugtreatmentdurationunit').string = str("804")
                    soup.find('activesubstancename').string = str(drugName)
                    final_tag.append(soup)
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return final_tag

    # second page drug information default group
    def get_concomitant_drug_continue_tag(self):

        final_tag = BeautifulSoup("", 'lxml-xml')
        if self.helper.isNan('Concomitant drugs (Cont ...)') == 1:

            Concomitant_drug_cont = self.row['Concomitant drugs (Cont ...)'].replace("Seq. No", "Seq.No.").replace(
                "SeqNo.", "Seq.No.").replace("...)", "").strip().split("Seq.No.")

            for index, x in enumerate(Concomitant_drug_cont):
                if x != "":
                    row = 20
                    column = 4
                    max_combination = 1
                    final_drug_combination = [[0 for x in range(column)] for x in range(row)]
                    drug_characterization = "2"
                    drug_date_format = "102";
                    item_block = self.helper.remove_headers(x).strip()
                    try:
                        item = item_block[item_block.find("Drug"):]
                        DrugName = ""
                        if item.find("Daily") > 0:
                            DrugName = item[item.find(":") + 1:item.find("Daily")]
                        elif item.find("Route") > 0:
                            DrugName = item[item.find(":") + 1:item.find("Route")]
                        elif item.find("Indication") > 0:
                            DrugName = item[item.find(":") + 1:item.find("Indication")]
                        elif item.find("Therapy") > 0:
                            DrugName = item[item.find(":") + 1:item.find("Therapy")]
                        elif item.find("Causality") > 0:
                            DrugName = item[item.find(":") + 1:item.find("Causality")]
                        else:
                            DrugName = item[item.find(":") + 1:]
                        # print(DrugName.strip())
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        item = item_block[item_block.find("Daily"):]
                        if item_block.find("Daily") > 0:
                            Daily = ""
                            if item.find("Route") > 0:
                                Daily = item[item.find(":") + 1:item.find("Route")]
                            elif item.find("Indication") > 0:
                                Daily = item[item.find(":") + 1:item.find("Indication")]
                            elif item.find("Therapy") > 0:
                                Daily = item[item.find(":") + 1:item.find("Therapy")]
                            elif item.find("Causality") > 0:
                                Daily = item[item.find(":") + 1:item.find("Causality")]
                            else:
                                Daily = item[item.find(":") + 1:]

                            result = self.insert_in_location(0, Daily, final_drug_combination, max_combination)
                            final_drug_combination = result[0]
                            max_combination = result[1]
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        item = item_block[item_block.find("Route"):]
                        if item_block.find("Route") > 0:
                            Route = ""
                            if item.find("Indication") > 0:
                                Route = item[item.find(":") + 1:item.find("Indication")]
                            elif item.find("Therapy") > 0:
                                Route = item[item.find(":") + 1:item.find("Therapy")]
                            elif item.find("Causality") > 0:
                                Route = item[item.find(":") + 1:item.find("Causality")]
                            else:
                                Route = item[item.find(":") + 1:]

                            result = self.insert_in_location(1, Route, final_drug_combination, max_combination)
                            final_drug_combination = result[0]
                            max_combination = result[1]

                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        item = item_block[item_block.find("Indication"):]
                        if item_block.find("Indication") > 0:
                            Indication = ""
                            if item.find("Therapy") > 0:
                                Indication = item[item.find(":") + 1:item.find("Therapy")]
                            elif item.find("Causality") > 0:
                                Indication = item[item.find(":") + 1:item.find("Causality")]
                            else:
                                Indication = item[item.find(":") + 1:]

                            result = self.insert_in_location(2, Indication, final_drug_combination, max_combination)
                            final_drug_combination = result[0]
                            max_combination = result[1]
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        item = item_block[item_block.find("Therapy"):]
                        if item_block.find("Therapy") > 0:
                            Therapy = ""
                            if item.find("Causality") > 0:
                                Therapy = item[item.find(":") + 1:item.find("Causality")]
                            else:
                                Therapy = item[item.find(":") + 1:]
                            Therapy = Therapy.strip().split("\n")
                            result = self.insert_in_location(3, Therapy, final_drug_combination, max_combination)
                            final_drug_combination = result[0]
                            max_combination = result[1]
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        if item_block.find("Causality") > 0:
                            Causality = item_block[item_block.find("Causality"):]
                            # result_Causality = self.get_drug_reaction_relatedness_tag(Causality)
                            result_Causality = self.get_drug_reaction_relatedness_tag_png(Causality)


                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    soup = self.get_mapping_done(DrugName, drug_characterization, final_drug_combination,
                                                 max_combination)
                    try:
                        if result_Causality['drug']:

                            if result_Causality['drug'].split('_')[0] != '0':
                                soup.find('actiondrug').string = str(result_Causality['drug'].split('_')[0])
                            if result_Causality['drug'].split('_')[1] != '0':
                                soup.find('drugrecurreadministration').string = str(
                                    result_Causality['drug'].split('_')[1])
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    try:
                        if result_Causality['tag']:
                            soup.find('drug').append(result_Causality['tag'])
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    final_tag.append(soup)
        return final_tag

    def get_drug_reaction_relatedness_tag_png(self):
        try:
            final_tag = BeautifulSoup("", 'lxml-xml')
            data = self.row['png-data']
            suspect_drug_prod = ''
            ls = ['Suspect Drugs (Cont...)', 'Suspect Products (Cont...)', 'Suspect Products (Cont...)']
            for i in ls:
                if i in data:
                    suspect_drug_prod = i
            if data[data.find(suspect_drug_prod):data.find("Labeling")].replace('\n', ' '):
                data = data[data.find(suspect_drug_prod):data.find("Labeling")].replace('\n', ' ')
            elif data[data.find(suspect_drug_prod):].replace('\n', ' '):
                data = data[data.find(suspect_drug_prod):].replace('\n', ' ')
            data = data[data.find("Causality "):]
            print(data)
            # Find the last occurrence of "Rechallenge"
            try:
                last_rechallenge_index = data.rfind("Rechallenge")
                if last_rechallenge_index < 1:
                    last_rechallenge_index = data.rfind("Dechallenge")

            except Exception as e:
                last_rechallenge_index = data.rfind("Dechallenge")
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            # Check if "Rechallenge" was found in the text
            print(last_rechallenge_index)
            # exit(7)
            if last_rechallenge_index != -1:
                # Extract the substring from the beginning of the text to the last "Rechallenge"
                data = data[:last_rechallenge_index]
            else:
                print("The text does not contain 'Rechallenge'.")

            causaulity_as_mfr = ''
            list = ['Causality as per Mf.(Drug/Vaccine)', 'Causality as per Mfi.(Drug/Vaccine)',
                    'Causality as per Mfr.(Drug/Vaccine)', 'Causality as per Mfi.(Drug/Vaccine)',
                    'Causality as per Mfi.(Drug/Vaccine}', 'Causality as per Mft.(Drug/Vaccine)']
            for i in list:
                if i in data:
                    causaulity_as_mfr = i
            # print(causaulity_as_mfr)
            causaulity_as_reporter = ''
            list = ['Causality as per reporter (Drug/Vaccinc)', 'Causality as per reporter (Drug/Vaccinc)',
                    'Causality as per reporter (Drug/Vaccine)']
            for i in list:
                if i in data:
                    causaulity_as_reporter = i
                    break
            print(causaulity_as_reporter)

            split_text = re.split(r'\s+\d+\)+\s', data)
            nes_keys = [causaulity_as_reporter, causaulity_as_mfr, 'Dechallenge']
            # child data
            inner_data = {}
            l = []
            for data in split_text[1:]:
                # print(j)
                inner = {}
                for i in range(len(nes_keys)):
                    start = nes_keys[i]
                    end = nes_keys[(i + 1) % len(nes_keys)]
                    if start in data:
                        # print(start,end)
                        inner[start] = (data.split(start))[1].split(end)[0].strip()
                l.append(inner)
                # print(inner)
                # print(inner)
            # print(l)

            print(len(l))
            for i in l:
                try:
                    reporter_result = i[causaulity_as_reporter]
                    print(reporter_result)
                    manufacturer_Result = i.get(causaulity_as_mfr)
                    print(manufacturer_Result)
                    soup = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')
                    soup.find('drugassessmentsource').string = str("Reporter")
                    soup.find('drugassessmentmethod').string = str(drugassessmentmethod)
                    soup.find('drugresult').string = str(reporter_result)
                    final_tag.append(soup)

                    soup_mfr = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')
                    soup_mfr.find('drugassessmentsource').string = str("Company")
                    soup_mfr.find('drugassessmentmethod').string = str(drugassessmentmethod)
                    soup_mfr.find('drugresult').string = str(manufacturer_Result)
                    final_tag.append(soup_mfr)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            final_data = {"tag": final_tag, "drug": ''}
            return final_data
        except Exception as e:
            print(str(e), 'error')

        # string=data
        # reporter_result=string[string.find('Causality as per reporter (Drug/Vaccine)'):string.find('Causality as per Mfi.(Drug/Vaccine)')].split(':')[-1]
        # manufacturer_Result=string[string.find('Causality as per Mfi.(Drug/Vaccine)'):string.find('Dechallenge')].split(':')[-1]
        # # soup = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')
        # # soup.find('drugassessmentsource').string = str(reporter)
        # # soup.find('drugassessmentmethod').string = str(drugassessmentmethod)
        # # soup.find('drugresult').string = str(reporter)
        # # final_tag.append(soup)
        # soup = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')
        # soup.find('drugassessmentsource').string = str("Reporter")
        # soup.find('drugassessmentmethod').string = str(drugassessmentmethod)
        # soup.find('drugresult').string = str(reporter_result)
        # final_tag.append(soup)

        # soup_mfr = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')
        # soup_mfr.find('drugassessmentsource').string = str("Company")
        # soup_mfr.find('drugassessmentmethod').string = str(drugassessmentmethod)
        # soup_mfr.find('drugresult').string = str(manufacturer_Result)
        # final_tag.append(soup_mfr)
        # final_data = {"tag": final_tag, "drug": ''}
        # return final_data

        # exit(1)

    # drug causality section
    def get_drug_reaction_relatedness_tag(self, Causality):
        final_data = {}
        final_tag = BeautifulSoup("", 'lxml-xml')
        index_list = ["Rechallenge", "Causality as per Mfr", "Causality as per reporter", "taken with drug"]
        index_exist = ""
        last_index = -1
        # print(Causality)
        # exit(2)
        for index, x in enumerate(index_list):
            if Causality.find(x) > -1:
                index_exist = x
                last_index = index
                break
        if index_exist != "":
            Causality_list = Causality.split(index_exist)
            Causality_list_final = []
            for index_y, y in enumerate(Causality_list):
                # print(index_exist)
                try:
                    if Causality_list[index_y + 1] != "":
                        sub_str = Causality_list[index_y + 1]
                        if sub_str.find(")") > -1:
                            Causality_list_final.append(
                                Causality_list[index_y] + index_exist + sub_str[: sub_str.find(")")])
                        else:
                            Causality_list_final.append(
                                Causality_list[index_y] + index_exist + sub_str)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            action_taken_all = []
            Rechallenge_all = []
            for index_z, z in enumerate(Causality_list_final):
                # print(index_z, z)
                # exit(1)
                if last_index == 0:
                    action_taken = z[z.find("Action(s)") + 1:z.find("Causality as per reporter")]
                    action_taken_all.append(
                        drugE2b(action_taken[action_taken.find(":") + 1:].strip()).get_drug_action_e2b())
                    reporter = z[z.find("Causality as per reporter") + 1:z.find("Causality as per Mfr")]
                    reporter_arr = reporter[reporter.find(":") + 1:].strip()

                    manu = z[z.find("Causality as per Mfr") + 1:z.find("Dechallenge")]
                    manu_arr = manu[manu.find(":") + 1:].strip()
                    Rechallenge = z[z.find("Rechallenge"):].replace("\n", "")
                    Rechallenge = re.sub(r'[0-9]', '', Rechallenge)
                    Rechallenge_all.append(eventOccurE2b(Rechallenge).get_current_e2b())
                    soup = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')
                    soup.find('drugassessmentsource').string = str("Reporter")
                    soup.find('drugassessmentmethod').string = str(drugassessmentmethod)
                    soup.find('drugresult').string = str(reporter_arr)
                    final_tag.append(soup)

                    soup_mfr = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')
                    soup_mfr.find('drugassessmentsource').string = str("Company")
                    soup_mfr.find('drugassessmentmethod').string = str(drugassessmentmethod)
                    soup_mfr.find('drugresult').string = str(manu_arr)
                    final_tag.append(soup_mfr)
            drug = str(max(action_taken_all, key=action_taken_all.count)) + '_' + str(
                max(Rechallenge_all, key=Rechallenge_all.count))
            final_data = {"tag": final_tag, "drug": drug}
        return final_data

    def get_mapping_done(self, DrugName, drug_characterization, final_drug_combination, max_combination):
        final_tag = BeautifulSoup("", 'lxml-xml')
        for y in range(max_combination):

            SuspectDrug = DrugName
            DailyDose = ""
            RouteOfAdministration = ""
            start_date = ""
            end_date = ""
            IndicationForUse = []
            if final_drug_combination[y][0] != 0:
                DailyDose = self.item_indexing(final_drug_combination[y][0], 0, 1)

            if final_drug_combination[y][1] != 0:
                drugE2b_data = drugE2b(
                    self.item_indexing(final_drug_combination[y][1], 0, 1))
                RouteOfAdministration = drugE2b_data.get_route_of_admin_e2b()
            if final_drug_combination[y][2] != 0:
                IndicationForUse = self.get_medra_code(final_drug_combination[y][2], 0, 1)

            if final_drug_combination[y][3] != 0:
                TherapyDatesFromTo = dateFormatCalculation().get_data(
                    self.item_indexing(final_drug_combination[y][3], 0, 1), 1).split('_')
                try:
                    if TherapyDatesFromTo[0]:
                        start_date = TherapyDatesFromTo[0]
                except IndexError as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    if TherapyDatesFromTo[1]:
                        end_date = TherapyDatesFromTo[1]
                except IndexError as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            if len(IndicationForUse) > 0:

                for x in IndicationForUse:
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    soup.find('drugcharacterization').string = str(drug_characterization)
                    soup.find('medicinalproduct').string = str(SuspectDrug)
                    soup.find('drugauthorizationholder').string = str("NA")
                    soup.find('drugdosagetext').string = str(DailyDose)
                    soup.find('drugadministrationroute').string = str(RouteOfAdministration)
                    soup.find('drugindication').string = str(x)
                    soup.find('drugstartdateformat').string = str("102")
                    soup.find('drugstartdate').string = str(start_date)
                    soup.find('drugenddateformat').string = str("102")
                    soup.find('drugenddate').string = str(end_date)
                    soup.find('activesubstancename').string = str(SuspectDrug)
                    final_tag.append(soup)
            else:
                soup = BeautifulSoup(self.text, 'lxml-xml')
                soup.find('drugcharacterization').string = str(drug_characterization)
                soup.find('medicinalproduct').string = str(SuspectDrug)
                soup.find('drugauthorizationholder').string = str("NA")
                soup.find('drugdosagetext').string = str(DailyDose)
                soup.find('drugadministrationroute').string = str(RouteOfAdministration)
                soup.find('drugstartdateformat').string = str("102")
                soup.find('drugstartdate').string = str(start_date)
                soup.find('drugenddateformat').string = str("102")
                soup.find('drugenddate').string = str(end_date)
                soup.find('activesubstancename').string = str(SuspectDrug)
                final_tag.append(soup)

        return final_tag

    # creating a list from drug combinations
    def insert_in_location(self, location, data, final_drug_combination, max_combination):
        data = data.strip().split("\n")

        [[final_drug_combination[index].insert(location, value)] for index, value in enumerate(data)]
        if len(data) > max_combination:
            max_combination = len(data)
        list_data = {0: final_drug_combination, 1: max_combination}
        return list_data

    def remove_junk_irms(self, str):
        str_final = str
        if str.lower().find("updated") > -1:
            str_final = str[str.lower().find("updated") + str.lower().find(")") + 1:]
        return str_final.strip()

    def get_irms_concomitant_drug_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        try:

            drugName = self.row['CONCOMITANT NAME:']
            drugName = self.helper.remove_junk_concomitant_drug_irms(drugName)
            drugName = [st for st in (re.sub(drug_regex, drug_delimeter, drugName)).split(drug_delimeter) if
                        len(st) > 0]
            IndicationForUse = self.row['CONCOMITANT INDICATION:']
            IndicationForUse = self.helper.remove_junk_concomitant_indication_irms(IndicationForUse)
            IndicationForUse = [st for st in
                                (re.sub(drug_regex, drug_delimeter, IndicationForUse)).split(drug_delimeter)
                                if
                                len(st) > 0]

            DrogDosage = [st for st in
                          (re.sub(drug_regex, drug_delimeter, self.helper.remove_junk_concomitant_daily_dosage_irms(
                              self.row['CONCOMITANT DOSE/FREQUENCY:']))).split(
                              drug_delimeter) if
                          len(st) > 0]
            start_date = self.row['CONCOMITANT START DATE:']
            start_date = self.helper.remove_junk_concomitant_start_date_irms(start_date)
            start_date = [st for st in (re.sub(drug_regex, drug_delimeter, start_date)).split(drug_delimeter) if
                          len(st) > 0]
            end_date = self.row['CONCOMITANT STOP DATE:']
            end_date = self.helper.remove_junk_concomitant_end_date_irms(end_date)
            end_date = [st for st in (re.sub(drug_regex, drug_delimeter, end_date)).split(drug_delimeter) if
                        len(st) > 0]

            if len(IndicationForUse) > 0:
                for i, x in enumerate(IndicationForUse):
                    if len(self.remove_junk_irms(drugName[i])) > 0:
                        soup = BeautifulSoup(self.text, 'lxml-xml')
                        soup.find('drugcharacterization').string = str("2")
                        soup.find('drugauthorizationholder').string = str("NA")
                        try:
                            if str(drugName[i]) != "":
                                soup.find('medicinalproduct').string = str(drugName[i])
                            else:
                                soup.find('medicinalproduct').string = str("unknown")
                        except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('drugdosagetext').string = str(DrogDosage[i].split("/")[0])
                        except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('drugstartdateformat').string = str("102")
                            soup.find('drugstartdate').string = str(
                                dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(start_date[i])))
                        except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('drugenddateformat').string = str("102")
                            soup.find('drugenddate').string = str(
                                dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(end_date[i])))
                        except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            soup.find('activesubstancename').string = str(drugName[i])
                        except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        try:
                            if self.get_medra_code(str(x), 'IndicationForUse', irms=1) != 0:
                                soup.find('drugindication').string = str(
                                    self.get_medra_code(str(x), 'IndicationForUse', irms=1))
                        except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                        final_tag.append(soup)
            else:
                if len(self.remove_junk_irms(drugName)) > 0:
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    soup.find('drugcharacterization').string = str("2")
                    soup.find('drugauthorizationholder').string = str("NA")
                    try:
                        if str(drugName) != "":
                            soup.find('medicinalproduct').string = str(drugName)
                        else:
                            soup.find('medicinalproduct').string = str("unknown")
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        soup.find('drugdosagetext').string = str(DrogDosage.split("/")[0])
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        soup.find('drugstartdateformat').string = str("102")
                        soup.find('drugstartdate').string = str(
                            dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(start_date)))
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        soup.find('drugenddateformat').string = str("102")
                        soup.find('drugenddate').string = str(
                            dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(end_date)))
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        soup.find('activesubstancename').string = str(drugName)
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        if self.get_medra_code(str(IndicationForUse), 'IndicationForUse', irms=1) != 0:
                            soup.find('drugindication').string = str(
                                self.get_medra_code(str(IndicationForUse), 'IndicationForUse', irms=1))
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    final_tag.append(soup)

        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return final_tag

    def get_irms_drug_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        try:
            SuspectDrug = self.row.get('SUSPECT PRODUCT INFORMATION:', '')

            SuspectDrug = self.helper.remove_junk_suspect_drug_irms(SuspectDrug.strip())
            SuspectDrug = [st for st in (re.sub(drug_regex, drug_delimeter, SuspectDrug)).split(drug_delimeter) if
                           len(st) > 0]

            IndicationForUse = self.helper.remove_junk_suspect_indication_irms(self.row.get('INDICATION:').strip())
            IndicationForUse = [st for st in
                                (re.sub(drug_regex, drug_delimeter, IndicationForUse)).split(drug_delimeter)
                                if
                                len(st) > 0]
            start_date = self.helper.remove_junk_suspect_start_date_irms(
                self.row.get('PRODUCT START DATE:', '').strip())
            start_date = [st for st in (re.sub(drug_regex, drug_delimeter, start_date)).split(drug_delimeter)
                          if
                          len(st) > 0]
            end_date = self.helper.remove_junk_suspect_end_date_irms(self.row.get('PRODUCT STOP DATE:', '').strip())
            end_date = [st for st in (re.sub(drug_regex, drug_delimeter, end_date)).split(drug_delimeter)
                        if
                        len(st) > 0]

            if len(IndicationForUse) > 0 and type(IndicationForUse) == list:
                for i, x in enumerate(IndicationForUse):
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    soup.find('drugcharacterization').string = str("1")

                    try:
                        if str(SuspectDrug[i]) != "":
                            soup.find('medicinalproduct').string = str(SuspectDrug[i])
                        else:
                            soup.find('medicinalproduct').string = str("unknown")
                    except Exception as e:
                        soup.find('medicinalproduct').string = str("unknown")
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    soup.find('drugauthorizationholder').string = str("NA")
                    try:
                        soup.find('drugstartdateformat').string = str("102")
                        soup.find('drugstartdate').string = str(
                            dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(start_date[i])))
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    try:
                        soup.find('drugenddateformat').string = str("102")
                        soup.find('drugenddate').string = str(
                            dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(end_date[i])))
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    try:
                        if str(SuspectDrug[i]) != "":
                            soup.find('activesubstancename').string = str(SuspectDrug[i])
                        else:
                            soup.find('activesubstancename').string = str("unknown")
                    except Exception as e:
                        soup.find('activesubstancename').string = str("unknown")
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        if self.get_medra_code(str(x), 'IndicationForUse', irms=1) != 0:
                            soup.find('drugindication').string = str(
                                self.get_medra_code(str(x), 'IndicationForUse', irms=1))
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    final_tag.append(soup)
            else:
                soup = BeautifulSoup(self.text, 'lxml-xml')
                soup.find('drugcharacterization').string = str("1")
                try:
                    if str(SuspectDrug) != "":
                        soup.find('medicinalproduct').string = str(SuspectDrug)
                    else:
                        soup.find('medicinalproduct').string = str("unknown")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    soup.find('drugstartdateformat').string = str("102")
                    soup.find('drugstartdate').string = str(
                        dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(start_date)))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                soup.find('drugauthorizationholder').string = str("NA")
                try:
                    soup.find('drugenddateformat').string = str("102")
                    soup.find('drugenddate').string = str(
                        dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(end_date)))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if str(SuspectDrug) != "":
                        soup.find('activesubstancename').string = str(SuspectDrug)
                    else:
                        soup.find('activesubstancename').string = str("unknown")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if self.get_medra_code(str(IndicationForUse), 'IndicationForUse', irms=1) != 0:
                        soup.find('drugindication').string = str(
                            self.get_medra_code(str(IndicationForUse), 'IndicationForUse', irms=1))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                final_tag.append(soup)
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        result_con = self.get_irms_concomitant_drug_tag()
        if result_con != "":
            final_tag.append(result_con)
        return final_tag

    def get_linelist_drug_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        # print("data",dateFormatCalculation().get_date('11-JAN-2022'))
        # exit(1)
        # print(self.helper.remove_junk_linelist('a. Sodium'))
        # print(active_substance)
        # exit(1)
        try:
            loop_len = []
            drug_name = []
            drug_category = []
            active_substance = []
            drug_start_date = []
            drug_end_date = []
            drug_indication = []
            Route_of_administration = []
            lot_number = []
            drugrecurreadministration = []
            actiondrug = []
            Dosage_form = []
            Dosage = []
            Dosage_Unit = []
            reporter_causality_assessment = []
            agency_causality_assessment = []

            try:
                drug_category = self.helper.linelist_scripting(self.row['drug_category'])
                loop_len.append(len(drug_category))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                drug_name = self.helper.linelist_scripting(self.row['drug_name'])
                loop_len.append(len(drug_name))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            try:
                active_substance = self.helper.linelist_scripting(self.row['active_substance'])
                loop_len.append(len(active_substance))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            try:
                drug_start_date = self.helper.linelist_scripting(self.row['drug_start_date'])
                loop_len.append(len(drug_start_date))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                drug_end_date = self.helper.linelist_scripting(self.row['drug_end_date'])
                loop_len.append(len(drug_end_date))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                drug_indication = self.helper.linelist_scripting(self.row['drug_indication'])
                loop_len.append(len(drug_indication))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                Route_of_administration = self.helper.linelist_scripting(self.row['Route_of_administration'])
                loop_len.append(len(Route_of_administration))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                lot_number = self.helper.linelist_scripting(self.row['lot_number'])
                loop_len.append(len(lot_number))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            try:
                drugrecurreadministration = self.helper.linelist_scripting(self.row['drugrecurreadministration'])
                loop_len.append(len(drugrecurreadministration))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            try:
                actiondrug = self.helper.linelist_scripting(self.row['actiondrug'])
                loop_len.append(len(actiondrug))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            try:
                Dosage_form = self.helper.linelist_scripting(self.row['Dosage_form'])
                loop_len.append(len(Dosage_form))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                Dosage = self.helper.linelist_scripting(self.row['Dosage'])
                loop_len.append(len(Dosage))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                Dosage_Unit = self.helper.linelist_scripting(self.row['Dosage_Unit'])
                loop_len.append(len(Dosage_Unit))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                reporter_causality_assessment = self.helper.linelist_scripting(
                    self.row['reporter_causality_assessment'])
                loop_len.append(len(reporter_causality_assessment))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                agency_causality_assessment = self.helper.linelist_scripting(self.row['agency_causality_assessment'])
                loop_len.append(len(agency_causality_assessment))
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            # print(max(loop_len))
            # print(actiondrug)
            # exit(1)
            for i in range(0, max(loop_len)):
                soup = BeautifulSoup(self.text, 'lxml-xml')
                try:
                    cat = ''
                    if i < len(drug_category):
                        if self.helper.remove_junk_linelist(drug_category[i].lower()) == 'suspect':
                            cat = 1
                        elif self.helper.remove_junk_linelist(drug_category[i].lower()) == 'concomitant':
                            cat = 2
                        elif self.helper.remove_junk_linelist(drug_category[i].lower()) == 'interacting':
                            cat = 3
                        drugcharacterization = str(cat)
                        soup.find('drugcharacterization').string = str(drugcharacterization.strip())
                except Exception as e:
                    soup.find('drugcharacterization').string = str(1)
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:

                    if i < len(drug_name):
                        soup.find('medicinalproduct').string = str(
                            self.helper.remove_junk_linelist(drug_name[i]))
                    elif i < len(active_substance):
                        soup.find('medicinalproduct').string = str(
                            self.helper.remove_junk_linelist(active_substance[i]))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    if i < len(drug_start_date[i]):
                        soup.find('drugstartdate').string = str(dateFormatCalculation().get_date(drug_start_date[i]))
                        soup.find('drugstartdateformat').string = str("102")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                # soup.find('drugauthorizationholder').string = str("NA")
                try:
                    if i < len(drug_end_date):
                        soup.find('drugenddate').string = str(dateFormatCalculation().get_date(drug_end_date[i]))
                        soup.find('drugenddateformat').string = str("102")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(active_substance):
                        soup.find('activesubstancename').string = str(
                            self.helper.remove_junk_linelist(active_substance[i]))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(drug_indication):
                        in_res = self.get_medra_code(str(self.helper.remove_junk_linelist(drug_indication[i])),
                                                     'IndicationForUse', irms=1)
                        if in_res != 0:
                            soup.find('drugindication').string = str(in_res)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(Route_of_administration):
                        Route_of_administration_data = drugE2b(Route_of_administration[i])
                        soup.find('drugadministrationroute').string = str(
                            Route_of_administration_data.get_route_of_admin_e2b())
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(lot_number):
                        soup.find('drugbatchnumb').string = str(lot_number[i])
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(drugrecurreadministration):
                        drugrecurreadministration_result = eventOccurE2b(drugrecurreadministration[i]).get_current_e2b()
                        if drugrecurreadministration_result != 0:
                            soup.find('drugrecurreadministration').string = str(drugrecurreadministration_result)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    if i < len(actiondrug):
                        actiondrug_data = drugE2b(actiondrug[i])
                        soup.find('actiondrug').string = str(
                            actiondrug_data.get_drug_action_e2b())
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(Dosage_form):
                        soup.find('drugdosageform').string = str(Dosage_form[i])
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(Dosage):
                        soup.find('drugstructuredosagenumb').string = str(int(Dosage[i]))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if i < len(Dosage_Unit):
                        soup.find('drugstructuredosageunit').string = str(
                            drugE2b(Dosage_Unit[i]).get_drug_dosage_linelist_unit_e2b())
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                final_tag.append(soup)
                try:
                    if i < len(reporter_causality_assessment):
                        soup_reporter = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')
                        soup_reporter.find('drugassessmentsource').string = str("Reporter")
                        soup_reporter.find('drugassessmentmethod').string = str(drugassessmentmethod)
                        soup_reporter.find('drugresult').string = str(
                            self.helper.remove_junk_linelist(reporter_causality_assessment[i]))
                        final_tag.findAll('drug')[i].append(soup_reporter)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    if i < len(agency_causality_assessment):
                        soup_mfr = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')
                        soup_mfr.find('drugassessmentsource').string = str("Company")
                        soup_mfr.find('drugassessmentmethod').string = str(drugassessmentmethod)
                        soup_mfr.find('drugresult').string = str(
                            self.helper.remove_junk_linelist(agency_causality_assessment[i]))
                        final_tag.findAll('drug')[i].append(soup_mfr)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return final_tag

    def process_list_values(self, data):
        try:
            return ", ".join(str(v) for v in eval(str(data)))
        except Exception as e:
            return data

    def get_litrature_drug_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        row = self.row
        PATIENTSUSPECT = self.helper.get_relation('PATIENTSUSPECT')
        if len(PATIENTSUSPECT) > 0:
            final_tag.append(self.get_litrature_drug_by_realtion_tag(PATIENTSUSPECT))
        elif 'suspectproduct' in row:
            med_prod = str(self.process_list_values(row['suspectproduct'])).split(',')
            if len(med_prod) > 0:
                for index, mp in enumerate(med_prod):
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    try:
                        soup.find('drugcharacterization').string = str("1")
                        soup.find('medicinalproduct').string = str(mp).strip()

                        if self.helper.isNan('obtaindrugcountry') == 1:
                            soup.find('obtaindrugcountry').string = str("")

                        if self.helper.isNan('drugbatchnumb') == 1:
                            soup.find('drugbatchnumb').string = str("")

                        if self.helper.isNan('drugauthorizationnumb') == 1:
                            soup.find('drugauthorizationnumb').string = str("")

                        if self.helper.isNan('drugauthorizationcountry') == 1:
                            soup.find('drugauthorizationcountry').string = str("")

                        if self.helper.isNan('drugauthorizationholder') == 1:
                            soup.find('drugauthorizationholder').string = str("")

                        if self.helper.isNan('drugstructuredosagenumb') == 1:
                            soup.find('drugstructuredosagenumb').string = str(
                                self.process_list_values(row['drugstructuredosagenumb']))

                        if self.helper.isNan('drugstructuredosageunit') == 1:
                            soup.find('drugstructuredosageunit').string = str(
                                self.process_list_values(row['drugstructuredosageunit']))

                        if self.helper.isNan('drugseparatedosagenumb') == 1:
                            soup.find('drugseparatedosagenumb').string = str("")

                        if self.helper.isNan('drugintervaldosageunitnumb') == 1:
                            soup.find('drugintervaldosageunitnumb').string = str(
                                self.process_list_values(row["drugintervaldosageunitnumb"]))

                        if self.helper.isNan('drugintervaldosagedefinition') == 1:
                            soup.find('drugintervaldosagedefinition').string = str(
                                self.process_list_values(row['drugintervaldosagedefinition']))

                        if self.helper.isNan('drugcumulativedosagenumb') == 1:
                            soup.find('drugcumulativedosagenumb').string = str("")

                        if self.helper.isNan('drugcumulativedosageunit') == 1:
                            soup.find('drugcumulativedosageunit').string = str("")

                        if self.helper.isNan('drugdosagetext') == 1:
                            dt = str(self.process_list_values(row["drugdosagetext"])).split(",")
                            if len(dt) > 0:
                                try:
                                    soup.find('drugdosagetext').string = str(dt[index]).strip()
                                except IndexError:
                                    soup.find('drugdosagetext').string = str("")

                        if self.helper.isNan('drugdosageform') == 1:
                            soup.find('drugdosageform').string = str(row['drugdosageform'])

                        if self.helper.isNan('drugadministrationroute') == 1:
                            soup.find('drugadministrationroute').string = str(
                                self.process_list_values(row["drugadministrationroute"]))

                        if self.helper.isNan('drugindication') == 1:
                            di = str(self.process_list_values(row['drugindication'])).split(",")
                            if len(di) > 0:
                                for dind in di:
                                    dind_meddra = self.get_medra_code(dind)
                                    if dind_meddra > 0:
                                        soup.find('drugindication').string = str(dind_meddra)

                        if self.helper.isNan('drugstartdateformat') == 1:
                            soup.find('drugstartdateformat').string = str("")

                        if self.helper.isNan('drugstartdate') == 1:
                            soup.find('drugstartdate').string = str("")

                        if self.helper.isNan('drugenddateformat') == 1:
                            soup.find('drugenddateformat').string = str("")

                        if self.helper.isNan('drugenddate') == 1:
                            soup.find('drugenddate').string = str("")

                        if self.helper.isNan('drugtreatmentduration') == 1:
                            soup.find('drugtreatmentduration').string = str("")

                        if self.helper.isNan('drugtreatmentdurationunit') == 1:
                            soup.find('drugtreatmentdurationunit').string = str("")

                        if self.helper.isNan('actiondrug') == 1:
                            soup.find('actiondrug').string = str("")

                        if self.helper.isNan('drugrecurreadministration') == 1:
                            soup.find('drugrecurreadministration').string = str("")

                        if self.helper.isNan('drugadditional') == 1:
                            soup.find('drugadditional').string = str("")

                        soup.find('activesubstancename').string = str(mp).strip()

                        soup_dr = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')

                        if 'drugassessmentsource' in row:
                            soup_dr.find('drugassessmentsource').string = str(
                                self.process_list_values(row["drugassessmentsource"]))

                        if 'drugassessmentmethod' in row:
                            soup_dr.find('drugassessmentmethod').string = str(
                                self.process_list_values(row["drugassessmentmethod"]))

                        if 'drugresult' in row:
                            soup_dr.find('drugresult').string = str(self.process_list_values(row['drugresult']))

                        soup.find('drug').append(soup_dr)
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    final_tag.append(soup)

        if 'concomitantproduct' in row:
            med_prod = str(self.process_list_values(row['concomitantproduct'])).split(',')
            if len(med_prod) > 0:
                for index, mp in enumerate(med_prod):
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    try:
                        soup.find('drugcharacterization').string = str("2")
                        soup.find('medicinalproduct').string = str(mp).strip()

                        if self.helper.isNan('obtaindrugcountry') == 2:
                            soup.find('obtaindrugcountry').string = str("")

                        if self.helper.isNan('drugbatchnumb') == 1:
                            soup.find('drugbatchnumb').string = str("")

                        if self.helper.isNan('drugauthorizationnumb') == 1:
                            soup.find('drugauthorizationnumb').string = str("")

                        if self.helper.isNan('drugauthorizationcountry') == 1:
                            soup.find('drugauthorizationcountry').string = str("")

                        if self.helper.isNan('drugauthorizationholder') == 1:
                            soup.find('drugauthorizationholder').string = str("")

                        if self.helper.isNan('drugstructuredosagenumb') == 1:
                            soup.find('drugstructuredosagenumb').string = str(
                                self.process_list_values(row['drugstructuredosagenumb']))

                        if self.helper.isNan('drugstructuredosageunit') == 1:
                            soup.find('drugstructuredosageunit').string = str(
                                self.process_list_values(row['drugstructuredosageunit']))

                        if self.helper.isNan('drugseparatedosagenumb') == 1:
                            soup.find('drugseparatedosagenumb').string = str("")

                        if self.helper.isNan('drugintervaldosageunitnumb') == 1:
                            soup.find('drugintervaldosageunitnumb').string = str(
                                self.process_list_values(row["drugintervaldosageunitnumb"]))

                        if self.helper.isNan('drugintervaldosagedefinition') == 1:
                            soup.find('drugintervaldosagedefinition').string = str(
                                self.process_list_values(row['drugintervaldosagedefinition']))

                        if self.helper.isNan('drugcumulativedosagenumb') == 1:
                            soup.find('drugcumulativedosagenumb').string = str("")

                        if self.helper.isNan('drugcumulativedosageunit') == 1:
                            soup.find('drugcumulativedosageunit').string = str("")

                        if self.helper.isNan('drugdosagetext') == 1:
                            dt = str(self.process_list_values(row["drugdosagetext"])).split(",")
                            if len(dt) > 0:
                                try:
                                    soup.find('drugdosagetext').string = str(dt[index]).strip()
                                except IndexError:
                                    soup.find('drugdosagetext').string = str("")

                        if self.helper.isNan('drugdosageform') == 1:
                            soup.find('drugdosageform').string = str(row['drugdosageform'])

                        if self.helper.isNan('drugadministrationroute') == 1:
                            soup.find('drugadministrationroute').string = str(
                                self.process_list_values(row["drugadministrationroute"]))

                        if self.helper.isNan('drugindication') == 1:
                            di = str(self.process_list_values(row['drugindication'])).split(",")
                            if len(di) > 0:
                                for dind in di:
                                    dind_meddra = self.get_medra_code(dind)
                                    if dind_meddra > 0:
                                        soup.find('drugindication').string = str(dind_meddra)

                        if self.helper.isNan('drugstartdateformat') == 1:
                            soup.find('drugstartdateformat').string = str("")

                        if self.helper.isNan('drugstartdate') == 1:
                            soup.find('drugstartdate').string = str("")

                        if self.helper.isNan('drugenddateformat') == 1:
                            soup.find('drugenddateformat').string = str("")

                        if self.helper.isNan('drugenddate') == 1:
                            soup.find('drugenddate').string = str("")

                        if self.helper.isNan('drugtreatmentduration') == 1:
                            soup.find('drugtreatmentduration').string = str("")

                        if self.helper.isNan('drugtreatmentdurationunit') == 1:
                            soup.find('drugtreatmentdurationunit').string = str("")

                        if self.helper.isNan('actiondrug') == 1:
                            soup.find('actiondrug').string = str("")

                        if self.helper.isNan('drugrecurreadministration') == 1:
                            soup.find('drugrecurreadministration').string = str("")

                        if self.helper.isNan('drugadditional') == 1:
                            soup.find('drugadditional').string = str("")

                        soup.find('activesubstancename').string = str(mp).strip()

                        soup_dr = BeautifulSoup(self.text_drug_reaction_relatedness, 'lxml-xml')

                        if 'drugassessmentsource' in row:
                            soup_dr.find('drugassessmentsource').string = str(
                                self.process_list_values(row["drugassessmentsource"]))

                        if 'drugassessmentmethod' in row:
                            soup_dr.find('drugassessmentmethod').string = str(
                                self.process_list_values(row["drugassessmentmethod"]))

                        if 'drugresult' in row:
                            soup_dr.find('drugresult').string = str(self.process_list_values(row['drugresult']))

                        soup.find('drug').append(soup_dr)
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    final_tag.append(soup)

        return final_tag

    def get_litrature_drug_by_realtion_tag(self, PATIENTSUSPECT):
        final_tag = BeautifulSoup("", 'lxml-xml')
        for val in PATIENTSUSPECT:
            try:
                entities = val['entities']
                soup = BeautifulSoup(self.text, 'lxml-xml')
                soup.find('drugcharacterization').string = str("1")
                soup.find('medicinalproduct').string = str(entities[1]['SUSPECTPRODUCT']).strip()
                soup.find('activesubstancename').string = str(entities[1]['SUSPECTPRODUCT']).strip()
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            final_tag.append(soup)
        return final_tag

    def get_medwatch_drug_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        try:
            SuspectDrugName = ""
            SuspectDrug = self.row.get('SuspectDrugName', '')
            print("SuspectDrugName", SuspectDrug)
            # SuspectDrug = self.helper.extract_indication_data(SuspectDrug)
            # Split the string into words
            words = SuspectDrug.split()

            # Filter out words with a length less than 6 characters
            filtered_words = [word for word in words if len(word) >= 6]

            # Join the filtered words back into a string
            SuspectDrug = ' '.join(filtered_words)

            result_list = self.helper.remove_junk_medwatch_suspect_name(SuspectDrug)
            print("Result List", result_list)

            result_list_length = len(result_list)

            SuspectDrugName1 = self.row.get('SuspectDrugNameContinue1', '')
            print("SuspectDrugName1", SuspectDrugName1)

            dosage_info1 = self.helper.extract_alphanumeric_words(SuspectDrugName1)
            print(dosage_info1)

            dosage_info1_length = len(dosage_info1)
            print(dosage_info1_length)

            SuspectDrugName2 = self.row.get('SuspectDrugNameContinue2', '')
            print("SuspectDrugName2", SuspectDrugName2)

            dosage_info2 = self.helper.extract_alphanumeric_words(SuspectDrugName2)
            print(dosage_info2)
            dosage_info2_length = len(dosage_info2)
            print(dosage_info2_length)

            DailyDose = self.row.get('DailyDose', '')
            print("DailyDose", DailyDose)

            DrugDosage = self.helper.remove_junk_medwatch_dose_used(DailyDose)
            print(DrugDosage)

            DailyDoseContinue1 = self.row.get('DailyDoseContinue1', '')
            print("DailyDoseContinue1", DailyDoseContinue1)

            DailyDoseContinue2 = self.row.get('DailyDoseContinue2', '')
            print("DailyDoseContinue2", DailyDoseContinue2)

            SuspectDrugOne = ""
            SuspectDrugTwo = ""
            SuspectDrug = []
            SuspectDosage = []
            SuspectDosageOne = ""
            SuspectDosageTwo = ""
            SuspectFrequency = []
            SuspectRoute = []
            if result_list_length >= 1 or result_list_length <= 2:
                # print("yes")
                for index, value in enumerate(result_list):
                    print(f"Index: {index}, Value: {value}")
                    if index == 0:
                        SuspectDrugOne = value + SuspectDrugName1
                        SuspectDosageOne = DrugDosage[index] + DailyDoseContinue1
                        frequency = self.helper.extract_frequesncy_route_used(SuspectDosageOne, 0)
                        route_used = self.helper.extract_frequesncy_route_used(SuspectDosageOne, 1)
                        #    print("frequency----->",frequency)
                        #    print("route_used----->",route_used)
                        SuspectDrug.append(value)
                        SuspectFrequency.append(frequency)
                        SuspectRoute.append(route_used)
                        for i, v in enumerate(dosage_info1):
                            # print(v)
                            SuspectDosage.append(v)

                    if index == 1:
                        SuspectDrugTwo = value + SuspectDrugName2
                        SuspectDosageTwo = DrugDosage[index] + DailyDoseContinue1
                        frequency = self.helper.extract_frequesncy_route_used(SuspectDosageTwo, 0)
                        route_used = self.helper.extract_frequesncy_route_used(SuspectDosageTwo, 1)
                        SuspectDrug.append(value)
                        SuspectFrequency.append(frequency)
                        SuspectRoute.append(route_used)
                        for i, v in enumerate(dosage_info2):
                            # print(v)
                            SuspectDosage.append(v)

                            # print("Drug----->",SuspectDrug)
            # print("Dosage---->",SuspectDosage)
            # print("SuspectFrequency----->",SuspectFrequency)
            # print("SuspectRoute---->",SuspectRoute)

            DiagnosisForUse = self.row.get('DiagnosisForUse', '')
            print("DiagnosisForUse", DiagnosisForUse)
            IndicationForUse = self.helper.extract_indication_data(DiagnosisForUse)
            print("IndicationForUse", IndicationForUse)
            # result_str = ''.join(char for char in input_str if not char.isdigit())

            dosage_length = len(DrugDosage)

            # if dosage_length >= 1 and dosage_length <= 2:
            #     print("yes")
            #     for index, value in enumerate(DrugDosage):
            #         print(f"Index: {index}, Value: {value}")
            #         if index == 0:
            #            SuspectDosageOne = value + DailyDoseContinue1
            #            SuspectDosage.append(SuspectDosageOne)

            #         if index == 1:
            #            SuspectDosageTwo = value + DailyDoseContinue2
            #            SuspectDosage.append(SuspectDosageTwo)

            TherapyDatesFromTo = self.row.get('TherapyDatesFromTo', '')
            print("TherapyDatesFromTo", TherapyDatesFromTo)

            # Split the string using '\n'
            split_result = TherapyDatesFromTo.split('\n')
            # Split each element using '-'
            split_result = list(map(lambda item: item.split('-'), split_result))

            # Iterate through the outer list
            for sublist in split_result:
                # Iterate through the inner list
                for item in sublist:
                    print(item.strip())  # Use strip() to remove leading and trailing whitespaces
                    # Replace '/' with '-'
                    modified_date = (item.strip()).replace('/', '-')
                    date_org = dateFormatCalculation().get_data(
                        self.item_indexing(modified_date, "TherapyDatesFromTo"), 1).split('_')
                    print(date_org)

            # SuspectDrug = self.helper.remove_junk_suspect_drug_irms(SuspectDrug.strip())
            # SuspectDrug = [st for st in (re.sub(drug_regex, drug_delimeter, SuspectDrug)).split(drug_delimeter) if
            #                len(st) > 0]

            # IndicationForUse = self.helper.remove_junk_suspect_indication_irms(self.row.get('INDICATION:').strip())
            # IndicationForUse = [st for st in
            #                     (re.sub(drug_regex, drug_delimeter, IndicationForUse)).split(drug_delimeter)
            #                     if
            #                     len(st) > 0]
            start_date = self.helper.remove_junk_suspect_start_date_irms(
                self.row.get('PRODUCT START DATE:', '').strip())
            start_date = [st for st in (re.sub(drug_regex, drug_delimeter, start_date)).split(drug_delimeter)
                          if
                          len(st) > 0]
            end_date = self.helper.remove_junk_suspect_end_date_irms(self.row.get('PRODUCT STOP DATE:', '').strip())
            end_date = [st for st in (re.sub(drug_regex, drug_delimeter, end_date)).split(drug_delimeter)
                        if
                        len(st) > 0]

            if len(IndicationForUse) > 0 and type(IndicationForUse) == list:
                for i, x in enumerate(IndicationForUse):
                    # print("x",x,"-----i--",i)
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    soup.find('drugcharacterization').string = str("1")

                    try:
                        if str(result_list[i]) != "":
                            soup.find('medicinalproduct').string = str(result_list[i])
                        else:
                            soup.find('medicinalproduct').string = str("unknown")
                    except Exception as e:
                        soup.find('medicinalproduct').string = str("unknown")
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    soup.find('drugauthorizationholder').string = str("NA")

                    try:
                        soup.find('drugstartdateformat').string = str("102")
                        soup.find('drugstartdate').string = str(
                            dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(start_date[i])))
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    try:
                        soup.find('drugenddateformat').string = str("102")
                        soup.find('drugenddate').string = str(
                            dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(end_date[i])))
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    try:
                        if str(result_list[i]) != "":
                            soup.find('activesubstancename').string = str(result_list[i])
                        else:
                            soup.find('activesubstancename').string = str("unknown")
                    except Exception as e:
                        soup.find('activesubstancename').string = str("unknown")
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        if self.get_medra_code(str(x), 'IndicationForUse', irms=1) != 0:
                            print(str(self.get_medra_code(str(x), 'IndicationForUse', irms=1)))
                            soup.find('drugindication').string = str(
                                self.get_medra_code(str(x), 'IndicationForUse', irms=1))
                    except Exception as e:
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        if str(SuspectDosage[i]) != "":
                            soup.find('drugdosagetext').string = str(SuspectDosage[i])
                        else:
                            soup.find('drugdosagetext').string = str("unknown")
                    except Exception as e:
                        soup.find('drugdosagetext').string = str("unknown")
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        if str(SuspectRoute[i]) != "":
                            soup.find('drugadministrationroute').string = str(SuspectRoute[i])
                        else:
                            soup.find('drugadministrationroute').string = str("unknown")
                    except Exception as e:
                        soup.find('drugadministrationroute').string = str("unknown")
                        self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    # soup.find('drugdosagetext').string = str(DailyDose)
                    # soup.find('drugadministrationroute').string = str(RouteOfAdministration)
                    #
                    final_tag.append(soup)
            else:
                print("else***************")
                print(str(result_list[0]))
                soup = BeautifulSoup(self.text, 'lxml-xml')
                soup.find('drugcharacterization').string = str("1")
                try:
                    if str(result_list[0]) != "":
                        soup.find('medicinalproduct').string = str(result_list[0])
                    else:
                        soup.find('medicinalproduct').string = str("unknown")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                try:
                    soup.find('drugstartdateformat').string = str("102")
                    # soup.find('drugstartdate').string = str(
                    #     dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(start_date)))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                soup.find('drugauthorizationholder').string = str("NA")
                try:
                    soup.find('drugenddateformat').string = str("102")
                    # soup.find('drugenddate').string = str(
                    #     dateFormatCalculation().get_date(self.helper.ambiguity_data_fix(end_date)))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if str(result_list[0]) != "":
                        soup.find('activesubstancename').string = str(result_list[0])
                    else:
                        soup.find('activesubstancename').string = str("unknown")
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if self.get_medra_code(str(IndicationForUse), 'IndicationForUse', irms=1) != 0:
                        soup.find('drugindication').string = str(
                            self.get_medra_code(str(IndicationForUse), 'IndicationForUse', irms=1))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if str(SuspectDosage[0]) != "":
                        soup.find('drugdosagetext').string = str(SuspectDosage[0])
                    else:
                        soup.find('drugdosagetext').string = str("unknown")
                except Exception as e:
                    soup.find('drugdosagetext').string = str("unknown")
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    if str(SuspectRoute[0]) != "":
                        soup.find('drugadministrationroute').string = str(SuspectRoute[0])
                    else:
                        soup.find('drugadministrationroute').string = str("unknown")
                except Exception as e:
                    soup.find('drugadministrationroute').string = str("unknown")
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                final_tag.append(soup)
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        result_con = self.get_irms_concomitant_drug_tag()
        if result_con != "":
            final_tag.append(result_con)

        return final_tag
