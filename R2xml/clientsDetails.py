# get client details
from . import configuration as con
import pandas as pd
import json
import math


class clientsDetails:
    def isNan(self, para):
        try:
            if math.isnan(para):
                return 0
        except Exception as e:
            return 1

    def get_all_clients(self):
        return self.df.columns

    def get_client_details(self):
        result = {'sender': '', 'receiver': ''}
        self.key
        if self.isNan(self.key) == 1:
            for index, row in self.df.head().iterrows():
                if self.key in row:
                    if self.isNan(row[self.key]) == 1:
                        data = row[self.key].split('_')
                        result = {'sender': data[0], 'receiver': data[1]}
        return json.dumps(result)

    def __init__(self, key):
        self.df = pd.read_csv(con.clients_path)
        self.key = key
