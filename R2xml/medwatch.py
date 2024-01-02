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
from .json_preprocess import Json
from spellchecker import SpellChecker
from .reporterAddress import reporterAddress


class R2XML_MEDWATCH:
    def __init__(self, json_file, sender, receiver):
        self.json_file = json_file

        self.sender = sender
        self.receiver = receiver
        path_check = self.path_check()
        self.helper = helper()
        if path_check == 1:
            try:
                self.medwatch()

            except Exception as e:
                self.error_log(e)

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

    # for medwatch data
    def medwatch(self):
        df = Json(self.json_file).medwatch_json_data()
        for index, row in df.head().iterrows():
            self.row = row
            self.helper = helper(row)
            self.r2exml_medwatch_mapping()
        print("medwatch to R2xml conversion successfull")

    # mapping process triggering
    def r2exml_mapping(self):
        row = self.row
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

        medicalHistory = medicalHistoryXmlElement(con, row, code_template)
        medicalHistory_tag = medicalHistory.get_medicalHistory_tag()

        reaction = reactionXmlElement(con, row, code_template)
        reaction_tag = reaction.get_reaction_tag()

        drug = drugXmlElement(con, row, code_template)
        drug_tag = drug.get_drug_tag()

        summary = summaryXmlElement(con, row, code_template)
        summary_tag = summary.get_summary_tag()

        text = open(con.xml_template, "r", encoding="utf8").read()
        soup = BeautifulSoup(text, 'lxml-xml')
        soup.find('messagenumb').string = str(uuid.uuid1()) + '-BIO'
        soup.find('messagesenderidentifier').string = str(self.sender)
        soup.find('messagereceiveridentifier').string = str(self.receiver)
        soup.find('messagedateformat').string = "204"
        soup.find('messagedate').string = str(get_date.get_data(row['Date_Received_Manufacturer']))
        soup.find('safetyreportversion').string = str(safety_data.get_safety_version())
        soup.find('reporttype').string = str(safety_data.get_report_type())
        country_code = safety_data.get_safety_country()
        soup.find('primarysourcecountry').string = str(country_code)
        soup.find('occurcountry').string = str(country_code)
        soup.find('transmissiondateformat').string = "102"
        soup.find('transmissiondate').string = str(get_date.get_data(row['Date_Received_Manufacturer'], 1))
        soup.find('receivedateformat').string = "102"
        soup.find('receivedate').string = get_date.get_data(row['Date_Received_Manufacturer'], 1)
        soup.find('receiptdateformat').string = "102"
        soup.find('receiptdate').string = get_date.get_data(row['Date_Received_Manufacturer'], 1)
        if self.helper.isNan('MFRControlNo') == 1:
            soup.find('duplicate').string = "1"
            soup.find('duplicatenumb').string = str(row['MFRControlNo'])
        if safety_data.get_reporter_country() != '':
            soup.find('reportercountry').string = str(safety_data.get_reporter_country())
        if self.helper.isNan('StudyNo') == 1:
            soup.find('sponsorstudynumb').string = str(row['StudyNo'])
        soup.find('senderorganization').string = self.sender
        soup.find('receiverorganization').string = self.receiver

        soup.find('safetyreport').append(patient_tag)
        soup.find('patient').append(medicalHistory_tag)
        soup.find('patient').append(reaction_tag)
        soup.find('patient').append(drug_tag)
        soup.find('patient').append(summary_tag)

        

        for x in soup.find_all():
            # print(x)
            if len(x.get_text(strip=True)) == 0:
                x.extract()
        f = open(con.r2xml_path + con.file_name_prefix + row['FileName_1'] + con.current_timestamp + '.xml', 'w',
                 encoding="utf8")
        f.write(str(soup))
        f.close()


