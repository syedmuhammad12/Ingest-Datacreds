import json
import datetime
import logging
import random
import string
import pandas as pd
from . import configuration as con
import os
from bs4 import BeautifulSoup
import uuid
# from ner_management.models import XMLSenderReceiver
# from product.models import SerchString, Country as CountryModel
# from configuration.models import Config
from .patientXmlElement import patientXmlElement
# from .patientPastDrugXmlElement import patientPastDrugXmlElement
from .patientDeathXmlElement import patientDeathXmlElement
from .patientDeathCauseXmlElement import patientDeathCauseXmlElement
# from .parentXmlElement import parentXmlElement
from .medicalHistoryXmlElement import medicalHistoryXmlElement
from .reactionXmlElement import reactionXmlElement
from .testXmlElement import testXmlElement
from .drugXmlElement import drugXmlElement
from .summaryXmlElement import summaryXmlElement
from .clientsDetails import clientsDetails
from .dataFormatCalculation import dateFormatCalculation
from .safetyReport import safetyReport
from .helper import helper
from .country import country
from .litraturekeys import jsonkey

keys = jsonkey().thisdict


class R2XML_LITRATURE:
    def __init__(self, json_file, relation_json, customer_db="default", sender="", receiver="", xml_type="R2"):
        self.customer_db = customer_db
        self.error_message = ""
        self.json_file = json_file
        self.relation_json = relation_json

        self.r2_filename = ""
        self.xml_type = xml_type
        self.sender = sender
        self.receiver = receiver
        if sender != "" or receiver != "":
            path_check = self.path_check()
            if path_check == 1:
                try:
                    f = {}
                    df = pd.json_normalize(json_file, errors='raise')
                    for search in df["key"].values:
                        for key, value in keys.items():
                            if search in value:
                                f[key] = df["value"].iloc[(df[df["key"] == search].index)[0]]

                    df = pd.DataFrame([f], columns=f.keys())
                    df['senderorganization'] = self.sender
                    df['receiverorganization'] = self.receiver
                    # df['VendorName']="BAXTER\JnJ"
                    df['FileName_1'] = "XML"
                    cmf = self.check_mandatory_fields(df, customer_db)

                    if len(cmf['missed']) >= 0:
                        for index, row in df.head().iterrows():
                            self.row = row
                            self.helper = helper(row)
                            self.error_message = self.r2exml_mapping()
                    else:
                        self.error_message = "r2_min_fields_missed"
                except Exception as e:
                    self.error_log(e)
                    self.error_message = "r2_creation_failed"
        else:
            self.error_message = "r2_creation_failed"

    # error log for entire project
    def error_log(self, message):
        logging.basicConfig(filename=con.logs_path + con.current_date + '.txt',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%d-%m-%Y %H:%M:%S',
                            level=logging.DEBUG, force=True)
        logging.error(message)

        self.logger = logging.getLogger('urbanGUI')

    # checking for all mandatory files
    def path_check(self):
        path_dir = []
        if not os.path.isdir(con.csv_path):
            path_dir.append(con.csv_path)
        if not os.path.exists(con.clients_path):
            path_dir.append(con.clients_path)
        if not os.path.exists(con.r2xml_path):
            os.makedirs(con.r2xml_path)
        if not path_dir:
            return 1
        else:
            result = {'content': path_dir, 'status': 'False'}
            self.error_log(result)
            print("check logs for errors")
            exit(0)

    def process_list_values(self, data):
        try:
            return ", ".join(str(v) for v in eval(str(data)))
        except Exception as e:
            return data

    # def get_sender_receiver(self, id):
    #     data = XMLSenderReceiver.objects.using(self.customer_db).filter(sr_id=id)
    #     if len(data) > 0:
    #         return data[0]
    #     else:
    #         return ""

    # mapping process triggering
    def r2exml_mapping(self):
        row = self.row
        row['relations'] = self.relation_json
        row['template'] = 'litrature'
        vendorname = con.default_code_template
        # client = clientsDetails(row['VendorName'])
        client = clientsDetails(vendorname)
        get_all_clients = client.get_all_clients()
        client_data = json.loads(client.get_client_details())
        code_template = con.default_code_template
        if vendorname in get_all_clients:
            code_template = vendorname

        safety_data = safetyReport(row, code_template)
        get_date = dateFormatCalculation()
        patient = patientXmlElement(con, row, code_template)
        patient_tag = patient.get_patient_tag()

        # parent = parentXmlElement(con, row, code_template)
        # parent_tag = parent.get_parent_tag()

        medicalHistory = medicalHistoryXmlElement(con, row, code_template)
        medicalHistory_tag = medicalHistory.get_medicalHistory_tag()

        # patientPastDrug = patientPastDrugXmlElement(con, row, code_template, self.customer_db)
        # patientPastDrug_tag = patientPastDrug.get_patient_past_drug_tag()

        patientDeath = patientDeathXmlElement(con, row, code_template)
        patientDeath_tag = patientDeath.get_patient_death_tag()

        patient_death_cause = patientDeathCauseXmlElement(con, row, code_template)
        patient_death_cause_tag = patient_death_cause.get_patient_death_cause_tag()

        reaction = reactionXmlElement(con, row, code_template)
        reaction_tag = reaction.get_reaction_tag()

        test = testXmlElement(con, row, code_template)
        test_tag = test.get_test_tag()

        drug = drugXmlElement(con, row, code_template)
        drug_tag = drug.get_drug_tag()

        summary = summaryXmlElement(con, row, code_template)
        summary_tag = summary.get_summary_tag()

        if self.xml_type == "R3":
            text = open(con.xml_r3_template, "r", encoding="utf8").read()
        else:
            text = open(con.xml_template, "r", encoding="utf8").read()

        soup = BeautifulSoup(text, 'lxml-xml')

        soup.find('messagenumb').string = str(uuid.uuid1()) + '-BIO'
        # soup.find('messagesenderidentifier').string = str(client_data['sender'])
        # soup.find('messagereceiveridentifier').string = str(client_data['receiver'])
        soup.find('messagesenderidentifier').string = str(row['senderorganization'])
        soup.find('messagereceiveridentifier').string = str(row['receiverorganization'])
        soup.find('messagedateformat').string = "204"
        # soup.find('messagedate').string = str(get_date.get_data(row['Date_Received_Manufacturer']))
        soup.find('safetyreportversion').string = str(safety_data.get_safety_version())
        soup.find('safetyreportid').string = str(row['safetyreportid']) if 'safetyreportid' in row else ""
        soup.find('reporttype').string = str(safety_data.get_report_type())
        country_code = safety_data.get_safety_country()
        soup.find('primarysourcecountry').string = str(country_code)
        country_code = safety_data.get_safety_cccur_country()
        soup.find('occurcountry').string = str(country_code)
        soup.find('transmissiondateformat').string = "102"
        # soup.find('transmissiondate').string = str(get_date.get_data(row['Date_Received_Manufacturer'], 1))
        soup.find('receivedateformat').string = "102"
        soup.find('receivedate').string = get_date.get_data(row['receivedate'], 1)
        soup.find('receiptdateformat').string = "102"
        soup.find('receiptdate').string = get_date.get_data(row['receiptdate'], 1)
        soup.find('companynumb').string = str(row['companynumb']) if 'companynumb' in row else ""
        if self.helper.isNan('MFRControlNo') == 1:
            soup.find('duplicate').string = "1"
            # soup.find('duplicatenumb').string = str(row['MFRControlNo'])
        if safety_data.get_reporter_country() != '':
            soup.find('reportercountry').string = str(safety_data.get_reporter_country())
        # if self.helper.isNan('StudyNo') == 1:
        # soup.find('sponsorstudynumb').string = str(row['StudyNo'])
        soup.find('senderorganization').string = row['senderorganization']
        soup.find('receiverorganization').string = row['receiverorganization']

        ser_case = "2"
        if 'seriousnessdeath' in row:
            ser_case = "1"
        if 'seriousnesslifethreatening' in row:
            ser_case = "1"
        if 'seriousnesshospitalization' in row:
            ser_case = "1"
        if 'seriousnessdisabling' in row:
            ser_case = "1"
        if 'seriousnesscongenitalanomali' in row:
            ser_case = "1"
        if 'seriousnessother' in row:
            ser_case = "1"
        soup.find('serious').string = str(ser_case)
        soup.find('seriousnessdeath').string = str("1") if 'seriousnessdeath' in row else "2"
        soup.find('seriousnesslifethreatening').string = str("1") if 'seriousnesslifethreatening' in row else "2"
        soup.find('seriousnesshospitalization').string = str("1") if 'seriousnesshospitalization' in row else "2"
        soup.find('seriousnessdisabling').string = str("1") if 'seriousnessdisabling' in row else "2"
        soup.find('seriousnesscongenitalanomali').string = str("1") if 'seriousnesscongenitalanomali' in row else "2"
        soup.find('seriousnessother').string = str("1") if 'seriousnessother' in row else "2"

        soup.find('reportertitle').string = str(
            self.process_list_values(row['reportertitle'])) if 'reportertitle' in row else ""
        soup.find('reportergivename').string = str(
            self.process_list_values(row['reportergivename'])) if 'reportergivename' in row else ""
        soup.find('reportermiddlename').string = str(
            self.process_list_values(row['reportermiddlename'])) if 'reportermiddlename' in row else ""
        soup.find('reporterfamilyname').string = str(
            self.process_list_values(row['reporterfamilyname'])) if 'reporterfamilyname' in row else ""
        soup.find('reporterorganization').string = self.process_list_values(
            str(row['reporterorganization'])) if 'reporterorganization' in row else ""
        soup.find('reporterdepartment').string = str(
            self.process_list_values(row['reporterdepartment'])) if 'reporterdepartment' in row else ""
        soup.find('reporterstreet').string = str(
            self.process_list_values(row['reporterstreet'])) if 'reporterstreet' in row else ""
        soup.find('reportercity').string = str(
            self.process_list_values(row['reportercity'])) if 'reportercity' in row else ""
        soup.find('reporterstate').string = str(
            self.process_list_values(row['reporterstate'])) if 'reporterstate' in row else ""
        soup.find('reporterpostcode').string = self.process_list_values(
            str(row['reporterpostcode'])) if 'reporterpostcode' in row else ""
        soup.find('qualification').string = str(row['qualification']) if 'qualification' in row else ""
        soup.find('literaturereference').string = str(
            self.process_list_values(row['literaturereference'])) if 'literaturereference' in row else ""
        soup.find('studyname').string = self.process_list_values(str(row['studyname'])) if 'studyname' in row else ""
        soup.find('sponsorstudynumb').string = str(
            self.process_list_values(row['sponsorstudynumb'])) if 'sponsorstudynumb' in row else ""
        soup.find('observestudytype').string = str(
            self.process_list_values(row['observestudytype'])) if 'observestudytype' in row else ""

        soup.find('safetyreport').append(patient_tag)

        # soup.find('patient').append(parent_tag)
        soup.find('patient').append(medicalHistory_tag)

        # soup.find('patient').append(patientPastDrug_tag)
        soup.find('patient').append(patientDeath_tag)

        soup.find('patient').append(patient_death_cause_tag)

        soup.find('patient').append(reaction_tag)

        soup.find('patient').append(test_tag)

        soup.find('patient').append(drug_tag)
        soup.find('patient').append(summary_tag)

        for x in soup.find_all():
            if len(x.get_text(strip=True)) == 0:
                x.extract()
        file_name = "{}{}{}.xml".format(con.file_name_prefix, row['FileName_1'],
                                        str(int(datetime.datetime.now().timestamp())))
        file_path = "{}{}".format(con.r2xml_path, file_name)
        f = open(file_path, 'w', encoding="utf8")
        f.write(str(soup))
        f.close()
        self.r2_filename = file_name
        return "r2_created"

    def check_mandatory_fields(self, data_frame, customer_db="default"):
        # print(data_frame["primarysourcecountry"][0])
        # print(type(data_frame["primarysourcecountry"][0]))

        missed = []
        fields = [str(k).lower() for k in list(data_frame.columns.values.tolist())]
        if 'primarysourcecountry' in fields:
            if type(data_frame['primarysourcecountry'].values[0]) == list:
                data_frame['primarysourcecountry'].values[0] = data_frame['primarysourcecountry'].values[0][0]

        if 'reportercountry' in fields:
            if type(data_frame['reportercountry'].values[0]) == list:
                data_frame['reportercountry'].values[0] = data_frame['reportercountry'].values[0][0]

        if 'occurcountry' in fields:
            if type(data_frame['occurcountry'].values[0]) == list:
                data_frame['occurcountry'].values[0] = data_frame['occurcountry'].values[0][0]


        if 'reporttype' not in fields:
            data_frame['reporttype'] = 1

        if 'reportertitle' not in fields:
            data_frame['reportertitle'] = "Dr"

        if 'reportercountry' not in fields:
            if 'primarysourcecountry' not in fields:
                data_frame['reportercountry'] = "United Kingdom"
                data_frame['primarysourcecountry'] = "United Kingdom"
                data_frame['occurcountry'] = "United Kingdom"
            else:
                if 'primarysourcecountry' in fields:
                    data_frame['reportercountry'] = data_frame['primarysourcecountry']
                    if 'occurcountry' not in fields:
                        data_frame['occurcountry'] = data_frame['primarysourcecountry']

        if 'occurcountry' not in fields:
            if 'primarysourcecountry' in fields:
                data_frame['occurcountry'] = data_frame['primarysourcecountry']

        if 'receivedate' not in fields:
            data_frame['receivedate'] = datetime.date.today().strftime("%d-%m-%Y")

        if 'receiptdate' not in fields:
            data_frame['receiptdate'] = datetime.date.today().strftime("%d-%m-%Y")

        if 'patientinitial' not in fields:
            data_frame['patientinitial'] = str("unknown")

        if 'authoritynumb' not in fields:
            if 'companynumb' not in fields:
                if 'reportercountry' not in fields:
                    if 'primarysourcecountry' not in fields:
                        data = country("United Kingdom")
                    else:
                        data = country(str(data_frame['primarysourcecountry'].values[0]).replace(".", ""))
                else:

                    data = country(str(data_frame['reportercountry'].values[0]).replace(".", ""))

                result = str(data.get_country_code())

                data_frame['companynumb'] = data_frame['senderorganization'] + "-" + result + "-" + str(
                    uuid.uuid1().int)[0:10]
                data_frame['safetyreportid'] = data_frame['senderorganization'] + "-" + result + "-" + str(
                    uuid.uuid1().int)[0:10]

        if 'senderorganization' not in fields:
            missed.append('senderorganization')

        if 'receiverorganization' not in fields:
            missed.append('receiverorganization')

        if 'patientinitial' not in fields:
            if 'patientbirthdate' not in fields:
                if 'patientonsetage' not in fields:
                    if 'patientsex' not in fields:
                        missed.append('patientinitial or patientbirthdateformat or patientonsetage or patientsex')

        if 'primarysourcereaction' not in fields:
            missed.append('primarysourcereaction')

        if 'suspectproduct' not in fields:
            if 'concomitantproduct' not in fields:
                missed.append('suspectproduct and concomitantproduct')
        else:
            susTest = 0
            susPro = self.process_list_values(str(data_frame['suspectproduct']))
            # try:
            #     if 'primarysourcecountry' in fields:
            #         for sp in susPro:
            #             products = SerchString.objects.using(customer_db).filter(product_name=sp)
            #             if len(products) > 0:
            #                 for prd in products:
            #                     prd_cntry = CountryModel.objects.using(customer_db).filter(country_id=prd['country_id'])
            #                     if len(prd_cntry) > 0:
            #                         for c in prd_cntry:
            #                             data = country(
            #                                 str(data_frame['primarysourcecountry'].values[0]).replace(".", ""))
            #                             if data.get_country_code() == c['country_code']:
            #                                 susTest = + 1
            #                             else:
            #                                 config_data = Config.objects.using(customer_db).filter(
            #                                     config_key="default_icsr_country")
            #                                 if len(config_data) > 0:
            #                                     for cnf in config_data:
            #                                         cntrs = [cn['code'] for cn in json.loads(cnf['config_value'])]
            #                                         if data.get_country_code() in cntrs:
            #                                             susTest = + 1
            # except Exception as e:
            #     missed.append(str(e))
            # if susTest != len(susPro):
            #     missed.append('suspectproduct country')

        if 'narrativeincludeclinical' not in fields:
            data_frame['narrativeincludeclinical'] = "narrative"

        return {'missed': missed, 'data_frame': data_frame}
