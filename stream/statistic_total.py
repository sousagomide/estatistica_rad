import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sqlite3 as sql
from streamlit_option_menu import option_menu

class StatisticTotal:

    def __init__(self, df):
        self.df = df
        self.regulamento = ['2014/1 a 2016/2', '2017/1 a 2018/2', '2019/1 a 2022/2', '2023/1 a 2024/1']
    
    def load(self):
        st.header('Análise Estatística da Pontuação Total por Revisão de Regulamento')
        opcoes = st.selectbox(
            'Selecione o regulamento',
            (self.regulamento)
        )
        limit = self.definirIQR(opcoes)
        self.printLimit(limit)

    def printLimit(self, limit):
        df_limit = limit.round(2).transpose()
        df_limit.columns = ['Valores']
        df_limit.index = [
            'Primeiro Quartil', 
            'Terceiro Quartil', 
            'Intervalo Interquartil',
            'Limite Inferior',
            'Limite Superior']
        st.dataframe(df_limit)


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
        return df.loc[filtro, ["campus", "periodo", "total"]]
    
    def periodo_para_num(self, p):
        ano, semestre = map(int, p.split('/'))
        return ano * 10 + semestre



# Definir os limites
# Limite inferior = Q1 - 1.5 × IQR

# Limite superior = Q3 + 1.5 × IQR