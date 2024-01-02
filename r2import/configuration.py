import os
import datetime
from time import time

project_path = os.path.dirname(os.path.realpath(__file__))
r2xml_path = project_path + '/temp/'
logs_path = project_path + '/logs/'
medra_path = project_path + '/medra/llt.csv'
current_date = str(datetime.datetime.now().day) + '-' + str(datetime.datetime.now().month) + '-' + str(
    datetime.datetime.now().year)
xml_template = project_path + '/xml_template/main.xml'
xml_template_primary_source = project_path + '/xml_template/primarySource.xml'
xml_template_report_duplicate = project_path + '/xml_template/reportDuplicate.xml'
xml_template_linked_report = project_path + '/xml_template/linkedReport.xml'
xml_template_patient = project_path + '/xml_template/patient.xml'
xml_template_reaction = project_path + '/xml_template/reaction.xml'
xml_template_medicalHistory = project_path + '/xml_template/medicalHistory.xml'
xml_template_patientPastDrugTherapy = project_path + '/xml_template/patientPastDrugTherapy.xml'
xml_template_patientDeath = project_path + '/xml_template/patientDeath.xml'
xml_template_patientAutopsy = project_path + '/xml_template/patientAutopsy.xml'
xml_template_patientDeathCause = project_path + '/xml_template/patientDeathCause.xml'
xml_template_patient_parent = project_path + '/xml_template/patientParent.xml'
xml_template_drug = project_path + '/xml_template/drug.xml'
xml_template_activeSubstance = project_path + '/xml_template/activeSubstance.xml'
xml_template_drug_reaction_relatedness = project_path + '/xml_template/drugReactionRelatedness.xml'
xml_template_summary = project_path + '/xml_template/summary.xml'
xml_template_test = project_path + '/xml_template/test.xml'
current_timestamp = "_" + str(int(datetime.datetime.now().timestamp()))
file_name_prefix = 'R2_'
file_name_suffix ='Import_R2_'
