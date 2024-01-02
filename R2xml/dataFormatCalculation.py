# get date calculation
import json
from .dateFormatE2b import dateFormatE2b
import datetime
import math
import re
from .helper import helper
from inspect import currentframe, getframeinfo

current_filename = str(getframeinfo(currentframe()).filename)


class dateFormatCalculation(object):
    def __init__(self):
        self.helper = helper()

    def date_verification(self, para):
        try:
            if math.isnan(para):
                return 0
        except Exception as e:
            # print(e)
            return 1

    def get_time(self):
        return str(datetime.datetime.now().time().hour) + str(datetime.datetime.now().time().minute) + str(
            datetime.datetime.now().time().second)

    def date_validate(self, date):
        return_date = date.lower().strip()
        list_junk = ["\\d+\\)", "unk", "unknown", "?", "ongoing", "1 )", "2 )", "#2", "#1", "#", "nan", "na", "1)",
                     "2)"]
        for x in list_junk:
            if len(return_date) > 0:
                temp = return_date.replace(x, "")
                return_date = temp
        return_date = return_date.strip()
        return_date = return_date.replace(" ", "-")
        return_date = return_date.replace("/", "-")
        return_date = return_date.replace("--", "")
        return_date = return_date.strip()
        if return_date:
            return return_date
        return 0

    def get_data(self, key, header=0):

        result = ''
        try:
            key = self.date_validate(key)
            if key != 0:

                data = key.split('-')
                if len(data) == 6:
                    month_number = dateFormatE2b(data[1])
                    year = int(data[2])
                    month_number_end = dateFormatE2b(data[4])
                    year_end = int(data[5])

                    result = str(year) + str(month_number.get_month_number()) + str(data[0]) + "_" + str(
                        year_end) + str(month_number_end.get_month_number()) + str(data[3])
                elif len(data) == 4:

                    month_number = dateFormatE2b(data[1])
                    year = str(int(data[2]))
                    if len(year) < 4:
                        year = "20" + year

                    result = year + str(month_number.get_month_number()) + str(data[0])
                elif len(data) == 3:
                    month_number = dateFormatE2b(data[1])
                    year = str(int(data[2]))
                    if len(year) < 4:
                        year = "20" + year

                    result = year + str(month_number.get_month_number()) + str(data[0])

                elif len(data) == 2:
                    month_number = dateFormatE2b(data[1])
                    result = str(month_number.get_month_number()) + data[0]
                elif len(data) > 6:
                    month_number = dateFormatE2b(data[1])
                    year = str(int(data[2]))
                    if len(year) < 4:
                        year = "20" + year

                    result = year + str(month_number.get_month_number()) + str(data[0])

                else:
                    result = data[0]
                if header == 0:
                    return result + self.get_time()
                else:
                    return result
            else:
                return result
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return result

    def get_date(self, key):
        key = str(key)
        date_string = key.strip().lower()
        patern = r"\s\d{2}:\d{2}:\d{2}$"
        date_string = re.sub(patern, '', date_string)
        print(date_string)
        date = ""
        try:
            if re.match(r'^\d{4}$', date_string):
                date = datetime.datetime.strptime(date_string, "%Y")
                date = date.strftime('%Y%m%d')
                return date

            elif re.match(r'^[A-Za-z]{3}\s\d{4}$', date_string) or re.match(r'^[A-Za-z]{3}-\d{4}$', date_string):
                date_str = date_string.replace("-", " ")
                date = datetime.datetime.strptime(date_str, "%b %Y")
                date = date.strftime('%Y%m%d')
                return date

            elif re.match(r'^\d{2}-[A-Za-z]{3}-\d{4}$', date_string):
                date = datetime.datetime.strptime(date_string, "%d-%b-%Y")
                date = date.strftime('%Y%m%d')
                return date

            elif re.match(r"^(0?[1-9]|[12][0-9]|3[01])-(0?[1-9]|1[0-2])-\d{4}$", date_string):
                date = datetime.datetime.strptime(date_string, "%d-%m-%Y")
                date = date.strftime("%Y%m%d")
                return date
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_string):
                date = date_string.replace('-', '')
                return date
            else:
                return ""
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

    def date_format_change(self, datevalue):
        try:
            print(datevalue)
            datevalue = re.sub(r'[^0-9/]', '', datevalue)
            # Parse the date string in the "dd/mm/yyyy" format 
            date_obj = datetime.datetime.strptime(datevalue, "%m/%d/%Y")
            # Format the date in the "yyyy/mm/dd" format
            formatted_date = date_obj.strftime("%Y/%m/%d")
            formatted_date = str(formatted_date.replace('/', ''))
        except Exception as e:
            # print(e)
            return 1

        return formatted_date
