# reaction element create
from urllib import request
from bs4 import BeautifulSoup
from case_general.models import ( CaseMaster, CaseE2BReportDuplicate, CaseLinkedReport, 
CaseSummary, CaseCurrentActivity)
from case_product.models import CaseProduct, ProductActiveSubstance, ProductDosageRegimen, ProductIndication
from case_reaction.models import CaseReaction
from case_causality.models import CaseCausality, CaseCausalityReaction, CaseCausalityInformation
from r2import.helper import helper
from company_unit.models import CompanyUnit

from case_patient.models import CasePatient
from case_reporter.models import CaseReporter
from case_general.models import CaseStudy, CaseAttachments
from case_med_history.models import ( MedicalHistory, LabDataInfo, TextMedicalHistory, 
LabDataInfo, PastDrugHistory )
from case_narrative.models import CaseNarrative


from inspect import currentframe, getframeinfo
from workflow.models import (
    WorkFlowActivityModel,
    WFActivityRoleModel,
    WorkFlowMasterModel,
    WFNextActivityModel,
)
from django.db.models import (
    Q,
    F,
    OuterRef,
    Subquery,
    Count,
    Func,
    Case,
    Value,
    When,
    CharField,
)
from datetime import date
from authorization.views import VerifyTenant
from app_seq_generator.views import SequenceGenerator

import boto3
from botocore.client import Config
from django.core.serializers.json import DjangoJSONEncoder
from django.core.files.uploadedfile import InMemoryUploadedFile
from users.models import Users
from safety_api import settings
from datetime import datetime
import os
from authorization.models import Config
from authorization.serializers import ConfigSerializer

current_filename = str(getframeinfo(currentframe()).filename)


