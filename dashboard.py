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

#Lucro_por_entrada_venda_descoberto = df_filtered['Lucro/Perda Por Entrada Venda Descoberto'].iloc[0]
#Lucro_por_entrada_compra = df_filtered['Lucro/Perda Por Entrada Compra'].iloc[0]

data_str, valor_str = df_filtered['Entrada Aberta Compra'][0].split(", ")

if not df_filtered.empty:
    # Cria um índice de datas baseado em 'Data Inicio' e 'Data Final'
    data_inicio = df_filtered['Data Inicio'].iloc[0].date()  # Extrai apenas a parte da data
    data_inicio_str = data_inicio.strftime('%Y-%m-%d')  # Formato de data
    end_date = dt.datetime.now().strftime('%Y-%m-%d')

    # Blocos de Resumo na barra lateral
    dtd = yf.Ticker(ativo + '.SA')
    cotacao_atual = dtd.history(period='1d')
    cotacao_atual = cotacao_atual['Close'].iloc[0]
    st.sidebar.markdown(f"**Cotação Atual:** {cotacao_atual:.2f}")
    st.sidebar.markdown(f"**Data de Inicio:** {data_inicio_str}")
    st.sidebar.markdown(f"**Data Final:** {end_date}")
    st.sidebar.markdown(f"**Banca Inicial:** R$ {df_filtered['Banca Inicial'].iloc[0]:.2f}")
    st.sidebar.markdown(f"**Banca Final:** R$ {df_filtered['Banca Final'].iloc[0]:.2f}")
    st.sidebar.markdown(f"**Lucro/Perda Total:** R$ {df_filtered['Lucro Perda'].iloc[0]:.2f}")
    st.sidebar.markdown(f"**Número Total de Operações:** {df_filtered['Numero Operacoes'].iloc[0]}")
    st.sidebar.markdown(f"**Número de Operações Ganhas:** {df_filtered['Numero Operacoes Ganhas'].iloc[0]}")
    st.sidebar.markdown(f"**Número de Operações Perdidas:** {df_filtered['Numero Operacoes'].iloc[0] - df_filtered['Numero Operacoes Ganhas'].iloc[0]}")
    st.sidebar.markdown(f"**Porcentagem de Acerto:** {df_filtered['Porcentagem Acerto'].iloc[0] * 100:.2f}%")
    st.sidebar.markdown(f"**Média de Ganhos:** {df_filtered['Media Ganhos'].iloc[0]:.2f}")
    st.sidebar.markdown(f"**Média de Perdas:** {df_filtered['Media Perdas'].iloc[0]:.2f}")
    st.sidebar.markdown(f"**Média de Dias Operações:** {df_filtered['Media Dias Operacao'].iloc[0]:.0f}")
    st.sidebar.markdown(f"**Total de Dias Passados:** {df_filtered['Total Dias Passados'].iloc[0]:.0f}")

    name = 'Sem Entrada em Aberto'
    data_inicio_new = ''
    valor_str = ''

    if not df_filtered['Entrada Aberta Compra'].empty and df_filtered['Entrada Aberta Compra'].iloc[0]:
        name = 'Entrada em Aberto de Compra'
        data_inicio_new, valor_str = df_filtered['Entrada Aberta Compra'][0].split(", ")
    elif not df_filtered['Entrada Aberta Venda Descoberto'].empty and df_filtered['Entrada Aberta Venda Descoberto'].iloc[0]:
        name = 'Entrada em Aberto de Venda a Descoberto'
        data_inicio_new, valor_str = df_filtered['Entrada Aberta Compra'][0].split(", ")

    # Exibir as informações no sidebar dentro de um bloco com borda
    st.sidebar.markdown(
        f"""
        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px;">
            <p><strong>{name}</strong></p>
            <p><strong>Data:</strong> {data_inicio_new}</p>
            <p><strong>Valor:</strong> {valor_str}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    dados_historico = df_filtered['Dados Historico'].iloc[0]
    if dados_historico:
        # Cria um DataFrame a partir dos dados históricos
        try:
            # Cria um índice de datas baseado em 'Data Inicio' e 'Data Final'
            data_inicio = df_filtered['Data Inicio'].iloc[0].date()  # Extrai apenas a parte da data
            data_inicio_str = data_inicio.strftime('%Y-%m-%d')  # Formato de data
            end_date = dt.datetime.now().strftime('%Y-%m-%d')
            ticker = ativo + '.SA'  # Exemplo para ação da Azul (B3)
            dff = yf.download(ticker, start=data_inicio_str, end=end_date)


            # Verifica se as colunas necessárias estão presentes
            required_columns = ['Open', 'High', 'Low', 'Close']
            if all(col in dff.columns for col in required_columns):
                # Extrair dados de Evolucao Banca
                evolucao_banca = df_filtered['Evolucao Banca'].iloc[0]
                data_list = ast.literal_eval(evolucao_banca)
                y_values = [item[0] for item in data_list]
                x_values = [item[1] for item in data_list]

                # Função para obter sinais com tratamento de erro
                # Função para obter sinais com tratamento de erro
                def get_signals(column):
                    try:
                        signals = ast.literal_eval(df_filtered[column].iloc[0])
                        # Converter as datas dos sinais para datetime se forem strings
                        if signals:
                            for i in range(len(signals)):
                                if isinstance(signals[i][0], str):  # Verifica se a data é uma string
                                    signals[i][0] = pd.to_datetime(signals[i][0])  # Converte para datetime
                        return signals
                    except (ValueError, SyntaxError):
                        return []  # Retorna uma lista vazia se houver erro

                # Obtendo sinais de compra e venda
                buy_signals = get_signals('Sinais de Compra')
                sell_signals = get_signals('Sinais de Venda')
                short_signals = get_signals('Sinais de Venda Descoberto')
                cover_signals = get_signals('Sinais de Compra Venda Descoberta')
                buy_openn = df_filtered['Entrada Aberta Compra'].iloc[0]
                sell_openn = df_filtered['Entrada Aberta Venda Descoberto'].iloc[0]

                buy_open = []
                sell_open = []
                try:
                    data_str, valor_str = buy_openn.split(", ")
                    data = dt.datetime.strptime(data_str, '%Y-%m-%d')  # Converte a string para formato datetime
                    valor = float(valor_str)
                    buy_open = [data, valor]
                except:
                    pass
                try:
                    data_str, valor_str = sell_openn.split(", ")
                    data = dt.datetime.strptime(data_str, '%Y-%m-%d')  # Converte a string para formato datetime
                    valor = float(valor_str)
                    sell_open = [data, valor]
                except:
                    pass

                # Verifica se dff e x_values/y_values têm dados
                if not dff.empty and y_values and x_values:
                    # Dados para os gráficos de Candle e Evolução da Banca
                    # Gráfico de Candlestick
                    data = [
                        go.Candlestick(
                            x=dff.index,
                            open=dff['Open'],
                            high=dff['High'],
                            low=dff['Low'],
                            close=dff['Close'],
                            name='Candle'
                        ),
                        # Adicionando os sinais de compra (buy_signals)
                        go.Scatter(
                            x=[signal[0] for signal in buy_signals],
                            y=[signal[1] for signal in buy_signals],
                            mode='markers',
                            name='Compras',
                            marker=dict(symbol='triangle-up', color='green', size=15),
                            showlegend=True
                        ),
                        # Adicionando os sinais de venda (sell_signals)
                        go.Scatter(
                            x=[signal[0] for signal in sell_signals],
                            y=[signal[1] for signal in sell_signals],
                            mode='markers',
                            name='Vendas',
                            marker=dict(symbol='triangle-down', color='red', size=15),
                            showlegend=True
                        ),
                        # Adicionando sinais de short (short_signals)
                        go.Scatter(
                            x=[signal[0] for signal in short_signals],
                            y=[signal[1] for signal in short_signals],
                            mode='markers',
                            name='Venda Descoberta',
                            marker=dict(symbol='triangle-down', color='black', size=10),
                            showlegend=True
                        ),
                        # Adicionando sinais de cover (cover_signals)
                        go.Scatter(
                            x=[signal[0] for signal in cover_signals],
                            y=[signal[1] for signal in cover_signals],
                            mode='markers',
                            name='Compra Descoberta',
                            marker=dict(symbol='triangle-up', color='blue', size=10),
                            showlegend=True
                        ),
                        # Adicionando sinais de abertura de compra
                        go.Scatter(
                            x=[buy_open[0]] if len(buy_open) > 1 else [],
                            y=[buy_open[1]] if len(buy_open) > 1 else [],
                            mode='markers',
                            marker=dict(symbol='star', color='green', size=15),
                            name='Abertura de Compra'
                        ),
                        # Adicionando sinais de abertura de venda
                        go.Scatter(
                            x=[sell_open[0]] if len(sell_open) > 1 else [],
                            y=[sell_open[1]] if len(sell_open) > 1 else [],
                            mode='markers',
                            marker=dict(symbol='star', color='red', size=15),
                            name='Abertura de Venda'
                        )
                    ]
                    # Cria o gráfico
                    fig_candle = go.Figure(data=data)

                    # Atualiza layout
                    fig_candle.update_layout(
                        title=f'Entradas',
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
                        title=f'Evolução da Banca',
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
