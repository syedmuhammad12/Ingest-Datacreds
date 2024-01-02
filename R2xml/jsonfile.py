import json
import logging
import pandas as pd
from . import configuration as con
import os
from bs4 import BeautifulSoup
import uuid
from .patientXmlElement import patientXmlElement
from .patientDeathXmlElement import patientDeathXmlElement
from .medicalHistoryXmlElement import medicalHistoryXmlElement
from .reactionXmlElement import reactionXmlElement
from .drugXmlElement import drugXmlElement
from .summaryXmlElement import summaryXmlElement
from .clientsDetails import clientsDetails
from .dataFormatCalculation import dateFormatCalculation
from .safetyReport import safetyReport
from .helper import helper
from .jsonkeys import jsonkey
from r2import import *
from datetime import datetime
from .seriousnessE2b import seriousnessE2b
import re

keys = jsonkey().thisdict


class R2XML:
    def __init__(self, json_file, sender, receiver):
        self.json_file = json_file

        self.sender = sender
        self.receiver = receiver
        path_check = self.path_check()
        self.helper = helper()
        if path_check == 1:
            try:
                self.irms()


            except Exception as e:
                self.error_log(e)

    # error log for entire project
    def error_log(self, message):
        logging.basicConfig(filename=con.logs_path + con.current_date + '.json',
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

    def irms(self):
        # first page data
        first_page = {d["key"]: d["value"] for d in self.json_file['first_page_data']}
        first_page['gender'] = first_page.pop('Gender')
        # second page data
        d = self.json_file
        data = ''
        df = {}

        key1 = 'PATIENT INFORMATION' if 'PATIENT INFORMATION' in d.keys() else 'Abstract'
        key2 = 'PREGNANCY INFORMATION (YES or NO):' if 'PREGNANCY INFORMATION (YES or NO):' in d.keys() else 'CONCOMITANT MEDICATIONS:'
        for key, value_html in d.items():
            if key1 in key:
                soup = BeautifulSoup(value_html, 'html.parser')
                td = soup.find_all('div')

                for t in td:
                    # print(t)
                    html = t.find_all(True, {"class": ['ocrx_word']})
                    for ht in html:
                        data += " " + (str(ht.text))
            elif key2 in key:
                soup = BeautifulSoup(value_html, 'html.parser')
                td = soup.find_all('div')

                for t in td:
                    # print(t)
                    html = t.find_all(True, {"class": ['ocrx_word']})
                    for ht in html:
                        data += " " + (str(ht.text))
        self.helper.remove_special_characters(data)
        # main data
        last = 'DESRCRIPTION OF THE ADVERSE EVENT:' if 'DESRCRIPTION OF THE ADVERSE EVENT:' in data else 'DESCRIPTION OF COURSE OF EVENTS:'
        lst = ['Case Information Client Data', 'template_name', 'Primary', 'Case Information',
               'Client Data', 'Abstract', 'PATIENT INFORMATION:',
               'DATE SALES REPRESENTATIVE INFORMED:', 'SUSPECT PRODUCT INFORMATION:',
               'DEATH INFORMATION', 'SERIOUSNESS CRITERIA', 'EVENT INFORMATION:',
               'PAST MEDICAL HISTORY:', 'ALLERGIES:', 'CONCOMITANT MEDICATIONS:',
               'PREGNANCY INFORMATION', last]
        outcome = 'OUTCOME (NOT RECOVERED/UNKNOWN/RECOVERING/RECOVERED):' if 'OUTCOME (NOT RECOVERED/UNKNOWN/RECOVERING/RECOVERED):' in data else 'OUTCOME(NOTRECOVERED/UNKNOWN/RECOVERING/RECOVERED):'
        weight = 'WEIGHT (POUNDS):' if 'WEIGHT (POUNDS):' in data else 'WEIGHT (Kg):'
        nes_keys = ['Gender:', 'DOB/AGE:', 'HEIGHT (INCHES):', weight, 'INDICATION:',
                    'PRODUCT START DATE:', 'PRODUCT STOP DATE:', 'DATE OF DEATH (If died):',
                    'AUTOPSY (YES/NO/UNKNOWN):', 'DATE OF AUTOPSY:', 'EVENT TERM:',
                    'START DATE OF EVENT:', 'STOP DATE OF EVENT:', outcome,
                    'DE-CHALLENGE (POSITIVE/NEGATIVE/UNKNOWN/NOT APPLICABLE):',
                    'RE-CHALLENGE (POSITIVE/NEGATIVE/UNKNOWN/NOT APPLICABLE):', 'CONCOMITANT NAME:',
                    'CONCOMITANT INDICATION:', 'CONCOMITANT DOSE/FREQUENCY:',
                    'CONCOMITANT START DATE:', 'CONCOMITANT STOP DATE:', 'GESTATION PERIOD:',
                    'PREGNANCY OUTCOME:', 'LAST MENSTRUAL PERIOD DATE:',
                    'EXPECTED DATE OF DELIVERY:', 'NUMBER OF CHILDREN (PRIOR TO PREGNANCY):']

        main = {}
        narrative = {}
        for i in range(len(lst)):
            start = lst[i]
            end = lst[(i + 1) % len(lst)]
            if start in data:
                # print(start,end)
                main[start] = (data.split(start))[1].split(end)[0].strip()
                narrative[start] = (data.split(start))[1].split(end)[0].strip()

        # child data
        inner = {}
        for i in range(len(nes_keys)):
            start = nes_keys[i]
            end = nes_keys[(i + 1) % len(nes_keys)]
            if start in data:
                inner[start] = (data.split(start))[1].split(end)[0].strip()

        if 'DOB/AGE:' in inner.keys():
            dob_age = inner['DOB/AGE:'].split('/')
            output_dict = {}
            if len(dob_age) > 2:
                output_dict.update(
                    {"DOB": str(dob_age[0] + "-" + dob_age[1] + "-" + dob_age[2]).strip(),
                    "AGE": dob_age[3].strip().replace("B.", "")})
            else:
                output_dict.update(
                    {"DOB": dob_age[0].strip(), "AGE": dob_age[1].strip().replace("B.", "")})
            inner.update(output_dict)
        df.update(main)
        df.update(inner)
        df.update(first_page)
        df.update({"data": data})
        df = self.remove_headers(df)

        df = pd.DataFrame(df, index=[0])
        df['template'] = d.get('template', 'IRMS')
        df['VendorName'] = "BAXTER\JnJ"
        df['FileName_1'] = "IRMS_"
        df['data'] = [narrative]
        for index, row in df.head().iterrows():
            self.row = row
            self.helper = helper(row)
            self.r2exml_mapping()
        print("irms to R2xml conversion successfull")

    def remove_headers(self, row):
        try:
            start_str = ["qinecsa", "bioclinica"]
            end_str = [" am", " pm"]
            for val in row:
                st_index = -1
                en_index = -1
                for start_index in start_str:
                    if row[val].lower().find(start_index) > -1:
                        st_index = row[val].lower().find(start_index)
                        break
                for end_index in end_str:
                    if row[val].lower().find(end_index) > -1:
                        en_index = row[val].lower().find(end_index)
                        break
                if st_index > -1 and en_index > -1:
                    temp = row[val]
                    row[val] = temp.replace(temp[st_index:en_index + 3], "")
        except Exception as e:
            self.error_log(e)

        return row



    # mapping process triggering
    def r2exml_mapping(self):
        row = self.row
        vendorname = con.default_code_template
        client = clientsDetails(row['VendorName'])
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

        patient_death = patientDeathXmlElement(con, row, code_template)
        patient_death_tag = patient_death.get_patient_death_tag()

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
        soup.find('messagesenderidentifier').string = self.sender
        soup.find('messagereceiveridentifier').string = self.receiver
        soup.find('messagedateformat').string = "204"
        # soup.find('messagedate').string = str(get_date.get_data(row['Date_Received_Manufacturer']))
        soup.find('safetyreportversion').string = str(safety_data.get_safety_version())
        soup.find('reporttype').string = str(safety_data.get_report_type())
        country_code = safety_data.get_safety_country()
        soup.find('primarysourcecountry').string = str(country_code)
        soup.find('occurcountry').string = str(country_code)
        soup.find('transmissiondateformat').string = "102"
        # soup.find('transmissiondate').string = str(get_date.get_data(row['Date_Received_Manufacturer'], 1))
        soup.find('receivedateformat').string = "102"

        recieved = str(get_date.get_data(row.get('Received', '').split(' ')[0].replace("/", "-"), 1))

        soup.find('receivedate').string = str(recieved)
        soup.find('receiptdateformat').string = "102"

        serious = 0
        soup.find('serious').string = str(serious)
        try:
            ser_text = self.helper.remove_junk_seriousness_criteria_irms(row['SERIOUSNESS CRITERIA'].replace(" ", ""))
            SERIOUSNESS_CRITERIA = 'NA'
            if ser_text.find('):') > -1:
                SERIOUSNESS_CRITERIA = str(ser_text[ser_text.find('):') + 2:])
            elif ser_text.find(':') > -1:
                SERIOUSNESS_CRITERIA = str(ser_text[ser_text.find(':') + 1:])

            if SERIOUSNESS_CRITERIA.strip() != "NA" and SERIOUSNESS_CRITERIA.strip() != "NA." and SERIOUSNESS_CRITERIA.strip() != "":

                result = seriousnessE2b(SERIOUSNESS_CRITERIA.strip()).get_seriousness_irms()
                if result == 1:
                    soup.find('seriousnessdeath').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnessdeath').string = str(2)

                if result == 2:
                    soup.find('seriousnesslifethreatening').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnesslifethreatening').string = str(2)

                if result == 3:
                    soup.find('seriousnesshospitalization').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnesshospitalization').string = str(2)

                if result == 4:
                    soup.find('seriousnessdisabling').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnessdisabling').string = str(2)

                if result == 5:
                    soup.find('seriousnesscongenitalanomali').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnesscongenitalanomali').string = str(2)

                if result == 6 or result == 0:
                    soup.find('seriousnessother').string = str(1)
                    serious = 1
                else:
                    soup.find('seriousnessother').string = str(2)
        except Exception as e:
            self.error_log(e)

        if serious == 1:
            soup.find('serious').string = str(serious)

        soup.find('receiptdate').string = str(recieved)
        soup.find('companynumb').string = self.sender + "_" + self.receiver + "_" + str(uuid.uuid1().int)[0:10]

        if self.helper.isNan('MFRControlNo') == 1:
            soup.find('duplicate').string = "1"
        if safety_data.get_reporter_country() != '':
            soup.find('reportercountry').string = str(safety_data.get_reporter_country())
        soup.find('senderorganization').string = self.sender
        soup.find('receiverorganization').string = self.receiver

        # soup.find('reportertitle').string = re.sub(r"[^\w\s]", "", str(row.get('Salutation', '')))
        # soup.find('reportergivename').string = str(row.get('Name', ''))
        # soup.find('mobilephone').string = re.sub(r"[^\w\s]", "", str(row.get('Mobile Phone', '')))
        # soup.find('e-mail').string = str(row.get('E-Mail', ''))
        #
        # address = str(row.get('Address', ''))
        # if len(address) > 1:
        #     search = re.search(r",(?=[^,]*$)", address)
        #     ind = search.start() if search else 0
        #     address = address[ind:]
        #
        # postcode = re.findall(r"\d{5,6}", address)
        # postcode = postcode[0] if len(postcode) > 1 else ""
        # state = re.findall(r'^(.*?)\d{5,6}', address)
        # state = state[0].lstrip(',') if len(state) > 1 else ""
        # country = re.findall(r'\b\d{5,6}(.*)$', address)
        # country = country[0] if len(country) > 1 else ""
        #
        # soup.find('reportercountry').string = country
        # soup.find('reporterstate').string = state
        # soup.find('reporterpostcode').string = postcode
        # soup.find('qualification').string = str(row.get('Degree', ''))

        soup.find('safetyreport').append(patient_tag)
        soup.find('patient').append(patient_death_tag)
        soup.find('patient').append(medicalHistory_tag)
        soup.find('patient').append(reaction_tag)
        soup.find('patient').append(drug_tag)
        soup.find('patient').append(summary_tag)
        # return

        for x in soup.find_all():
            if len(x.get_text(strip=True)) == 0:
                x.extract()

        f = open(con.r2xml_path + con.file_name_prefix + row['FileName_1'] + con.current_timestamp + '.xml', 'w',
                 encoding="utf8")
        f.write(str(soup))
        f.close()

# starts main class of R2XML process
# R2XML()