class general:

    def __init__(self, r2xml_dict, tenant, current_file_name):
        """constructor general tab information for case creation"""
        self.r2xml_dict = r2xml_dict
        self.tenant = tenant
        self.helper = helper(self.tenant, r2xml_dict, current_file_name)

    def company_unit(self, key):
        """r2xml class function to get sender and receiver"""
        try:
            data = CompanyUnit.objects.using(self.tenant).get(name=key.strip())
        except Exception as e:
            print(e)
            data = None

        return data

    def generate_case_id(self):
        """generate case id - (SB-2021-01699)"""
        var_case_no = " "
        try:
            result = SequenceGenerator.getNextSequence(
                'CASE_NO_SEQUENCE', self.tenant)
            if result:
                var_case_no = result
            else:
                var_case_no = " "
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return var_case_no

    def save_activity(self, tenant, case_id):
        """save intial Activity status"""
        initialActivity = (
            WorkFlowMasterModel.objects.prefetch_related("wf_activity")
                .annotate(
                id=Subquery(
                    WorkFlowActivityModel.objects.using(tenant)
                        .filter(
                        activity_id_pk=OuterRef("wf_activity__activity_id_pk"),
                        activity_status="Initial",
                    )
                        .values("activity_id_pk")[:1]
                )
            )
                .using(tenant)
                .filter(wf_active=1, id__gt=0)
                .values("id")
        )

        if initialActivity[0]["id"] is not None:
            activityId = initialActivity[0]["id"]
            act = CaseCurrentActivity(
                case_id_fk=CaseMaster.objects.using(
                    tenant).get(case_id_pk=case_id),
                case_activity_id_fk=WorkFlowActivityModel.objects.using(tenant).get(
                    activity_id_pk=activityId
                ),
                is_current_activity=1,
            )
            act.save(using=tenant)

    #  general tab information added
    def insert_general_information_section(self):
        data = None
        try:
            # print(self.helper.get_table_name(CaseMaster)+'_'+'case_version')
            case_no = self.generate_case_id()
            case_version = 0
            report_type = self.helper.simplesafety_code(
                CaseMaster, 'report_type', self.helper.r2_mapping_data(
                    self.helper.get_table_name(CaseMaster) + '_' + 'report_type')) 
            
            primary_src_country = self.helper.simplesafety_code(
                CaseMaster, 'primary_src_country',self.helper.r2_mapping_data(
                    self.helper.get_table_name(CaseMaster) + '_' + 'primary_src_country'))
            
            occurance_country = self.helper.simplesafety_code(
                CaseMaster, 'occurance_country',self.helper.r2_mapping_data(
                    self.helper.get_table_name(CaseMaster) + '_' + 'occurance_country'))
            
            case_init_recv_date = self.helper.date_format_e2b(
                self.helper.r2_mapping_data(self.helper.get_table_name(
                    CaseMaster) + '_' + 'case_init_recv_date'),
                    self.helper.get_table_name(CaseMaster), 'case_init_recv_date')
            
            init_safety_recv_date = self.helper.date_format_e2b(
                self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseMaster) + '_' + 'init_safety_recv_date'),
                self.helper.get_table_name(CaseMaster), 'init_safety_recv_date')        
            
            medically_confirmed = self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseMaster) + '_' + 'medically_confirmed')
            
            company_no = self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseMaster) + '_' + 'company_no')
            

            ''' nullification section'''
            nullify_amend_rep =  self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseMaster) + '_' + 'nullify_amend_rep')
            
            reason_for_nullify =  self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseMaster) + '_' + 'reason_for_nullify')
          
            if nullify_amend_rep == '1':
                nullify_amend_rep = '1'
            elif nullify_amend_rep == '2':
                nullify_amend_rep = '2'
            else:
                nullify_amend_rep = ''
            
            if medically_confirmed == '1':
                medically_confirmed = '1'
            elif medically_confirmed == '2':
                medically_confirmed = '2'
            else:
                medically_confirmed = ''

            is_r2_import = 1

            result = CaseMaster(case_no=case_no,
                                case_version=case_version,
                                report_type=report_type,
                                primary_src_country=primary_src_country,
                                occurance_country=occurance_country,
                                case_init_recv_date=case_init_recv_date,
                                init_safety_recv_date=init_safety_recv_date,
                                medically_confirmed=medically_confirmed,                             
                                company_no=company_no,
                                is_r2_import=is_r2_import,
                                
                                nullify_amend_rep=nullify_amend_rep,
                                reason_for_nullify=reason_for_nullify
                                )
            result.save(using=self.tenant)
            data = CaseMaster.objects.using(self.tenant).latest('case_id_pk')
            return data
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data
    
    #  patient tab information added
    def insert_patient_information_section(self, case_master):
        data = None
        try:
            initials = self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'initials')            
            
            patient_dob = self.helper.date_format_e2b(self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'patient_dob'),
                self.helper.get_table_name(CasePatient), 'patient_dob')            
            
            weight = self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'weight')            
            
            gender = self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'gender')


            height = self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'height') 
            
            age = self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'age') 

            age_unit = self.helper.simplesafety_code(
                CasePatient, 'age_unit',self.helper.r2_mapping_data(
                    self.helper.get_table_name(CasePatient) + '_' + 'age_unit'))
            
            age_group = self.helper.simplesafety_code(
                CasePatient, 'age_group',self.helper.r2_mapping_data(
                    self.helper.get_table_name(CasePatient) + '_' + 'age_group'))
            
            date_of_LMP = self.helper.date_format_e2b(self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'date_of_LMP'),
                self.helper.get_table_name(CasePatient), 'date_of_LMP') 

            '''Parent info '''   

            parent_dob = self.helper.date_format_e2b(self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'parent_dob'),
                self.helper.get_table_name(CasePatient), 'parent_dob')            
            
            p_weight = self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'p_weight')            
            
            p_gender = self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'p_gender')

            # if initials:
            #     patient_result['initials']=initials

            p_height = self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'p_height') 
            
            p_age = self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'p_age') 

            p_age_unit = self.helper.simplesafety_code(
                CasePatient, 'p_age_unit',self.helper.r2_mapping_data(
                    self.helper.get_table_name(CasePatient) + '_' + 'p_age_unit'))
            
            p_date_of_LMP = self.helper.date_format_e2b(self.helper.r2_mapping_data(
                self.helper.get_table_name(CasePatient) + '_' + 'p_date_of_LMP'),
                self.helper.get_table_name(CasePatient), 'p_date_of_LMP') 

            
            
            patient_result = CasePatient()
            patient_result.case_id_fk=case_master

            if initials:
                patient_result.initials=initials
            if patient_dob:
                patient_result.patient_dob=patient_dob           
            if weight:
                patient_result.weight=weight          
            if gender:
                patient_result.gender=gender           
            if height:
                patient_result.height=height           
            if age:
                patient_result.age=age
            if age_unit:
                patient_result.age_unit=age_unit           
            if age_group:
                patient_result.age_group=age_group    
            if date_of_LMP:
                patient_result.date_of_LMP=date_of_LMP   
       

            if parent_dob:
                patient_result.parent_dob=parent_dob           
            if p_weight:
                patient_result.p_weight=p_weight          
            if p_gender:
                patient_result.p_gender=p_gender           
            if p_height:
                patient_result.p_height=p_height           
            if p_age:
                patient_result.p_age=p_age
            if p_age_unit:
                patient_result.p_age_unit=p_age_unit           
            if p_date_of_LMP:
                patient_result.p_date_of_LMP=p_date_of_LMP                   
            
            patient_result.save(using=self.tenant)
            data = CasePatient.objects.using(self.tenant).latest('patient_id_pk')
            return data
        
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data


    # reporter tab information added  
    def insert_reporter_information_section(self,case_master, reporter_data):
        data = None
        try:
            rank = reporter_data['rank']
            primary_reporter='Y'
            reportertitle = reporter_data['reportertitle']
            reportergivename = reporter_data['reportergivename']
            reportermiddlename = reporter_data['reportermiddlename']
            reporterfamilyname = reporter_data['reporterfamilyname']
            reporterorganization = reporter_data['reporterorganization']
            reporterdepartment = reporter_data['reporterdepartment']          
            reporterstreet = reporter_data['reporterstreet']
            reportercity = reporter_data['reportercity']
            reporterstate = reporter_data['reporterstate']
            reporterpostcode = reporter_data['reporterpostcode']
            reportercountry = self.helper.simplesafety_code(
                CaseReporter, 'reporter_country', reporter_data['reportercountry'])
            qualification = self.helper.simplesafety_code(
                CaseReporter, 'qualification', reporter_data['qualification'])
        
            reporter_result = CaseReporter(
                case_id_fk=case_master,
                rank=rank,
                primary_reporter=primary_reporter,
                salutation=reportertitle,
                first_name=reportergivename,
                middle_name=reportermiddlename,
                last_name=reporterfamilyname,
                hospital_name=reporterorganization,
                department=reporterdepartment,
                street=reporterstreet,
                city=reportercity,
                state=reporterstate,
                postal_code=reporterpostcode,
                reporter_country=reportercountry,
                qualification=qualification,                
            )
            reporter_result.save(using=self.tenant)
            data = CaseReporter.objects.using(self.tenant).latest('reporter_id_pk')
            return data
            
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    #  case_study table  information added
    def insert_case_study_table_information(self,case_master, study_data):
        data = None
        try:
            study_desc = study_data['studyname']
            sponsor_study_no = study_data['sponsorstudynumb']
            study_type =  study_data['observestudytype']
            
            study_result = CaseStudy(
                case_id_fk=case_master,
                study_desc=study_desc,
                sponsor_study_no=sponsor_study_no,
                study_type=study_type,           
            )
            study_result.save(using=self.tenant)
            data = CaseStudy.objects.using(self.tenant).latest('study_id_pk')
            return data
            
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data


    #  medical history and lab data information added
    def insert_medical_history_lab_data_information(self, case_master,medical_history_data):
        data = None
        try:
            rank = medical_history_data['rank']
            meddra_llt = medical_history_data['meddra_llt']
            if (medical_history_data['meddra_version']):
                meddra_version = 'v.'+ medical_history_data['meddra_version']
            else:
                meddra_version = ''
            
            is_continuing = medical_history_data['is_continuing']
            comments = medical_history_data['comments']

            start_date = medical_history_data['start_date']
            stop_date = medical_history_data['stop_date']

            medical_history_data = MedicalHistory( 
                case_id_fk=case_master,  
                rank=rank,
                meddra_llt=meddra_llt,
                meddra_version=meddra_version,
                is_continuing=is_continuing,
                comments=comments,
                start_date=start_date,
                stop_date=stop_date
            )
            medical_history_data.save(using=self.tenant)
            data = MedicalHistory.objects.using(self.tenant).latest('med_history_id_pk')
            return data

        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    # Pushpak Code

    def insert_reaction_information_section(self,case_id,reaction_data):
        data = None
        
        try:
            case_no = case_id
            reaction_reported = reaction_data["primarysourcereaction"]
            if (reaction_data["reactionmeddraversionllt"]):
                reaction_coded_version = "v." + reaction_data["reactionmeddraversionllt"]
            else:
                reaction_coded_version = ''

            reaction_coded_llt = reaction_data["reactionmeddrallt"]
            reaction_coded_pt = reaction_data["reactionmeddrapt"]
            # below tag need to check, which column in table to be store
            # reactionmeddraversionpt = reaction_data["reactionmeddraversionpt"]

            reactionstartdateformat = reaction_data["reactionstartdateformat"]
            reaction_start_date = self.helper.date_format_e2b_with_date_format_tag(reaction_data["reactionstartdate"], reactionstartdateformat)

            if reaction_data["reactionoutcome"]:
                reaction_outcome = self.helper.simplesafety_code(CaseReaction, 'reaction_outcome', reaction_data["reactionoutcome"])
            else:
                reaction_outcome=''

            if reaction_data["termhighlighted"]:
                term_highlight_rptr = self.helper.simplesafety_code(CaseReaction, 'term_highlight_rptr', reaction_data["termhighlighted"])
            else:
                term_highlight_rptr=''
            
            reactionenddateformat = reaction_data["reactionenddateformat"]
            reaction_end_date = self.helper.date_format_e2b_with_date_format_tag(reaction_data["reactionenddate"], reactionenddateformat)
            
            reaction_duration =reaction_data["reactionduration"]
            
            if reaction_data["reactiondurationunit"]:
                reaction_unit = self.helper.simplesafety_code(CaseReaction, 'reaction_unit', reaction_data["reactiondurationunit"])
            else:
                reaction_unit=''
            
            data_level = 2
            reaction_count =reaction_data["reaction_count"]
            
            country_rectn_occr =reaction_data["rcountry_rectn_occr"]
            medically_confirmed =reaction_data["medically_confirmed"]
            serious_reaction =reaction_data["serious"]
            result = CaseReaction()
            if case_no:
                result.case_id_fk = case_no
            if reaction_reported:
                result.reaction_reported = reaction_reported
            if reaction_coded_version:
                result.reaction_coded_version = reaction_coded_version
            if reaction_coded_llt:
                result.reaction_coded_llt = reaction_coded_llt
            
            if reaction_coded_pt:
                result.reaction_coded_pt = reaction_coded_pt
            
            if data_level:
                result.data_level = data_level
            if reaction_start_date:
                result.reaction_start_date = reaction_start_date
            if reaction_end_date:
                result.reaction_end_date = reaction_end_date
            if reaction_duration:
                result.reaction_duration = reaction_duration
            if reaction_unit:
                result.reaction_unit = reaction_unit

            result.rank = reaction_count

            result.reaction_outcome = reaction_outcome
            result.term_highlight_rptr = term_highlight_rptr
            result.country_rectn_occr = country_rectn_occr
            result.medically_confirmed = medically_confirmed
            result.serious_reaction = serious_reaction

            result.save(using=self.tenant)
            data = CaseReaction.objects.using(self.tenant).latest('reaction_id_pk')
            return data
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data


    def insert_product_information_section(self,case_id, product_tab_data):
        data = None
        try:
            case_no = case_id
            char_of_product = product_tab_data["drugcharacterization"]
            if product_tab_data["drugauthorizationcountry"]:
                drug_authorization_country = self.helper.simplesafety_code(CaseProduct, 'drug_authorization_country', product_tab_data["drugauthorizationcountry"])
            else:
                drug_authorization_country=''
            
            product_name = product_tab_data["medicinalproduct"]

            if product_tab_data["obtaindrugcountry"]:
                country_obtained = self.helper.simplesafety_code(CaseProduct, 'country_obtained', product_tab_data["obtaindrugcountry"])
            else:
                country_obtained=''

            drug_authorization_number = product_tab_data["drugauthorizationnumb"]
            
            drug_code = product_tab_data["drugdosageform"]
            
            ma_holder = product_tab_data["drugauthorizationholder"]
            
            if product_tab_data["actiondrug"]:
                action_with_prod = self.helper.simplesafety_code(CaseProduct, 'action_with_prod', product_tab_data["actiondrug"])
            else:
                action_with_prod=''

            cum_dos_first_rectn = product_tab_data["drugcumulativedosagenumb"]
            gest_prd_tim_expsre = product_tab_data["reactiongestationperiod"]
            
            if product_tab_data["reactiongestationperiodunit"]:
                gest_expsre_unit = self.helper.simplesafety_code(CaseProduct, 'gest_expsre_unit', product_tab_data["reactiongestationperiodunit"])
            else:
                gest_expsre_unit=''

            if product_tab_data["unique_product_id"]:
                unique_product_id = product_tab_data["unique_product_id"]
            else:
                unique_product_id=''

            if product_tab_data["drugadditional"]:
                drugadditional = product_tab_data["drugadditional"]
            else:
                drugadditional=''
            
            product_class = 1  

            result = CaseProduct()
            if case_no:
                result.case_id_fk = case_no
            if char_of_product:
                result.char_of_product = char_of_product
            if drug_authorization_country:
                result.drug_authorization_country = drug_authorization_country
            if product_name:
                result.product_name = product_name
            if product_class:
                result.product_class = product_class
            if country_obtained:
                result.country_obtained = country_obtained
            if drug_authorization_number:
                result.drug_authorization_number = drug_authorization_number
            if ma_holder:
                result.ma_holder = ma_holder
            if action_with_prod:
                result.action_with_prod = action_with_prod
            if cum_dos_first_rectn:
                result.cum_dos_first_rectn = cum_dos_first_rectn
            if gest_prd_tim_expsre:
                result.gest_prd_tim_expsre = gest_prd_tim_expsre
            if gest_expsre_unit:
                result.gest_expsre_unit = gest_expsre_unit   
            if drug_code:
                result.drug_code = drug_code   

            if unique_product_id:
                result.unique_product_id = unique_product_id
            
            if drugadditional:
                result.product_addl_info = drugadditional

            result.save(using=self.tenant)
            data = CaseProduct.objects.using(self.tenant).latest('product_id_pk')
            return data
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data


    def insert_product_active_sub_information_section(self,case_id, product_id, activesubstance_data):
        data = None
        try:
            case_no = case_id
            product_id = product_id
            act_sub_name = activesubstance_data["activesubstancename"]
            rank = activesubstance_data["rank"]

            result = ProductActiveSubstance()
            if case_no != '':
                result.case_id_fk = case_no
            if product_id != '':
                result.product_id_fk = product_id
            if act_sub_name != '':
                result.act_sub_name = act_sub_name
            if rank != '':
                result.rank = rank
            result.save(using=self.tenant)
        
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    def insert_case_prod_dosage_regimen_section(self,case_id, product_id, dosage_regimen_data):
        data = None
        try:
            case_no = case_id
            product_id = product_id
            dose = dosage_regimen_data["drugstructuredosagenumb"]

            if dosage_regimen_data["drugstructuredosageunit"]:
                dose_units = self.helper.simplesafety_code(ProductDosageRegimen, 'dose_units', dosage_regimen_data["drugstructuredosageunit"])
            else:
                dose_units=''
            
            dosage_text = dosage_regimen_data["drugdosagetext"]

            if dosage_regimen_data["drugadministrationroute"]:
                patient_roa = self.helper.simplesafety_code(ProductDosageRegimen, 'patient_roa', dosage_regimen_data["drugadministrationroute"])
            else:
                patient_roa=''
            
            batch_lot_no = dosage_regimen_data["drugbatchnumb"]

            rank = dosage_regimen_data["rank"]

            drugtreatmentduration = dosage_regimen_data["drugtreatmentduration"]
            
            drugstartdateformat = dosage_regimen_data["drugstartdateformat"]
            drugstartdate = self.helper.date_format_e2b_with_date_format_tag(dosage_regimen_data["drugstartdate"], drugstartdateformat)

            drugenddateformat = dosage_regimen_data["drugenddateformat"]
            drugenddate = self.helper.date_format_e2b_with_date_format_tag(dosage_regimen_data["drugenddate"], drugenddateformat)

            if dosage_regimen_data["drugtreatmentdurationunit"]:
                drugtreatmentdurationunit = self.helper.simplesafety_code(ProductDosageRegimen, 'units', dosage_regimen_data["drugtreatmentdurationunit"])
            else:
                drugtreatmentdurationunit = ''
            
            if dosage_regimen_data["drugparadministration"]:
                drugparadministration = self.helper.simplesafety_code(ProductDosageRegimen, 'parent_roa', dosage_regimen_data["drugparadministration"])
            else:
                drugparadministration = ''
            
            
            result = ProductDosageRegimen()
            if case_no:
                result.case_id_fk = case_no
            if product_id:
                result.product_id_fk = product_id
            if dose:
                result.dose = dose
            if dose_units:
                result.dose_units = dose_units
            if dosage_text:
                result.dosage_text = dosage_text
            if patient_roa:
                result.patient_roa = patient_roa
            if batch_lot_no:
                result.batch_lot_no = batch_lot_no
            if rank:
                result.rank = rank
            
            if drugtreatmentduration:
                result.duration_of_regimen = drugtreatmentduration
            if drugstartdate:
                result.start_date = drugstartdate
            if drugenddate:
                result.stop_date = drugenddate
            if drugtreatmentdurationunit:
                result.units = drugtreatmentdurationunit
            if drugparadministration:
                result.parent_roa = drugparadministration


            result.save(using=self.tenant)
        
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    def insert_case_causality_section(self,case_id):
        data = None
        try:
            case_no = case_id
            if case_no:
                product_id_pk_all = self.helper.get_product_id_pk(case_no)
            else:
                product_id_pk_all=''
            
            rank = 1
            for product_id in product_id_pk_all:
                pid_fk = product_id[0]
            
                result = CaseCausality()
                if case_no:
                    result.case_id_fk = case_no

                if pid_fk:
                    prod_id_pk = CaseProduct.objects.using(self.tenant).get(product_id_pk=pid_fk)
                    result.product_id_fk = prod_id_pk

                if rank:
                    result.rank = rank
                
                result.save(using=self.tenant)
                rank = rank + 1
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data        
    
    def insert_case_causality_reaction_section(self, case_id, casecausalityreactiondata):
        data = None
        try:
            case_no = case_id
            if casecausalityreactiondata["drugcharacterization_causality"]:
                drugcharacterization_causality = casecausalityreactiondata["drugcharacterization_causality"]
            else:
                drugcharacterization_causality = ''
            
            if casecausalityreactiondata["medicinalproduct_causality"]:
                medicinalproduct_causality = casecausalityreactiondata["medicinalproduct_causality"]
            else:
                medicinalproduct_causality = ''

            if casecausalityreactiondata["reactionmeddraversionllt1"]:
                reactionmeddraversionllt1 = "v." + casecausalityreactiondata["reactionmeddraversionllt1"]
            else:
                reactionmeddraversionllt1 = ''
            
            if casecausalityreactiondata["reactionmeddrallt1"]:
                reactionmeddrallt1 = casecausalityreactiondata["reactionmeddrallt1"]
            else:
                reactionmeddrallt1 = ''
                    
            if case_no:
                    product_id_fk1 = self.helper.get_product_id_fk(case_no, drugcharacterization_causality, medicinalproduct_causality)
                    for prodid in product_id_fk1:
                        product_id_fk = prodid[0]
            else:
                product_id_fk=''
            
            if case_no:
                causality_id_fk = self.helper.get_causality_id_fk(case_no, product_id_fk)
            else:
                causality_id_fk=''
            if causality_id_fk:
                caus_id_fk = CaseCausality.objects.using(self.tenant).get(causality_id_pk=causality_id_fk)

            if case_no:
                reaction_id_fk1 = self.helper.get_reaction_id_pk(case_no, reactionmeddraversionllt1, reactionmeddrallt1)
                for reactionid in reaction_id_fk1:
                    reaction_id_fk = reactionid[0]
            else:
                reaction_id_fk=''
            if(reaction_id_fk):
                reactionidfk = CaseReaction.objects.using(self.tenant).get(reaction_id_pk=reaction_id_fk)

            if casecausalityreactiondata["drugrecurreadministration"]:
                rechallenge = casecausalityreactiondata["drugrecurreadministration"]
            else:
                rechallenge = ''
            
            if casecausalityreactiondata["drugstartperiod_causality"]:
                drugstartperiod_causality = casecausalityreactiondata["drugstartperiod_causality"]
            else:
                drugstartperiod_causality = ''
            
            if casecausalityreactiondata["drugstartperiodunit_causality"]:
                drugstartperiodunit_causality = self.helper.simplesafety_code(CaseCausalityReaction, 'time_intrvl_begn_admin_unit', casecausalityreactiondata["drugstartperiodunit_causality"])
            else:
                drugstartperiodunit_causality = ''

            if casecausalityreactiondata["druglastperiod_causality"]:
                druglastperiod_causality = casecausalityreactiondata["druglastperiod_causality"]
            else:
                druglastperiod_causality = ''

            if casecausalityreactiondata["druglastperiodunit_causality"]:
                druglastperiodunit_causality = self.helper.simplesafety_code(CaseCausalityReaction, 'time_intrvl_last_dose_unit', casecausalityreactiondata["druglastperiodunit_causality"])
            else:
                druglastperiodunit_causality = ''

            result = CaseCausalityReaction()
            if case_no:
                result.case_id_fk = case_no
            if caus_id_fk:
                result.causality_id_fk = caus_id_fk
            if reactionidfk:
                result.reaction_id_fk = reactionidfk
            if rechallenge:
                result.rechallenge = rechallenge
            
            if drugstartperiod_causality:
                result.time_intrvl_begn_admin  = drugstartperiod_causality
            if drugstartperiodunit_causality:
                result.time_intrvl_begn_admin_unit  = drugstartperiodunit_causality
            if druglastperiod_causality:
                result.time_intrvl_last_dose  = druglastperiod_causality
            if druglastperiodunit_causality:
                result.time_intrvl_last_dose_unit  = druglastperiodunit_causality

            result.save(using=self.tenant)

                    
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    def insert_case_causality_reaction_section_without_values(self, case_id, casecausalityreactiondata):
        data = None
        try:
            case_no = case_id
            if casecausalityreactiondata["drugcharacterization_causality"]:
                drugcharacterization_causality = casecausalityreactiondata["drugcharacterization_causality"]
            else:
                drugcharacterization_causality = ''
            
            if casecausalityreactiondata["medicinalproduct_causality"]:
                medicinalproduct_causality = casecausalityreactiondata["medicinalproduct_causality"]
            else:
                medicinalproduct_causality = ''

            if casecausalityreactiondata["reactionmeddraversionllt1"]:
                reactionmeddraversionllt1 = "v." + casecausalityreactiondata["reactionmeddraversionllt1"]
            else:
                reactionmeddraversionllt1 = ''
            
            if casecausalityreactiondata["reactionmeddrallt1"]:
                reactionmeddrallt1 = casecausalityreactiondata["reactionmeddrallt1"]
            else:
                reactionmeddrallt1 = ''

            if case_no:
                    product_id_fk1 = self.helper.get_product_id_fk(case_no, drugcharacterization_causality, medicinalproduct_causality)
                    for prodid in product_id_fk1:
                        product_id_fk = prodid[0]
            else:
                product_id_fk=''
            
            if case_no:
                causality_id_fk = self.helper.get_causality_id_fk(case_no, product_id_fk)
            else:
                causality_id_fk=''

            if causality_id_fk:
                caus_id_fk = CaseCausality.objects.using(self.tenant).get(causality_id_pk=causality_id_fk)

            if case_no:
                reaction_id_fk1 = self.helper.get_reaction_id_pk(case_no, reactionmeddraversionllt1, reactionmeddrallt1)
                for reactionid in reaction_id_fk1:
                    reaction_id_fk = reactionid[0]
            else:
                reaction_id_fk=''

            if(reaction_id_fk):
                reactionidfk = CaseReaction.objects.using(self.tenant).get(reaction_id_pk=reaction_id_fk)

            if casecausalityreactiondata["drugstartperiod_causality"]:
                drugstartperiod_causality = casecausalityreactiondata["drugstartperiod_causality"]
            else:
                drugstartperiod_causality = ''
            
            if casecausalityreactiondata["drugstartperiodunit_causality"]:
                drugstartperiodunit_causality = self.helper.simplesafety_code(CaseCausalityReaction, 'time_intrvl_begn_admin_unit', casecausalityreactiondata["drugstartperiodunit_causality"])
            else:
                drugstartperiodunit_causality = ''

            if casecausalityreactiondata["druglastperiod_causality"]:
                druglastperiod_causality = casecausalityreactiondata["druglastperiod_causality"]
            else:
                druglastperiod_causality = ''

            if casecausalityreactiondata["druglastperiodunit_causality"]:
                druglastperiodunit_causality = self.helper.simplesafety_code(CaseCausalityReaction, 'time_intrvl_last_dose_unit', casecausalityreactiondata["druglastperiodunit_causality"])
            else:
                druglastperiodunit_causality = ''

            result = CaseCausalityReaction()
            if case_no:
                result.case_id_fk = case_no
            if caus_id_fk:
                result.causality_id_fk = caus_id_fk
            if reactionidfk:
                result.reaction_id_fk = reactionidfk

            if drugstartperiod_causality:
                result.time_intrvl_begn_admin  = drugstartperiod_causality
            if drugstartperiodunit_causality:
                result.time_intrvl_begn_admin_unit  = drugstartperiodunit_causality
            if druglastperiod_causality:
                result.time_intrvl_last_dose  = druglastperiod_causality
            if druglastperiodunit_causality:
                result.time_intrvl_last_dose_unit  = druglastperiodunit_causality

            result.save(using=self.tenant)

                    
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    def aws_file_import(self, caseid, xmlfilename, xmlfilepath, tenantprefix):
        data = None
        try:
            case_no = caseid
            target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION
            target_file_path = (
                target_file_path
                + "/"
                + str(tenantprefix)
                + "/r2import/"
                + str(case_no)
                        )

            fnameArray = xmlfilename.split(".")
            extn = fnameArray[-1]
            f_name = (
                "".join(fnameArray[:-1]) +"_"
                + str(round(datetime.now().timestamp())) + "." + extn)
            file_name = (
                target_file_path + "/" 
                + f_name
                )
            xmlfilepath.seek(0)
            s_3 = boto3.resource(
                "s3",
                aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
            )
            s_3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(
                Key=file_name, 
                Body=xmlfilepath,
            )
            
            result = CaseAttachments()
            if case_no:
                result.case_id_fk  = case_no

            result.attachment_type  = '001'

            if xmlfilename:
                result.attachment  = xmlfilename
            if file_name:
                result.attachment_loc   = file_name
            
            result.rank   = '1'
            result.attachment_description   = 'R2 Import Source Document'
            
            result.save(using=self.tenant)

        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data
    
    def insert_case_prod_indication_section(self,case_id, product_id, prodindicationdata):
        data = None
        try:
            case_no = case_id
            product_id = product_id
            drugindication = prodindicationdata["drugindication"]
            if (prodindicationdata["drugindicationmeddraversion"]):
                drugindicationmeddraversion = "v." + prodindicationdata["drugindicationmeddraversion"]
            else:
                drugindicationmeddraversion = ''
            

            result = ProductIndication()
            if case_no != '':
                result.case_id_fk = case_no
            if product_id != '':
                result.product_id_fk = product_id
            if drugindication != '':
                result.indication_coded_llt = drugindication
            
            if drugindicationmeddraversion != '':
                result.meddra_version = drugindicationmeddraversion
            
            result.save(using=self.tenant)
        
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data
    # Pushpak code end



    # e2b report duplicate data section information
    def insert_e2b_report_duplicate_section(self, case_master,duplicate_data):
        data = None
        try:   
            duplicate_source = duplicate_data['duplicatesource']
            duplicate_number = duplicate_data['duplicatenumb']
            previously_reported = duplicate_data["duplicate"]
            rank = duplicate_data['rank']
            if previously_reported == '1':
                previously_reported = '1'
            else:
                previously_reported = ''

            report_duplicate = CaseE2BReportDuplicate(
                case_id_fk=case_master,
                rank = rank,
                duplicate_source = duplicate_source,
                duplicate_number = duplicate_number,
                previously_reported = previously_reported
            )
            report_duplicate.save(using=self.tenant)
            # data = CaseE2BReportDuplicate.objects.using(self.tenant).latest('case_e2b_rpt_dup_id_pk')
            # return data

            
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    
    # linked report data section information
    def insert_linked_report_section(self, case_master, linked_data):
        data = None
        try:
            linkreportnumb = linked_data['linkreportnumb']
            linked_case_no = linked_data['linked_case_no']
            record_type = linked_data['record_type']
            rank = linked_data['rank']
            if linked_case_no:
                case_number = self.helper.get_case_no(linked_case_no)  

            linked_report = CaseLinkedReport()
            if case_master:
                linked_report.case_id_fk = case_master
            if rank:
                linked_report.rank = rank 
            if linkreportnumb:
                linked_report.linked_report_no = linkreportnumb     
            if case_number:
                linked_report.linked_case_no = case_number       
            if record_type:
                linked_report.record_type = record_type

            linked_report.save(using=self.tenant)
            # data = CaseLinkedReport.objects.using(self.tenant).latest('case_linked_report_id_pk')
            # return data
        
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    # case narrative tab section information
    def insert_narrative_tab_section_info(self,case_master):
        data = None
        try:
            narrative_data = {}         
            summary_tag = self.r2xml_dict['summary']

            for narrative_tag in summary_tag:
                if narrative_tag.find("narrativeincludeclinical"):
                    if narrative_tag.find("narrativeincludeclinical").text:
                        narrative_data['narrative'] = narrative_tag.find("narrativeincludeclinical").text
                else:
                    narrative_data['narrative'] = ""

                if narrative_tag.find("reportercomment"):
                    if narrative_tag.find("reportercomment").text:
                        narrative_data['reporter_comment'] = narrative_tag.find("reportercomment").text
                else:
                    narrative_data['reporter_comment'] = ""
            
                if narrative_tag.find("sendercomment"):
                    if narrative_tag.find("sendercomment").text:
                        narrative_data['sender_comment'] = narrative_tag.find("sendercomment").text
                else:
                    narrative_data['sender_comment'] = ""

            case_narrative = CaseNarrative(
                case_id_fk=case_master,
                narrative=narrative_data['narrative'],
                reporter_comment = narrative_data['reporter_comment'],
                sender_comment = narrative_data['sender_comment']
            )
            case_narrative.save(using=self.tenant)
            data = CaseNarrative.objects.using(self.tenant).latest('narrative_id_pk')
            return data

        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

     #  text relevant medical data section information
    def insert_text_relevant_medical_data_information(self, case_master):
        data = None
        try:
            txt_med_hist = self.helper.r2_mapping_data(
                self.helper.get_table_name(TextMedicalHistory) + '_' + 'txt_med_hist')         
            
            txt_relevant_data = TextMedicalHistory( 
                case_id_fk=case_master,
                txt_med_hist=txt_med_hist
            )
            txt_relevant_data.save(using=self.tenant)
            # data = TextMedicalHistory.objects.using(self.tenant).latest('txt_med_hist_id_pk')
            # return data
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data


    #  relevant past drug theropy data section information
    def insert_relevant_past_drug_data_tab_section_info(self, case_master, past_drug_data):
        data = None
        try: 
            rank = past_drug_data['rank']
            drug_hist_rpt = past_drug_data['drug_hist_rpt']
            ind_start_date = past_drug_data['ind_start_date']
            ind_stop_date = past_drug_data['ind_stop_date']
            if (past_drug_data['lab_data_version']):
                lab_data_version = 'v.' + past_drug_data['lab_data_version']
            else:
                lab_data_version = ''
            lab_data_llt = past_drug_data['lab_data_llt']

            patientdrugreaction = past_drug_data['patientdrugreaction']
            if (past_drug_data['patientdrgreactionmeddraversion']):
                patientdrgreactionmeddraversion = 'v.'+ past_drug_data['patientdrgreactionmeddraversion']
            else:
                patientdrgreactionmeddraversion = ''
            
            pastdrug_data = PastDrugHistory(
                case_id_fk=case_master,
                rank=rank,
                drug_hist_rpt=drug_hist_rpt,
                ind_start_date=ind_start_date,
                ind_stop_date=ind_stop_date,
                lab_data_version=lab_data_version,
                lab_data_llt=lab_data_llt,
                rectn_meddra_llt=patientdrugreaction,
                rectn_meddra_version=patientdrgreactionmeddraversion

            )
            pastdrug_data.save(using=self.tenant)
            # data = PastDrugHistory.objects.using(self.tenant).latest('lab_data_id_pk')
            # return data
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    # case medical lab data section information (not done)
    def insert_medical_lab_data_tab_section_info(self,case_master, lab_data):
        data = None
        try: 
            rank = lab_data['rank']
            lab_meddra_llt = lab_data['lab_meddra_llt']
            test_result_value = lab_data['test_result_value']
            test_result_units = lab_data['test_result_units']
            normal_low_range = lab_data['normal_low_range']
            normal_high_range = lab_data['normal_high_range']
            testdate = lab_data['testdate']
            
            case_lab_data = LabDataInfo(
                case_id_fk=case_master,
                rank=rank,
                lab_meddra_llt=lab_meddra_llt,
                test_result_value=test_result_value,
                test_result_units=test_result_units,
                normal_low_range=normal_low_range,
                normal_high_range=normal_high_range,
                test_date=testdate
            )
            case_lab_data.save(using=self.tenant)

            data = LabDataInfo.objects.using(self.tenant).latest('lab_data_id_pk')
            return data

        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    #  general tab - case type summary section data
    def insert_case_summary_section(self, case_master):
        data = None
        try:              
            serious_reaction =  self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseSummary) + '_' + 'serious_reaction')

            ser_cri_death = self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseSummary) + '_' + 'ser_cri_death')

            ser_cri_life_threat = self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseSummary) + '_' + 'ser_cri_life_threat')
            
            ser_cri_hospital_pro = self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseSummary) + '_' + 'ser_cri_hospital_pro')
            
            ser_cri_disability = self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseSummary) + '_' + 'ser_cri_disability')
            
            ser_cri_cgential_anomaly = self.helper.r2_mapping_data(
                self.helper.get_table_name(CaseSummary) + '_' + 'ser_cri_cgential_anomaly')

            if serious_reaction=='1':
                serious_reaction='1'
            elif serious_reaction=='2':
                serious_reaction='2'
            else:
                serious_reaction=''

            if ser_cri_death=='1':
                ser_cri_death='Y'
            elif ser_cri_death=='2':
                ser_cri_death='N'
            else:
                ser_cri_death=''

            if ser_cri_life_threat=='1':
                ser_cri_life_threat='Y'
            elif ser_cri_life_threat==2:
                ser_cri_life_threat='N'
            else:
                ser_cri_life_threat=''

            if ser_cri_hospital_pro=='1':
                ser_cri_hospital_pro='Y'
            elif ser_cri_hospital_pro=='2':
                ser_cri_hospital_pro='N'
            else:
                ser_cri_hospital_pro=''
            
            if ser_cri_disability=='1':
                ser_cri_disability='Y'
            elif ser_cri_disability=='2':
                ser_cri_disability='N'
            else:
                ser_cri_disability=''
            
            if ser_cri_cgential_anomaly=='1':
                ser_cri_cgential_anomaly='Y'
            elif ser_cri_cgential_anomaly=='2':
                ser_cri_cgential_anomaly='N'
            else:
                ser_cri_cgential_anomaly=''

            case_summary = CaseSummary(
                case_id_fk=case_master,
                serious_reaction=serious_reaction,
                ser_cri_death=ser_cri_death ,
                ser_cri_life_threat=ser_cri_life_threat,
                ser_cri_hospital_pro=ser_cri_hospital_pro,
                ser_cri_disability=ser_cri_disability,
                ser_cri_cgential_anomaly=ser_cri_cgential_anomaly
            )
            case_summary.save(using=self.tenant)
            data = CaseSummary.objects.using(self.tenant).latest('case_summary_id_pk')
            return data
        
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            data = None
        return data

    

    def case_version_creation(self):
        return 1

    def general_tab(self):
        """push general information section for case creation"""
        # result = Nones
        senderorganization = self.company_unit(self.r2xml_dict["senderorganization"])
        receiverorganization = self.company_unit(self.r2xml_dict["receiverorganization"])
        
        primarysource_info = self.r2xml_dict["primarysource"]
        medicalhistoryepisode_info = self.r2xml_dict["medicalhistoryepisode"]

        duplicatetag_info = self.r2xml_dict["duplicate"] # 1

        reportduplicate_tag = self.r2xml_dict["reportduplicate"]
        linkedreport_tag = self.r2xml_dict["linkedreport"] 
        test_tag_info = self.r2xml_dict['test']
        patientpastdrugtherapy_tag = self.r2xml_dict["patientpastdrugtherapy"]
        
        reactioninfo = self.r2xml_dict["reaction"]
        productinfo = self.r2xml_dict["drug"]
        xmlfilename = self.r2xml_dict["xmlfilename"]
        xmlfilepath = self.r2xml_dict["xmlfilepath"]
        tenantprefix = self.r2xml_dict["tenantprefix"]

        try:
            if senderorganization is not None and receiverorganization is not None:
                authority_no = self.helper.duplicate_values(
                    self.helper.get_table_name(CaseMaster), 'authority_no',
                        self.helper.r2_mapping_data(self.helper.get_table_name(
                            CaseMaster) + "_authority_no"),None, "Text")

                company_no = self.helper.duplicate_values(
                    self.helper.get_table_name(CaseMaster), 'company_no',
                        self.helper.r2_mapping_data(
                            self.helper.get_table_name(CaseMaster) + "_company_no"),None, "Text")

                if authority_no['data'] is not None or company_no['data'] is not None:
                    result = {'error': 0,
                              'message': 'case creation version coming soon'}
                else:
                    #  general tab - general information section added
                    case_id = self.insert_general_information_section()
                    self.save_activity(
                        self.tenant, case_id.case_id_pk)
		      
                    # uplaod file to s3
                    uplaodfile = self.aws_file_import(case_id, xmlfilename, xmlfilepath, tenantprefix)
                    
                    
                    #  patient tab information added
                    self.insert_patient_information_section(case_id)
                    
                    # reporter tab information added
                    count = 1
                    try:
                        primarysource_data = {}
                        for primarysource in primarysource_info:
                            primarysource_data["rank"] = count
                            # primarysource_data["primary_reporter"]='Y'

                            if primarysource.find("reportertitle"):
                                if primarysource.find("reportertitle").text:
                                    primarysource_data["reportertitle"] = primarysource.find("reportertitle").text
                            else:
                                primarysource_data["reportertitle"]=''

                            if primarysource.find("reportergivename"):
                                if primarysource.find("reportergivename").text:
                                    primarysource_data["reportergivename"] = primarysource.find("reportergivename").text
                            else:
                                primarysource_data["reportergivename"]=''

                            if primarysource.find("reportermiddlename"):
                                if primarysource.find("reportermiddlename").text:
                                    primarysource_data["reportermiddlename"] = primarysource.find("reportermiddlename").text
                            else:
                                primarysource_data["reportermiddlename"]=''

                            if primarysource.find("reporterfamilyname"):
                                if primarysource.find("reporterfamilyname").text:
                                    primarysource_data["reporterfamilyname"] = primarysource.find("reporterfamilyname").text
                            else:
                                primarysource_data["reporterfamilyname"]=''

                            if primarysource.find("reporterorganization"):
                                if primarysource.find("reporterorganization").text:
                                    primarysource_data["reporterorganization"] = primarysource.find("reporterorganization").text
                            else:
                                primarysource_data["reporterorganization"]=''

                            if primarysource.find("reporterdepartment"):
                                if primarysource.find("reporterdepartment").text:
                                    primarysource_data["reporterdepartment"] = primarysource.find("reporterdepartment").text
                            else:
                                primarysource_data["reporterdepartment"]=''

                            if primarysource.find("reporterstreet"):
                                if primarysource.find("reporterstreet").text:
                                    primarysource_data['reporterstreet'] = primarysource.find("reporterstreet").text
                            else:
                                primarysource_data['reporterstreet'] = ""

                            if primarysource.find("reportercity"):
                                if primarysource.find("reportercity").text:
                                    primarysource_data['reportercity'] = primarysource.find("reportercity").text
                            else:
                                primarysource_data['reportercity'] = ""

                            if primarysource.find("reporterstate"):
                                if primarysource.find("reporterstate").text:
                                    primarysource_data['reporterstate'] = primarysource.find("reporterstate").text
                            else:
                                primarysource_data['reporterstate'] = ""

                            if primarysource.find("reporterpostcode"):
                                if primarysource.find("reporterpostcode").text:
                                    primarysource_data['reporterpostcode'] = primarysource.find("reporterpostcode").text
                            else:
                                primarysource_data['reporterpostcode'] = ""

                            if  primarysource.find("reportercountry"):
                                if  primarysource.find("reportercountry").text:
                                    primarysource_data['reportercountry'] = primarysource.find("reportercountry").text
                            else:
                                primarysource_data['reportercountry'] = ""

                            if primarysource.find("qualification"):
                                if primarysource.find("qualification").text:
                                    primarysource_data['qualification'] = primarysource.find("qualification").text
                            else:
                                primarysource_data['qualification'] = ""

                            self.insert_reporter_information_section(case_id,primarysource_data)
                            count = count + 1
                    except Exception as e:
                            self.helper.error_log(
                                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                   
                     #  case_study table  information added 
                    study_data = {}
                    try:
                        for study_primary in primarysource_info:
                            if study_primary.find("studyname"):
                                if study_primary.find("studyname").text:
                                    study_data['studyname'] = study_primary.find("studyname").text

                            if study_primary.find("sponsorstudynumb"):
                                if study_primary.find("sponsorstudynumb").text:
                                    study_data['sponsorstudynumb'] = study_primary.find("sponsorstudynumb").text

                            if study_primary.find("observestudytype"):
                                if study_primary.find("observestudytype").text:
                                    study_data['observestudytype'] = study_primary.find("observestudytype").text

                            # if len(study_data)  == 3:
                            #     break
                            if ('studyname' in study_data and 'sponsorstudynumb' in study_data and
                                    'observestudytype' in study_data):
                                break

                        self.insert_case_study_table_information(case_id, study_data)
                    except Exception as e:
                        self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    
                    try:

                        #  medical history data information added
                        medical_history_data = {}
                        count = 1
                        for  medical_tag in medicalhistoryepisode_info:
                            medical_history_data['rank'] = count

                            if medical_tag.find('patientepisodenamemeddraversion'):
                                if medical_tag.find('patientepisodenamemeddraversion').text:
                                    medical_history_data['meddra_version']= medical_tag.find('patientepisodenamemeddraversion').text
                            else:
                                medical_history_data['meddra_version']= ""

                            if medical_tag.find("patientepisodename"):
                                if medical_tag.find("patientepisodename").text:
                                    medical_history_data['meddra_llt'] = medical_tag.find("patientepisodename").text
                            else:
                                medical_history_data['meddra_llt'] = ""

                            if medical_tag.find("patientmedicalcontinue"):
                                if medical_tag.find("patientmedicalcontinue").text:
                                    medical_history_data['is_continuing'] =  medical_tag.find("patientmedicalcontinue").text
                            else:
                                medical_history_data['is_continuing'] = ""


                            if medical_tag.find("patientmedicalcomment"):
                                if medical_tag.find("patientmedicalcomment").text:
                                    medical_history_data['comments'] =  medical_tag.find("patientmedicalcomment").text
                            else:
                                medical_history_data['comments'] = ""

                            if medical_tag.find("patientmedicalstartdateformat"):
                                if medical_tag.find("patientmedicalstartdateformat").text:
                                   startdateformat = medical_tag.find("patientmedicalstartdateformat").text
                            else:
                                startdateformat = ""

                            if medical_tag.find("patientmedicalstartdate"):
                                if medical_tag.find("patientmedicalstartdate").text:
                                    medical_history_data['start_date'] =  self.helper.date_format_e2b_with_date_format_tag(
                                        medical_tag.find("patientmedicalstartdate").text, startdateformat)
                            else:
                                medical_history_data['start_date'] = ""

                            if medical_tag.find("patientmedicalenddateformat"):
                                if medical_tag.find("patientmedicalenddateformat").text:
                                   enddateformat = medical_tag.find("patientmedicalenddateformat").text
                            else:
                                enddateformat = ""

                            if medical_tag.find("patientmedicalenddate"):
                                if medical_tag.find("patientmedicalenddate").text:
                                    medical_history_data['stop_date'] =  self.helper.date_format_e2b_with_date_format_tag(
                                        medical_tag.find("patientmedicalenddate").text, enddateformat)
                            else:
                                medical_history_data['stop_date'] = ""

                            self.insert_medical_history_lab_data_information(case_id,medical_history_data)
                            count = count + 1
                    except Exception as e:
                        self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        # general tab - E2B report duplicare tab section information
                        duplicate_data = {}
                        count = 1
                        if duplicatetag_info == '1':
                            duplicate_data["duplicate"] = duplicatetag_info
                        else:
                            duplicate_data["duplicate"] = ''

                        for duplicate_tag in reportduplicate_tag:
                            rank = count
                            duplicate_data['rank'] = count
                            if duplicate_tag.find("duplicatesource"):
                                if duplicate_tag.find("duplicatesource").text:
                                    duplicate_data["duplicatesource"] = duplicate_tag.find("duplicatesource").text
                            else:
                                duplicate_data["duplicatesource"]=''

                            if duplicate_tag.find("duplicatenumb"):
                                if duplicate_tag.find("duplicatenumb").text:
                                    duplicate_data["duplicatenumb"] = duplicate_tag.find("duplicatenumb").text
                            else:
                                duplicate_data["duplicatenumb"]=''

                            self.insert_e2b_report_duplicate_section(case_id,duplicate_data)
                            count = count + 1
                    except Exception as e:
                        self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        # general tab - linkedreport tab section information
                        linkedreport_data = {}
                        count = 1
                        for link_tag in linkedreport_tag:
                            linkedreport_data['rank'] = count
                            if link_tag.find("linkreportnumb"):
                                if link_tag.find("linkreportnumb").text:
                                    linkedreport_data["linkreportnumb"] = link_tag.find(
                                        "linkreportnumb").text
                            else:
                                linkedreport_data["linkreportnumb"] = ''

                            # linkedreport_data['linked_case_no'] = case_id.case_no
                            # case_id_fk =  self.helper.get_case_id_fk(linkedreport_data["linkreportnumb"])
                            # linkedreport_data['linked_case_no'] = self.helper.get_case_no(case_id_fk)

                            if linkedreport_data["linkreportnumb"]:
                                linkedreport_data['linked_case_no'] = linkedreport_data["linkreportnumb"]
                            else:
                                linkedreport_data['linked_case_no'] = ''

                            if linkedreport_data['linked_case_no']:
                                linkedreport_data['record_type'] ='002'
                            else:
                                linkedreport_data['record_type'] =''

                            self.insert_linked_report_section(case_id, linkedreport_data)
                            count = count + 1
                    except Exception as e:
                        self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        # case narrative tab section information
                        self.insert_narrative_tab_section_info(case_id)


                        # case txt relevant  medical data section information
                        self.insert_text_relevant_medical_data_information(case_id)


                        # case past drug therapy data section information
                        past_drug_data = {}
                        count = 1
                        for pastdrugtherapy_tag in patientpastdrugtherapy_tag:
                            past_drug_data['rank'] = count
                            if pastdrugtherapy_tag.find("patientdrugname"):
                                if pastdrugtherapy_tag.find("patientdrugname").text:
                                    past_drug_data['drug_hist_rpt'] = pastdrugtherapy_tag.find("patientdrugname").text
                            else:
                                past_drug_data['drug_hist_rpt'] = ''

                            if pastdrugtherapy_tag.find("patientdrugstartdateformat"):
                                if pastdrugtherapy_tag.find("patientdrugstartdateformat").text:
                                   drug_startdateformat = pastdrugtherapy_tag.find("patientdrugstartdateformat").text
                            else:
                                drug_startdateformat = ""

                            if pastdrugtherapy_tag.find("patientdrugstartdate"):
                                if pastdrugtherapy_tag.find("patientdrugstartdate").text:
                                    past_drug_data['ind_start_date'] = self.helper.date_format_e2b_with_date_format_tag(
                                        pastdrugtherapy_tag.find("patientdrugstartdate").text, drug_startdateformat)
                            else:
                                past_drug_data['ind_start_date'] = ''

                            if pastdrugtherapy_tag.find("patientdrugenddateformat"):
                                if pastdrugtherapy_tag.find("patientdrugenddateformat").text:
                                   drug_enddateformat = pastdrugtherapy_tag.find("patientdrugenddateformat").text
                            else:
                                drug_enddateformat = ""

                            if pastdrugtherapy_tag.find("patientdrugenddate"):
                                if pastdrugtherapy_tag.find("patientdrugenddate").text:
                                    past_drug_data['ind_stop_date'] = self.helper.date_format_e2b_with_date_format_tag(
                                        pastdrugtherapy_tag.find("patientdrugenddate").text, drug_enddateformat)
                            else:
                                past_drug_data['ind_stop_date'] = ''

                            if pastdrugtherapy_tag.find("patientindicationmeddraversion"):
                                if pastdrugtherapy_tag.find("patientindicationmeddraversion").text:
                                    past_drug_data['lab_data_version'] = pastdrugtherapy_tag.find("patientindicationmeddraversion").text
                            else:
                                past_drug_data['lab_data_version'] = ''

                            if pastdrugtherapy_tag.find("patientdrugindication"):
                                if pastdrugtherapy_tag.find("patientdrugindication").text:
                                    past_drug_data['lab_data_llt'] = pastdrugtherapy_tag.find("patientdrugindication").text
                            else:
                                past_drug_data['lab_data_llt'] = ''

                            if pastdrugtherapy_tag.find("patientdrugreaction"):
                                if pastdrugtherapy_tag.find("patientdrugreaction").text:
                                    past_drug_data['patientdrugreaction'] = pastdrugtherapy_tag.find("patientdrugreaction").text
                            else:
                                past_drug_data['patientdrugreaction'] = ''

                            if pastdrugtherapy_tag.find("patientdrgreactionmeddraversion"):
                                if pastdrugtherapy_tag.find("patientdrgreactionmeddraversion").text:
                                    past_drug_data['patientdrgreactionmeddraversion'] = pastdrugtherapy_tag.find("patientdrgreactionmeddraversion").text
                            else:
                                past_drug_data['patientdrgreactionmeddraversion'] = ''

                            self.insert_relevant_past_drug_data_tab_section_info(case_id, past_drug_data)
                            count = count + 1
                    except Exception as e:
                        self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                    try:
                        # case lab data  info - section information
                        lab_data = {}
                        count = 1
                        for test_tag in test_tag_info:
                            lab_data['rank'] = count
                            if test_tag.find("testname"):
                                if test_tag.find("testname").text:
                                    lab_data['lab_meddra_llt'] = test_tag.find("testname").text
                            else:
                                lab_data['lab_meddra_llt'] = ""

                            if test_tag.find("testresult"):
                                if test_tag.find("testresult").text:
                                    lab_data['test_result_value'] = test_tag.find("testresult").text
                            else:
                                lab_data['test_result_value'] = ""

                            if test_tag.find("testunit"):
                                if test_tag.find("testunit").text:
                                    lab_data['test_result_units'] = test_tag.find("testunit").text
                            else:
                                lab_data['test_result_units'] = ""

                            if test_tag.find("lowtestrange"):
                                if test_tag.find("lowtestrange").text:
                                    lab_data['normal_low_range'] = test_tag.find("lowtestrange").text
                            else:
                                lab_data['normal_low_range'] = ""

                            if test_tag.find("hightestrange"):
                                if test_tag.find("hightestrange").text:
                                    lab_data['normal_high_range'] = test_tag.find("hightestrange").text
                            else:
                                lab_data['normal_high_range'] = ""

                            if test_tag.find("testdateformat"):
                                if test_tag.find("testdateformat").text:
                                    testdateformat = test_tag.find("testdateformat").text
                            else:
                                testdateformat = ""

                            if test_tag.find("testdate"):
                                if test_tag.find("testdate").text:
                                    lab_data['testdate'] = self.helper.date_format_e2b_with_date_format_tag(
                                        test_tag.find("testdate").text, testdateformat)
                            else:
                                lab_data['testdate'] = ''


                            self.insert_medical_lab_data_tab_section_info(case_id, lab_data)
                            count = count + 1
                    except Exception as e:
                        self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    
                    try:
                        # general tab - case type summary section information added
                        self.insert_case_summary_section(case_id)

                        # Reaction tab information added
                        reaction_count=1
                        for reaction in reactioninfo:
                            if reaction.find("primarysourcereaction"):
                                if reaction.find("primarysourcereaction").text:
                                    primarysourcereaction = reaction.find("primarysourcereaction").text
                                else:
                                    primarysourcereaction=''
                            else:
                                primarysourcereaction= ''

                            if reaction.find("reactionmeddraversionllt"):
                                if reaction.find("reactionmeddraversionllt").text:
                                    reactionmeddraversionllt = reaction.find("reactionmeddraversionllt").text
                                else:
                                    reactionmeddraversionllt=''

                            else:
                                reactionmeddraversionllt=''

                            if reaction.find("reactionmeddrallt"):
                                if reaction.find("reactionmeddrallt").text:
                                    reactionmeddrallt = reaction.find("reactionmeddrallt").text
                                else:
                                    reactionmeddrallt=''
                            else:
                                reactionmeddrallt=''


                            if reaction.find("reactionmeddraversionpt"):
                                if reaction.find("reactionmeddraversionpt").text:
                                    reactionmeddraversionpt = reaction.find("reactionmeddraversionpt").text
                                else:
                                    reactionmeddraversionpt=''

                            else:
                                reactionmeddraversionpt=''

                            if reaction.find("reactionmeddrapt"):
                                if reaction.find("reactionmeddrapt").text:
                                    reactionmeddrapt = reaction.find("reactionmeddrapt").text
                                else:
                                    reactionmeddrapt =''

                            else:
                                reactionmeddrapt =''

                            if  reaction.find("reactionstartdateformat"):
                                if  reaction.find("reactionstartdateformat").text:
                                    reactionstartdateformat = reaction.find("reactionstartdateformat").text
                                else:
                                    reactionstartdateformat=''
                            else:
                                reactionstartdateformat=''

                            if reaction.find("reactionstartdate"):
                                if reaction.find("reactionstartdate").text:
                                    reactionstartdate = reaction.find("reactionstartdate").text
                                else:
                                    reactionstartdate=''
                            else:
                                reactionstartdate=''

                            if reaction.find("reactionfirsttime"):
                                if reaction.find("reactionfirsttime").text:
                                    reactionfirsttime = reaction.find("reactionfirsttime").text
                                else:
                                    reactionfirsttime=''
                            else:
                                reactionfirsttime=''

                            if  reaction.find("reactionfirsttimeunit"):
                                if reaction.find("reactionfirsttimeunit").text:
                                    reactionfirsttimeunit = reaction.find("reactionfirsttimeunit").text
                                else:
                                    reactionfirsttimeunit=''
                            else:
                                reactionfirsttimeunit=''

                            if reaction.find("reactionoutcome"):
                                if reaction.find("reactionoutcome").text:
                                    reactionoutcome = reaction.find("reactionoutcome").text
                                else:
                                    reactionoutcome=''
                            else:
                                reactionoutcome=''

                            if reaction.find("termhighlighted"):
                                if reaction.find("termhighlighted").text:
                                    reaction_termhighlighted = reaction.find("termhighlighted").text
                                else:
                                    reaction_termhighlighted=''
                            else:
                                reaction_termhighlighted=''

                            if reaction.find("rcountry_rectn_occr"):
                                if reaction.find("rcountry_rectn_occr").text:
                                    rcountry_rectn_occr = reaction.find("rcountry_rectn_occr").text
                                else:
                                    rcountry_rectn_occr=''
                            else:
                                rcountry_rectn_occr=''

                            if reaction.find("medically_confirmed"):
                                if reaction.find("medically_confirmed").text:
                                    medically_confirmed = reaction.find("medically_confirmed").text
                                else:
                                    medically_confirmed=''
                            else:
                                medically_confirmed=''

                            if reaction.find("medically_confirmed"):
                                if reaction.find("medically_confirmed").text:
                                    medically_confirmed = reaction.find("medically_confirmed").text
                                else:
                                    medically_confirmed=''
                            else:
                                medically_confirmed=''

                            if reaction.find("serious"):
                                if reaction.find("serious").text:
                                    serious = reaction.find("serious").text
                                else:
                                    serious=''
                            else:
                                serious=''

                            if  reaction.find("reactionenddateformat"):
                                if  reaction.find("reactionenddateformat").text:
                                    reactionenddateformat = reaction.find("reactionenddateformat").text
                                else:
                                    reactionenddateformat=''
                            else:
                                reactionenddateformat=''

                            if reaction.find("reactionenddate"):
                                if reaction.find("reactionenddate").text:
                                    reactionenddate = reaction.find("reactionenddate").text
                                else:
                                    reactionenddate=''
                            else:
                                reactionenddate=''

                            if reaction.find("reactionduration"):
                                if reaction.find("reactionduration").text:
                                    reactionduration = reaction.find("reactionduration").text
                                else:
                                    reactionduration=''
                            else:
                                reactionduration=''

                            if reaction.find("reactiondurationunit"):
                                if reaction.find("reactiondurationunit").text:
                                    reactiondurationunit = reaction.find("reactiondurationunit").text
                                else:
                                    reactiondurationunit=''
                            else:
                                reactiondurationunit=''

                            reaction_count = reaction_count

                            reaction_data = {"primarysourcereaction": primarysourcereaction,
                            "reactionmeddraversionllt":reactionmeddraversionllt,
                            "reactionmeddrallt":reactionmeddrallt,
                            "reactionmeddraversionpt":reactionmeddraversionpt,
                            "reactionmeddrapt":reactionmeddrapt,
                            "reactionfirsttime":reactionfirsttime,
                            "reactionstartdateformat":reactionstartdateformat,
                            "reactionstartdate":reactionstartdate,
                            "reactionfirsttimeunit":reactionfirsttimeunit,
                            "reactionoutcome":reactionoutcome,
                            "termhighlighted":reaction_termhighlighted,
                            "rcountry_rectn_occr":rcountry_rectn_occr,
                            "medically_confirmed":medically_confirmed,
                            "serious":serious,
                            "reactionenddateformat":reactionenddateformat,
                            "reactionenddate":reactionenddate,
                            "reactionduration":reactionduration,
                            "reactiondurationunit":reactiondurationunit,
                            "reaction_count":reaction_count

                             }
                            reaction_id = self.insert_reaction_information_section(case_id,reaction_data)
                            reaction_count = reaction_count + 1
                    except Exception as e:
                        self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    

                    # insert Product tab data
                    product_count=1
                    unique_product_id = 1
                    try:
                        for product in productinfo:
                            if (product_count == 1):
                                if product.find("drugcharacterization"):
                                    if product.find("drugcharacterization").text:
                                        drugcharacterization = product.find("drugcharacterization").text
                                    else:
                                        drugcharacterization = ''
                                else:
                                    drugcharacterization = ''

                                if product.find("medicinalproduct"):
                                    if product.find("medicinalproduct").text:
                                        medicinalproduct = product.find("medicinalproduct").text
                                    else:
                                        medicinalproduct = ''
                                else:
                                    medicinalproduct = ''

                                if product.find("drugdosageform"):
                                    if product.find("drugdosageform").text:
                                        drugdosageform = product.find("drugdosageform").text
                                    else:
                                        drugdosageform = ''
                                else:
                                    drugdosageform = ''

                                if product.find("obtaindrugcountry"):
                                    if product.find("obtaindrugcountry").text:
                                        obtaindrugcountry = product.find("obtaindrugcountry").text
                                    else:
                                        obtaindrugcountry = ''
                                else:
                                    obtaindrugcountry = ''

                                if product.find("drugauthorizationcountry"):
                                    if product.find("drugauthorizationcountry").text:
                                        drugauthorizationcountry = product.find("drugauthorizationcountry").text
                                    else:
                                        drugauthorizationcountry = ''
                                else:
                                    drugauthorizationcountry = ''

                                if product.find("actiondrug"):
                                    if product.find("actiondrug").text:
                                        actiondrug = product.find("actiondrug").text
                                    else:
                                        actiondrug = ''
                                else:
                                    actiondrug = ''

                                if product.find("drugindication"):
                                    if product.find("drugindication").text:
                                        drugindication = product.find("drugindication").text
                                    else:
                                        drugindication = ''
                                else:
                                    drugindication = ''

                                if product.find("drugauthorizationnumb"):
                                    if product.find("drugauthorizationnumb").text:
                                        drugauthorizationnumb = product.find("drugauthorizationnumb").text
                                    else:
                                        drugindication = ''
                                else:
                                    drugauthorizationnumb = ''

                                if product.find("drugauthorizationholder"):
                                    if product.find("drugauthorizationholder").text:
                                        drugauthorizationholder = product.find("drugauthorizationholder").text
                                    else:
                                        drugauthorizationholder = ''
                                else:
                                    drugauthorizationholder = ''

                                if product.find("drugcumulativedosagenumb"):
                                    if product.find("drugcumulativedosagenumb").text:
                                        drugcumulativedosagenumb = product.find("drugcumulativedosagenumb").text
                                    else:
                                        drugcumulativedosagenumb = ''
                                else:
                                    drugcumulativedosagenumb = ''

                                if product.find("reactiongestationperiod"):
                                    if product.find("reactiongestationperiod").text:
                                        reactiongestationperiod = product.find("reactiongestationperiod").text
                                else:
                                    reactiongestationperiod = ''

                                if product.find("reactiongestationperiodunit"):
                                    if product.find("reactiongestationperiodunit").text:
                                        reactiongestationperiodunit = product.find("reactiongestationperiodunit").text
                                else:
                                    reactiongestationperiodunit = ''

                                if product.find("drugadditional"):
                                    if product.find("drugadditional").text:
                                        drugadditional = product.find("drugadditional").text
                                else:
                                    drugadditional = ''

                                product_data = {"drugcharacterization": drugcharacterization,
                                                "medicinalproduct": medicinalproduct,
                                                "drugdosageform": drugdosageform,
                                                "obtaindrugcountry": obtaindrugcountry,
                                                "drugauthorizationcountry": drugauthorizationcountry,
                                                "drugauthorizationnumb": drugauthorizationnumb,
                                                "drugindication": drugindication,
                                                "actiondrug": actiondrug,
                                                "drugauthorizationholder": drugauthorizationholder,
                                                "drugcumulativedosagenumb": drugcumulativedosagenumb,
                                                "reactiongestationperiod": reactiongestationperiod,
                                                "reactiongestationperiodunit": reactiongestationperiodunit,
                                                "unique_product_id": unique_product_id,
                                                "drugadditional": drugadditional,
                                                "drugindication": drugindication
                                                }

                                product_id = self.insert_product_information_section(case_id, product_data)
                                unique_product_id = unique_product_id + 1

                                # insert active_substance
                                activesbstancerank = 1
                                if product.findChildren("activesubstance"):
                                    activesubstanceinfo = product.findChildren("activesubstance")
                                    # act_subs_name = {activesubstanceinfo}
                                    for activesubstancedata in activesubstanceinfo:
                                        if activesubstancedata.find("activesubstancename").text:
                                            act_name = activesubstancedata.find("activesubstancename").text

                                        activesubstancedata = {"activesubstancename": act_name,
                                                               "rank": activesbstancerank}
                                        self.insert_product_active_sub_information_section(case_id, product_id,
                                                                                           activesubstancedata)
                                        activesbstancerank = activesbstancerank + 1

                                # insert dosage_regimen_section
                                if product.find("drugstructuredosagenumb"):
                                    if product.find("drugstructuredosagenumb").text:
                                        drugstructuredosagenumb = product.find("drugstructuredosagenumb").text
                                    else:
                                        drugstructuredosagenumb = ''
                                else:
                                    drugstructuredosagenumb = ''

                                if product.find("drugstructuredosageunit"):
                                    if product.find("drugstructuredosageunit").text:
                                        drugstructuredosageunit = product.find("drugstructuredosageunit").text
                                    else:
                                        drugstructuredosageunit = ''
                                else:
                                    drugstructuredosageunit = ''

                                if product.find("drugdosagetext"):
                                    if product.find("drugdosagetext").text:
                                        drugdosagetext = product.find("drugdosagetext").text
                                    else:
                                        drugdosagetext = ''
                                else:
                                    drugdosagetext = ''

                                if product.find("drugadministrationroute"):
                                    if product.find("drugadministrationroute").text:
                                        drugadministrationroute = product.find("drugadministrationroute").text
                                    else:
                                        drugadministrationroute = ''
                                else:
                                    drugadministrationroute = ''

                                if product.find("drugbatchnumb"):
                                    if product.find("drugbatchnumb").text:
                                        drugbatchnumb = product.find("drugbatchnumb").text
                                    else:
                                        drugbatchnumb = ''
                                else:
                                    drugbatchnumb = ''

                                if product.find("drugstartdate"):
                                    if product.find("drugstartdate").text:
                                        drugstartdate = product.find("drugstartdate").text
                                else:
                                    drugstartdate = ''

                                if product.find("drugenddate"):
                                    if product.find("drugenddate").text:
                                        drugenddate = product.find("drugenddate").text
                                else:
                                    drugenddate = ''

                                if product.find("drugtreatmentduration"):
                                    if product.find("drugtreatmentduration").text:
                                        drugtreatmentduration = product.find("drugtreatmentduration").text
                                else:
                                    drugtreatmentduration = ''

                                if product.find("drugtreatmentdurationunit"):
                                    if product.find("drugtreatmentdurationunit").text:
                                        drugtreatmentdurationunit = product.find("drugtreatmentdurationunit").text
                                else:
                                    drugtreatmentdurationunit = ''

                                if product.find("drugparadministration"):
                                    if product.find("drugparadministration").text:
                                        drugparadministration = product.find("drugparadministration").text
                                else:
                                    drugparadministration = ''

                                if product.find("drugstartdateformat"):
                                    if product.find("drugstartdateformat").text:
                                        drugstartdateformat = product.find("drugstartdateformat").text
                                else:
                                    drugstartdateformat = ''

                                if product.find("drugenddateformat"):
                                    if product.find("drugenddateformat").text:
                                        drugenddateformat = product.find("drugenddateformat").text
                                else:
                                    drugenddateformat = ''

                                proddosageregimendata = {"drugstructuredosagenumb": drugstructuredosagenumb,
                                                         "drugstructuredosageunit": drugstructuredosageunit,
                                                         "drugdosagetext": drugdosagetext,
                                                         "drugbatchnumb": drugbatchnumb,
                                                         "drugadministrationroute": drugadministrationroute,
                                                         "rank": activesbstancerank,
                                                         "drugstartdate": drugstartdate,
                                                         "drugenddate": drugenddate,
                                                         "drugtreatmentduration": drugtreatmentduration,
                                                         "drugtreatmentdurationunit": drugtreatmentdurationunit,
                                                         "drugparadministration": drugparadministration,
                                                         "drugstartdateformat": drugstartdateformat,
                                                         "drugenddateformat": drugenddateformat}

                                self.insert_case_prod_dosage_regimen_section(case_id, product_id, proddosageregimendata)

                                # insert case_prod_indication
                                if product.find("drugindication"):
                                    if product.find("drugindication").text:
                                        drugindication = product.find("drugindication").text
                                else:
                                    drugindication = ''

                                if product.find("drugindicationmeddraversion"):
                                    if product.find("drugindicationmeddraversion").text:
                                        drugindicationmeddraversion = product.find("drugindicationmeddraversion").text
                                else:
                                    drugindicationmeddraversion = ''

                                prodindicationdata = {"drugindication": drugindication,
                                                      "drugindicationmeddraversion": drugindicationmeddraversion}

                                self.insert_case_prod_indication_section(case_id, product_id, prodindicationdata)

                                product_count = product_count + 1
                            else:
                                if product.find("drugcharacterization"):
                                    if product.find("drugcharacterization").text:
                                        drugcharacterization1 = product.find("drugcharacterization").text
                                    else:
                                        drugcharacterization1 = ''
                                else:
                                    drugcharacterization1 = ''

                                if product.find("medicinalproduct"):
                                    if product.find("medicinalproduct").text:
                                        medicinalproduct1 = product.find("medicinalproduct").text
                                    else:
                                        medicinalproduct1 = ''
                                else:
                                    medicinalproduct1 = ''

                                if ((drugcharacterization1 == drugcharacterization) and (
                                        medicinalproduct1 == medicinalproduct)):

                                    if product.find("drugstructuredosagenumb"):
                                        if product.find("drugstructuredosagenumb").text:
                                            drugstructuredosagenumb = product.find("drugstructuredosagenumb").text
                                        else:
                                            drugstructuredosagenumb = ''
                                    else:
                                        drugstructuredosagenumb = ''

                                    if product.find("drugstructuredosageunit"):
                                        if product.find("drugstructuredosageunit").text:
                                            drugstructuredosageunit = product.find("drugstructuredosageunit").text
                                        else:
                                            drugstructuredosageunit = ''
                                    else:
                                        drugstructuredosageunit = ''

                                    if product.find("drugdosagetext"):
                                        if product.find("drugdosagetext").text:
                                            drugdosagetext = product.find("drugdosagetext").text
                                        else:
                                            drugdosagetext = ''
                                    else:
                                        drugdosagetext = ''

                                    if product.find("drugadministrationroute"):
                                        if product.find("drugadministrationroute").text:
                                            drugadministrationroute = product.find("drugadministrationroute").text
                                        else:
                                            drugadministrationroute = ''
                                    else:
                                        drugadministrationroute = ''

                                    if product.find("drugbatchnumb"):
                                        if product.find("drugbatchnumb").text:
                                            drugbatchnumb = product.find("drugbatchnumb").text
                                        else:
                                            drugbatchnumb = ''
                                    else:
                                        drugbatchnumb = ''

                                    if product.find("drugstartdate"):
                                        if product.find("drugstartdate").text:
                                            drugstartdate = product.find("drugstartdate").text
                                    else:
                                        drugstartdate = ''

                                    if product.find("drugenddate"):
                                        if product.find("drugenddate").text:
                                            drugenddate = product.find("drugenddate").text
                                    else:
                                        drugenddate = ''
                                    if product.find("drugtreatmentduration"):
                                        if product.find("drugtreatmentduration").text:
                                            drugtreatmentduration = product.find("drugtreatmentduration").text
                                    else:
                                        drugtreatmentduration = ''

                                    if product.find("drugtreatmentdurationunit"):
                                        if product.find("drugtreatmentdurationunit").text:
                                            drugtreatmentdurationunit = product.find("drugtreatmentdurationunit").text
                                    else:
                                        drugtreatmentdurationunit = ''

                                    if product.find("drugparadministration"):
                                        if product.find("drugparadministration").text:
                                            drugparadministration = product.find("drugparadministration").text
                                    else:
                                        drugparadministration = ''

                                    if product.find("drugstartdateformat"):
                                        if product.find("drugstartdateformat").text:
                                            drugstartdateformat = product.find("drugstartdateformat").text
                                    else:
                                        drugstartdateformat = ''

                                    if product.find("drugenddateformat"):
                                        if product.find("drugenddateformat").text:
                                            drugenddateformat = product.find("drugenddateformat").text
                                    else:
                                        drugenddateformat = ''

                                    proddosageregimendata = {"drugstructuredosagenumb": drugstructuredosagenumb,
                                                             "drugstructuredosageunit": drugstructuredosageunit,
                                                             "drugdosagetext": drugdosagetext,
                                                             "drugbatchnumb": drugbatchnumb,
                                                             "drugadministrationroute": drugadministrationroute,
                                                             "rank": activesbstancerank,
                                                             "drugstartdate": drugstartdate,
                                                             "drugenddate": drugenddate,
                                                             "drugtreatmentduration": drugtreatmentduration,
                                                             "drugtreatmentdurationunit": drugtreatmentdurationunit,
                                                             "drugparadministration": drugparadministration,
                                                             "drugstartdateformat": drugstartdateformat,
                                                             "drugenddateformat": drugenddateformat}

                                    self.insert_case_prod_dosage_regimen_section(case_id, product_id,
                                                                                 proddosageregimendata)

                                else:
                                    if product.find("drugcharacterization"):
                                        if product.find("drugcharacterization").text:
                                            drugcharacterization = product.find("drugcharacterization").text
                                        else:
                                            drugcharacterization = ''
                                    else:
                                        drugcharacterization = ''

                                    if product.find("medicinalproduct"):
                                        if product.find("medicinalproduct").text:
                                            medicinalproduct = product.find("medicinalproduct").text
                                        else:
                                            medicinalproduct = ''
                                    else:
                                        medicinalproduct = ''

                                    if product.find("drugdosageform"):
                                        if product.find("drugdosageform").text:
                                            drugdosageform = product.find("drugdosageform").text
                                        else:
                                            drugdosageform = ''
                                    else:
                                        drugdosageform = ''

                                    if product.find("obtaindrugcountry"):
                                        if product.find("obtaindrugcountry").text:
                                            obtaindrugcountry = product.find("obtaindrugcountry").text
                                        else:
                                            obtaindrugcountry = ''
                                    else:
                                        obtaindrugcountry = ''

                                    if product.find("drugauthorizationcountry"):
                                        if product.find("drugauthorizationcountry").text:
                                            drugauthorizationcountry = product.find("drugauthorizationcountry").text
                                        else:
                                            drugauthorizationcountry = ''
                                    else:
                                        drugauthorizationcountry = ''

                                    if product.find("actiondrug"):
                                        if product.find("actiondrug").text:
                                            actiondrug = product.find("actiondrug").text
                                        else:
                                            actiondrug = ''
                                    else:
                                        actiondrug = ''

                                    if product.find("drugindication"):
                                        if product.find("drugindication").text:
                                            drugindication = product.find("drugindication").text
                                        else:
                                            drugindication = ''
                                    else:
                                        drugindication = ''

                                    if product.find("drugauthorizationnumb"):
                                        if product.find("drugauthorizationnumb").text:
                                            drugauthorizationnumb = product.find("drugauthorizationnumb").text
                                        else:
                                            drugindication = ''
                                    else:
                                        drugauthorizationnumb = ''

                                    if product.find("drugauthorizationholder"):
                                        if product.find("drugauthorizationholder").text:
                                            drugauthorizationholder = product.find("drugauthorizationholder").text
                                        else:
                                            drugauthorizationholder = ''
                                    else:
                                        drugauthorizationholder = ''

                                    if product.find("drugcumulativedosagenumb"):
                                        if product.find("drugcumulativedosagenumb").text:
                                            drugcumulativedosagenumb = product.find("drugcumulativedosagenumb").text
                                        else:
                                            drugcumulativedosagenumb = ''
                                    else:
                                        drugcumulativedosagenumb = ''

                                    if product.find("reactiongestationperiod"):
                                        if product.find("reactiongestationperiod").text:
                                            reactiongestationperiod = product.find("reactiongestationperiod").text
                                    else:
                                        reactiongestationperiod = ''

                                    if product.find("reactiongestationperiodunit"):
                                        if product.find("reactiongestationperiodunit").text:
                                            reactiongestationperiodunit = product.find(
                                                "reactiongestationperiodunit").text
                                    else:
                                        reactiongestationperiodunit = ''

                                    if product.find("drugadditional"):
                                        if product.find("drugadditional").text:
                                            drugadditional = product.find("drugadditional").text
                                    else:
                                        drugadditional = ''

                                    product_data = {"drugcharacterization": drugcharacterization1,
                                                    "medicinalproduct": medicinalproduct1,
                                                    "drugdosageform": drugdosageform,
                                                    "obtaindrugcountry": obtaindrugcountry,
                                                    "drugauthorizationcountry": drugauthorizationcountry,
                                                    "drugauthorizationnumb": drugauthorizationnumb,
                                                    "drugindication": drugindication,
                                                    "actiondrug": actiondrug,
                                                    "drugauthorizationholder": drugauthorizationholder,
                                                    "drugcumulativedosagenumb": drugcumulativedosagenumb,
                                                    "reactiongestationperiod": reactiongestationperiod,
                                                    "reactiongestationperiodunit": reactiongestationperiodunit,
                                                    "unique_product_id": unique_product_id,
                                                    "drugadditional": drugadditional
                                                    }

                                    product_id = self.insert_product_information_section(case_id, product_data)
                                    unique_product_id = unique_product_id + 1

                                    activesbstancerank = 1
                                    if product.findChildren("activesubstance"):
                                        activesubstanceinfo = product.findChildren("activesubstance")
                                        # act_subs_name = {activesubstanceinfo}
                                        for activesubstancedata in activesubstanceinfo:
                                            if activesubstancedata.find("activesubstancename").text:
                                                act_name = activesubstancedata.find("activesubstancename").text

                                            activesubstancedata = {"activesubstancename": act_name,
                                                                   "rank": activesbstancerank}
                                            self.insert_product_active_sub_information_section(case_id, product_id,
                                                                                               activesubstancedata)
                                            activesbstancerank = activesbstancerank + 1

                                    if product.find("drugstructuredosagenumb"):
                                        if product.find("drugstructuredosagenumb").text:
                                            drugstructuredosagenumb = product.find("drugstructuredosagenumb").text
                                        else:
                                            drugstructuredosagenumb = ''
                                    else:
                                        drugstructuredosagenumb = ''

                                    if product.find("drugstructuredosageunit"):
                                        if product.find("drugstructuredosageunit").text:
                                            drugstructuredosageunit = product.find("drugstructuredosageunit").text
                                        else:
                                            drugstructuredosageunit = ''
                                    else:
                                        drugstructuredosageunit = ''

                                    if product.find("drugdosagetext"):
                                        if product.find("drugdosagetext").text:
                                            drugdosagetext = product.find("drugdosagetext").text
                                        else:
                                            drugdosagetext = ''
                                    else:
                                        drugdosagetext = ''

                                    if product.find("drugadministrationroute"):
                                        if product.find("drugadministrationroute").text:
                                            drugadministrationroute = product.find("drugadministrationroute").text
                                        else:
                                            drugadministrationroute = ''
                                    else:
                                        drugadministrationroute = ''

                                    if product.find("drugbatchnumb"):
                                        if product.find("drugbatchnumb").text:
                                            drugbatchnumb = product.find("drugbatchnumb").text
                                        else:
                                            drugbatchnumb = ''
                                    else:
                                        drugbatchnumb = ''

                                    if product.find("drugstartdate"):
                                        if product.find("drugstartdate").text:
                                            drugstartdate = product.find("drugstartdate").text
                                    else:
                                        drugstartdate = ''

                                    if product.find("drugenddate"):
                                        if product.find("drugenddate").text:
                                            drugenddate = product.find("drugenddate").text
                                    else:
                                        drugenddate = ''

                                    if product.find("drugtreatmentduration"):
                                        if product.find("drugtreatmentduration").text:
                                            drugtreatmentduration = product.find("drugtreatmentduration").text
                                    else:
                                        drugtreatmentduration = ''

                                    if product.find("drugtreatmentdurationunit"):
                                        if product.find("drugtreatmentdurationunit").text:
                                            drugtreatmentdurationunit = product.find("drugtreatmentdurationunit").text
                                    else:
                                        drugtreatmentdurationunit = ''

                                    if product.find("drugparadministration"):
                                        if product.find("drugparadministration").text:
                                            drugparadministration = product.find("drugparadministration").text
                                    else:
                                        drugparadministration = ''

                                    if product.find("drugstartdateformat"):
                                        if product.find("drugstartdateformat").text:
                                            drugstartdateformat = product.find("drugstartdateformat").text
                                    else:
                                        drugstartdateformat = ''

                                    if product.find("drugenddateformat"):
                                        if product.find("drugenddateformat").text:
                                            drugenddateformat = product.find("drugenddateformat").text
                                    else:
                                        drugenddateformat = ''
                                    proddosageregimendata = {"drugstructuredosagenumb": drugstructuredosagenumb,
                                                             "drugstructuredosageunit": drugstructuredosageunit,
                                                             "drugdosagetext": drugdosagetext,
                                                             "drugbatchnumb": drugbatchnumb,
                                                             "drugadministrationroute": drugadministrationroute,
                                                             "rank": activesbstancerank,
                                                             "drugstartdate": drugstartdate,
                                                             "drugenddate": drugenddate,
                                                             "drugtreatmentduration": drugtreatmentduration,
                                                             "drugtreatmentdurationunit": drugtreatmentdurationunit,
                                                             "drugparadministration": drugparadministration,
                                                             "drugstartdateformat": drugstartdateformat,
                                                             "drugenddateformat": drugenddateformat}

                                    self.insert_case_prod_dosage_regimen_section(case_id, product_id,
                                                                                 proddosageregimendata)

                                    # insert case_prod_indication
                                    if product.find("drugindication"):
                                        if product.find("drugindication").text:
                                            drugindication = product.find("drugindication").text
                                    else:
                                        drugindication = ''

                                    if product.find("drugindicationmeddraversion"):
                                        if product.find("drugindicationmeddraversion").text:
                                            drugindicationmeddraversion = product.find(
                                                "drugindicationmeddraversion").text
                                    else:
                                        drugindicationmeddraversion = ''

                                    prodindicationdata = {"drugindication": drugindication,
                                                          "drugindicationmeddraversion": drugindicationmeddraversion}

                                    self.insert_case_prod_indication_section(case_id, product_id, prodindicationdata)
                    except Exception as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                                

                    #Insert case_causality table data
                    
                    causality_id_pk = self.insert_case_causality_section(case_id)

                    #insert case_causality_reaction table data
                    prodcount = 1
                    try:
                        for product in productinfo:
                            if (prodcount == 1):
                                try:
                                    if product.find("drugcharacterization"):
                                        if product.find("drugcharacterization").text:
                                            drugcharacterization_causality= product.find("drugcharacterization").text
                                        else:
                                            drugcharacterization_causality=''
                                    else:
                                        drugcharacterization_causality=''

                                    if product.find("medicinalproduct"):
                                        if product.find("medicinalproduct").text:
                                            medicinalproduct_causality= product.find("medicinalproduct").text
                                        else:
                                            medicinalproduct_causality=''
                                    else:
                                        medicinalproduct_causality=''

                                    reactionloopcout = 1
                                    for reactiondata in reactioninfo:

                                        drugstartperiod_causality = ''
                                        drugstartperiodunit_causality = ''
                                        druglastperiod_causality = ''
                                        druglastperiodunit_causality = ''
                                        drugrecurreadministration = ''

                                        if reactiondata.find("reactionmeddraversionllt").text:
                                            reactionmeddraversionllt= reactiondata.find("reactionmeddraversionllt").text
                                        else:
                                            reactionmeddraversionllt = ''

                                        if reactiondata.find("reactionmeddrallt").text:
                                            reactionmeddrallt= reactiondata.find("reactionmeddrallt").text
                                        else:
                                            reactionmeddrallt = ''
                                        if (reactionloopcout == 1):
                                            if product.find("drugstartperiod"):
                                                if product.find("drugstartperiod").text:
                                                    drugstartperiod_causality= product.find("drugstartperiod").text
                                                else:
                                                    drugstartperiod_causality=''
                                            else:
                                                drugstartperiod_causality=''

                                            if product.find("drugstartperiodunit"):
                                                if product.find("drugstartperiodunit").text:
                                                    drugstartperiodunit_causality= product.find("drugstartperiodunit").text
                                                else:
                                                    drugstartperiodunit_causality=''
                                            else:
                                                drugstartperiodunit_causality=''

                                            if product.find("druglastperiod"):
                                                if product.find("druglastperiod").text:
                                                    druglastperiod_causality= product.find("druglastperiod").text
                                                else:
                                                    druglastperiod_causality=''
                                            else:
                                                druglastperiod_causality=''

                                            if product.find("druglastperiodunit"):
                                                if product.find("druglastperiodunit").text:
                                                    druglastperiodunit_causality= product.find("druglastperiodunit").text
                                                else:
                                                    druglastperiodunit_causality=''
                                            else:
                                                druglastperiodunit_causality=''

                                        ''' below drugrecurrence and drugrecuractionmeddraversion taking for 
                                            finding reaction_id_fk to insert case_reaction data '''

                                        insertdone = 1
                                        if product.findChildren("drugrecurrence"):
                                            drugrecurrenceinfo = product.findChildren("drugrecurrence")
                                            for drugrecurrencedata in drugrecurrenceinfo:
                                                if drugrecurrencedata.find("drugrecuractionmeddraversion").text:
                                                    drugrecuractionmeddraversion= drugrecurrencedata.find("drugrecuractionmeddraversion").text
                                                else:
                                                    drugrecuractionmeddraversion = ''

                                                if drugrecurrencedata.find("drugrecuraction").text:
                                                    drugrecuraction= drugrecurrencedata.find("drugrecuraction").text
                                                else:
                                                    drugrecuraction = ''

                                                if ((drugrecuractionmeddraversion == reactionmeddraversionllt) and (drugrecuraction == reactionmeddrallt) and (insertdone == 1)):
                                                    if product.find("drugrecurreadministration"):
                                                        if product.find("drugrecurreadministration").text:
                                                            drugrecurreadministration= product.find("drugrecurreadministration").text
                                                        else:
                                                            drugrecurreadministration=''
                                                    else:
                                                        drugrecurreadministration=''

                                                    casecausalityreactiondata = {"drugrecurreadministration": drugrecurreadministration,
                                                    "rank":count,
                                                    "drugrecuractionmeddraversion": drugrecuractionmeddraversion,
                                                    "drugrecuraction": drugrecuraction,
                                                    "drugcharacterization_causality": drugcharacterization_causality,
                                                    "medicinalproduct_causality": medicinalproduct_causality,
                                                    "reactionmeddraversionllt1":reactionmeddraversionllt,
                                                    "reactionmeddrallt1":reactionmeddrallt,
                                                    "drugstartperiod_causality": drugstartperiod_causality,
                                                    "drugstartperiodunit_causality":drugstartperiodunit_causality,
                                                    "druglastperiod_causality":druglastperiod_causality,
                                                    "druglastperiodunit_causality":druglastperiodunit_causality
                                                    }

                                                    self.insert_case_causality_reaction_section(case_id, casecausalityreactiondata)
                                                    count = count + 1
                                                    insertdone = 2

                                            if (insertdone == 1):
                                                casecausalityreactiondata = {"drugcharacterization_causality": drugcharacterization_causality,
                                                "medicinalproduct_causality": medicinalproduct_causality,
                                                "reactionmeddraversionllt1":reactionmeddraversionllt,
                                                "reactionmeddrallt1":reactionmeddrallt,
                                                "drugstartperiod_causality": drugstartperiod_causality,
                                                "drugstartperiodunit_causality":drugstartperiodunit_causality,
                                                "druglastperiod_causality":druglastperiod_causality,
                                                "druglastperiodunit_causality":druglastperiodunit_causality
                                                }
                                                self.insert_case_causality_reaction_section_without_values(case_id, casecausalityreactiondata)
                                                insertdone = 2
                                        else:
                                            if (insertdone == 1):
                                                casecausalityreactiondata = {"drugcharacterization_causality": drugcharacterization_causality,
                                                "medicinalproduct_causality": medicinalproduct_causality,
                                                "reactionmeddraversionllt1":reactionmeddraversionllt,
                                                "reactionmeddrallt1":reactionmeddrallt,
                                                "drugstartperiod_causality": drugstartperiod_causality,
                                                "drugstartperiodunit_causality":drugstartperiodunit_causality,
                                                "druglastperiod_causality":druglastperiod_causality,
                                                "druglastperiodunit_causality":druglastperiodunit_causality
                                                }
                                                self.insert_case_causality_reaction_section_without_values(case_id, casecausalityreactiondata)
                                                insertdone = 2
                                        reactionloopcout = reactionloopcout + 1
                                    prodcount = prodcount + 1
                                except Exception as e:
                                    self.helper.error_log(
                                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                            else:
                                try:
                                    if product.find("drugcharacterization"):
                                        if product.find("drugcharacterization").text:
                                            drugcharacterization_causality1= product.find("drugcharacterization").text
                                        else:
                                            drugcharacterization_causality1=''
                                    else:
                                        drugcharacterization_causality1=''

                                    if product.find("medicinalproduct"):
                                        if product.find("medicinalproduct").text:
                                            medicinalproduct_causality1= product.find("medicinalproduct").text
                                        else:
                                            medicinalproduct_causality1=''
                                    else:
                                        medicinalproduct_causality1=''

                                    if ((drugcharacterization_causality1 == drugcharacterization_causality) and (medicinalproduct_causality1 == medicinalproduct_causality)):
                                        if product.find("drugcharacterization"):
                                            if product.find("drugcharacterization").text:
                                                drugcharacterization_causality= product.find("drugcharacterization").text
                                            else:
                                                drugcharacterization_causality=''
                                        else:
                                            drugcharacterization_causality=''

                                        if product.find("medicinalproduct"):
                                            if product.find("medicinalproduct").text:
                                                medicinalproduct_causality= product.find("medicinalproduct").text
                                            else:
                                                medicinalproduct_causality=''
                                        else:
                                            medicinalproduct_causality=''
                                    else:
                                        if product.find("drugcharacterization"):
                                            if product.find("drugcharacterization").text:
                                                drugcharacterization_causality= product.find("drugcharacterization").text
                                            else:
                                                drugcharacterization_causality=''
                                        else:
                                            drugcharacterization_causality=''

                                        if product.find("medicinalproduct"):
                                            if product.find("medicinalproduct").text:
                                                medicinalproduct_causality= product.find("medicinalproduct").text
                                            else:
                                                medicinalproduct_causality=''
                                        else:
                                            medicinalproduct_causality=''

                                        reactionloopcout = 1
                                        for reactiondata in reactioninfo:
                                            drugstartperiod_causality = ''
                                            drugstartperiodunit_causality = ''
                                            druglastperiod_causality = ''
                                            druglastperiodunit_causality = ''
                                            drugrecurreadministration = ''

                                            if reactiondata.find("reactionmeddraversionllt").text:
                                                reactionmeddraversionllt= reactiondata.find("reactionmeddraversionllt").text
                                            else:
                                                reactionmeddraversionllt = ''

                                            if reactiondata.find("reactionmeddrallt").text:
                                                reactionmeddrallt= reactiondata.find("reactionmeddrallt").text
                                            else:
                                                reactionmeddrallt = ''

                                            if (reactionloopcout == 1):
                                                if product.find("drugstartperiod"):
                                                    if product.find("drugstartperiod").text:
                                                        drugstartperiod_causality= product.find("drugstartperiod").text
                                                    else:
                                                        drugstartperiod_causality=''
                                                else:
                                                    drugstartperiod_causality=''

                                                if product.find("drugstartperiodunit"):
                                                    if product.find("drugstartperiodunit").text:
                                                        drugstartperiodunit_causality= product.find("drugstartperiodunit").text
                                                    else:
                                                        drugstartperiodunit_causality=''
                                                else:
                                                    drugstartperiodunit_causality=''

                                                if product.find("druglastperiod"):
                                                    if product.find("druglastperiod").text:
                                                        druglastperiod_causality= product.find("druglastperiod").text
                                                    else:
                                                        druglastperiod_causality=''
                                                else:
                                                    druglastperiod_causality=''

                                                if product.find("druglastperiodunit"):
                                                    if product.find("druglastperiodunit").text:
                                                        druglastperiodunit_causality= product.find("druglastperiodunit").text
                                                    else:
                                                        druglastperiodunit_causality=''
                                                else:
                                                    druglastperiodunit_causality=''

                                            insertdone = 1
                                            if product.findChildren("drugrecurrence"):
                                                drugrecurrenceinfo = product.findChildren("drugrecurrence")
                                                for drugrecurrencedata in drugrecurrenceinfo:
                                                    if drugrecurrencedata.find("drugrecuractionmeddraversion").text:
                                                        drugrecuractionmeddraversion= drugrecurrencedata.find("drugrecuractionmeddraversion").text
                                                    else:
                                                        drugrecuractionmeddraversion = ''

                                                    if drugrecurrencedata.find("drugrecuraction").text:
                                                        drugrecuraction= drugrecurrencedata.find("drugrecuraction").text
                                                    else:
                                                        drugrecuraction = ''

                                                    if ((drugrecuractionmeddraversion == reactionmeddraversionllt) and (drugrecuraction == reactionmeddrallt) and (insertdone == 1)):
                                                        if product.find("drugrecurreadministration"):
                                                            if product.find("drugrecurreadministration").text:
                                                                drugrecurreadministration= product.find("drugrecurreadministration").text
                                                            else:
                                                                drugrecurreadministration=''
                                                        else:
                                                            drugrecurreadministration=''

                                                        casecausalityreactiondata = {"drugrecurreadministration": drugrecurreadministration,
                                                        "rank":count,
                                                        "drugrecuractionmeddraversion": drugrecuractionmeddraversion,
                                                        "drugrecuraction": drugrecuraction,
                                                        "drugcharacterization_causality": drugcharacterization_causality,
                                                        "medicinalproduct_causality": medicinalproduct_causality,
                                                        "reactionmeddraversionllt1":reactionmeddraversionllt,
                                                        "reactionmeddrallt1":reactionmeddrallt,
                                                        "drugstartperiod_causality": drugstartperiod_causality,
                                                        "drugstartperiodunit_causality":drugstartperiodunit_causality,
                                                        "druglastperiod_causality":druglastperiod_causality,
                                                        "druglastperiodunit_causality":druglastperiodunit_causality
                                                        }

                                                        self.insert_case_causality_reaction_section(case_id, casecausalityreactiondata)
                                                        count = count + 1
                                                        insertdone = 2

                                                if (insertdone == 1):
                                                    casecausalityreactiondata = {"drugcharacterization_causality": drugcharacterization_causality,
                                                    "medicinalproduct_causality": medicinalproduct_causality,
                                                    "reactionmeddraversionllt1":reactionmeddraversionllt,
                                                    "reactionmeddrallt1":reactionmeddrallt,
                                                    "drugstartperiod_causality": drugstartperiod_causality,
                                                    "drugstartperiodunit_causality":drugstartperiodunit_causality,
                                                    "druglastperiod_causality":druglastperiod_causality,
                                                    "druglastperiodunit_causality":druglastperiodunit_causality
                                                    }
                                                    self.insert_case_causality_reaction_section_without_values(case_id, casecausalityreactiondata)
                                                    insertdone = 2
                                            else:
                                                if (insertdone == 1):
                                                    casecausalityreactiondata = {"drugcharacterization_causality": drugcharacterization_causality,
                                                    "medicinalproduct_causality": medicinalproduct_causality,
                                                    "reactionmeddraversionllt1":reactionmeddraversionllt,
                                                    "reactionmeddrallt1":reactionmeddrallt,
                                                    "drugstartperiod_causality": drugstartperiod_causality,
                                                    "drugstartperiodunit_causality":drugstartperiodunit_causality,
                                                    "druglastperiod_causality":druglastperiod_causality,
                                                    "druglastperiodunit_causality":druglastperiodunit_causality
                                                    }
                                                    self.insert_case_causality_reaction_section_without_values(case_id, casecausalityreactiondata)
                                                    insertdone = 2
                                            reactionloopcout = reactionloopcout + 1
                                except Exception as e:
                                        self.helper.error_log(
                                            current_filename + " " + str(
                                                getframeinfo(currentframe()).lineno) + ":" + str(e))
                                prodcount = prodcount + 1
                    except Exception as e:
                            self.helper.error_log(
                            current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                    result = {'error': 0,
                              'message': 'case creation successfull case number:' + case_id.case_no}
            else:

                result = {'error': 1,
                          'message': 'senderorganization or receiverorganization are not matching'}

        except Exception as e:
            # print(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            result = {'error': 1,
                      'message': 'failed to create a case at general tab information'}
        return result

        
