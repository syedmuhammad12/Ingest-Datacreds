import shutil

import json
import logging
import pandas as pd
from . import configuration as con
import os
from bs4 import BeautifulSoup
import uuid
from .patientXmlElement import patientXmlElement
from .medicalHistoryXmlElement import medicalHistoryXmlElement
from .reactionXmlElement import reactionXmlElement
from .drugXmlElement import drugXmlElement
from .summaryXmlElement import summaryXmlElement
from .clientsDetails import clientsDetails
from .dataFormatCalculation import dateFormatCalculation
from .safetyReport import safetyReport
from .helper import helper
from .testXmlElement import testXmlElement
from .linelist_preprocess import Json
from .seriousnessE2b import seriousnessE2b
import datetime
from .patientDeathXmlElement import patientDeathXmlElement
from .patientDeathCauseXmlElement import patientDeathCauseXmlElement
from data_ingestion import settings
import boto3
from inspect import currentframe, getframeinfo

current_filename = str(getframeinfo(currentframe()).filename)


class R2XML_LINELIST:
    def __init__(self, data, tenant):
        self.data = data
        self.id_file = data['file_id']
        self.sender = self.data['sender']
        self.receiver = self.data['receiver']
        # self.customer_path = con.linelist_path + self.data['customer']
        self.customer_path = os.path.dirname(__file__) + '/linelist/' + tenant + '/' + str(
            self.id_file) + '/'
    
        s_3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
       
        target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION
        target_file_path = target_file_path + '/uploads/' + tenant + '/' + str(
            self.id_file) + "/1.xlsx"
        print("h")
        shutil.rmtree(self.customer_path, ignore_errors=True)
        print("he")
        if not os.path.exists(self.customer_path ):
            os.makedirs(self.customer_path)

        if not os.path.exists(self.customer_path + "r2xml/"):
            os.makedirs(self.customer_path + "r2xml/")
        print("hee")
        try:
            s_3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).download_file(target_file_path,
                                                                   self.customer_path + "/1.xlsx")
        except Exception as e:
            print(e)
            print(target_file_path)
            print(self.customer_path + "/1.xlsx")
            s_3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).download_file(target_file_path,
                                                                   self.customer_path + "/1.xlsx")
            
        print("heee")
        path_check = self.path_check()
        print("heeee")
        if path_check == 1:
            try:
                for root, dirs, files in os.walk(self.customer_path):
                    for file in files:
                        print(file)
                        self.line_list(file)
            except Exception as e:
                self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

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
        if not os.path.isdir(self.customer_path):
            path_dir.append(self.customer_path)
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

    # for linelist data
    def line_list(self, file):
        df = Json(self.customer_path + "/" + file).json_data()
        # print(df)
        # exit(1)
        for index, row in df.head(len(df)).iterrows():
            self.row = row
            self.row['template'] = 'linelist'
            self.row['VendorName'] = 'linelist'
            self.helper = helper(row)
            self.r2exml_mapping(index)
            # break
        print("linelist to R2xml conversion successfull")

    def get_time(self):
        return str(datetime.datetime.now().time().hour) + str(datetime.datetime.now().time().minute) + str(
            datetime.datetime.now().time().second)

    def get_date(self, key, header=0):
        result = key.replace('-', '')
        if header == 0:
            return result + self.get_time()
        else:
            return result

    # mapping process triggering
    def r2exml_mapping(self, index):
        row = self.row
        # print(row)
        # exit(1)
        client = clientsDetails(row['VendorName'])
        get_all_clients = client.get_all_clients()
        client_data = json.loads(client.get_client_details())
        code_template = con.default_code_template
        if row['VendorName'] in get_all_clients:
            code_template = row['VendorName']

        safety_data = safetyReport(row, code_template)

        get_date = dateFormatCalculation()
        patient = patientXmlElement(con, row, code_template)
        patient_tag = patient.get_patient_tag()

        patient_death = patientDeathXmlElement(con, row, code_template)
        patient_death_tag = patient_death.get_patient_death_tag()

        patient_death_cause = patientDeathCauseXmlElement(con, row, code_template)
        patient_death_cause_tag = patient_death_cause.get_patient_death_cause_tag()

        medicalHistory = medicalHistoryXmlElement(con, row, code_template)
        medicalHistory_tag = medicalHistory.get_medicalHistory_tag()
        #
        reaction = reactionXmlElement(con, row, code_template)
        reaction_tag = reaction.get_reaction_tag()
        #
        # test = testXmlElement(con, row, code_template)
        # test_tag = test.get_test_tag()

        drug = drugXmlElement(con, row, code_template)
        drug_tag = drug.get_drug_tag()

        summary = summaryXmlElement(con, row, code_template)
        summary_tag = summary.get_summary_tag()

        text = open(con.xml_template, "r", encoding="utf8").read()
        soup = BeautifulSoup(text, 'lxml-xml')
        soup.find('messagenumb').string = str(uuid.uuid1()) + '-BIO'
        soup.find('messagesenderidentifier').string = str(self.sender)
        soup.find('messagereceiveridentifier').string = str(self.receiver)
        try:

            soup.find('messagedate').string = str(self.get_date(row['Date_Received_Manufacturer']))
            soup.find('messagedateformat').string = "204"
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        if self.helper.isNan('safetyreportversion') == 1:
            soup.find('safetyreportversion').string = str(safety_data.get_safety_version())

        soup.find('reporttype').string = str('1')
        # country_code = safety_data.get_safety_country()
        # soup.find('primarysourcecountry').string = str(country_code)
        # soup.find('occurcountry').string = str(country_code)
        try:

            soup.find('transmissiondate').string = str(
                self.get_date(dateFormatCalculation().get_date(row['Date_Received_Manufacturer']), 1))
            soup.find('transmissiondateformat').string = "102"
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:

            soup.find('receivedate').string = dateFormatCalculation().get_date(row['receivedate'])
            soup.find('receivedateformat').string = "102"
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:

            soup.find('receiptdate').string = dateFormatCalculation().get_date(row['receiptdate'])
            soup.find('receiptdateformat').string = "102"
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            if self.helper.isNan('authority_number') == 1:
                soup.find('authoritynumb').string = str(row['authority_number'])
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        # if safety_data.get_reporter_country() != '':
        #     soup.find('reportercountry').string = str(safety_data.get_reporter_country())

        # if self.helper.isNan('StudyNo') == 1:
        #     soup.find('sponsorstudynumb').string = str(row['StudyNo'])
        soup.find('senderorganization').string = str(self.sender)
        soup.find('receiverorganization').string = str(self.receiver)
        serious = 2
        soup.find('serious').string = str(serious)
        try:
            SERIOUSNESS_CRITERIA = row['seriousness_criteria']

            if SERIOUSNESS_CRITERIA.strip() != "NA" and SERIOUSNESS_CRITERIA.strip() != "NA." and SERIOUSNESS_CRITERIA.strip() != "":

                result = seriousnessE2b(SERIOUSNESS_CRITERIA.strip()).get_seriousness_linelist()
                if 1 in result:
                    soup.find('seriousnessdeath').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnessdeath').string = str(2)

                if 2 in result:
                    soup.find('seriousnesslifethreatening').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnesslifethreatening').string = str(2)

                if 3 in result:
                    soup.find('seriousnesshospitalization').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnesshospitalization').string = str(2)

                if 4 in result:
                    soup.find('seriousnessdisabling').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnessdisabling').string = str(2)

                if 5 in result:
                    soup.find('seriousnesscongenitalanomali').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnesscongenitalanomali').string = str(2)

                if 6 in result:
                    soup.find('seriousnessother').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnessother').string = str(2)
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            Event_Death = row['Event_Death']
            Life_Threatening = row['Life_Threatening']
            Other_Medically_Imp_Condition = row['Other_Medically_Imp_Condition']
            Congenital_anomaly = row['Congenital_anomaly']
            Hospitalization_Required = row['Hospitalization_Required']

            if Event_Death.lower().find("y") > -1:
                soup.find('seriousnessdeath').string = str(1)
                serious = 1
            else:
                soup.find('seriousnessdeath').string = str(2)

            if Life_Threatening.lower().find("y") > -1:
                soup.find('seriousnesslifethreatening').string = str(1)
                serious = 1
            else:
                soup.find('seriousnesslifethreatening').string = str(2)

            if Hospitalization_Required.lower().find("y") > -1:
                soup.find('seriousnesshospitalization').string = str(1)
                serious = 1
            else:
                soup.find('seriousnesshospitalization').string = str(2)

            if Congenital_anomaly.lower().find("y") > -1:
                soup.find('seriousnesscongenitalanomali').string = str(1)
                serious = 1
            else:
                soup.find('seriousnesscongenitalanomali').string = str(2)

            if Other_Medically_Imp_Condition.lower().find("y") > -1:
                soup.find('seriousnessother').string = str(1)
                serious = 1
            else:
                soup.find('seriousnessother').string = str(2)
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        if serious == 1:
            soup.find('serious').string = str(serious)

        soup.find('safetyreport').append(patient_tag)
        soup.find('patient').append(patient_death_tag)
        soup.find('patient').append(patient_death_cause_tag)
        soup.find('patient').append(medicalHistory_tag)
        soup.find('patient').append(reaction_tag)
        # soup.find('patient').append(test_tag)
        soup.find('patient').append(drug_tag)
        soup.find('patient').append(summary_tag)
        for x in soup.find_all():
            if len(x.get_text(strip=True)) == 0:
                x.extract()

        current_timestamp = "_" + str(index) + "_" + str(int(datetime.datetime.now().timestamp()))
        f = open(self.customer_path + "r2xml/" + con.file_name_prefix + current_timestamp + '.xml', 'w',
                 encoding="utf8")
        f.write(str(soup))
        f.close()