# mapping process triggering
    def r2exml_medwatch_mapping(self):
        print('in function')
        row = self.row
        client = clientsDetails(row['VendorName'])
        
        get_all_clients = client.get_all_clients()
        client_data = json.loads(client.get_client_details())
        code_template = con.default_medwatch_code_template
        if row['VendorName'] in get_all_clients:
            code_template = row['VendorName']
        # print(code_template)
        safety_data = safetyReport(row, code_template)
        
        get_date = dateFormatCalculation()
        # print(row)
        patient = patientXmlElement(con, row, code_template) 
        patient_tag = patient.get_patient_tag()
        # print(patient_tag)

        medicalHistory = medicalHistoryXmlElement(con, row, code_template)
        medicalHistory_tag = medicalHistory.get_medicalHistory_tag()

        reaction = reactionXmlElement(con, row, code_template)
        reaction_tag = reaction.get_reaction_tag()

        drug = drugXmlElement(con, row, code_template)
        drug_tag = drug.get_drug_tag()

        summary = summaryXmlElement(con, row, code_template)
        summary_tag = summary.get_summary_tag()
        # print(summary_tag)
        
        # print(row['Date_This_Report'])
        # print(row['PatientDied'])
        # return
        # print(str(dateFormatCalculation().date_format_change(str(row['Date_This_Report']))))
        # return
        text = open(con.xml_template, "r", encoding="utf8").read()
        soup = BeautifulSoup(text, 'lxml-xml')
        soup.find('messagenumb').string = str(uuid.uuid1()) + '-BIO'
        soup.find('messagesenderidentifier').string = str(self.sender)
        soup.find('messagereceiveridentifier').string = str(self.receiver)
        soup.find('messagedateformat').string = "204"
        try:
            soup.find('messagedate').string = str(dateFormatCalculation().date_format_change(str(row['Date_This_Report'])))
        except Exception as e:
            self.error_log(e)
        soup.find('companynumb').string = self.sender+"_"+self.receiver+"_"+str(uuid.uuid1().int)[0:10]
        soup.find('safetyreportversion').string = str(safety_data.get_safety_version())
        soup.find('reporttype').string = str(safety_data.get_report_type())
        # print("888")
        soup.find('serious').string = str(safety_data.get_med_serious_tag())
        # return
        soup.find('seriousnessdeath').string=str(safety_data.get_med_serious_death())
        soup.find('seriousnesslifethreatening').string=str(safety_data.get_med_serious_life_threatening())
        soup.find('seriousnesshospitalization').string=str(safety_data.get_med_serious_hospitalization())
        soup.find('seriousnessdisabling').string=str(safety_data.get_med_serious_disability())
        soup.find('seriousnesscongenitalanomali').string=str(safety_data.get_med_serious_congenitalanomali())
        soup.find('seriousnessother').string=str(safety_data.get_med_serious_other())
        country_code = safety_data.get_safety_country()
        soup.find('primarysourcecountry').string = str(country_code)
        soup.find('occurcountry').string = str(country_code)
        soup.find('transmissiondateformat').string = "102"
        try:
            soup.find('transmissiondate').string = str(dateFormatCalculation().date_format_change(str(row['Date_This_Report'])))
        except Exception as e:
            self.error_log(e)
        soup.find('receivedateformat').string = "102"
        try:
            soup.find('receivedate').string = str(dateFormatCalculation().date_format_change(str(row['Date_This_Report'])))
        except Exception as e:
            self.error_log(e)
        soup.find('receiptdateformat').string = "102"
        try:
            soup.find('receiptdate').string = str(dateFormatCalculation().date_format_change(str(row['Date_This_Report'])))
        except Exception as e:
            self.error_log(e)
        if self.helper.isNan('MFRControlNo') == 1:
            soup.find('duplicate').string = "1"
            soup.find('duplicatenumb').string = str(row['MFRControlNo'])
        if safety_data.get_reporter_country() != '':
            soup.find('reportercountry').string = str(safety_data.get_reporter_country())
        if self.helper.isNan('StudyNo') == 1:
            soup.find('sponsorstudynumb').string = str(row['StudyNo'])
        soup.find('senderorganization').string = self.sender
        soup.find('receiverorganization').string = self.receiver
        # print("before tags")
        # return
        soup.find('safetyreport').append(patient_tag)
        soup.find('patient').append(medicalHistory_tag)
        soup.find('patient').append(reaction_tag)
        soup.find('patient').append(drug_tag)
        soup.find('patient').append(summary_tag)

        try:
            address = str(row.get('ReporterInformation',''))
            # print(address)
            if len(address)>0:
                address = reporterAddress(address).get_address_split()
                soup.find('reportercountry').string = str(address.get('country_code',''))
                soup.find('reporterstreet').string = str(address.get('text',''))
                soup.find('reporterpostcode').string = str(address.get('postal_code',''))    
        except Exception as e:
            self.error_log(e)

        # print("tt")
        # return

        for x in soup.find_all():
            # print(x)
            if len(x.get_text(strip=True)) == 0:
                x.extract()
        f = open(con.r2xml_path + con.file_name_prefix + row['FileName_1'] + con.current_timestamp + '.xml', 'w',
                 encoding="utf8")
        f.write(str(soup))
        f.close()

# starts main class of R2XML process
# R2XML()
