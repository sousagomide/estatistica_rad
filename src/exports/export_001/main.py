import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

connection = sqlite3.connect('../../rad_statistic.db')
cursor = connection.cursor()

# Versões:
#    2014/1 a 2016/2
#    2017/1 a 2018/2
#    2019/1 a 2022/2
#    2023/1 ...

interval = [
    ['2014/2', '2015/1', '2015/2', '2016/1', '2016/2'],
    ['2017/1', '2017/2', '2018/1', '2018/2'],
    ['2019/1', '2019/2', '2020/1', '2020/2', '2021/1', '2021/2', '2022/1', '2022/2'],
    ['2023/1', '2023/2', '2024/1']    
]
category = ['total <= 0', 'total > 0']

for i in interval:
    i_label = ", ".join(f"'{item}'" for item in i)
    for j in category:
        filename = f"rads_{i[0].split('/')[0]}_{i[-1].split('/')[0]}_total_{'menor' if j == 'total <= 0' else 'maior'}_0"
        query = f"SELECT * FROM rads WHERE {j} AND situacao = 'Homologado' AND periodo IN ({i_label}) ORDER BY periodo"
        cursor.execute(query)
        rows = cursor.fetchall()
        data = {'id': [], 'periodo': [], 'situacao': [], 'total': [], 'aula': [], 'ensino': [], 'capacitacao': [], 'pesquisa': [], 'extensao': [], 'administracao': [], 'total_nao_homologado': [], 'siape': []}
        [data[column].append(line) for row in rows for line, column in zip(row, data.keys())]
        df = pd.DataFrame(data)
        df.to_excel(f'output/{filename}.xlsx', index=False)




# query = """SELECT periodo, situacao, COUNT(*) AS total FROM rads GROUP BY periodo, situacao ORDER BY periodo, situacao;"""
# cursor.execute(query)
# rows = cursor.fetchall()
# data = {'periodo': [], 'total': [], 'situacao': []}
# for row in rows:
#     if row[1] in ['Não Entregue', 'Não Homologado']:
#         data['periodo'].append(row[0])
#         data['total'].append(row[2])
#         data['situacao'].append(row[1])
# df = pd.DataFrame(data)
# df = df.iloc[::-1].reset_index(drop=True)
# # print(df)

# sns.set_theme(style="whitegrid")
# g = sns.catplot(
#     data=df, kind="bar",
#     x="total", y="periodo", hue="situacao",
#     errorbar="sd", palette="dark", alpha=.6, height=6
# )
# g.despine(left=True)
# g.set_axis_labels("Total (UNIDADE)", "Período (ANO/SEMESTRE)")
# for ax in g.axes.flat:
#     for p in ax.patches:
#         bar_value = p.get_width()
#         if bar_value != 0:
#             ax.annotate(f'{bar_value:.2f}',  # Display the width (value) of the bar
#                         (bar_value, p.get_y() + p.get_height() / 2.),  # Position at the end of each bar
#                         ha='right', va='center',  # Align text to the right and center vertically
#                         fontsize=8, color='#191919',  # Font size and color
#                         xytext=(5, 0),  # Offset text to avoid overlap with the bar
#                         textcoords='offset points')
# g.legend.set_title("")
# plt.title('Quantidade de Relatórios de Atividades Não Entregues ou Não Homologados por Período', fontsize=14, fontweight='bold')
# plt.xticks(rotation=45)
# plt.savefig('imgs/report_001.png', dpi=600, bbox_inches='tight')
# plt.show()

cursor.close()
connection.close()