import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json
import numpy as np
import datetime as dt
import yfinance as yf
import ast

# ocupar a pagina toda
st.set_page_config(layout='wide')

# Carregar dados do arquivo JSON
with open('dados_ativos.json', 'r') as f:
    data_json = [json.loads(line) for line in f]

df = pd.DataFrame(data_json)
df['Data Inicio'] = pd.to_datetime(df['Data Inicio'])
df['Data Final'] = pd.to_datetime(df['Data Final'])
# Tratar a coluna 'Sinais de Venda Descoberto' para garantir que os valores sejam do tipo correto
def clean_column(value):
    if isinstance(value, float):
        # Se for um float, manter o valor ou convertê-lo para string
        return str(value)
    elif isinstance(value, list):
        # Se for uma lista, converter para string ou extrair o que você precisa
        return ', '.join(map(str, value))
    return str(value)  # Caso contrário, converter tudo para string

df['Sinais de Venda Descoberto'] = df['Sinais de Venda Descoberto'].apply(clean_column)
df['Sinais de Compra Venda Descoberta'] = df['Sinais de Compra Venda Descoberta'].apply(clean_column)
df['Entrada Aberta Compra'] = df['Entrada Aberta Compra'].apply(clean_column)
df['Entrada Aberta Venda Descoberto'] = df['Entrada Aberta Venda Descoberto'].apply(clean_column)
df['Sinais de Compra'] = df['Sinais de Compra'].apply(clean_column)
df['Sinais de Venda'] = df['Sinais de Venda'].apply(clean_column)
df['Evolucao Banca'] = df['Evolucao Banca'].apply(clean_column)

ativo = st.sidebar.selectbox('Ativo', df['Ativo'])

# Cria filtro dos ativo
df_filtered = df[df['Ativo'] == ativo]
if not df_filtered.empty:

    dados_historico = df_filtered['Dados Historico'].iloc[0]
    if dados_historico:
        # Cria um DataFrame a partir dos dados históricos
        try:
            dff = pd.DataFrame(dados_historico)
            #st.write(f"Dados históricos para {ativo}:", dff)  # Exibir dados para depuração

            # Verifica se as colunas necessárias estão presentes
            required_columns = ['Open', 'High', 'Low', 'Close']
            if all(col in dff.columns for col in required_columns):
                # Extrair dados de Evolucao Banca
                evolucao_banca = df_filtered['Evolucao Banca'].iloc[0]
                data_list = ast.literal_eval(evolucao_banca)
                y_values = [item[0] for item in data_list]
                x_values = [item[1] for item in data_list]

                # Verifica se dff e x_values/y_values têm dados
                if not dff.empty and y_values and x_values:
                    # Dados para os gráficos de Candle e Evolução da Banca
                    # Gráfico de Candlestick
                    fig_candle = go.Figure(data=[
                        go.Candlestick(
                        x=dff.index,
                        open=dff['Open'],
                        high=dff['High'],
                        low=dff['Low'],
                        close=dff['Close'],
                        name='Candle'
                        )
                    ])
                    fig_candle.update_layout(
                        title=f'Ativo {ativo} - Gráfico Candlestick',
                        xaxis_title='Data',
                        yaxis_title='Preço',
                        hovermode='closest'
                    )

                    # Evolução da banca (simulada para ilustrar)
                    # Gráfico de Evolução da Banca
                    fig_banca = go.Figure(data=[
                        go.Scatter(
                            x=x_values,
                            y=y_values,
                            mode='lines+markers',
                            name='Banca (R$)',
                            marker=dict(color='blue')
                        )
                    ])
                    fig_banca.update_layout(
                        title=f'Evolução da Banca - {ativo}',
                        xaxis_title='Data',
                        yaxis_title='Banca (R$)',
                        hovermode='closest'
                    )

                    # Exibir gráficos lado a lado
                    st.plotly_chart(fig_candle, use_container_width=True)
                    st.plotly_chart(fig_banca, use_container_width=True)
                else:
                    st.warning(f"Nenhum dado disponível para o gráfico de {ativo}.")
            else:
                st.error(f"O DataFrame de histórico não contém todas as colunas necessárias: {required_columns}.")
        except Exception as e:
            st.error(f"Erro ao processar dados para {ativo}: {e}")
    else:
        st.warning(f"Nenhum dado histórico encontrado para o ativo {ativo}.")
else:
    st.warning("Nenhum ativo selecionado ou não há dados disponíveis para o ativo selecionado.")

col3, col4, col5 = st.columns(3)
