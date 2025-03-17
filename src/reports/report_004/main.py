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
    # query = f"""
    #     SELECT total
    #     FROM rads
    #     WHERE periodo = '{p}' and situacao = 'Homologado' and total > 0
    #     ORDER BY total
    #     """
    # cursor.execute(query)
    # rows = cursor.fetchall()
    # dados = [row[0] for row in rows]
    estatistica_periodo = []
    # Q1 = np.percentile(dados, 25)  # 1º quartil (25%)
    # Q3 = np.percentile(dados, 75)  # 3º quartil (75%)
    # estatistica_periodo.append([0, round(float(Q1),2)])
    # estatistica_periodo.append([round(float(Q1),2), round(float(np.median(dados)),2)])
    # estatistica_periodo.append([round(float(np.median(dados)),2), round(float(Q3),2)])
    # estatistica_periodo.append([round(float(Q3),2), None])
    estatistica_periodo.append([0, 100])
    estatistica_periodo.append([100, 150])
    estatistica_periodo.append([150, 200])
    estatistica_periodo.append([200, None])
    count_hist = {'Categoria': [], 'Valor': []}
    for i in estatistica_periodo:
        if i[1] == None:
            count_hist['Categoria'].append(f'Maior que {i[0]}')
            intervalo = f'total > {i[0]}'
        else:
            count_hist['Categoria'].append(f']{i[0]} - {i[1]}]')
            intervalo = f'(total > {i[0]} and total <= {i[1]})'
        query = f"""
            SELECT count(*)
            FROM rads
            WHERE periodo = '{p}' and situacao = 'Homologado' and {intervalo}
            ORDER BY total
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        count_hist['Valor'].append(rows[0][0])
    df = pd.DataFrame(count_hist)
    ax = sns.barplot(x='Categoria', y='Valor', data=df)
    for x in ax.patches:
        ax.annotate(f'{x.get_height()}',  (x.get_x() + x.get_width() / 2., x.get_height()-25),  ha='center', va='center', fontsize=12, fontweight='bold', color='white', xytext=(0, 5), textcoords='offset points')
    plt.title(f'Frequência da pontuação total por intervalo ({p})')
    plt.xlabel('Categoria (Intervalo)')
    plt.ylabel('Valor (Unidade)')
    plt.savefig(f'imgs/frequencia_{p.replace('/', '_')}.png', bbox_inches='tight')
    plt.close()

cursor.close()
connection.close()