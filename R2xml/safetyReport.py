# safety data calculation
from .country import country
from .helper import helper
from .reportSourceE2b import reportSourceE2b
import datetime
import math
from inspect import currentframe, getframeinfo

current_filename = str(getframeinfo(currentframe()).filename)


class safetyReport:
    def __init__(self, key, code_template):
        self.key = key
        self.code_template = code_template
        self.helper = helper()
        self.safety_version = {
            "initial": 0,
            "followup": 1,
            "final": 2
        }

    # checks for empty fields
    def isNan(self, para):
        try:
            if math.isnan(para):
                return 0
        except Exception as e:
            return 1

    # to get timestamps
    def get_time(self):
        return str(datetime.datetime.now().time().hour) + str(datetime.datetime.now().time().minute) + str(
            datetime.datetime.now().time().second)

    # safety version calculation
    def get_safety_version(self):

        result = ''
        try:
            if 'safetyreportversion' in self.key:
                return self.safety_version[self.key['safetyreportversion']]
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return result

    # To get country for primary source, occurcountry
    def get_safety_country(self):
        result = ''
        try:
            if 'Country' in self.key:
                if self.isNan(self.key['Country']) == 1:
                    data = country(self.key['Country'])
                    result = data.get_country_code()
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return result

    def get_safety_cccur_country(self):
        result = ''
        try:
            if 'occurcountry' in self.key:
                if self.isNan(self.key['occurcountry']) == 1:
                    data = country(str(self.key['occurcountry']).replace(".", ""))
                    result = data.get_country_code()
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return result

    # gets a initial reporter country
    def get_reporter_country(self):
        result = ''
        try:
            if 'InitialReporter' in self.key:
                if self.isNan(self.key['InitialReporter']) == 1:
                    data = country(self.key['InitialReporter'])
                    result = data.get_country_code()
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return result

    # Report Type decision taken
    def get_report_type(self):
        result = '1'
        try:
            if 'Study' in self.key:
                if self.isNan(self.key['Study']) == 1:
                    data = reportSourceE2b(self.key['Study'])
                    result = data.get_study()
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
        return result

    def get_serious_tag(self):
        try:
            if self.key['PatientDied'][0] == 1 or self.key['LifeThreatening'][0] == 1 or \
                    self.key['InvolvedOrProlongedInpatientHospitalisation'][0] == 1 or self.key['Other'][0] == 1 or \
                    self.key['InvolvedPersistentOrSignificantDisabilityOrIncapacity'][0] == 1 or \
                    self.key['CongenitalAnomaly'][0] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_serious_death(self):
        try:
            if self.key['PatientDied'][0] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_serious_life_threatening(self):
        try:
            if self.key['LifeThreatening'][0] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_serious_hospitalization(self):
        try:
            if self.key['InvolvedOrProlongedInpatientHospitalisation'][0] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_serious_other(self):
        try:
            if self.key['Other'][0] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_serious_disability(self):
        try:
            if self.key['InvolvedPersistentOrSignificantDisabilityOrIncapacity'][0] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_serious_congenitalanomali(self):
        try:
            if self.key['CongenitalAnomaly'][0] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_med_serious_tag(self):
        try:
            if self.key['PatientDied'] == 1 or self.key['LifeThreatening'] == 1 or self.key['Hospitalization'] == 1 or \
                    self.key['OtherSerious'] == 1 or self.key['Disability'] == 1 or self.key['Congenital'] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_med_serious_death(self):
        try:
            if self.key['PatientDied'] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_med_serious_life_threatening(self):
        try:
            if self.key['LifeThreatening'] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_med_serious_hospitalization(self):
        try:
            if self.key['Hospitalization'] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_med_serious_other(self):
        try:
            if self.key['OtherSerious'] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_med_serious_disability(self):
        try:
            if self.key['Disability'] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')

    def get_med_serious_congenitalanomali(self):
        try:
            if self.key['Congenital'] == 1:
                return str('1')
            else:
                return str('2')
        except Exception as e:
            self.helper.error_log(
                current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            return str('2')