import pandas as pd
from .linelistkey import linelistkey

keys = linelistkey().thisdict


class Json:
    def __init__(self, file_path):
        self.file_path = file_path

    def json_data(self):
        # print(self.file)
        # exit(1)
        skip_rows = []
        self.file = pd.read_excel(self.file_path)
        # print(self.file)
        # exit(1)
        flag = 0
        count = 0
        while flag == 0 and len(skip_rows) < 5:
            for index in self.file.columns:
                for key, value in keys.items():
                    if index.replace('\n', ' ') in value:
                        flag = 1
                        self.file.rename(columns={index: key}, inplace=True)
            if flag == 0:
                skip_rows.append(count)
                self.file = pd.read_excel(self.file_path, skiprows=skip_rows)
                count += 1
        # print('flag', flag)
        # print(skip_rows)
        # print(self.file)
        # exit(1)
        return self.file
