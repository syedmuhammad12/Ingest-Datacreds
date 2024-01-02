# summary element create
from bs4 import BeautifulSoup
from .helper import helper


class summaryXmlElement:

    def __init__(self, con, row, code_template):
        text = open(con.xml_template_summary, "r", encoding="utf8").read()
        self.soup = BeautifulSoup(text, 'lxml-xml')
        self.row = row
        self.helper = helper(row)

    # narative tag data mapping
    def get_summary_tag(self):
        if self.row['template'] =='IRMS':
            return self.get_irms_summary_tag()
        elif self.row['template'] =='linelist':
            return self.get_linelist_summary_tag()
        narrative = ""
        try:
            if self.helper.isNan("DescribeReaction") == 1:
                narrative = narrative + "DescribeReaction\n"
                narrative = narrative + self.helper.remove_headers(self.row["DescribeReaction"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("Describe Reaction(s)(Include relevant test/lab data) ( Cont...)") == 1:
                narrative = narrative + "\nDescribe Reaction(s)(Include relevant test/lab data) ( Cont...)\n"
                narrative = narrative + self.helper.remove_headers(
                    self.row["Describe Reaction(s)(Include relevant test/lab data) ( Cont...)"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("Remarks") == 1:
                narrative = narrative + "\nRemarks\n"
                narrative = narrative + self.helper.remove_headers(self.row["Remarks"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("7+13. DESCRIBE REACTION(S) continued") == 1:
                narrative = narrative + "\n7+13. DESCRIBE REACTION(S) continued\n"
                narrative = narrative + self.helper.remove_headers(
                    self.row["7+13. DESCRIBE REACTION(S) continued"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("Suspect Drugs (Cont...)") == 1:
                narrative = narrative + "\nSuspect Drugs (Cont...)\n"
                narrative = narrative + self.helper.remove_headers(self.row["Suspect Drugs (Cont...)"]).strip()
        except Exception as e:
            e
        try:
            if self.helper.isNan("Suspect Drugs (Cont...)") == 1:
                narrative = narrative + "\nSuspect Drugs (Cont...)\n"
                narrative = narrative + self.helper.remove_headers(self.row["Suspect Drugs (Cont...)"]).strip()
        except Exception as e:
            e
        try:
            if self.helper.isNan("SUSPECT DRUG(S) continued") == 1:
                narrative = narrative + "\nSUSPECT DRUG(S) continued\n"
                narrative = narrative + self.helper.remove_headers(self.row["SUSPECT DRUG(S) continued"].strip())
        except Exception as e:
            e

        try:
            if self.helper.isNan("OtherRelevantHistory") == 1:
                narrative = narrative + "\nOtherRelevantHistory\n"
                narrative = narrative + self.helper.remove_headers(self.row["OtherRelevantHistory"].strip())
        except Exception as e:
            e

        try:
            if self.helper.isNan("Other relevant history (Cont...)") == 1:
                narrative = narrative + "\nOther relevant history (Cont...)\n"
                narrative = narrative + self.helper.remove_headers(self.row["Other relevant history (Cont...)"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("23. OTHER RELEVANT HISTORY  continued") == 1:
                narrative = narrative + "\n23. OTHER RELEVANT HISTORY  continued\n"
                narrative = narrative + self.helper.remove_headers(
                    self.row["23. OTHER RELEVANT HISTORY  continued"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("Company Remarks  (Cont...)") == 1:
                narrative = narrative + "\nCompany Remarks  (Cont...)\n"
                narrative = narrative + self.helper.remove_headers(self.row["Company Remarks  (Cont...)"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("Company Remarks (Sender's comments) (Cont...)") == 1:
                narrative = narrative + "\nCompany Remarks (Sender's comments) (Cont...)\n"
                narrative = narrative + self.helper.remove_headers(
                    self.row["Company Remarks (Sender's comments) (Cont...)"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("Literature Information (Cont...)") == 1:
                narrative = narrative + "\nLiterature Information (Cont...)\n"
                narrative = narrative + self.helper.remove_headers(self.row["Literature Information (Cont...)"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("Additional information (continuation)") == 1:
                narrative = narrative + "\nAdditional information (continuation)\n"
                narrative = narrative + self.helper.remove_headers(
                    self.row["Additional information (continuation)"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("Additional Information(Continuation)") == 1:
                narrative = narrative + "\nAdditional Information(Continuation)\n"
                narrative = narrative + self.helper.remove_headers(
                    self.row["Additional Information(Continuation)"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("EUDRACTNO") == 1:
                narrative = narrative + "\nEUDRACTNO\n"
                narrative = narrative + self.row["EUDRACTNO"].strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("MFRControlNo") == 1:
                narrative = narrative + "\nMFRControlNo\n"
                narrative = narrative + self.row["MFRControlNo"].replaceAll("O", "0").strip()
        except Exception as e:
            e

        try:
            didAbateYES = self.row["DidAbateYES"].strip().lower()
            didAbateNO = self.row["DidAbateNO"].strip().lower()
            didAbateNA = self.row["DidAbateNA"].strip().lower()
            didAbate = "NA"
            if didAbateYES == "yes":
                didAbate = "YES"
            elif didAbateNO == "yes":
                didAbate = "NO"
            elif didAbateNA == "yes":
                didAbate = "NA"
            narrative = narrative + "\n\nDID EVENT ABATE AFTER STOPPING DRUG?\n"
            narrative = narrative + didAbate

        except Exception as e:
            e

        try:
            EventReapperYES = self.row["EventReapperYES"].strip().lower()
            EventReappearNO = self.row["EventReappearNO"].strip().lower()
            EventReappearNA = self.row["EventReappearNA"].strip().lower()
            eventReapper = "NA"
            if EventReapperYES == "yes":
                eventReapper = "YES"
            elif EventReappearNO == "yes":
                eventReapper = "NO"
            elif EventReappearNA == "yes":
                eventReapper = "NA"
            narrative = narrative + "\n\nDID EVENT REAPPEAR AFTER REINTRODUCTION?\n"
            narrative = narrative + eventReapper

        except Exception as e:
            e

        try:
            if self.helper.isNan("ConcomitantDrugs") == 1:
                narrative = narrative + "\nConcomitantDrugs\n"
                narrative = narrative + self.helper.remove_headers(self.row["ConcomitantDrugs"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("CONCOMITANT DRUG(S) AND DATES OF ADMINISTRATION continued") == 1:
                narrative = narrative + "\nCONCOMITANT DRUG(S) AND DATES OF ADMINISTRATION continued\n"
                narrative = narrative + self.helper.remove_headers(
                    self.row["CONCOMITANT DRUG(S) AND DATES OF ADMINISTRATION continued"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("Concomitant Drugs (Cont...)") == 1:
                narrative = narrative + "\nConcomitant Drugs (Cont...)\n"
                narrative = narrative + self.helper.remove_headers(self.row["Concomitant Drugs (Cont...)"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("13. Lab Data") == 1:
                narrative = narrative + "\n13. Lab Data\n"
                narrative = narrative + self.helper.remove_headers(self.row["13. Lab Data"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("24d. Report Source Literature") == 1:
                narrative = narrative + "\n24d. Report Source Literature\n"
                narrative = narrative + self.helper.remove_headers(self.row["24d. Report Source Literature"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("REACTION INFORMATION") == 1:
                narrative = narrative + "\nREACTION INFORMATION\n"
                narrative = narrative + self.helper.remove_headers(self.row["REACTION INFORMATION"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("IndicationForUse") == 1:
                narrative = narrative + "\nIndicationForUse\n"
                narrative = narrative + self.row["IndicationForUse"].strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("Reaction Information ( Cont...)") == 1:
                narrative = narrative + "\nReaction Information ( Cont...)\n"
                narrative = narrative + self.helper.remove_headers(self.row["Reaction Information ( Cont...)"]).strip()
        except Exception as e:
            e

        self.soup.find("narrativeincludeclinical").string = str(narrative)
        return self.soup

    def get_irms_summary_tag(self):
        narrative = ""
        try:
            if self.helper.isNan("DESCRIPTION OF COURSE OF EVENTS:") == 1:
                narrative = narrative + "\nDESCRIPTION OF COURSE OF EVENTS:\n"
                narrative = narrative + self.helper.remove_headers(self.row["DESCRIPTION OF COURSE OF EVENTS:"]).strip()
        except Exception as e:
            e

        try:
            if self.helper.isNan("DESRCRIPTION OF THE ADVERSE EVENT:") == 1:
                narrative = narrative + "\nDESRCRIPTION OF THE ADVERSE EVENT:\n"
                narrative = narrative + self.helper.remove_headers(self.row["DESRCRIPTION OF THE ADVERSE EVENT:"]).strip()
        except Exception as e:
            e
            
        try:
            if self.helper.isNan("PREGNANCY INFORMATION (YES or NO):") == 1:
                narrative = narrative + "\nPREGNANCY INFORMATION (YES or NO):\n"
                narrative = narrative + self.helper.remove_headers(self.row["PREGNANCY INFORMATION (YES or NO):"]).strip()
        except Exception as e:
            e
        
        try:
            if self.helper.isNan("DATE SALES REPRESENTATIVE INFORMED:") == 1:
                narrative = narrative + "\nDATE SALES REPRESENTATIVE INFORMED:\n"
                narrative = narrative + self.helper.remove_headers(self.row["DATE SALES REPRESENTATIVE INFORMED:"]).strip()
        except Exception as e:
            e
        self.soup.find("narrativeincludeclinical").string = str(narrative)

        return self.soup

    def get_linelist_summary_tag(self):
        narrative = ""
        try:
            if self.helper.isNan("description_reaction") == 1:
                narrative = narrative + self.helper.remove_headers(self.row["description_reaction"]).strip()
        except Exception as e:
            e
        self.soup.find("narrativeincludeclinical").string = str(narrative)

        return self.soup