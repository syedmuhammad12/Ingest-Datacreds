# json key mapping
class linelistkey:
    def __init__(self):
        self.thisdict = {'authority_number': ['Regulatory Authority reference number',
                                              'Worldwide Unique Case Identification Number'],
                         'safetyreportversion': ['Initial/FU report', 'VERSION_NO', 'Version'],
                         'Report type-unexpectedness': ['Report type-unexpectedness'],
                         'seriousness': ['Report type-Seriousness', 'Serious case', 'SERIOUSNESS'],
                         'seriousness_criteria': ['Serious adverse drug reaction - seriousness criteria','Seriousness Criteria','Seriousness criteria'],
                         'Category of the Reporter Agency': ['Category of the Reporter Agency'],
                         'sex': ['Gender', 'SEX'],
                         'birth_date': ['Birth date', 'DOB'],
                         'age_val': ['Age', 'AGE'],
                         'age_unit': ['Age unit'],
                         'Nationality': ['Nationality'],
                         'weight': ['Weight(kg)'],
                         'past_medical_history': ['Past history of adverse drug reaction/event'],
                         'Familial adverse drug reaction/event': ['Familial adverse drug reaction/event'],
                         'onset_reaction': ['Onset date of adverse reaction','AE_ONSET_DATE'],
                         'description_reaction': ['Description of adverse reaction','Case narrative'],
                         'outcome_reaction': ['Outcome of adverse reaction',
                                              'Outcome of reaction/event at the time of last observation',
                                              'Event Outcome', 'OUTCOME','Outcome of reaction/eventat the time of last observation'],
                         'Sequelae manifestations': ['Sequelae manifestations'],
                         'death_date': ['Date of Death'],
                         'death_cause': ['Direct cause of death','Cause Of Death'],
                         'actiondrug': [
                             'Whether the reaction remits or disappears following drug withdrawal or dose reduction (Dechallenge)',
                             'Action Taken with Suspect', 'DECHALLENGE'],
                         'drugrecurreadministration': [
                             'Whether the same reaction occurs when rechallenged with the suspected drug (Rechallenge)',
                             'RECHALLENGE'],
                         'Impact on underlying disease': ['Impact on underlying disease'],
                         'reporter_causality_assessment': ['Reporter causality assessment', 'Reporter Causality',
                                                           'CAUSALITY_REPORTER','Reporter causality'],
                         'agency_causality_assessment': [
                             'Causality Assessment by the Agency (where reporter works in, but not authority)',
                             'Company Causality', 'CAUSALITY_COMPANY'],
                         'Date_Received_Manufacturer': [
                             'Reporting to ADR agency (Regulatory Authority)', 'Date received by the company'],
                         'Origin': ['Origin'],
                         'Notes': ['Notes'],
                         'past_medical_history_continue1': ['Underlying disease'],
                         'past_medical_history_continue': ['Family ADR history [Adverse Reaction Term]','Medical History PT'],
                         'Family ADR history [Trade Name]': ['Family ADR history [Trade Name]'],
                         'Family ADR history [Severity]': ['Family ADR history [Severity]'],
                         'Past history of Adverse Ddrug Reaction/ Event [Adverse Drug Reaction/ Event Term]': [
                             'Past history of Adverse Ddrug Reaction/ Event [Adverse Drug Reaction/ Event Term]'],
                         'Past history of Adverse Ddrug Reaction/ Event [Severity]': [
                             'Past history of Adverse Ddrug Reaction/ Event [Severity]'],
                         'Past history of Adverse Ddrug Reaction/ Event [trade name]': [
                             'Past history of Adverse Ddrug Reaction/ Event [trade name]'],
                         'Relevant important information': ['Relevant important information'],
                         'Other Relevant important information': ['Other Relevant important information'],
                         'Suspected/Concomitant': ['Suspected/Concomitant'],
                         'drug_category': ['Suspected/Concomitant', 'Characterization of product','PRODUCT_FLAG'],
                         'National Approval No.': ['National Approval No.'],
                         'active_substance': ['Generic name', 'Active Ingredient', 'GENERIC_NAME', 'Medicinal product name as reported'],
                         'drug_name': ['Trade name',
                                       'Suspect Drug Product Description', 'TRADE_NAME','Name of Suspect as reported','Product Description'],
                         'Dosage_form': ['Dosage form'],
                         'Manufacturer': ['Manufacturer'],
                         'lot_number': ['Manufacturing batch number/ lot number', 'Lot Number'],
                         'Dosage': ['Dosage'],
                         'Dosage_Unit': ['Dosage Unit'],
                         'Administration frequency-time': ['Administration frequency-time'],
                         'Administration frequency-day': ['Administration frequency-day'],
                         'Route_of_administration': ['Route of administration'],
                         'drug_start_date': ['Start time of drug administration'],
                         'drug_end_date': ['End time of drug administration'],
                         'drug_duration':['Duration'],
                         'drug_indication': ['Reason for Drug Administration','Indication of suspect as Reported by the Primary Source'],
                         'primary_source_reaction': ['Adverse Reaction Terms', 'Reaction/event as reported',
                                                     'Reported Term Text', 'REPORTED_TERM_TEXT','Reaction/event as reported by primary source in Native Language','Reaction/event as reported by primary source for Translation'],
                         'reaction_pt': ['MedDRA PT', 'PT_CODE','Reaction/event (PT)','PT (Event Level)'],
                         'reaction_llt': ['LLT_CODE'],
                         'reaction_seriousness': ['Event Seriousness','Serious AE'],
                         'reaction_end_date': ['AE_CESSATION_DATE'],
                         'Severity': ['Severity'],
                         'patientinitial': ['Identifier #1', 'Patient ID', 'ID'],
                         'safetyreportid': ['Case Id', 'AER_NO', 'AER (Ver #)', 'Case ID with version number','AER No'],
                         'receivedate': ['IRD', 'AER_INIT_RECV_DATE','Received date/IRD','Received date'],
                         'receiptdate': ['Receipt date', 'LRD','Received date/LRD'],
                         'reportercountry': ["Reporter's country","Reporter's Country"],
                         'qualification': ['Qualification',"Reporter's Qualification"],
                         'reaction_pt': ['Reaction/event (PT)'],
                         'Source_of_assessment': ['Source of assessment', 'SOURCE'],
                         'Source_of_assessment_result': ['Result', 'RESULT'],
                         'narrative': ['Case narrative'],
                         'reporttype': ['Type of report'],
                         'primarysourcecountry': ['country', 'AER_COUNTRY'],
                         "Event_Death": ['Event Death'],
                         'Life_Threatening': ['Life Threatening'],
                         'Other_Medically_Imp_Condition': ['Other Medically Imp Condition'],
                         'Congenital_anomaly': ['Congenital anomaly'],
                         'Hospitalization_Required': ['Hospitalization Required']
                         }
