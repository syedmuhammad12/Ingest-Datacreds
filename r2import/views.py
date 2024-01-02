from bs4 import BeautifulSoup
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
# from authorization.views import VerifyTenant
from r2import.helper import helper
import r2import.configuration as con
import logging
import json
from inspect import currentframe, getframeinfo
# from r2import.general import general

current_filename = str(getframeinfo(currentframe()).filename)
logging.basicConfig(level=logging.DEBUG)


class R2XML_IMPORT:
    """r2xml class"""

    def __init__(self,file):
        """r2xml import class constructor"""
        self.file = file
        self.xmlfilename = file.split('\\')[-1]
        self.xmlfilepath = file
        self.soup = BeautifulSoup(open(file),'lxml-xml')
        # self.tenant = VerifyTenant(self.request.META['HTTP_TENANT_CODE']).GetTenant()
        self.tenant = 'simplesafety'
        self.tenant_prefix = self.tenant
        # self.current_user = self.request.data.get('id')
        
        self.current_file_name = self.file.split('\\')[-1]+'_log'
        self.helper = helper(self.tenant, None, self.current_file_name)

    def duplicate_check(self, r2xml_dict):
        result = None
        helper_dict = helper(self.tenant, r2xml_dict, self.current_file_name)
        try:

            duplicate_config = Config.objects.using(self.tenant).get(
                config_key="duplicate_search_fields_json"
            )

            json_data = json.loads(duplicate_config.config_value)
            duplicate_list = []
            for value_index in json_data:

                for value in json_data[str(value_index)]:
                    arr_data = json_data[str(value_index)][value]['field_name'].split('__')
                    codelist_id = json_data[str(value_index)][value]['codelist_id']
                    field_type = json_data[str(value_index)][value]['field_type']
                    if isinstance(helper_dict.r2_mapping_data(arr_data[0] + "_" + arr_data[1]), list):
                        list_data = helper_dict.r2_mapping_data(arr_data[0] + "_" + arr_data[1])
                        for list_value in list_data:
                            duplicate_values = helper_dict.duplicate_values(arr_data[0], arr_data[1],
                                                                            list_value,
                                                                            codelist_id, field_type)

                            if duplicate_values['data'] is not None:
                                duplicate_list.append(duplicate_values['data'])
                    else:

                        duplicate_values = helper_dict.duplicate_values(arr_data[0], arr_data[1],
                                                                        helper_dict.r2_mapping_data(
                                                                            arr_data[0] + "_" + arr_data[1]),
                                                                        codelist_id, field_type)
                        if duplicate_values['data'] is not None:
                            duplicate_list.append(duplicate_values['data'])
                if duplicate_list:
                    result = duplicate_list
            return result
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

    def mandatory_fields_check(self, r2xml_dict):
        """r2xml import mandatory fields check function"""
        helper_dict = helper(self.tenant, r2xml_dict, self.current_file_name)
        is_valid = 1
        r2xml_mandatory = {}
        r2xml_mandatory_missing = []

        if r2xml_dict:
            if helper_dict.check_data_exist('reporttype'):
                r2xml_mandatory['reporttype'] = helper_dict.check_data_exist('reporttype')
            else:
                is_valid = 0
                r2xml_mandatory_missing.append('reporttype')
            
            if helper_dict.check_data_exist('receivedateformat') and helper_dict.check_data_exist('receivedate'):
                r2xml_mandatory['receivedateformat'] = helper_dict.check_data_exist('receivedateformat')
                r2xml_mandatory['receivedate'] = helper_dict.check_data_exist('receivedate')
            else:
                is_valid = 0
                r2xml_mandatory_missing.append('receivedateformat')
                r2xml_mandatory_missing.append('receivedate')
           
            if helper_dict.check_data_exist('receiptdateformat') and helper_dict.check_data_exist('receiptdate'):
                r2xml_mandatory['receiptdateformat'] = helper_dict.check_data_exist('receiptdateformat')
                r2xml_mandatory['receiptdate'] = helper_dict.check_data_exist('receiptdate')
            else:
                is_valid = 0
                r2xml_mandatory_missing.append('receiptdateformat')
                r2xml_mandatory_missing.append('receiptdate')

            if helper_dict.check_data_exist('authoritynumb'):
                r2xml_mandatory['authoritynumb'] = helper_dict.check_data_exist('authoritynumb')
            elif helper_dict.check_data_exist('companynumb'):
                r2xml_mandatory['companynumb'] = helper_dict.check_data_exist('companynumb')
            else:
                is_valid = 0
                r2xml_mandatory_missing.append('authoritynumb or companynumb')

            if helper_dict.check_data_exist('senderorganization'):
                r2xml_mandatory['senderorganization'] = helper_dict.check_data_exist('senderorganization')
            else:
                is_valid = 0
                r2xml_mandatory_missing.append('senderorganization')
            
            if helper_dict.check_data_exist('receiverorganization'):
                r2xml_mandatory['receiverorganization'] = helper_dict.check_data_exist('receiverorganization')
            else:
                is_valid = 0
                r2xml_mandatory_missing.append('receiverorganization')
            
            if helper_dict.check_data_exist('patientinitial'):
                r2xml_mandatory['patientinitial'] = helper_dict.check_data_exist('patientinitial')
            elif helper_dict.check_data_exist('patientbirthdateformat') and \
                    helper_dict.check_data_exist('patientbirthdate'):
                r2xml_mandatory['patientbirthdateformat'] = helper_dict.check_data_exist('patientbirthdateformat')
                r2xml_mandatory['patientbirthdate'] = helper_dict.check_data_exist('patientbirthdate')
            elif helper_dict.check_data_exist('patientonsetage'):
                r2xml_mandatory['patientonsetage'] = helper_dict.check_data_exist('patientonsetage')
            elif helper_dict.check_data_exist('patientsex'):
                r2xml_mandatory['patientsex'] = helper_dict.check_data_exist('patientsex')
            else:
                is_valid = 0
                r2xml_mandatory_missing.append('patient DOB with format or gender or age or initail')
            
            if helper_dict.check_list_data_exist('reaction', 'primarysourcereaction'):
                r2xml_mandatory['primarysourcereaction'] = helper_dict.check_list_data_exist('reaction',
                                                                                             'primarysourcereaction')
            else:
                is_valid = 0
                r2xml_mandatory_missing.append('primarysourcereaction')
            
            if helper_dict.check_list_data_exist('drug', 'medicinalproduct'):
                r2xml_mandatory['medicinalproduct'] = helper_dict.check_list_data_exist('drug', 'medicinalproduct')
            else:
                is_valid = 0
                r2xml_mandatory_missing.append('medicinalproduct')
        else:
            is_valid = 0

        result = {}
        if is_valid == 1:

            duplicate_result = self.duplicate_check(r2xml_dict)
            if duplicate_result:

                self.helper.error_log("Duplicate data: " + str(duplicate_result))
                result = {'error': 1,
                          'message': 'Duplicate data available!'}
            else:
                # case creation
                result = {'error': 0,
                          'message': 'case creation needs to start!'}
                # self.helper.error_log(str(result))
                # result = r2xml_dict
        else:
            self.helper.error_log("Mandatory data missing: " + str(r2xml_mandatory_missing))

            result = {'error': 1,
                      'message': 'Mandatory data not available!'}
        # self.helper.error_log(str(result))
        return result

    # def case_creation(self, r2xml_dict):
    #     """r2xml data import starts after all validations"""
    #     general_tab = general(r2xml_dict, self.tenant, self.current_file_name)
    #     result = general_tab.general_tab()
    #     self.helper.error_log(str(result))
    #     return result



    def r2xml_validations(self):
        """r2xml checking is it valid or not"""
        r2xml_dict = {}
        ichicsr_tag = self.soup.find('ichicsr')
        # print(ichicsr_tag)
        if ichicsr_tag:
            """r2xml ichicsrmessageheader tag"""
            ichicsrmessageheader_tag = ichicsr_tag.find("ichicsrmessageheader")
           
            if ichicsrmessageheader_tag:
                if ichicsrmessageheader_tag.findChildren("messagetype"):
                    r2xml_dict["messagetype"] = self.helper.string_remove_junk(ichicsrmessageheader_tag.find("messagetype").text)
                if ichicsrmessageheader_tag.findChildren("messageformatversion"):
                    r2xml_dict["messageformatversion"] = self.helper.string_remove_junk(ichicsrmessageheader_tag.find("messageformatversion").text)
                if ichicsrmessageheader_tag.findChildren("messageformatrelease"):
                    r2xml_dict["messageformatrelease"] = self.helper.string_remove_junk(ichicsrmessageheader_tag.find("messageformatrelease").text)
                if ichicsrmessageheader_tag.findChildren("messagenumb"):
                    r2xml_dict["messagenumb"] = self.helper.string_remove_junk(ichicsrmessageheader_tag.find("messagenumb").text)
                if ichicsrmessageheader_tag.findChildren("messagesenderidentifier"):
                    r2xml_dict["messagesenderidentifier"] = self.helper.string_remove_junk(ichicsrmessageheader_tag.find(
                        "messagesenderidentifier").text)
                if ichicsrmessageheader_tag.findChildren("messagereceiveridentifier"):
                    r2xml_dict["messagereceiveridentifier"] = self.helper.string_remove_junk(ichicsrmessageheader_tag.find(
                        "messagereceiveridentifier").text)
                if ichicsrmessageheader_tag.findChildren("messagedateformat"):
                    r2xml_dict["messagedateformat"] = self.helper.string_remove_junk(ichicsrmessageheader_tag.find("messagedateformat").text)
                if ichicsrmessageheader_tag.findChildren("messagedate"):
                    r2xml_dict["messagedate"] = self.helper.string_remove_junk(ichicsrmessageheader_tag.find("messagedate").text)

            """r2xml safetyreport tag"""
            safetyreport_tag = ichicsr_tag.find("safetyreport")
            if safetyreport_tag:
                if safetyreport_tag.findChildren("safetyreportversion"):
                    r2xml_dict["safetyreportversion"] = self.helper.string_remove_junk(safetyreport_tag.find("safetyreportversion").text)

                if safetyreport_tag.findChildren("safetyreportid"):
                    r2xml_dict["safetyreportid"] = self.helper.string_remove_junk(safetyreport_tag.find("safetyreportid").text)

                if safetyreport_tag.findChildren("primarysourcecountry"):
                    r2xml_dict["primarysourcecountry"] = self.helper.string_remove_junk(safetyreport_tag.find("primarysourcecountry").text)

                if safetyreport_tag.findChildren("occurcountry"):
                    r2xml_dict["occurcountry"] = self.helper.string_remove_junk(safetyreport_tag.find("occurcountry").text)

                if safetyreport_tag.findChildren("transmissiondateformat"):
                    r2xml_dict["transmissiondateformat"] = self.helper.string_remove_junk(safetyreport_tag.find("transmissiondateformat").text)

                if safetyreport_tag.findChildren("reporttype"):
                    r2xml_dict["reporttype"] = safetyreport_tag.find("reporttype").text

                if safetyreport_tag.findChildren("serious"):
                    r2xml_dict["serious"] = self.helper.string_remove_junk(safetyreport_tag.find("serious").text)

                if safetyreport_tag.findChildren("seriousnessdeath"):
                    r2xml_dict["seriousnessdeath"] = self.helper.string_remove_junk(safetyreport_tag.find("seriousnessdeath").text)

                if safetyreport_tag.findChildren("seriousnesslifethreatening"):
                    r2xml_dict["seriousnesslifethreatening"] = self.helper.string_remove_junk(safetyreport_tag.find("seriousnesslifethreatening").text)

                if safetyreport_tag.findChildren("seriousnesslifethreatening"):
                    r2xml_dict["seriousnesslifethreatening"] = self.helper.string_remove_junk(safetyreport_tag.find("seriousnesslifethreatening").text)

                if safetyreport_tag.findChildren("seriousnesshospitalization"):
                    r2xml_dict["seriousnesshospitalization"] = self.helper.string_remove_junk(safetyreport_tag.find("seriousnesshospitalization").text)

                if safetyreport_tag.findChildren("seriousnessdisabling"):
                    r2xml_dict["seriousnessdisabling"] = self.helper.string_remove_junk(safetyreport_tag.find("seriousnessdisabling").text)

                if safetyreport_tag.findChildren("seriousnesscongenitalanomali"):
                    r2xml_dict["seriousnesscongenitalanomali"] = self.helper.string_remove_junk(safetyreport_tag.find(
                        "seriousnesscongenitalanomali").text)

                if safetyreport_tag.findChildren("seriousnessother"):
                    r2xml_dict["seriousnessother"] = self.helper.string_remove_junk(safetyreport_tag.find("seriousnessother").text)

                if safetyreport_tag.findChildren("receivedateformat"):
                    r2xml_dict["receivedateformat"] = self.helper.string_remove_junk(safetyreport_tag.find("receivedateformat").text)

                if safetyreport_tag.findChildren("receivedate"):
                    r2xml_dict["receivedate"] = self.helper.string_remove_junk(safetyreport_tag.find("receivedate").text)

                if safetyreport_tag.findChildren("receiptdateformat"):
                    r2xml_dict["receiptdateformat"] = self.helper.string_remove_junk(safetyreport_tag.find("receiptdateformat").text)

                if safetyreport_tag.findChildren("receiptdate"):
                    r2xml_dict["receiptdate"] = self.helper.string_remove_junk(safetyreport_tag.find("receiptdate").text)

                if safetyreport_tag.findChildren("additionaldocument"):
                    r2xml_dict["additionaldocument"] = self.helper.string_remove_junk(safetyreport_tag.find("additionaldocument").text)

                if safetyreport_tag.findChildren("authoritynumb"):
                    r2xml_dict["authoritynumb"] = self.helper.string_remove_junk(safetyreport_tag.find("authoritynumb").text)

                if safetyreport_tag.findChildren("companynumb"):
                    r2xml_dict["companynumb"] = self.helper.string_remove_junk(safetyreport_tag.find("companynumb").text)

                if safetyreport_tag.findChildren("medicallyconfirm"):
                    r2xml_dict["medicallyconfirm"] = self.helper.string_remove_junk(safetyreport_tag.find("medicallyconfirm").text)
                else:
                    r2xml_dict["medicallyconfirm"] = ''
                
                if safetyreport_tag.findChildren("casenullification"):
                    r2xml_dict["casenullification"] = self.helper.string_remove_junk(safetyreport_tag.find("casenullification").text)
                else:
                    r2xml_dict["casenullification"] = ''
                
                if safetyreport_tag.findChildren("nullificationreason"):
                    r2xml_dict["nullificationreason"] = self.helper.string_remove_junk(safetyreport_tag.find("nullificationreason").text)
                else:
                    r2xml_dict["nullificationreason"] = ''

                if safetyreport_tag.findChildren("linkedreport"):
                    r2xml_dict["linkedreport"] = safetyreport_tag.findChildren("linkedreport")
                else:
                    r2xml_dict["linkedreport"]=''    

                if safetyreport_tag.findChildren("duplicate"):
                    r2xml_dict["duplicate"] = self.helper.string_remove_junk(safetyreport_tag.find("duplicate").text)
                else:
                    r2xml_dict["duplicate"] = ''

                if safetyreport_tag.findChildren("reportduplicate"):
                    r2xml_dict["reportduplicate"] = safetyreport_tag.findChildren("reportduplicate")
                else:
                    r2xml_dict["reportduplicate"] =''
                
                """r2xml primarysource tag - reporter info"""
                if safetyreport_tag.findChildren("primarysource"):
                    r2xml_dict["primarysource"] = safetyreport_tag.findChildren("primarysource")
                else:
                    r2xml_dict["primarysource"]=''
                
                """r2xml medicalhistoryepisode tag info"""
                if safetyreport_tag.findChildren("medicalhistoryepisode"):
                    r2xml_dict["medicalhistoryepisode"] = safetyreport_tag.findChildren("medicalhistoryepisode")
                else:
                    r2xml_dict["medicalhistoryepisode"] = ''

                """r2xml sender tag"""
                sender_tag = safetyreport_tag.find("sender")
                if sender_tag.findChildren("sendertype"):
                    r2xml_dict["sendertype"] = self.helper.string_remove_junk(sender_tag.find("sendertype").text)

                if sender_tag.findChildren("senderorganization"):
                    r2xml_dict["senderorganization"] = self.helper.string_remove_junk(sender_tag.find("senderorganization").text)

                if sender_tag.findChildren("senderdepartment"):
                    r2xml_dict["senderdepartment"] = self.helper.string_remove_junk(sender_tag.find("senderdepartment").text)

                if sender_tag.findChildren("sendertitle"):
                    r2xml_dict["sendertitle"] = self.helper.string_remove_junk(sender_tag.find("sendertitle").text)

                if sender_tag.findChildren("sendergivename"):
                    r2xml_dict["sendergivename"] = self.helper.string_remove_junk(sender_tag.find("sendergivename").text)

                if sender_tag.findChildren("sendermiddlename"):
                    r2xml_dict["sendermiddlename"] = self.helper.string_remove_junk(sender_tag.find("sendermiddlename").text)

                if sender_tag.findChildren("senderstreetaddress"):
                    r2xml_dict["senderstreetaddress"] = self.helper.string_remove_junk(sender_tag.find("senderstreetaddress").text)

                if sender_tag.findChildren("sendercity"):
                    r2xml_dict["sendercity"] = self.helper.string_remove_junk(sender_tag.find("sendercity").text)

                if sender_tag.findChildren("senderstate"):
                    r2xml_dict["senderstate"] = self.helper.string_remove_junk(sender_tag.find("senderstate").text)

                if sender_tag.findChildren("senderpostcode"):
                    r2xml_dict["senderpostcode"] = self.helper.string_remove_junk(sender_tag.find("senderpostcode").text)

                if sender_tag.findChildren("sendercountrycode"):
                    r2xml_dict["sendercountrycode"] = self.helper.string_remove_junk(sender_tag.find("sendercountrycode").text)

                if sender_tag.findChildren("sendertel"):
                    r2xml_dict["sendertel"] = self.helper.string_remove_junk(sender_tag.find("sendertel").text)

                if sender_tag.findChildren("sendertelextension"):
                    r2xml_dict["sendertelextension"] = self.helper.string_remove_junk(sender_tag.find("sendertelextension").text)

                if sender_tag.findChildren("sendertelcountrycode"):
                    r2xml_dict["sendertelcountrycode"] = self.helper.string_remove_junk(sender_tag.find("sendertelcountrycode").text)

                if sender_tag.findChildren("senderfax"):
                    r2xml_dict["senderfax"] = self.helper.string_remove_junk(sender_tag.find("senderfax").text)

                if sender_tag.findChildren("senderfaxextension"):
                    r2xml_dict["senderfaxextension"] = self.helper.string_remove_junk(sender_tag.find("senderfaxextension").text)

                if sender_tag.findChildren("senderfaxcountrycode"):
                    r2xml_dict["senderfaxcountrycode"] = self.helper.string_remove_junk(sender_tag.find("senderfaxcountrycode").text)

                if sender_tag.findChildren("senderemailaddress"):
                    r2xml_dict["senderemailaddress"] = self.helper.string_remove_junk(sender_tag.find("senderemailaddress").text)

                """r2xml receiver tag"""
                receiver_tag = ichicsr_tag.find("receiver")
                if receiver_tag.findChildren("receivertype"):
                    r2xml_dict["receivertype"] = self.helper.string_remove_junk(receiver_tag.find("receivertype").text)

                if receiver_tag.findChildren("receiverorganization"):
                    r2xml_dict["receiverorganization"] = self.helper.string_remove_junk(receiver_tag.find("receiverorganization").text)

                if receiver_tag.findChildren("receiverdepartment"):
                    r2xml_dict["receiverdepartment"] = self.helper.string_remove_junk(receiver_tag.find("receiverdepartment").text)

                if receiver_tag.findChildren("receivertitle"):
                    r2xml_dict["receivertitle"] = self.helper.string_remove_junk(receiver_tag.find("receivertitle").text)

                if receiver_tag.findChildren("receivergivename"):
                    r2xml_dict["receivergivename"] = self.helper.string_remove_junk(receiver_tag.find("receivergivename").text)

                if receiver_tag.findChildren("receivermiddlename"):
                    r2xml_dict["receivermiddlename"] = self.helper.string_remove_junk(receiver_tag.find("receivermiddlename").text)

                if receiver_tag.findChildren("receiverstreetaddress"):
                    r2xml_dict["receiverstreetaddress"] = self.helper.string_remove_junk(receiver_tag.find("receiverstreetaddress").text)

                if receiver_tag.findChildren("receivercity"):
                    r2xml_dict["receivercity"] = self.helper.string_remove_junk(receiver_tag.find("receivercity").text)

                if receiver_tag.findChildren("receiverstate"):
                    r2xml_dict["receiverstate"] = self.helper.string_remove_junk(receiver_tag.find("receiverstate").text)

                if receiver_tag.findChildren("receiverpostcode"):
                    r2xml_dict["receiverpostcode"] = self.helper.string_remove_junk(receiver_tag.find("receiverpostcode").text)

                if receiver_tag.findChildren("receivercountrycode"):
                    r2xml_dict["receivercountrycode"] = self.helper.string_remove_junk(receiver_tag.find("receivercountrycode").text)

                if receiver_tag.findChildren("receivertel"):
                    r2xml_dict["receivertel"] = self.helper.string_remove_junk(receiver_tag.find("receivertel").text)

                if receiver_tag.findChildren("receivertelextension"):
                    r2xml_dict["receivertelextension"] = self.helper.string_remove_junk(receiver_tag.find("receivertelextension").text)

                if receiver_tag.findChildren("receivertelcountrycode"):
                    r2xml_dict["receivertelcountrycode"] = self.helper.string_remove_junk(receiver_tag.find("receivertelcountrycode").text)

                if receiver_tag.findChildren("receiverfax"):
                    r2xml_dict["receiverfax"] = self.helper.string_remove_junk(receiver_tag.find("receiverfax").text)

                if receiver_tag.findChildren("receiverfaxextension"):
                    r2xml_dict["receiverfaxextension"] = self.helper.string_remove_junk(receiver_tag.find("receiverfaxextension").text)

                if receiver_tag.findChildren("receiverfaxcountrycode"):
                    r2xml_dict["receiverfaxcountrycode"] = self.helper.string_remove_junk(receiver_tag.find("receiverfaxcountrycode").text)

                if receiver_tag.findChildren("receiveremailaddress"):
                    r2xml_dict["receiveremailaddress"] = self.helper.string_remove_junk(receiver_tag.find("receiveremailaddress").text)



                """r2xml patient tag"""
                if safetyreport_tag.find("patient"):
                    patient_tag = safetyreport_tag.find("patient")
                
                    if patient_tag.findChildren("patientinitial"):
                        r2xml_dict["patientinitial"] = self.helper.string_remove_junk(patient_tag.find("patientinitial").text)
                    
                    if patient_tag.findChildren("patientgpmedicalrecordnumb"):
                        r2xml_dict["patientgpmedicalrecordnumb"] = self.helper.string_remove_junk(patient_tag.find("patientgpmedicalrecordnumb").text)

                    if patient_tag.findChildren("patienthospitalrecordnumb"):
                        r2xml_dict["patienthospitalrecordnumb"] = self.helper.string_remove_junk(patient_tag.find("patienthospitalrecordnumb").text)

                    if patient_tag.findChildren("patientinvestigationnumb"):
                        r2xml_dict["patientinvestigationnumb"] = self.helper.string_remove_junk(patient_tag.find("patientinvestigationnumb").text)

                    if patient_tag.findChildren("patientbirthdateformat"):
                        r2xml_dict["patientbirthdateformat"] = self.helper.string_remove_junk(patient_tag.find("patientbirthdateformat").text)

                    if patient_tag.findChildren("patientbirthdate"):
                        r2xml_dict["patientbirthdate"] = self.helper.string_remove_junk(patient_tag.find("patientbirthdate").text)

                    if patient_tag.findChildren("patientonsetage"):
                        r2xml_dict["patientonsetage"] = self.helper.string_remove_junk(patient_tag.find("patientonsetage").text)

                    if patient_tag.findChildren("patientonsetageunit"):
                        r2xml_dict["patientonsetageunit"] = self.helper.string_remove_junk(patient_tag.find("patientonsetageunit").text)

                    if patient_tag.findChildren("gestationperiod"):
                        r2xml_dict["gestationperiod"] = self.helper.string_remove_junk(patient_tag.find("gestationperiod").text)

                    if patient_tag.findChildren("gestationperiodunit"):
                        r2xml_dict["gestationperiodunit"] = self.helper.string_remove_junk(patient_tag.find("gestationperiodunit").text)

                    if patient_tag.findChildren("patientagegroup"):
                        r2xml_dict["patientagegroup"] = self.helper.string_remove_junk(patient_tag.find("patientagegroup").text)

                    if patient_tag.findChildren("patientweight"):
                        r2xml_dict["patientweight"] = self.helper.string_remove_junk(patient_tag.find("patientweight").text)

                    if patient_tag.findChildren("patientheight"):
                        r2xml_dict["patientheight"] = self.helper.string_remove_junk(patient_tag.find("patientheight").text)

                    if patient_tag.findChildren("patientsex"):
                        r2xml_dict["patientsex"] = self.helper.string_remove_junk(patient_tag.find("patientsex").text)

                    if patient_tag.findChildren("lastmenstrualdateformat"):
                        r2xml_dict["lastmenstrualdateformat"] = self.helper.string_remove_junk(patient_tag.find("lastmenstrualdateformat").text)

                    if patient_tag.findChildren("patientlastmenstrualdate"):
                        r2xml_dict["patientlastmenstrualdate"] = self.helper.string_remove_junk(patient_tag.find("patientlastmenstrualdate").text)

                    if patient_tag.findChildren("patientmedicalhistorytext"):
                        r2xml_dict["patientmedicalhistorytext"] = self.helper.string_remove_junk(patient_tag.find("patientmedicalhistorytext").text)

                    if patient_tag.findChildren("resultstestsprocedures"):
                        r2xml_dict["resultstestsprocedures"] = self.helper.string_remove_junk(patient_tag.find("resultstestsprocedures").text)

                    if patient_tag.findChildren("medicalhistoryepisode"):
                        r2xml_dict["medicalhistoryepisode"] = patient_tag.findChildren("medicalhistoryepisode")

                    if patient_tag.findChildren("patientpastdrugtherapy"):
                        r2xml_dict["patientpastdrugtherapy"] = patient_tag.findChildren("patientpastdrugtherapy")
                    else:
                        r2xml_dict["patientpastdrugtherapy"] = ''

                    if patient_tag.findChildren("patientdeath"):
                        r2xml_dict["patientdeath"] = patient_tag.findChildren("patientdeath")

                    if patient_tag.findChildren("patientdeathcause"):
                        r2xml_dict["patientdeathcause"] = patient_tag.findChildren("patientdeathcause")

                    if patient_tag.findChildren("patientautopsy"):
                        r2xml_dict["patientautopsy"] = patient_tag.findChildren("patientautopsy")

                    if patient_tag.findChildren("parentidentification"):
                        r2xml_dict["parentidentification"] = self.helper.string_remove_junk(patient_tag.find("parentidentification").text)

                    if patient_tag.findChildren("parentbirthdateformat"):
                        r2xml_dict["parentbirthdateformat"] = self.helper.string_remove_junk(patient_tag.find("parentbirthdateformat").text)

                    if patient_tag.findChildren("parentbirthdate"):
                        r2xml_dict["parentbirthdate"] = self.helper.string_remove_junk(patient_tag.find("parentbirthdate").text)

                    if patient_tag.findChildren("parentage"):
                        r2xml_dict["parentage"] = self.helper.string_remove_junk(patient_tag.find("parentage").text)

                    if patient_tag.findChildren("parentageunit"):
                        r2xml_dict["parentageunit"] = self.helper.string_remove_junk(patient_tag.find("parentageunit").text)

                    if patient_tag.findChildren("parentlastmenstrualdateformat"):
                        r2xml_dict["parentlastmenstrualdateformat"] = self.helper.string_remove_junk(patient_tag.find("parentlastmenstrualdateformat").text)

                    if patient_tag.findChildren("parentlastmenstrualdateformat"):
                        r2xml_dict["parentlastmenstrualdateformat"] = self.helper.string_remove_junk(patient_tag.find("parentlastmenstrualdateformat").text)

                    if patient_tag.findChildren("parentlastmenstrualdate"):
                        r2xml_dict["parentlastmenstrualdate"] = self.helper.string_remove_junk(patient_tag.find("parentlastmenstrualdate").text)

                    if patient_tag.findChildren("parentweight"):
                        r2xml_dict["parentweight"] = self.helper.string_remove_junk(patient_tag.find("parentweight").text)

                    if patient_tag.findChildren("parentheight"):
                        r2xml_dict["parentheight"] = self.helper.string_remove_junk(patient_tag.find("parentheight").text)

                    if patient_tag.findChildren("parentsex"):
                        r2xml_dict["parentsex"] = self.helper.string_remove_junk(patient_tag.find("parentsex").text)

                    if patient_tag.findChildren("parentmedicalrelevanttext"):
                        r2xml_dict["parentmedicalrelevanttext"] = self.helper.string_remove_junk(patient_tag.find("parentmedicalrelevanttext").text)

                    if patient_tag.findChildren("reaction"):
                        r2xml_dict["reaction"] = patient_tag.findChildren("reaction")

                    if patient_tag.findChildren("test"):
                        r2xml_dict["test"] = patient_tag.findChildren("test")
                    else:
                        r2xml_dict["test"] = ''

                    if patient_tag.findChildren("drug"):
                        r2xml_dict["drug"] = patient_tag.findChildren("drug")
                    else:
                        r2xml_dict["drug"] = ''

                    if patient_tag.findChildren("summary"):
                        r2xml_dict["summary"] = patient_tag.findChildren("summary")
                

            """r2xml File upload"""
            r2xml_dict["xmlfilename"] = self.xmlfilename
            r2xml_dict["xmlfilepath"] = self.xmlfilepath
            r2xml_dict["tenantprefix"] = self.tenant_prefix
            # Pushpak code end
        
        mandatory_result = self.mandatory_fields_check(r2xml_dict)
        result = {'mandatory_result': mandatory_result}
        return result

    def r2xml_import_mapping(self):
        """r2xml import mapping class function"""
        from os.path import exists
        file_name = self.current_file_name
        file_path = con.logs_path + file_name + '.txt'
 
        if exists(file_path):
            self.helper.error_log_refresh('')
        self.helper.error_log('start')
        result = self.r2xml_validations()
        file_pointer = open(file_path, 'r').read()
        response = {'file_path': file_pointer, 'file_name': file_name + '.txt', 'result': result}
        return response





class r2import(APIView):
    """R2xml import starts"""

    def post(self, request):
        try:
            # data = request.data
            # print(data)
            # print(request.data.get('id'))
            result = R2XML_IMPORT(request).r2xml_import_mapping()
            # print(result,'api')
            file_name = result['file_name']
            
            return Response({'data': result, 'file_name': file_name},
                            content_type='application/txt',
                            status=status.HTTP_201_CREATED)
            # return Response({'data': result}, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response(str(exc), status=status.HTTP_401_UNAUTHORIZED)
