import pandas as pd
from .jsonkeys import jsonkey
from bs4 import BeautifulSoup
from .medwatchkey import medwatchjsonkey

keys = jsonkey().thisdict
medkeys = medwatchjsonkey().thisdict


class Json:
    def __init__(self, json_file):
        self.json_file = json_file

    def remove_junk(self, str):
        str = str.replace('\n', ' ')
        str = str.replace('(cid:1)', '')
        str = str.replace(",", "")
        return str.strip()

    def json_data(self):
        df = pd.json_normalize(self.json_file['first_page_data'])

        # data = eval(self.json_file['from_second_page'])
        # from_second_page = pd.json_normalize(data)
        from_second_page = self.json_file['from_second_page']

        lst = df["key"].values

        f = {}
        # if any('REACTION ONSET' in st for st in lst):
        #     key = next(x for x in lst if 'REACTION ONSET' in x)
        #     value = df["value"].iloc[(df[df["key"] == key].index)[0]]
        #     f['Day_ReactionOnset']=value.split(" ")[0]
        #     f['Month_ReactionOnset']= value.split(" ")[1]
        #     f['Year_ReactionOnset']= value.split(" ")[2]
        # if any('DATE OF BIRTH' in st for st in lst):
        #     key = next(x for x in lst if 'DATE OF BIRTH' in x)
        #     value = df["value"].iloc[(df[df["key"] == key].index)[0]]
        #     f['Day_DOB']=value.split(" ")[0]
        #     f['Month_DOB']= value.split(" ")[1]
        #     f['Year_DOB']= value.split(" ")[2]
        # print(df["key"].str.lower())
        # exit(1)
        for search in lst:
            for key, value in keys.items():

                if search in value:
                    f[key] = df["value"].iloc[(df[df["key"].str.lower() == search.strip().lower()].index)[0]]

        # for index in from_second_page.columns:
        #     for key, value in keys.items():
        #         if index in value:
        #             str = self.remove_junk(BeautifulSoup(from_second_page[index][0], 'html.parser').text)
        #             str = str[str.find(index) + len(index):]
        #             f[key] = str

        # f['reporter_details']=self.json_file['reporter_details']
        f['png-data'] = self.json_file['from_png_data']
        data = pd.DataFrame([f], columns=f.keys())
        # data.to_csv(r"C:\Users\rakshith.gk\Downloads\data.csv")
        data = pd.DataFrame([f], columns=f.keys())
        data['VendorName'] = "BAXTER\JnJ"
        data['FileName_1'] = "CIOMS"
        data['template'] = self.json_file['template_name']
        return data

    def medwatch_json_data(self):
        df = pd.json_normalize(self.json_file)

        # data = eval(self.json_file['from_second_page'])
        # from_second_page = pd.json_normalize(data)

        lst = df["key"].values

        print(lst)
        print(df)

        f = {}
        # if any('REACTION ONSET' in st for st in lst):
        #     key = next(x for x in lst if 'REACTION ONSET' in x)
        #     value = df["value"].iloc[(df[df["key"] == key].index)[0]]
        #     f['Day_ReactionOnset']=value.split(" ")[0]
        #     f['Month_ReactionOnset']= value.split(" ")[1]
        #     f['Year_ReactionOnset']= value.split(" ")[2]
        # if any('DATE OF BIRTH' in st for st in lst):
        #     key = next(x for x in lst if 'DATE OF BIRTH' in x)
        #     value = df["value"].iloc[(df[df["key"] == key].index)[0]]
        #     f['Day_DOB']=value.split(" ")[0]
        #     f['Month_DOB']= value.split(" ")[1]
        #     f['Year_DOB']= value.split(" ")[2]
        # print(df["key"].str.lower())
        # exit(1)
        for search in lst:
            for key, value in medkeys.items():

                if search in value:
                    f[key] = df["value"].iloc[(df[df["key"].str.lower() == search.strip().lower()].index)[0]]

        data = pd.DataFrame([f], columns=f.keys())
        # data.to_csv(r"C:\Users\suma.k\Desktop\data.csv")
        # print(data)
        # return
        data['VendorName'] = "Akrimax"
        data['FileName_1'] = "MedWatch"
        data['template'] = "MedWatch"
        return data