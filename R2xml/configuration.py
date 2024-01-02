import os
import datetime

project_path = os.path.dirname(os.path.realpath(__file__))
json_path = project_path + '/json/'
csv_path = project_path + '/csv/'
file_starts_with = 'outputfinal_'
file_ends_width = '.csv'
ends_width='.json'
upload_file_path = project_path + '/file_uploads/'
clients_path = project_path + '/clients/projects.csv'
r2xml_path = project_path + '/r2xml/'
logs_path = project_path + '/logs/'
medra_path = project_path + '/medra/llt.csv'
pdf_path = project_path + '/pdf/'
bfc_path = project_path + '/BFC/'
r2_path = project_path + '/BFC/r2/'
current_date = str(datetime.datetime.now().day) + '-' + str(datetime.datetime.now().month) + '-' + str(
    datetime.datetime.now().year)
xml_template = project_path + '/xml_template/main.xml'
xml_r3_template = project_path + '/xml_template/main_r3.xml'
xml_template_patient = project_path + '/xml_template/patient.xml'
xml_template_reaction = project_path + '/xml_template/reaction.xml'
xml_template_test = project_path + '/xml_template/test.xml'
xml_template_medicalHistory = project_path + '/xml_template/medicalHistory.xml'
xml_template_drug = project_path + '/xml_template/drug.xml'
xml_template_drug_reaction_relatedness = project_path + '/xml_template/drugReactionRelatedness.xml'
xml_template_summary = project_path + '/xml_template/summary.xml'
xml_template_patientDeath = project_path +'/xml_template/patientDeath.xml'
xml_template_patientDeathCause=project_path +'/xml_template/patientDeathCause.xml'
current_timestamp = "_" + str(int(datetime.datetime.now().timestamp()))
default_code_template = "BAXTER\JnJ"
history_code_group_default = ["BAXTER\JnJ"]
reaction_code_group_default = ["BAXTER\JnJ"]
drug_code_group_default = ["BAXTER\JnJ"]
reaction_code_group_1 = ["PFIZERINC\EMERCK"]
drug_code_group_1 = ["PFIZERINC\EMERCK"]
test_code_group_default = ["BAXTER\JnJ"]
test_code_group_1 = ["PFIZERINC\EMERCK"]
file_name_prefix = 'R2_'
linelist_path = project_path + '/linelist/'
default_medwatch_code_template = "Akrimax"
