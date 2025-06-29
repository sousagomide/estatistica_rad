import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sqlite3 as sql
from streamlit_option_menu import option_menu
from scipy.stats import norm, shapiro, kruskal
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import statsmodels.api as sm
import scikit_posthocs as sp
import seaborn as sns
import matplotlib.pyplot as plt

class StatisticCategory:

    def __init__(self, df):
        self.df = df
        self.regulamento = ['2018/1 a 2018/2', '2019/1 a 2022/2', '2023/1 a 2024/1']

    ######################################################################################
    ####### Visualização
    ######################################################################################

    def load(self):
        st.header('Análise Estatística da Pontuação por Categoria por Revisão de Regulamento')
        opcoes = st.selectbox('Selecione o regulamento', (self.regulamento))
        limit = self.definirIQR(opcoes)
        df = self.buscarRegulamento(opcoes)
        df_limit = self.filterLimit(limit, df)
        opcoesCampus = st.selectbox('Selecione o campus', (self.listarCampus(df_limit)))
        self.pizza(df_limit, opcoesCampus)
        self.barras_agrupadas(df_limit, opcoesCampus)
        self.quadroDocente()
        self.barras_agrupadas_individuos(df_limit, opcoesCampus)
        self.relacao_carga_horaria(df_limit, opcoesCampus, opcoes)
        self.diferentes_eixos(df_limit, opcoesCampus)


    def pizza(self, df, opcoesCampus):
        colunas_atividade = ["aula", "ensino", "capacitacao", "pesquisa", "extensao", "administracao"]
        color_scale = alt.Scale(scheme='tableau10')
        if opcoesCampus != 'TODOS':
            df = df[df['campus'] == opcoesCampus]
        totais = df[colunas_atividade].sum().reset_index()
        totais.columns = ['Atividade', 'Total']
        chart = alt.Chart(totais).mark_arc().encode(
            theta=alt.Theta(field='Total', type='quantitative'),
            color=alt.Color(field='Atividade', type='nominal', scale=color_scale),
            tooltip=[
                alt.Tooltip("Atividade", title="Atividade"),
                alt.Tooltip("Total", title="Total")
            ]
        ).properties(
            width=300,
            height=300
        )
        barras = alt.Chart(totais).mark_bar().encode(
            y=alt.Y('Atividade', sort='-x', title=''),
            x=alt.X('Total', title='Total'),
            color=alt.Color('Atividade', scale=color_scale, legend=None),
            tooltip=['Atividade', 'Total']
        ).properties(
            width=300,
            height=300
        )
        text = alt.Chart(totais).mark_text(
            align='left',
            baseline='middle',
            dx=3  # desloca o texto um pouco à direita
        ).encode(
            y=alt.Y('Atividade', sort='-x'),
            x=alt.X('Total'),
            text=alt.Text('Total')
        )
        grafico_combinado = alt.hconcat(chart, barras+text)
        st.subheader(f'Total de atividades realizadas - Campus: {opcoesCampus}')
        st.altair_chart(grafico_combinado, use_container_width=True)
        st.dataframe(totais)

    def barras_agrupadas(self, df, opcoesCampus):
        atividades = ["aula", "ensino", "capacitacao", "pesquisa", "extensao", "administracao"]
        color_scale = alt.Scale(scheme='tableau10')
        if opcoesCampus != 'TODOS':
            df = df[df['campus'] == opcoesCampus]
        df[atividades] = df[atividades].apply(pd.to_numeric, errors='coerce')
        df_agrupado = df.groupby('periodo')[atividades].sum().reset_index()
        df_melted = df_agrupado.melt(id_vars='periodo', 
                             value_vars=atividades,
                             var_name='Atividade', 
                             value_name='Total')
        df_melted = df_melted[df_melted['Total'].notnull()]
        chart = alt.Chart(df_melted).mark_bar().encode(
            x=alt.X('periodo:N', title='Período', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Total:Q', title='Total de Atividades'),
            color=alt.Color('Atividade:N', scale=color_scale, legend=alt.Legend(title='Atividade')),
            tooltip=['periodo', 'Atividade', 'Total'],
            xOffset='Atividade:N'
        ).properties(
            width=600,
            height=400
        )
        st.subheader('Atividades por Período')
        st.altair_chart(chart, use_container_width=True)
        df_pivotado = df_melted.pivot(
            index='Atividade',
            columns='periodo',
            values='Total'
        ).fillna(0).astype(int)
        st.dataframe(df_pivotado)
        variacao_percentual = ((df_pivotado.iloc[:, -1] - df_pivotado.iloc[:, 0]) / df_pivotado.iloc[:, 0]) * 100
        df_variacao = pd.DataFrame({
            'Atividade': df_pivotado.index,
            'Variação Percentual (%)': variacao_percentual.round(2)
        }).set_index('Atividade')
        styled_df = df_variacao.style \
        .applymap(self.colorir_valor) \
        .format("{:.2f}")
        st.write("**Variação Percentual do primero período em relação ao último período**")
        st.dataframe(styled_df)

    def barras_agrupadas_individuos(self, df, opcoesCampus):
        atividades = ["aula", "ensino", "capacitacao", "pesquisa", "extensao", "administracao"]
        color_scale = alt.Scale(scheme='tableau10')
        if opcoesCampus != 'TODOS':
            df = df[df['campus'] == opcoesCampus]
        df[atividades] = df[atividades].apply(pd.to_numeric, errors='coerce')
        df_individuos = df.copy()
        for atividade in atividades:
            df_individuos[atividade] = df_individuos[atividade].apply(lambda x: 1 if x != 0 else 0)
        df_contagem = df_individuos.groupby('periodo')[atividades].sum().reset_index()
        df_melted = df_contagem.melt(
            id_vars='periodo',
            value_vars=atividades,
            var_name='Atividade',
            value_name='Quantidade de Docentes'
        )
        df_melted = df_melted[df_melted['Quantidade de Docentes'].notnull()]
        chart = alt.Chart(df_melted).mark_bar().encode(
            x=alt.X('periodo:N', title='Período', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Quantidade de Docentes:Q', title='Docentes Participantes'),
            color=alt.Color('Atividade:N', scale=color_scale, legend=alt.Legend(title='Atividade')),
            tooltip=['periodo', 'Atividade', 'Quantidade de Docentes'],
            xOffset='Atividade:N'
        ).properties(
            width=600,
            height=400
        )
        st.subheader('Quantidade de docentes que prestam serviço nos eixos (aula, ensino, extensão, pesquisa, capacitação e administração e representação)')
        st.altair_chart(chart, use_container_width=True)
        df_pivotado = df_melted.pivot(
            index='Atividade',
            columns='periodo',
            values='Quantidade de Docentes'
        ).fillna(0).astype(int)
        st.dataframe(df_pivotado)

    def relacao_carga_horaria(self, df, opcoesCampus, opcoes):
        if opcoesCampus != 'TODOS':
            df = df[df['campus'] == opcoesCampus]

        valor_aula = 0.25 if opcoes == '2018/1 a 2018/2' else 0.35 if opcoes == '2019/1 a 2022/2' else 0.40
        df['carga_semanal'] = df['aula'] / (valor_aula * 20)

        bins = [0, 12, 18, float('inf')]
        labels = ['0 a 12h', '12 a 18h', 'Acima de 18h']
        df['faixa_carga'] = pd.cut(df['carga_semanal'], bins=bins, labels=labels, right=False)

        df_faixas = df.groupby(['periodo', 'faixa_carga']).size().reset_index(name='quantidade')
        df_faixas['faixa_carga'] = pd.Categorical(df_faixas['faixa_carga'], categories=labels, ordered=True)
        df_faixas = df_faixas.sort_values(['periodo', 'faixa_carga'])

        chart = alt.Chart(df_faixas).mark_bar().encode(
            x=alt.X('periodo:N', title='Período'),
            xOffset='faixa_carga:N',  # distribui as barras dentro de cada grupo período
            y=alt.Y('quantidade:Q', title='Número de Docentes'),
            color=alt.Color('faixa_carga:N', legend=alt.Legend(title='Faixa de Carga')),
            tooltip=['periodo', 'faixa_carga', 'quantidade']
        ).properties(
            width=700,
            height=400
        )
        st.subheader("Número de Docentes por Período e Faixa de Carga Horária")
        st.altair_chart(chart, use_container_width=True)
        df_pivot = df_faixas.pivot(index='periodo', columns='faixa_carga', values='quantidade').fillna(0).astype(int)
        st.dataframe(df_pivot)

    def diferentes_eixos(self, df, opcoesCampus):
        if opcoesCampus != 'TODOS':
            df = df[df['campus'] == opcoesCampus]
        st.subheader("Porcentagem de Docentes que atuam em diferentes eixos")
        opcoes = ['administracao', 'aula', 'capacitacao', 'ensino', 'extensao', 'pesquisa']
        selecionados = st.multiselect('Selecione os eixos:', options = opcoes, default = ['aula'])
        if not selecionados:
            st.warning("Por favor, selecione pelo menos um eixo para exibir o gráfico.")
            return
        df_filtrado = df[(df[selecionados] > 0).all(axis=1)]
        df_agrupado = df_filtrado.groupby('periodo').size().reset_index(name='count')
        area_chart = alt.Chart(df_agrupado).mark_area(opacity=0.3).encode(
            x='periodo:N',
            y='count:Q',
            tooltip=['periodo', 'count']
        ).properties(
            title='Contagem por Período (Área)',
            width=400,
            height=300
        )

        st.altair_chart(area_chart)
        st.dataframe(df_agrupado)
        
        



    def colorir_valor(self, val):
        if val > 0:
            return 'background-color: #d4edda'  # verde claro
        elif val < 0:
            return 'background-color: #f8d7da'  # vermelho claro
        return ''

    def quadroDocente(self):
        dados = {
            'ano': [2018, 2019, 2020, 2021, 2022, 2023],
            'número de docentes': [774, 812, 792, 814, 820, 805],
            'docente efetivo': [674, 721, 722, 729, 726, 713]
        }
        df_docentes = pd.DataFrame(dados)
        
        # Transformando os dados para o formato adequado para o gráfico
        df_melted = df_docentes.melt(id_vars=['ano'], var_name='Tipo de Docente', value_name='Quantidade')

        # Garantindo que "Tipo de Docente" seja tratado como uma variável categórica
        df_melted['Tipo de Docente'] = df_melted['Tipo de Docente'].astype(str)

        # Gráfico de linha
        chart = alt.Chart(df_melted).mark_line().encode(
            x='ano:O',  # Eixo X com os anos
            y='Quantidade:Q',  # Eixo Y com o número de docentes
            color='Tipo de Docente:N',  # Cor por tipo de docente (número de docentes ou efetivos)
            tooltip=['ano', 'Tipo de Docente', 'Quantidade']  # Tooltip para mostrar valores
        ).properties(
            width=600,
            height=400
        )

        # Exibindo o gráfico no Streamlit
        st.subheader("Número de Docentes e Docente Efetivo (Plataforma Nilo Peçanha)")
        st.altair_chart(chart, use_container_width=True)
        # st.subheader("Tabela de Docentes por Ano (Plataforma Nilo Peçanha)")
        st.dataframe(df_docentes)
        


    ######################################################################################
    ####### Método
    ######################################################################################
    def definirIQR(self, regulamento):
        df = self.buscarRegulamento(regulamento)
        descricao = df.describe()
        return pd.DataFrame({
            'q1': descricao.loc["25%"], 
                'q3': descricao.loc["75%"], 
            'iqr': (descricao.loc["75%"] - descricao.loc["25%"]),
            'limitinf': (descricao.loc["25%"] - 1.5 * (descricao.loc["75%"] - descricao.loc["25%"])).clip(lower=0),
            'limitsup': descricao.loc["75%"] + 1.5 * (descricao.loc["75%"] - descricao.loc["25%"])
        })

    def buscarRegulamento(self, regulamento):
        inicio, fim = regulamento.split(' a ')
        df = self.df.copy()
        df["periodo_num"] = df["periodo"].apply(self.periodo_para_num)        
        filtro = (df["periodo_num"] >= self.periodo_para_num(inicio)) & (df["periodo_num"] <= self.periodo_para_num(fim))
        return df.loc[filtro, ["campus", "periodo", "total", "aula", "ensino", "capacitacao", "pesquisa", "extensao", "administracao"]]
    
    def periodo_para_num(self, p):
        ano, semestre = map(int, p.split('/'))
        return ano * 10 + semestre
    
    def filterLimit(self, limit, df):
        df_filter = df.copy()
        # return df_filter[(df_filter['total'] >= limit.loc['total', 'limitinf']) & (df_filter['total'] <= limit.loc['total', 'limitsup'])]
        return df_filter[(df_filter['total'] >= limit.loc['total', 'limitinf'])]
    
    def listarCampus(self, df):
        valores_ordenados = sorted(df['campus'].dropna().unique().tolist())
        valores_ordenados.insert(0, 'TODOS')
        return valores_ordenados
