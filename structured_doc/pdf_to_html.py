import requests
from bs4 import BeautifulSoup

keys_list = ["7+13. DESCRIBE REACTION(S) continued", "13. Lab Data", "13. Relevant Tests",
             "14-19. SUSPECT DRUG(S) continued", "Reaction Information ( Cont...)",
             "Describe Reaction(s)(Include relevant test/lab data) ( Cont...)", "Suspect Drugs (Cont...)",
             "Concomitant drugs (Cont...)", "Other relevant history (Cont...)"]
keys_list_irms = ["Primary", "Case Information", "Client Data", "Abstract", "PATIENT INFORMATION",
                  "DATE SALES REPRESENTATIVE INFORMED", "SUSPECT PRODUCT INFORMATION:",
                  "DEATH INFORMATION",
                  "SERIOUSNESS CRITERIA (DEATH/LIFE-THREATENING/NEW OR PROLONGED HOSPITALIZATION/DISABILITY/CONGENITAL ANOMALY/IME):",
                  "EVENT INFORMATION:", "PAST MEDICAL HISTORY:", "ALLERGIES:", "CONCOMITANT MEDICATIONS:",
                  "PREGNANCY INFORMATION (YES or NO):", "DESRCRIPTION OF THE ADVERSE EVENT:"]


class html_blocks:

    def __init__(self, file_path, page_number, irms=0, last_key=None):
        req = requests.get(file_path)
        self.soup = BeautifulSoup(req.content, 'html.parser')

        self.keys_list = keys_list
        if irms == 1:
            self.keys_list = keys_list_irms
        self.page_number = "page_" + str(page_number)
        self.irms = irms

    def compress_pass(self, data):
        data = data.replace("\n", " ").replace(" ", "")
        return data

    def get_html_blocks(self):

        if self.irms == 0:
            # current_page = self.soup.find("div", {"id": self.page_number})
            current_page = self.soup
        else:
            current_page = self.soup
        filtter_list = current_page.find_all(True, {"class": ['ocrx_block', 'ocr_table']})

        dict_keys = {}
        for index, value in enumerate(self.keys_list):
            next_index = index + 1
            try:
                start_key = self.keys_list[index]
                start_key_index = -1
                end_key_index = -1
                for index_html, filtter_list_value in enumerate(filtter_list):
                    soup1 = BeautifulSoup(str(filtter_list_value), 'html.parser')
                    text_current = self.compress_pass(soup1.text)
                    if text_current.find(self.compress_pass(start_key)) > -1:
                        start_key_index = index_html
                        break
                if start_key_index > -1:
                    for next_val in range(next_index, len(self.keys_list) - 1):
                        end_key = self.keys_list[next_val]
                        for index_html1, filtter_list_value1 in enumerate(filtter_list):
                            soup2 = BeautifulSoup(str(filtter_list_value1), 'html.parser')
                            text_current_2 = self.compress_pass(soup2.text)
                            if text_current_2.find(self.compress_pass(end_key)) > -1:
                                end_key_index = index_html1
                                break
                if start_key_index > -1 and end_key_index > -1:
                    dict_keys[start_key] = str(filtter_list[start_key_index:end_key_index])
                elif start_key_index > -1 and end_key_index == -1:
                    dict_keys[start_key] = str(filtter_list[start_key_index:])
                # elif start_key_index > -1 and index == len(keys_list) - 1:
                #     dict_keys[start_key] = str(filtter_list[start_key_index:])
            except Exception as e:
                print("end", e)
        return dict_keys
