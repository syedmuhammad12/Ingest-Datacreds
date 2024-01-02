# json key mapping
class jsonkey:
    def __init__(self):
        self.thisdict = {
            # Patient
            "patientinitial": ["PATIENTINITIAL"],
            "patientonsetage": ['PATIENTONSETAGE'],
            "patientonsetageunit": ['PATIENTONSETAGEUNIT'],
            "patientsex": ['PATIENTSEX'],
            "patientheight": ['PATIENTHEIGHT'],
            "patientweight": ['PATIENTWEIGHT'],
            "patientmedicalhistorytext": ["PATIENTMEDICALHISTORYTEXT"],
            "resultstestsprocedures": ["RESULTSTESTSPROCEDURES"],

            # Patient Drug Name
            "patientdrugname": ["PATIENTDRUGNAME"],
            "patientdrugindication": ["PATIENTDRUGINDICATION"],
            "patientdrugreaction": ["PATIENTDRUGREACTION"],
            "patientautopsyyesno": ["PATIENTAUTOPSYYESNO"],
            "patientdeathreport": ["PATIENTDEATHREPORT"],
            "gestationperiod": ["GESTATIONPERIOD"],

            # Parent
            "parentage": ["PARENTAGE"],
            "parentweight": ["PARENTWEIGHT"],
            "parentheight": ["PARENTHEIGHT"],
            "parentsex": ["PARENTSEX"],
            "parentmedicalrelevanttext": ["PARENTMEDICALRELEVANTTEXT"],
            "patientepisodename": ["PATIENTEPISODENAME"],
            "patientmedicalstartdate": ["PATIENTMEDICALSTARTDATE"],
            "patientmedicalenddate": ["PATIENTMEDICALENDDATE"],
            "patientmedicalcontinue": ["PATIENTMEDICALCONTINUE"],
            "patientmedicalcomment": ["PATIENTMEDICALCOMMENT"],
            "primarysourcereaction": ["PRIMARYSOURCEREACTION"],
            "reactionoutcome": ["REACTIONOUTCOME"],

            # Seriousness
            "primarysourcecountry": ['PRIMARYSOURCECOUNTRY'],
            "occurcountry": ['OCCURCOUNTRY'],
            "seriousnessdeath": ["SERIOUSNESSDEATH"],
            "seriousnesslifethreatening": ["SERIOUSNESSLIFETHREATENING"],
            "seriousnesshospitalization": ["SERIOUSNESSHOSPITALIZATION"],
            "seriousnessdisabling": ["SERIOUSNESSDISABLING"],
            "seriousnesscongenitalanomali": ["SERIOUSNESSCONGENITALANOMALI"],
            "seriousnessother": ["SERIOUSNESSOTHER"],

            # Reporter
            "reportertitle": ["REPORTERTITLE"],
            "reportergivename": ["REPORTERGIVENAME"],
            "reportermiddlename": ["REPORTERMIDDLENAME"],
            "reporterfamilyname": ["REPORTERFAMILYNAME"],
            "reporterorganization": ["REPORTERORGANIZATION"],
            "reporterdepartment": ["REPORTERDEPARTMENT"],
            "reportercountry": ["REPORTERCOUNTRY"],
            "reporterstate": ["REPORTERSTATE"],
            "reportercity": ["REPORTERCITY"],
            "reporterstreet": ["REPORTERSTREET"],
            "reporterpostcode": ["REPORTERPOSTCODE"],
            "qualification": ["qualification"],
            "literaturereference": ["LITERATURE REFERENCE", "LITERATUREREFERENCE"],
            "studyname": ["STUDYNAME"],
            "sponsorstudynumb": ["SPONSORSTUDYNUMB"],
            "observestudytype": ["OBSERVESTUDYTYPE"],

            # Test
            "testname": ["TESTNAME"],
            "testresult": ["TESTRESULT", "TEST RESULT"],
            "lowtestrange": ["LOWTESTRANGE"],
            "hightestrange": ["HIGHTESTRANGE"],
            "moreinformation": ["MOREINFORMATION"],

            # Drug
            "suspectproduct": ["SUSPECTPRODUCT"],
            "concomitantproduct": ["CONCOMITANTPRODUCT"],
            "drugadministrationroute": ["DRUGADMINISTRATIONROUTE"],
            "drugdosageform": ["DRUGDOSAGEFORM"],
            "drugdosagetext": ["DRUGDOSAGETEXT"],
            "drugindication": ["DRUGINDICATION"],
            "drugintervaldosagedefinition": ["DRUGINTERVALDOSAGEDEFINITION"],
            "drugintervaldosageunitnumb": ["DRUGINTERVALDOSAGEUNITNUMB"],
            "drugresult": ["DRUGRESULT"],
            "drugassessmentmethod": ["DRUGASSESSMENTMETHOD"],
            "drugassessmentsource": ["DRUGASSESSMENTSOURCE"],
            "drugstructuredosagenumb": ["DRUGSTRUCTUREDOSAGENUMB"],
            "drugstructuredosageunit": ["DRUGSTRUCTUREDOSAGEUNIT"],

            # Summary
            "narrativeincludeclinical": ["NARRATIVEINCLUDECLINICAL"],

            # "DescribeReaction":['DESCRIBE REACTION(S)','7+13DESCRIBE REACTION(S)'],
            "Day_DOB": [''],
            "Month_DOB": [''],
            "Year_DOB": [''],
        }
