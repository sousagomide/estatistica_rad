import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

connection = sqlite3.connect('../../rad_statistic.db')
cursor = connection.cursor()

query = """SELECT 
	        periodo, 
	        ROUND(MIN(total),2) AS 'menor',
	        ROUND(MAX(total),2) AS 'maior',
	        ROUND(AVG(total),2) AS 'media'
        FROM rads
        WHERE situacao = 'Homologado' and total > 0.0
        GROUP BY periodo
        ORDER BY periodo;"""
cursor.execute(query)
rows = cursor.fetchall()
data_menor = {'periodo': [], 'menor': []}
data_maior = {'periodo': [], 'maior': []}
data_media = {'periodo': [], 'media': []}
for row in rows:
    data_menor['periodo'].append(row[0])
    data_menor['menor'].append(row[1])
    data_maior['periodo'].append(row[0])
    data_maior['maior'].append(row[2])
    data_media['periodo'].append(row[0])
    data_media['media'].append(row[3])

data = [data_menor, data_maior, data_media]
value = ['menor', 'maior', 'media']
report = ['report_001', 'report_002', 'report_003']
title = ['As menores homologações por período', 'As maiores homologações por período', 'As médias das homologações por período']
for i,j,k,l in zip(data, report, title, value):
    df = pd.DataFrame(i)
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(x='periodo', y=l, data=df)
    plt.xlabel('Período (ANO/SEMESTRE)', fontsize=12)
    plt.ylabel('Valor (UNIDADE)', fontsize=12)
    plt.xticks(rotation=90)
    for p in ax.patches:
        ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.1, f'{p.get_height():.1f}', ha='center', va='bottom', fontsize=10)
    plt.title(k, fontsize=14)
    plt.savefig(f'imgs/{j}.png', bbox_inches='tight')
cursor.close()
connection.close()