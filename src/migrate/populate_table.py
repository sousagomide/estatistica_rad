import os
import re
import pandas as pd
import sqlite3

connection = sqlite3.connect('rad_statistic.db')
# contents = os.listdir('download')
contents = ['rad_2018_1.xlsx']
cursor = connection.cursor()
pattern = r'^(.*?)\s\((\d+)\)$'
for item in contents:
    path = f'download/{item}'
    df = pd.read_excel(path, engine='openpyxl')
    for index, row in df.iterrows():
        result = re.match(pattern, df.loc[index, 'Professor'])
        nome, siape = (result.group(1), result.group(2))
        cursor.execute(f'SELECT * FROM servidores WHERE siape = "{siape}"')
        rows = cursor.fetchall()
        if len(rows) == 0:
            campus = df.loc[index, 'Campus']
            cursor.execute(f'INSERT INTO servidores (siape, nome, campus) VALUES ("{siape}", "{nome}", "{campus}")')
            connection.commit()


        
cursor.close()
connection.close()
        