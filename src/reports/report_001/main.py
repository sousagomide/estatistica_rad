import os
import re
import pandas as pd
import sqlite3

connection = sqlite3.connect('../../rad_statistic.db')
cursor = connection.cursor()

query = """SELECT periodo, situacao, COUNT(*) AS total FROM rads GROUP BY periodo, situacao ORDER BY periodo, situacao;"""
cursor.execute(query)
rows = cursor.fetchall()
print(rows)

cursor.close()
connection.close()