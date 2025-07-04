import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import json
import datetime as dt
import yfinance as yf
import ast

# EXECUTAR  streamlit run dashboard.py
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

tipo_operacao = st.sidebar.selectbox(
    "Filtrar por tipo de operação",
    ["Todas as operações", "Apenas Compras e Vendas", "Apenas Venda a Descoberto"]
)

# Cria filtro dos ativo
df_filtered = df[df['Ativo'] == ativo]


if not df_filtered.empty:

    ###########################################################################################################
    # Cria um índice de datas baseado em 'Data Inicio' e 'Data Final'
    # Cria um índice de datas baseado em 'Data Inicio' e 'Data Final'
    data_inicio = df_filtered['Data Inicio'].iloc[0].date()
    data_inicio_str = data_inicio.strftime('%Y-%m-%d')
    end_date = dt.datetime.now().strftime('%Y-%m-%d')

    # Preparar dados para o resumo com base no filtro selecionado
    Lucro_por_entrada_compra = df_filtered['Lucro/Perda Por Entrada Compra'].iloc[0]
    Lucro_por_entrada_venda_descoberto = df_filtered['Lucro/Perda Por Entrada Venda Descoberto'].iloc[0]

    # Combinar e filtrar
    if tipo_operacao == "Todas as operações":
        operacoes_filtradas = Lucro_por_entrada_compra + Lucro_por_entrada_venda_descoberto
    elif tipo_operacao == "Apenas Compras e Vendas":
        operacoes_filtradas = Lucro_por_entrada_compra
    else:  # Apenas Venda a Descoberto
        operacoes_filtradas = Lucro_por_entrada_venda_descoberto

    # Cálculos dinâmicos
    numero_operacoes = len(operacoes_filtradas)
    numero_ganhas = sum(1 for op in operacoes_filtradas if op['Lucro Perda'] > 0)
    numero_perdidas = numero_operacoes - numero_ganhas
    lucro_total = sum(op['Lucro Perda'] for op in operacoes_filtradas)
    porcentagem_acerto = (numero_ganhas / numero_operacoes) * 100 if numero_operacoes else 0
    media_ganhos = (
        sum(op['Lucro Perda'] for op in operacoes_filtradas if op['Lucro Perda'] > 0) / numero_ganhas
        if numero_ganhas else 0
    )
    media_perdas = (
        sum(op['Lucro Perda'] for op in operacoes_filtradas if op['Lucro Perda'] < 0) / numero_perdidas
        if numero_perdidas else 0
    )
    media_dias = (
        sum(op['Dias Ativo'] for op in operacoes_filtradas) / numero_operacoes
        if numero_operacoes else 0
    )

    banca_inicial = df_filtered['Banca Inicial'].iloc[0]
    banca_final = banca_inicial + lucro_total
    total_dias = df_filtered['Total Dias Passados'].iloc[0]

    # Cotação atual
    dtd = yf.Ticker(ativo + '.SA')
    cotacao_atual = dtd.history(period='1d')
    cotacao_atual = cotacao_atual['Close'].iloc[0]

    # Sidebar dinâmico
    st.sidebar.markdown(f"**Cotação Atual:** {cotacao_atual:.2f}")
    st.sidebar.markdown(f"**Data de Inicio:** {data_inicio_str}")
    st.sidebar.markdown(f"**Data Final:** {end_date}")
    st.sidebar.markdown(f"**Banca Inicial:** R$ {banca_inicial:.2f}")
    st.sidebar.markdown(f"**Banca Final:** R$ {banca_final:.2f}")
    st.sidebar.markdown(f"**Lucro/Perda Total:** R$ {lucro_total:.2f}")
    st.sidebar.markdown(f"**Número Total de Operações:** {numero_operacoes}")
    st.sidebar.markdown(f"**Número de Operações Ganhas:** {numero_ganhas}")
    st.sidebar.markdown(f"**Número de Operações Perdidas:** {numero_perdidas}")
    st.sidebar.markdown(f"**Porcentagem de Acerto:** {porcentagem_acerto:.2f}%")
    st.sidebar.markdown(f"**Média de Ganhos:** {media_ganhos:.2f}")
    st.sidebar.markdown(f"**Média de Perdas:** {media_perdas:.2f}")
    st.sidebar.markdown(f"**Média de Dias Operações:** {media_dias:.0f}")
    st.sidebar.markdown(f"**Total de Dias Passados:** {total_dias}")

    # Entradas em aberto
    name = 'Sem Entrada em Aberto'
    data_inicio_new = ''
    valor_str = ''

    if tipo_operacao in ["Todas as operações", "Apenas Compras e Vendas"]:
        if 'Entrada Aberta Compra' in df_filtered.columns and not df_filtered['Entrada Aberta Compra'].isna().all():
            if df_filtered['Entrada Aberta Compra'].iloc[0]:
                name = 'Entrada em Aberto de Compra'
                data_inicio_new, valor_str = df_filtered['Entrada Aberta Compra'].iloc[0].split(", ")

    if tipo_operacao in ["Todas as operações", "Apenas Venda a Descoberto"]:
        if 'Entrada Aberta Venda Descoberto' in df_filtered.columns and not df_filtered[
            'Entrada Aberta Venda Descoberto'].isna().all():
            if df_filtered['Entrada Aberta Venda Descoberto'].iloc[0]:
                name = 'Entrada em Aberto de Venda a Descoberto'
                data_inicio_new, valor_str = df_filtered['Entrada Aberta Venda Descoberto'].iloc[0].split(", ")

    # Bloco em destaque
    st.sidebar.markdown(
        f"""
        <style>
            @keyframes blink {{
                0% {{ border-color: yellow; }}
                50% {{ border-color: transparent; }}
                200% {{ border-color: yellow; }}
            }}
        </style>
        <div style="border: 3px solid yellow; padding: 2px; border-radius: 5px; animation: blink 1s infinite;">
            <p><strong>{name}</strong></p>
            <p><strong>Data:</strong> {data_inicio_new}</p>
            <p><strong>Valor:</strong> {valor_str}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    ###########################################################################################################
    Lucro_por_entrada_compra = df_filtered['Lucro/Perda Por Entrada Compra'].iloc[0]

    # Função para definir a cor da borda com base no lucro ou perda
    def define_borda(lucro_perda):
        return "green" if lucro_perda > 0 else "red"


    if tipo_operacao in ["Todas as operações", "Apenas Compras e Vendas"] and Lucro_por_entrada_compra:
        # Layout para exibir os blocos de operações
        st.write("### Operações Finalizadas Compra")

        # Dividir operações em grupos de 7 blocos
        chunk_size = 6
        for i in range(0, len(Lucro_por_entrada_compra), chunk_size):
            colunas = st.columns(chunk_size)
            for idx, operacao in enumerate(Lucro_por_entrada_compra[i:i + chunk_size]):
                borda = define_borda(Lucro_por_entrada_compra[idx+i]['Lucro Perda'])

                # Usando HTML para estilizar cada bloco individualmente
                colunas[idx].markdown(
                    f"""
                        <div style="
                            border: 2px solid {borda}; 
                            padding: 2px; 
                            font-size: 16px;
                            border-radius: 10px; 
                            text-align: center; 
                            margin-bottom: 8px;
                        ">
                            <strong>Entrada:</strong> {Lucro_por_entrada_compra[idx+i]['Entrada']} | 
                            <strong> R$</strong> {Lucro_por_entrada_compra[idx+i]['Valor Entrada']}<br>
                            <strong>Saída:</strong> {Lucro_por_entrada_compra[idx+i]['Saida']} | 
                            <strong> R$</strong> {Lucro_por_entrada_compra[idx+i]['Valor Saida']}<br>
                            <strong>Lucro/Perda:</strong> {'+' if Lucro_por_entrada_compra[idx+i]['Lucro Perda'] > 0
                    else ''}{Lucro_por_entrada_compra[idx+i]['Lucro Perda']:.2f}
                        </div>
                        """,
                    unsafe_allow_html=True
                )
    ###########################################################################################################
    # Dados das operações
    Lucro_por_entrada_venda_descoberto = df_filtered['Lucro/Perda Por Entrada Venda Descoberto'].iloc[0]

    # Função para definir a cor da borda com base no lucro ou perda
    def define_borda(lucro_perda):
        return "green" if lucro_perda > 0 else "red"


    if tipo_operacao in ["Todas as operações", "Apenas Venda a Descoberto"] and Lucro_por_entrada_venda_descoberto:
        # Layout para exibir os blocos de operações
        st.write("### Operações Finalizadas Venda Descoberta")

        # Dividir operações em grupos de 7 blocos
        chunk_size = 6
        for i in range(0, len(Lucro_por_entrada_venda_descoberto), chunk_size):
            colunas = st.columns(chunk_size)
            for idx, operacao in enumerate(Lucro_por_entrada_venda_descoberto[i:i + chunk_size]):
                borda = define_borda(Lucro_por_entrada_venda_descoberto[idx+i]['Lucro Perda'])

                # Usando HTML para estilizar cada bloco individualmente
                colunas[idx].markdown(
                    f"""
                    <div style="
                        border: 2px solid {borda}; 
                        padding: 2px; 
                        font-size: 16px;
                        border-radius: 10px; 
                        text-align: center; 
                        margin-bottom: 8px;
                    ">
                        <strong>Entrada:</strong> {Lucro_por_entrada_venda_descoberto[idx+i]['Entrada']} | 
                        <strong> R$</strong> {Lucro_por_entrada_venda_descoberto[idx+i]['Valor Entrada']}<br>
                        <strong>Saída:</strong> {Lucro_por_entrada_venda_descoberto[idx+i]['Saida']} | 
                        <strong> R$</strong> {Lucro_por_entrada_venda_descoberto[idx+i]['Valor Saida']}<br>
                        <strong>Lucro/Perda:</strong> {'+' if Lucro_por_entrada_venda_descoberto[idx+i]['Lucro Perda'] > 0 
                    else ''}{Lucro_por_entrada_venda_descoberto[idx+i]['Lucro Perda']:.2f}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    ###########################################################################################################
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

            if isinstance(dff.columns[0], tuple):
                dff.columns = [col[0] for col in dff.columns]

            # Converter colunas para numérico
            for col in ['Open', 'High', 'Low', 'Close']:
                dff[col] = pd.to_numeric(dff[col], errors='coerce')

            # Garantir que o índice é datetime
            if not isinstance(dff.index, pd.DatetimeIndex):
                dff.index = pd.to_datetime(dff.index)

            # Remover linhas com valores ausentes
            dff = dff.dropna(subset=['Open', 'High', 'Low', 'Close'])

            # Verifica se as colunas necessárias estão presentes
            required_columns = ['Open', 'High', 'Low', 'Close']
            if all(col in dff.columns for col in required_columns):
                # Extrair dados de Evolucao Banca
                evolucao_banca = df_filtered['Evolucao Banca'].iloc[0]
                data_list = ast.literal_eval(evolucao_banca)
                y_values = [item[0] for item in data_list]
                x_values = [item[1] for item in data_list]

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
                    fig_data = [
                        go.Candlestick(
                            x=dff.index,
                            open=dff['Open'],
                            high=dff['High'],
                            low=dff['Low'],
                            close=dff['Close'],
                            name='Candle'
                        )]
                    # Filtrar sinais conforme o menu
                    if tipo_operacao in ["Todas as operações", "Apenas Compras e Vendas"]:
                        fig_data.extend([
                            go.Scatter(
                                x=[signal[0] for signal in buy_signals],
                                y=[signal[1] for signal in buy_signals],
                                mode='markers',
                                name='Compras',
                                marker=dict(symbol='triangle-up', color='green', size=15),
                                showlegend=True
                            ),
                            go.Scatter(
                                x=[signal[0] for signal in sell_signals],
                                y=[signal[1] for signal in sell_signals],
                                mode='markers',
                                name='Vendas',
                                marker=dict(symbol='triangle-down', color='red', size=15),
                                showlegend=True
                            ),
                            go.Scatter(
                                x=[buy_open[0]] if len(buy_open) > 1 else [],
                                y=[buy_open[1]] if len(buy_open) > 1 else [],
                                mode='markers',
                                marker=dict(symbol='star', color='green', size=15),
                                name='Abertura de Compra'
                            )
                        ])

                    if tipo_operacao in ["Todas as operações", "Apenas Venda a Descoberto"]:
                        fig_data.extend([
                            go.Scatter(
                                x=[signal[0] for signal in short_signals],
                                y=[signal[1] for signal in short_signals],
                                mode='markers',
                                name='Venda Descoberta',
                                marker=dict(symbol='triangle-down', color='black', size=10),
                                showlegend=True
                            ),
                            go.Scatter(
                                x=[signal[0] for signal in cover_signals],
                                y=[signal[1] for signal in cover_signals],
                                mode='markers',
                                name='Compra Descoberta',
                                marker=dict(symbol='triangle-up', color='blue', size=10),
                                showlegend=True
                            ),
                            go.Scatter(
                                x=[sell_open[0]] if len(sell_open) > 1 else [],
                                y=[sell_open[1]] if len(sell_open) > 1 else [],
                                mode='markers',
                                marker=dict(symbol='star', color='red', size=15),
                                name='Abertura de Venda'
                            )
                        ])

                    # Cria o gráfico
                    fig_candle = go.Figure(data=fig_data)

                    # Atualiza layout
                    fig_candle.update_layout(
                        title=f'Entradas',
                        xaxis_title='Data',
                        yaxis_title='Preço',
                        hovermode='closest'
                    )

                    # Gráfico de Evolução da Banca
                    # Recalcular a evolução da banca com base nas operações filtradas
                    banca_inicial = df_filtered['Banca Inicial'].iloc[0]
                    banca = banca_inicial
                    banca_points = [(banca, None)]  # Começa com valor inicial

                    # Ordenar todas as operações filtradas por data de saída
                    operacoes_ordenadas = sorted(operacoes_filtradas, key=lambda x: pd.to_datetime(x['Saida']))

                    for op in operacoes_ordenadas:
                        lucro = op['Lucro Perda']
                        banca += lucro
                        banca_points.append((banca, pd.to_datetime(op['Saida'])))

                    # Separar valores
                    y_valores = [pt[0] for pt in banca_points if pt[1] is not None]
                    x_valores = [pt[1] for pt in banca_points if pt[1] is not None]

                    # Gráfico
                    fig_banca = go.Figure(data=[
                        go.Scatter(
                            x=x_valores,
                            y=y_valores,
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
    ###########################################################################################################
else:
    st.warning("Nenhum ativo selecionado ou não há dados disponíveis para o ativo selecionado.")
