import os
import re
import json
import pandas as pd

contents = os.listdir('download')
for item in contents:
    path = f'download/{item}'
    df = pd.read_excel(path, engine='openpyxl')
    for index, row in df.iterrows():
        print(df.loc[index, 'Campus'])