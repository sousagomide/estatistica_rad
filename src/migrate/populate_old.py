import os
import re
import pandas as pd
import sqlite3

df = pd.read_csv("cleaning/atividade_docente_relatorios-modulo-antigo.csv", delimiter=",")  # Ou "\t" para tabulação
select_columns = ['ano_letivo', 'periodo_letivo', 'campus', 'siape', 'professor', 'tipo_atividade', 'pontuacao_atividade', 'quantidade_atividade_relatorio']
df_filter = df[select_columns]
# print(df_filter.head())

df_filtrado = df_filter[(df_filter["ano_letivo"] == 2016) & 
                        (df_filter["periodo_letivo"] == 1) & 
                        (df_filter["siape"] == 2578102)]
# print(df_filtrado)
for index, row in df_filtrado.iterrows():
    # print(f"Linha {index}: {row.to_dict()}")
    print(f"{row['ano_letivo']}/{row['periodo_letivo']}")
    print(f"{row['siape']}")
    print(f"{row['professor']}")
    print(f"{row['pontuacao_atividade'] * row['quantidade_atividade_relatorio']}")