# its a helper class
from datetime import date

# from asyncio.log import logger
from django.db import connection
from bs4 import BeautifulSoup
import logging

# logging.root.handlers
# import logging.config
import r2import.configuration as con
import r2import.r2mapping as r2mapping
from r2import.views import *
from inspect import currentframe, getframeinfo

current_filename = str(getframeinfo(currentframe()).filename)


class helper:

    def __init__(self, tenant, r2xml_dict=None, file_name=None):
        self.tenant = tenant
        self.r2xml_dict = r2xml_dict
        self.file_name = file_name
        self.cursor = connection.cursor()
        self.r2_mapping = r2mapping.r2_mapping
        self.r2_mapping_date_format = r2mapping.r2_mapping_date_format

    def r2_mapping_data(self, key):
        data = ""
        try:
            data = self.r2xml_dict[self.r2_mapping[key]]
        except Exception as e:
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            try:
                map_data = self.r2_mapping[key].split('_')
                result = self.check_list_data_exist(map_data[0], map_data[1], 1)

                data = result
            except Exception as e:
                self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        return data

    def date_format_e2b(self, value, table_name, column_name):
        """102 - Format CCYYMMDD,610 - Format CCYYMM, 602 - Format CCYY"""
        data = ""

        try:
            e2b_date_code = int(self.r2xml_dict[
                                    self.r2_mapping_date_format[self.r2_mapping[table_name + "_" + column_name]]])
            if e2b_date_code == 102:

                data = value[0] + value[1] + value[2] + value[3] + "-" + value[4] + value[5] + "-" + value[6] + value[7]
            elif e2b_date_code == 610:
                data = value[0] + value[1] + value[2] + value[3] + "-" + value[4] + value[5] + "-01"
            elif e2b_date_code == 602:
                data = value[0] + value[1] + value[2] + value[3] + "-01-01"
        except Exception as e:
            e
        return data

    def duplicate_values(self, table_name, column_name, r2data, codelist_id, field_type):
        try:
            data = None
            if r2data != '':
                if codelist_id:
                    self.cursor.execute(
                        "SELECT * FROM " + self.tenant + ".codelist_code as cc JOIN " + self.tenant + "." + table_name + " as cm ON cc.code=cm." + column_name + " WHERE codelist_id=" + str(
                            codelist_id) + " AND e2b_code=" + str(r2data))

                    if self.cursor.rowcount > 0:
                        data = self.cursor.fetchall()
                else:
                    if field_type == "Date" or field_type == "date":
                        r2data = self.date_format_e2b(r2data, table_name, column_name)

                    self.cursor.execute(
                        "SELECT * FROM " + self.tenant + "." + table_name + " WHERE " + column_name + " ='" + str(
                            r2data) + "'")

                    if self.cursor.rowcount > 0:
                        data = self.cursor.fetchall()

            result = {'data': data}

            return result
        except Exception as e:
            print(e)
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return {'data': 0}

    def get_codelist_id(self, table_name, column_name):
        self.cursor.execute(
            "SELECT codelist_id FROM " + self.tenant + ".meta_data WHERE table_name LIKE '%" + table_name + "%'" "AND column_name LIKE '%" + column_name + "%'")
        row = self.cursor.fetchone()
        return row[0]

    def e2b_code(self, modal, column_name, key_code):
        """r2xml class function to get e2b_code"""
        try:

            table_name = self.get_table_name(modal)
            # print(table_name)
            codelist_id = self.get_codelist_id(table_name, column_name)
            self.cursor.execute(
                "SELECT e2b_code FROM " + self.tenant + ".codelist_code WHERE code= '" + str(
                    key_code) + "' " "AND codelist_id= " + str(codelist_id) + " ")
            e2b_code_data = self.cursor.fetchone()

            if e2b_code_data[0]:
                e2b_code_data = e2b_code_data[0]
            else:
                e2b_code_data = ""

        except Exception as e:
            # print(e,key_code)
            e2b_code_data = ""

        return e2b_code_data

    def simplesafety_code(self, modal, column_name, key_code):
        """r2import class function to get code"""

        try:

            table_name = self.get_table_name(modal)
            # print(table_name)
            codelist_id = self.get_codelist_id(table_name, column_name)
            self.cursor.execute(
                "SELECT code FROM " + self.tenant + ".codelist_code WHERE e2b_code= '" + str(
                    key_code) + "' " "AND codelist_id= " + str(codelist_id) + " ")
            code_data = self.cursor.fetchone()

            if code_data[0]:
                code_data = code_data[0]
            else:
                code_data = ""

        except Exception as e:
            # print(e,key_code)
            code_data = ""

        return code_data

    def get_table_name(self, modal):
        try:
            data = modal.objects.using(self.tenant).model._meta.db_table
        except Exception as e:
            # print(e,modal)
            data = ""
        return data

    def get_meddra_version_float(self, version_number):
        version_number = version_number.replace('v.', '')
        version_number = version_number.replace('v', '')
        return version_number

    def check_data_exist(self, key):
        data = None
        try:
            if len(self.r2xml_dict[key].strip()) > 0:
                data = self.r2xml_dict[key].strip()

        except Exception as e:
            # print(e)
            self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            data = None
        return data

    def check_list_data_exist(self, key, child_key, duplicate=0):
        data = None

        if duplicate == 1:
            try:

                if self.r2xml_dict[key]:
                    data_list = []
                    for values in self.r2xml_dict[key]:
                        soup = BeautifulSoup(str(values), 'lxml-xml')
                        data = soup.find(child_key).text.strip()
                        data_list.append(data)
                    data = data_list
            except Exception as e:
                data = None
                self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        else:
            try:

                if self.r2xml_dict[key]:
                    soup = BeautifulSoup(str(self.r2xml_dict[key][0]), 'lxml-xml')
                    data = soup.find(child_key).text.strip()
            except Exception as e:
                self.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
                data = None

        return data

    def string_remove_junk(self, key):
        """r2xml data import starts after all validations"""
        string = key.strip()
        # print("*****"+string+"*****")
        return string

    def error_log(self, message):
        filename = str(con.logs_path) + str(self.file_name) + '.txt'
        logging.basicConfig(filename=filename,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%d-%m-%Y %H:%M:%S',
                            level=logging.DEBUG, force=True)

        logging.error(message)
        self.logger = logging.getLogger('urbanGUI')

    def error_log_refresh(self, message):
        filename = con.logs_path + self.file_name + '.txt'
        # print(message)
        logging.basicConfig(filename=filename,
                            filemode='w',
                            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%d-%m-%Y %H:%M:%S',
                            level=logging.DEBUG, force=True)

        logging.error(message)
        self.logger = logging.getLogger('urbanGUI')
    

    # Pushpak
    def date_format_e2b_with_date_format_tag(self, value, dateformat):
        """102 - Format CCYYMMDD,610 - Format CCYYMM, 602 - Format CCYY"""
        data = ""

        try:
            e2b_date_code = int(dateformat)
            if e2b_date_code == 102:

                data = value[0] + value[1] + value[2] + value[3] + "-" + value[4] + value[5] + "-" + value[6] + value[7]
            elif e2b_date_code == 610:
                data = value[0] + value[1] + value[2] + value[3] + "-" + value[4] + value[5] + "-01"
            elif e2b_date_code == 602:
                data = value[0] + value[1] + value[2] + value[3] + "-01-01"
        except Exception as e:
            e
        return data


    def get_reaction_id_pk(self, case_no, drugrecuractionmeddraversion, drugrecuraction):
        
        # self.cursor.execute("SELECT reaction_id_pk FROM " + self.tenant + ".case_reaction WHERE case_id_fk = " + str(case_no)+ "")

        self.cursor.execute("SELECT reaction_id_pk FROM " + self.tenant + ".case_reaction WHERE case_id_fk = " + str(case_no)+ " and reaction_coded_version = '" + drugrecuractionmeddraversion +"' and reaction_coded_llt = " + drugrecuraction + "")

        row = self.cursor.fetchall()
        # return row[0]
        return row

    def get_product_id_fk(self, case_no, drugcharacterization_causality, medicinalproduct_causality):
        
        # self.cursor.execute("SELECT reaction_id_pk FROM " + self.tenant + ".case_reaction WHERE case_id_fk = " + str(case_no)+ "")

        self.cursor.execute("SELECT product_id_pk FROM " + self.tenant + ".case_product WHERE case_id_fk = " + str(case_no)+ " and product_name = '" + medicinalproduct_causality +"' and char_of_product = " + drugcharacterization_causality + "")

        row = self.cursor.fetchall()
        # return row[0]
        return row

    def get_all_reaction_id(self, case_no):
        
        self.cursor.execute("SELECT reaction_id_pk FROM " + self.tenant + ".case_reaction WHERE case_id_fk = " + str(case_no)+ "")
        row = self.cursor.fetchall()
        # return row[0]
        return row
    
    def get_product_id_pk(self, case_no):
        
        self.cursor.execute("SELECT product_id_pk FROM " + self.tenant + ".case_product WHERE case_id_fk = " + str(case_no)+ "")
        row = self.cursor.fetchall()
        # return row[0]
        return row

    def get_causality_id_pk(self, case_no):
        
        self.cursor.execute("SELECT causality_id_pk FROM " + self.tenant + ".case_causality WHERE case_id_fk = " + str(case_no)+ "")
        row = self.cursor.fetchall()
        # return row[0]
        return row

    def get_causality_id_fk(self, case_no, productidfk):
        
        self.cursor.execute("SELECT causality_id_pk FROM " + self.tenant + ".case_causality WHERE case_id_fk = " + str(case_no)+ " and product_id_fk = " + str(productidfk) + "")

        row = self.cursor.fetchone()
        return row[0]
        # return row
    
    def get_causality_reaction_id_pk(self, case_no, causality_id_fk, reaction_id_fk):

        self.cursor.execute("SELECT causality_reaction_id_pk FROM " + self.tenant + ".case_causality_reaction WHERE case_id_fk = " + str(case_no)+ " and causality_id_fk = " + str(causality_id_fk)+ " and reaction_id_fk =" + str(reaction_id_fk)+ "")

        row = self.cursor.fetchone()
        return row[0]
    

    def get_case_no(self, linked_report_no):
        row = ''
        try:
            self.cursor.execute(
            "SELECT distinct case_no FROM " + self.tenant + ".case_master WHERE company_no='"+ linked_report_no+"'")
            while True:
                row = self.cursor.fetchone()
                if row is None:  # better: if not row
                    break
                else:
                    return row[0]
            return row
        except Exception as e:
            return e

        
        
