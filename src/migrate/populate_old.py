import os
import re
import pandas as pd
import sqlite3

connection = sqlite3.connect('auxiliar_database.db')
cursor = connection.cursor()

df = pd.read_csv("cleaning/atividade_docente_relatorios-modulo-antigo.csv", delimiter=",")  # Ou "\t" para tabulação
select_columns = ['ano_letivo', 'periodo_letivo', 'campus', 'siape', 'professor', 'tipo_atividade', 'pontuacao_atividade', 'quantidade_atividade_relatorio', 'status_relatorio']
df_filter = df[select_columns]

semestres = [[2014, 2], [2015, 1], [2015, 2], [2016, 1], [2016, 2], [2017, 1], [2017, 2]]
for i in semestres:
    df_filtrado = df_filter[(df_filter["ano_letivo"] == i[0]) & (df_filter["periodo_letivo"] == i[1])]
    distinct_df = df_filtrado.drop_duplicates(subset=['siape'])
    for index, row in distinct_df.iterrows():
        # print(f"{row['siape']} - {row['professor']}")
        servidor = df_filtrado[(df_filtrado['siape'] == row['siape'])]
        query = f"SELECT * FROM servidores WHERE siape = '{row['siape']}'"
        cursor.execute(query)
        if len(cursor.fetchall()) == 0:
            query = f"INSERT INTO servidores (siape, nome, campus) VALUES ('{row['siape']}', '{row['professor']}', '{row['campus']}')"
            cursor.execute(query)
            connection.commit()
        df_atividades = df_filtrado[(df_filtrado['siape'] == row['siape'])]
        total = round(sum([row2['pontuacao_atividade'] * row2['quantidade_atividade_relatorio'] for index2, row2 in df_atividades.iterrows()]), 2)
        query = f"INSERT INTO rads (periodo, situacao, total, aula, ensino, capacitacao, pesquisa, extensao, administracao, total_nao_homologado, siape) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        situacao = ''
        if row['status_relatorio'] in [0, 1, 2, 3]:
            situacao = 'Homologado'
        elif row['status_relatorio'] == 4:
            situacao = 'Não Homologado'
        values = (f"{row['ano_letivo']}/{row['periodo_letivo']}", situacao, total, 0, 0, 0, 0, 0, 0, 0, row['siape'])
        cursor.execute(query, values)
        connection.commit()
    query = f"SELECT campus, periodo, nome || ' (' || servidores.siape || ')' AS nome_siape, situacao, total, aula, ensino, capacitacao, pesquisa, extensao, administracao, total_nao_homologado FROM rads, servidores WHERE rads.siape = servidores.siape AND periodo = ?"
    values = (f"{i[0]}/{i[1]}",)
    filename = f"rad_{i[0]}_{i[1]}"
    cursor.execute(query, values)
    lines = cursor.fetchall()
    data = {'Campus': [], 'Periodo letivo': [], 'Professor': [], 'Situação': [], 'Total': [], 'Aula': [], 'Ensino': [], 'Capacitação': [], 'Pesquisa': [], 'Extensão': [], 'Administração e Representação': [], 'Total não homologado': []}
    [data[column].append(l2) for l in lines for l2, column in zip(l, data.keys())]
    # for l in lines:
    #     for l2, column in zip(l, data.keys()):
    #         if column == 'Professor':
    #             data[column].append(f"{l2} ({siape})")
    #         else: 
    #             data[column].append(l2)
    df = pd.DataFrame(data)
    df.to_excel(f'output/{filename}.xlsx', index=False)
cursor.close()
connection.close()