import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import numpy as np
import scipy.stats as stats

connection = sqlite3.connect('../../rad_statistic.db')
cursor = connection.cursor()

periodo = ['2018/1', '2018/2', '2019/1', '2019/2', '2020/1', '2020/2', '2021/1', '2021/2', '2022/1', '2022/2', '2023/1', '2023/2', '2024/1']
output = {}
for p in periodo:
    query = f"""
        SELECT total
        FROM rads
        WHERE periodo = '{p}' and situacao = 'Homologado' and total > 0
        ORDER BY total
        """
    cursor.execute(query)
    rows = cursor.fetchall()
    dados = [row[0] for row in rows]
    estatistica_periodo = []
    estatistica_periodo.append(round(float(np.mean(dados)),2))
    estatistica_periodo.append(round(float(np.median(dados)),2))
    estatistica_periodo.append(round(float(stats.mode(dados)[0]),2))
    estatistica_periodo.append(round(float(np.std(dados)),2))
    estatistica_periodo.append(round(float(np.var(dados)),2))
    estatistica_periodo.append(round(float(np.max(dados)) - float(np.min(dados)),2))
    Q1 = np.percentile(dados, 25)  # 1º quartil (25%)
    estatistica_periodo.append(round(float(Q1),2))
    Q3 = np.percentile(dados, 75)  # 3º quartil (75%)
    estatistica_periodo.append(round(float(Q3),2))
    estatistica_periodo.append(round(float(Q3) - float(Q1),2))
    output[p] = estatistica_periodo
index = ['MÉDIA', 'MEDIANA', 'MODA', 'DESVIO PADRÃO', 'VARIÂNCIA', 'AMPLITUDE', 'Q1', 'Q3', 'IQR']
df = pd.DataFrame(output, index=index)
df.to_excel('estatistica_rad.xlsx', index=True)
cursor.close()
connection.close()