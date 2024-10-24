import streamlit as st
import pandas as pd
import plotly.express as px
import json

# ocupar a pagina toda
st.set_page_config(layout='wide')

# Carregar dados do arquivo JSON
with open('dados_ativos.json', 'r') as f:
    data_json = [json.loads(line) for line in f]

df = pd.DataFrame(data_json)
df['Data Inicio'] = pd.to_datetime(df['Data Inicio'])
df['Data Final'] = pd.to_datetime(df['Data Final'])

ativo = st.sidebar.selectbox('Ativo', df['Ativo'].unique())

