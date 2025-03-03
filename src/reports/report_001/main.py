import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

connection = sqlite3.connect('../../rad_statistic.db')
cursor = connection.cursor()

query = """SELECT periodo, situacao, COUNT(*) AS total FROM rads GROUP BY periodo, situacao ORDER BY periodo, situacao;"""
cursor.execute(query)
rows = cursor.fetchall()
data = {'periodo': [], 'total': [], 'situacao': []}
for row in rows:
    if row[1] in ['Não Entregue', 'Não Homologado']:
        data['periodo'].append(row[0])
        data['total'].append(row[2])
        data['situacao'].append(row[1])
df = pd.DataFrame(data)
df = df.iloc[::-1].reset_index(drop=True)
print(df)

sns.set_theme(style="whitegrid")
g = sns.catplot(
    data=df, kind="bar",
    x="total", y="periodo", hue="situacao",
    errorbar="sd", palette="dark", alpha=.6, height=6
)
g.despine(left=True)
g.set_axis_labels("Total (UNIDADE)", "Período (ANO/SEMESTRE)")
for ax in g.axes.flat:
    for p in ax.patches:
        bar_value = p.get_width()
        if bar_value != 0:
            ax.annotate(f'{bar_value:.2f}',  # Display the width (value) of the bar
                        (bar_value, p.get_y() + p.get_height() / 2.),  # Position at the end of each bar
                        ha='right', va='center',  # Align text to the right and center vertically
                        fontsize=8, color='#191919',  # Font size and color
                        xytext=(5, 0),  # Offset text to avoid overlap with the bar
                        textcoords='offset points')
g.legend.set_title("")
plt.title('Quantidade de Relatórios de Atividades Não Entregues ou Não Homologados por Período', fontsize=14, fontweight='bold')
plt.xticks(rotation=45)
plt.savefig('imgs/report_001.png', dpi=600, bbox_inches='tight')
plt.show()

cursor.close()
connection.close()