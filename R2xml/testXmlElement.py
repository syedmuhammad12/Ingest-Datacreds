# test element create
import os
from bs4 import BeautifulSoup
from .helper import helper
from .dataFormatCalculation import dateFormatCalculation
import re
from inspect import currentframe, getframeinfo
import pdftotree

current_filename = str(getframeinfo(currentframe()).filename)


class testXmlElement:

    def __init__(self, con, row, code_template):
        self.row = row
        self.con = con
        self.code_template = code_template
        self.text = open(self.con.xml_template_test, "r", encoding="utf8").read()
        self.soup = BeautifulSoup("", 'lxml-xml')
        self.test_code_group_default = con.test_code_group_default
        self.test_code_group_1 = con.test_code_group_1
        self.pdf_path = self.con.pdf_path
        self.helper = helper(row)

    # lab test tag calculation with information based on vendor groups
    def get_test_tag(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        if self.row['template'] == 'litrature':
            return self.get_litrature_test_tag()
        # Default group mapping
        if self.code_template in self.test_code_group_default:
            result_default = self.data_test_code_group_default()
            if result_default != "":
                final_tag.append(result_default)
        # group1 template calculation
        elif self.code_template in self.test_code_group_1:
            result = self.data_test_code_group_1()
            if result != "":
                final_tag.append(result)
        return final_tag

    def data_test_code_group_default(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        if os.path.exists(self.pdf_path + self.row['FileName_1']):
            pdf_str = pdftotree.parse(self.pdf_path + self.row['FileName_1'], html_path=None, model_type=None,
                                      model_path=None, visualize=False)
            pdf_tag = BeautifulSoup(pdf_str, 'html.parser')

            dict = {}
            for rows in pdf_tag.findAll('table'):
                try:
                    if len(rows.findAll(text='Test')) > 0:
                        for index_row, tr in enumerate(rows.findAll('tr')):
                            if index_row > 0:
                                lab_data = []
                                td_list = tr.findAll('td')
                                for index_td, td in enumerate(tr.findAll('td')):
                                    if index_td <= 2:
                                        if index_row == 1:
                                            lab_data.append(
                                                str(td_list[index_td].text.replace("\n", " ").replace('(cid:1)',
                                                                                                      " ").strip()))

                                        elif index_row > 1:
                                            lab_data.append(
                                                str(td_list[index_td].text.replace("\n", " ").replace('(cid:1)',
                                                                                                      " ").strip()))
                                if lab_data[0] == '' and lab_data[1] == '':
                                    last_index = list(dict)[-1]
                                    pre_list = dict[last_index]
                                    dict[last_index][2] = pre_list[2] + " " + str(lab_data[2])
                                elif lab_data[1] == '' and lab_data[2] == '':
                                    last_index = list(dict)[-1]
                                    pre_list = dict[last_index]
                                    dict[last_index][0] = pre_list[0] + " " + str(lab_data[0])
                                else:
                                    dict[index_row] = lab_data
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                for list_dat in dict:
                    soup = BeautifulSoup(self.text, 'lxml-xml')
                    if dict[list_dat][1]:
                        date_both = dateFormatCalculation().get_data(dict[list_dat][1], 1)
                        try:
                            if date_both:
                                soup.find('testdateformat').string = "102"
                                soup.find('testdate').string = str(date_both)
                        except Exception as e:
                            self.helper.error_log(current_filename + " " + str(
                                getframeinfo(currentframe()).lineno) + ":" + str(e))

                    soup.find('testname').string = str(dict[list_dat][0])
                    soup.find('testresult').string = str(dict[list_dat][2])
                    final_tag.append(soup)
            except Exception as e:
                self.helper.error_log(
                    current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return final_tag

    def data_test_code_group_1(self):
        final_tag = BeautifulSoup("", 'lxml-xml')
        if os.path.exists(self.pdf_path + self.row['FileName_1']):
            pdf_str = pdftotree.parse(self.pdf_path + self.row['FileName_1'], html_path=None, model_type=None,
                                      model_path=None, visualize=False)
            pdf_tag = BeautifulSoup(pdf_str, 'html.parser')

            for rows in pdf_tag.findAll('table'):
                try:
                    if len(rows.findAll(text='Test')) > 0:
                        dict = {}
                        str_data = " _BIO_ "
                        for index_row, tr in enumerate(rows.findAll('tr')):
                            try:
                                lab_data = []
                                if index_row > 0:
                                    td_list = tr.findAll('td')
                                    size = len(tr.findAll('td'))
                                    for index_td, td in enumerate(tr.findAll('td')):

                                        if index_td <= size:
                                            if index_row == 1:
                                                lab_data.append(
                                                    str(td_list[index_td].text.replace("\n", " ").replace('(cid:1)',
                                                                                                          " ").strip()))

                                            elif index_row > 1:
                                                lab_data.append(
                                                    str(td_list[index_td].text.replace("\n", " ").replace('(cid:1)',
                                                                                                          " ").strip()))
                                    count = 0;
                                    push_index = 0
                                    for index_lab_data, values in enumerate(lab_data):
                                        if values.strip() != '':
                                            count += 1
                                            push_index = index_lab_data
                                    if count == 1:
                                        last_index = list(dict)[-1]
                                        pre_list = dict[last_index]
                                        dict[last_index][push_index] = pre_list[push_index] + " " + str(
                                            lab_data[push_index])
                                    else:
                                        dict[index_row] = lab_data
                            except Exception as e:
                                self.helper.error_log(current_filename + " " + str(
                                    getframeinfo(currentframe()).lineno) + ":" + str(e))

                        for dict_index in dict:
                            try:
                                list_row = dict[dict_index]
                                data = str_data.join(list_row)
                                date = re.findall(r'[0-9]{1,}-[A-Z-a-z]{3}-[0-9]{4}', data)
                                medra_name_list = self.helper.get_medra_name_list()
                                contained = [x + "_" + str(data.find(x)) for x in medra_name_list if
                                             " " + x + " " in data]
                                dict_medra = {}
                                for y in contained:
                                    arr = y.split("_")
                                    index_medra = int(arr[1])
                                    try:
                                        if dict_medra[index_medra] != "":
                                            if len(dict_medra[index_medra]) < len(arr[0]):
                                                dict_medra[index_medra] = arr[0]
                                    except Exception as e:
                                        dict_medra[index_medra] = arr[0]
                                dict_index = sorted(list(dict_medra))
                                if len(date) > 0:
                                    data = data[data.find(date[0]) + len(date[0]) + 1:]
                                test_name = ""
                                if len(dict_medra) > 0:
                                    test_name = dict_medra[dict_index[0]]
                                    data = data[data.find(test_name) + len(test_name) + 1:]
                                    pattern = re.compile("\(" + test_name + "\)", re.IGNORECASE)
                                    data = pattern.sub("", data)
                                remaing_data = data.split(str_data)
                                data_range = ""
                                result_data = ""
                                if len(remaing_data) > 0:
                                    for remain_index, remain_value in enumerate(remaing_data):
                                        if len(remaing_data) > 1 and remain_index == len(remaing_data) - 1:
                                            data_range = remain_value
                                        else:
                                            result_data += str(remain_value)

                                soup = BeautifulSoup(self.text, 'lxml-xml')
                                if len(date) > 0:
                                    date_both = dateFormatCalculation().get_data(date[0], 1)
                                    try:
                                        if date_both:
                                            soup.find('testdateformat').string = "102"
                                            soup.find('testdate').string = str(date_both)
                                    except Exception as e:
                                        self.helper.error_log(current_filename + " " + str(
                                            getframeinfo(currentframe()).lineno) + ":" + str(e))

                                soup.find('testname').string = str(test_name)
                                soup.find('testresult').string = str(result_data.replace('_BIO_', ""))

                                if data_range.replace('/', ' ').strip() != "":
                                    data_range_list = data_range.split(" ")
                                    min_data = float(data_range_list[1])
                                    max_data = float(data_range_list[0])
                                    if min_data > max_data:
                                        temp = min_data
                                        min_data = max_data
                                        max_data = temp
                                    soup.find('lowtestrange').string = str(min_data)
                                    soup.find('hightestrange').string = str(max_data)
                                final_tag.append(soup)
                            except Exception as e:
                                self.helper.error_log(current_filename + " " + str(
                                    getframeinfo(currentframe()).lineno) + ":" + str(e))
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return final_tag

    def convert_str_to_list(self, data):
        try:
            return [str(v) for v in eval(str(data))]
        except Exception as e:
            return [].append(data)

    def process_list_values(self, data):
        try:
            return ", ".join(str(v) for v in eval(str(data)))
        except Exception as e:
            return data

    def convert_str_to_list(self, data):
        try:
            return [str(v) for v in eval(str(data))]
        except Exception as e:
            return [].append(data)

    def get_medra_code(self, name):
        medra_code_list_final = 0
        try:
            result = self.helper.get_medra_with_string(name.strip())
            medra_code = list(result['medra_code'])
            if len(medra_code) > 0:
                medra_code_list_final = int(medra_code[0])
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return medra_code_list_final

    def get_litrature_test_tag(self):
        soup = self.soup
        row = self.row

        REACTIONTESTRESULT = self.helper.get_relation('REACTIONTESTRESULT')

        if len(REACTIONTESTRESULT) > 0:
            return self.get_litrature_test_by_realtion_tag(REACTIONTESTRESULT)
        try:
            if 'testname' in row:
                test_name = str(self.process_list_values(row['testname'])).split(',')
                # test_name=row['testname']

                if len(test_name) > 0:
                    for idx, tn in enumerate(test_name):

                        tn_meddra = self.get_medra_code(str(tn).strip())

                        if tn_meddra > 0:
                            print("testname", tn)
                            tn_soup = BeautifulSoup(self.text, 'lxml-xml')
                            tn_soup.find('testname').string = str(tn_meddra)

                            if 'testresult' in row:
                                # tres = self.convert_str_to_list(str(row['testresult']))
                                tres = row['testresult']
                                print(type(tres))
                                if len(tres) > 0 and type(tres) == list:
                                    try:
                                        tn_soup.find('testresult').string = str(tres[idx])
                                    except IndexError:
                                        tn_soup.find('testresult').string = str("")
                                elif type(tres) == str:
                                    try:
                                        tn_soup.find('testresult').string = str(tres)
                                    except IndexError:
                                        tn_soup.find('testresult').string = str("")

                            if 'lowtestrange' in row:
                                tn_soup.find('lowtestrange').string = str(row['lowtestrange'])

                            if 'hightestrange' in row:
                                tn_soup.find('hightestrange').string = str(row['hightestrange'])

                            if 'moreinformation' in row:
                                tn_soup.find('moreinformation').string = str(row['moreinformation'])

                            soup.append(tn_soup)

        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return soup

    def get_litrature_test_by_realtion_tag(self, REACTIONTESTRESULT):
        soup = self.soup
        for val in REACTIONTESTRESULT:
            entities = val['entities']
            tn_meddra = self.get_medra_code(str(entities[0]['TESTNAME']).strip())

            if tn_meddra > 0:
                tn_soup = BeautifulSoup(self.text, 'lxml-xml')
                try:
                    tn_soup.find('testname').string = str(tn_meddra)
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

                try:
                    tn_soup.find('testresult').string = str(entities[1]['TESTRESULT'])
                except Exception as e:
                    self.helper.error_log(
                        current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                soup.append(tn_soup)
        return soup
