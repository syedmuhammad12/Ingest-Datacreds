# Report address full mapping
from .helper import helper
import pycountry
import spacy
from geotext import GeoText
import re
from .country import country
from inspect import currentframe, getframeinfo

current_filename = str(getframeinfo(currentframe()).filename)

# def upper_case(func):
#     def wrapper(self):
#         # print(self.key)
#         # exit(1)
#         a = func(self)
#         return a
#     return wrapper

class reporterAddress:
    def __init__(self, key):

        self.qualification = {
            "physician": 1,
            "pharmacist": 2,
            "other health professional": 3,
            "nurse": 3,
            "lawyer": 4,
            "consumer": 5,
            "consumer or other non-health professional": 5
        }
        self.key = key
        self.helper = helper()
        self.country_dictionary = {}
        self.country_name = ""
        self.country_code = ""

        # creating a countries dictionary with it alpha2 codes
        for country_names in pycountry.countries:
            self.country_dictionary[country_names.alpha_2] = country_names.name.lower()
            if key.lower().find(country_names.name.lower()) > -1:
                self.country_code = country_names.alpha_2
                self.country_name = country_names.name

        # Load English tokenizer, tagger, parser and NER
        self.nlp = spacy.load("en_core_web_trf")

    def get_address_split(self):
        name = ""
        city_name = ""
        country_name = self.country_name
        organisation = ""
        department = ""
        street = ""
        qualification_match = ""
        country_code = self.country_code
        text = self.key.strip()
        before_length = len(text)

        try:
            postal_code = re.findall(r"\d{5,}", text)[0]
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))
            postal_code = ''

        doc = self.nlp(text)
        for token in doc.ents:
            try:
                if token.label_ == "PERSON":
                    search_data = token.text
                    data = text.find(search_data)
                    name = text[:data + len(search_data)].strip()
                    text = text[data + len(search_data):].strip()
            except Exception as e:
                self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

            try:
                if token.label_ == "GPE":
                    country_value = token.text.lower() in self.country_dictionary.values()

                    if country_value:
                        if len(GeoText(token.text).cities) > 0:
                            city_name = text[text.find(token.text):].strip()
                            text = text[:text.find(token.text)].strip()
                        else:
                            if text.find(token.text) > -1:
                                country_name = text[text.find(token.text):].strip()
                                text = text[:text.find(token.text)].strip()

                            else:

                                country_name = city_name[city_name.find(token.text):].strip()
                                city_name = city_name[:city_name.find(token.text)].strip()
                    else:

                        exist = 0
                        temp = ""
                        for country_in in self.country_dictionary.values():
                            if token.text.lower().find(country_in) > -1:
                                exist = 1
                                temp = country_in.upper()
                                break
                        if exist == 0:
                            if len(token.text) > 2:
                                city_name = text[text.find(token.text):].strip()
                                text = text[:text.find(token.text)].strip()
                            else:
                                country_key = token.text in self.country_dictionary.keys()
                                if country_key:
                                    if text.find(token.text) > -1:
                                        country_name = text[text.find(token.text):].strip()
                                        text = text[:text.find(token.text)].strip()
                        else:
                            if text.find(temp) > -1:
                                country_name = text[text.find(temp):].strip()
                                text = text[:text.find(temp)].strip()
            except Exception as e:
                self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        try:
            r = re.compile(
                r"\bphysician\b|\bpharmacist\b|\bother health professional\b|\bnurse\b|\bconsumer\b|\bconsumer or other non-health professional\b",
                flags=re.I | re.X)
            text = text.replace(r.findall(text)[0].lower(), '')
            qualification = re.compile(re.escape(r.findall(text)[0].lower()), re.IGNORECASE)
            qualification_match = qualification.search(text).group()
            qualification_match = self.qualification[qualification_match.lower()]
            text = qualification.sub('', text).strip()
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        after_length = len(text.strip())
        try:
            if 0 < after_length < before_length:
                doc = self.nlp(text)
                count = 1
                for entity in doc.ents:
                    if entity.label_ == "ORG":

                        if count == 1:
                            organisation = text[:text.find(entity.text) + len(entity.text)].strip()
                            text = text[text.find(entity.text) + len(entity.text):].strip()
                            count = count + 1
                        elif count == 2:
                            department = text[:text.find(entity.text) + len(entity.text)].strip()
                            text = text[text.find(entity.text) + len(entity.text):].strip()
                            count = count + 1
        except Exception as e:
            self.helper.error_log(current_filename + " " + str(getframeinfo(currentframe()).lineno) + ":" + str(e))

        if len(text.strip()) > 0 and country_name != "" and name != "":
            street = text

        city_name = city_name.replace(postal_code, "")
        country_code = country(country_name).get_country_code()
        reporter_address = {
            "person": name,
            "city_name": city_name,
            "postal_code": postal_code,
            "country": country_name,
            "organisation": organisation,
            "department": department,
            "street": street,
            "qualification": qualification_match,
            "country_code":country_code,
            "text": text
        }
        return reporter_address

    def get_current_e2b(self):

        if self.key in self.qualification:
            return self.qualification[self.key]
        else:
            return 0
